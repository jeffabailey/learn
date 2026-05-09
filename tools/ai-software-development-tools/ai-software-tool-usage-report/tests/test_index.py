"""Tests for index.py — the report orchestrator.

Adapters are stubbed out so these tests don't need network or env vars."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest

import index
from vendors.base import VendorReport


# --- helpers ---------------------------------------------------------------

@dataclass
class _StubAdapter:
    name: str
    tool: str
    report: VendorReport | Exception

    def fetch(self, env, period_start, period_end):
        if isinstance(self.report, Exception):
            raise self.report
        return self.report


def _make_report(vendor: str, tool: str, *, cost: float | None = 12.5,
                 tokens: int | None = 1000, period=(date(2026, 5, 1), date(2026, 5, 31))) -> VendorReport:
    return VendorReport(
        vendor=vendor,
        tool=tool,
        period_start=period[0],
        period_end=period[1],
        monthly_cost_usd=cost,
        active_users=None,
        licensed_seats=None,
        tokens_or_requests=tokens,
        pricing_model="token",
        notes="ok",
    )


# --- _month_range ----------------------------------------------------------

def test_month_range_uses_explicit_month():
    start, end = index._month_range("2026-02")
    assert start == date(2026, 2, 1)
    assert end == date(2026, 2, 28)


def test_month_range_handles_leap_year():
    start, end = index._month_range("2024-02")
    assert end == date(2024, 2, 29)


def test_month_range_defaults_to_today(monkeypatch):
    class _FrozenDate(date):
        @classmethod
        def today(cls):
            return date(2026, 7, 15)

    monkeypatch.setattr(index, "date", _FrozenDate)
    start, end = index._month_range(None)
    assert start == date(2026, 7, 1)
    assert end == date(2026, 7, 31)


# --- _parse_args -----------------------------------------------------------

def test_parse_args_defaults():
    args = index._parse_args([])
    assert args.month is None
    assert args.output is None


def test_parse_args_reads_month_and_output():
    args = index._parse_args(["--month", "2026-04", "--output", "/tmp/x"])
    assert args.month == "2026-04"
    assert args.output == "/tmp/x"


# --- _write_csv ------------------------------------------------------------

def test_write_csv_round_trip(tmp_path: Path):
    rows = [
        _make_report("VendorA", "ToolA", cost=10.0, tokens=500),
        VendorReport.skipped("VendorB", "ToolB", "missing key", date(2026, 5, 1), date(2026, 5, 31)),
    ]
    output = tmp_path / "out.csv"

    index._write_csv(output, rows)

    with output.open() as fh:
        loaded = list(csv.DictReader(fh))
    assert [row["vendor"] for row in loaded] == ["VendorA", "VendorB"]
    assert loaded[0]["monthly_cost_usd"] == "10.00"
    assert loaded[0]["tokens_or_requests"] == "500"
    assert loaded[1]["monthly_cost_usd"] == ""
    assert loaded[1]["notes"].startswith("SKIPPED:")


def test_write_csv_uses_expected_headers(tmp_path: Path):
    output = tmp_path / "out.csv"
    index._write_csv(output, [])
    with output.open() as fh:
        header = fh.readline().strip().split(",")
    assert header == index.CSV_FIELDS


# --- main ------------------------------------------------------------------

def test_main_writes_csv_with_one_row_per_adapter(monkeypatch, tmp_path: Path, capsys):
    adapters = [
        _StubAdapter("VendorA", "ToolA", _make_report("VendorA", "ToolA")),
        _StubAdapter("VendorB", "ToolB", _make_report("VendorB", "ToolB", cost=None, tokens=None)),
    ]
    monkeypatch.setattr(index, "ADAPTERS", adapters)
    monkeypatch.delenv("ANTHROPIC_ADMIN_KEY", raising=False)
    # Prevent .env from being read
    monkeypatch.setattr(index, "load_dotenv", lambda *a, **kw: None)

    rc = index.main(["--month", "2026-05", "--output", str(tmp_path)])
    assert rc == 0

    output = tmp_path / "ai-tool-usage-2026-05.csv"
    assert output.exists()
    with output.open() as fh:
        rows = list(csv.DictReader(fh))
    assert [row["vendor"] for row in rows] == ["VendorA", "VendorB"]


def test_main_records_adapter_exception_as_skipped(monkeypatch, tmp_path: Path):
    boom = _StubAdapter("Boom", "Toolish", AttributeError("'str' object has no attribute 'get'"))
    monkeypatch.setattr(index, "ADAPTERS", [boom])
    monkeypatch.setattr(index, "load_dotenv", lambda *a, **kw: None)

    rc = index.main(["--month", "2026-05", "--output", str(tmp_path)])
    assert rc == 0

    output = tmp_path / "ai-tool-usage-2026-05.csv"
    with output.open() as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["vendor"] == "Boom"
    assert rows[0]["notes"].startswith("SKIPPED: adapter raised AttributeError")
    assert "'str' object has no attribute 'get'" in rows[0]["notes"]


def test_main_uses_output_dir_env_when_no_flag(monkeypatch, tmp_path: Path):
    adapter = _StubAdapter("VendorA", "ToolA", _make_report("VendorA", "ToolA"))
    monkeypatch.setattr(index, "ADAPTERS", [adapter])
    monkeypatch.setattr(index, "load_dotenv", lambda *a, **kw: None)
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

    rc = index.main(["--month", "2026-05"])
    assert rc == 0
    assert (tmp_path / "ai-tool-usage-2026-05.csv").exists()


def test_main_creates_missing_output_dir(monkeypatch, tmp_path: Path):
    adapter = _StubAdapter("VendorA", "ToolA", _make_report("VendorA", "ToolA"))
    monkeypatch.setattr(index, "ADAPTERS", [adapter])
    monkeypatch.setattr(index, "load_dotenv", lambda *a, **kw: None)
    nested = tmp_path / "does" / "not" / "exist"

    rc = index.main(["--month", "2026-05", "--output", str(nested)])
    assert rc == 0
    assert (nested / "ai-tool-usage-2026-05.csv").exists()
