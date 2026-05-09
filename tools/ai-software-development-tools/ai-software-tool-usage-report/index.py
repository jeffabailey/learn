"""Entry point for the AI software tool usage report.

Reads .env, calls each vendor adapter, and writes one CSV summarising
monthly cost, active users, licensed seats, and token / request counts
for every configured vendor. Idempotent: rerunning for the same month
overwrites the same CSV file.

Usage:
    uv run python index.py                  # current month
    uv run python index.py --month 2026-04  # specific month
    uv run python index.py --output ./out   # custom output dir
"""
from __future__ import annotations

import argparse
import calendar
import csv
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from vendors import ADAPTERS, VendorReport


CSV_FIELDS = [
    "vendor",
    "tool",
    "period_start",
    "period_end",
    "monthly_cost_usd",
    "active_users",
    "licensed_seats",
    "tokens_or_requests",
    "pricing_model",
    "notes",
]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    load_dotenv(override=False)
    env = dict(os.environ)

    period_start, period_end = _month_range(args.month)
    output_dir = Path(args.output or env.get("OUTPUT_DIR") or ".")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"ai-tool-usage-{period_start:%Y-%m}.csv"

    rows: list[VendorReport] = []
    for adapter in ADAPTERS:
        print(f"  -> {adapter.name} ({adapter.tool})", file=sys.stderr)
        try:
            rows.append(adapter.fetch(env, period_start, period_end))
        except Exception as exc:  # noqa: BLE001 - one vendor's failure should not block the report
            rows.append(
                VendorReport.skipped(
                    adapter.name,
                    adapter.tool,
                    f"adapter raised {type(exc).__name__}: {exc}",
                    period_start,
                    period_end,
                )
            )

    _write_csv(output_path, rows)
    print(f"wrote {output_path} ({len(rows)} rows)")
    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="ai-usage-report", description=__doc__)
    parser.add_argument(
        "--month",
        help="YYYY-MM (defaults to current month). The window covers the full calendar month.",
    )
    parser.add_argument("--output", help="Directory for the CSV (defaults to OUTPUT_DIR env or '.').")
    return parser.parse_args(argv)


def _month_range(month_arg: str | None) -> tuple[date, date]:
    today = date.today()
    if month_arg:
        year, month = (int(part) for part in month_arg.split("-", 1))
    else:
        year, month = today.year, today.month
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _write_csv(path: Path, rows: list[VendorReport]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "vendor": row.vendor,
                    "tool": row.tool,
                    "period_start": row.period_start.isoformat(),
                    "period_end": row.period_end.isoformat(),
                    "monthly_cost_usd": "" if row.monthly_cost_usd is None else f"{row.monthly_cost_usd:.2f}",
                    "active_users": "" if row.active_users is None else row.active_users,
                    "licensed_seats": "" if row.licensed_seats is None else row.licensed_seats,
                    "tokens_or_requests": "" if row.tokens_or_requests is None else row.tokens_or_requests,
                    "pricing_model": row.pricing_model,
                    "notes": row.notes,
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
