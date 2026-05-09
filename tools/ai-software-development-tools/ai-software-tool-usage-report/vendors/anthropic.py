"""Anthropic admin API adapter.

Docs: https://docs.anthropic.com/en/api/admin-api/usage-cost/get-cost-report
The cost_report endpoint returns daily cost buckets for the org.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import httpx

from .base import VendorAdapter, VendorReport

_COST_URL = "https://api.anthropic.com/v1/organizations/cost_report"
_USAGE_URL = "https://api.anthropic.com/v1/organizations/usage_report/messages"


class AnthropicAdapter(VendorAdapter):
    name = "Anthropic"
    tool = "Claude API / Claude Code"

    def is_configured(self, env: dict[str, str]) -> bool:
        return bool(env.get("ANTHROPIC_ADMIN_KEY"))

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        if not self.is_configured(env):
            return VendorReport.skipped(self.name, self.tool, "ANTHROPIC_ADMIN_KEY missing", period_start, period_end)

        headers = {
            "x-api-key": env["ANTHROPIC_ADMIN_KEY"],
            "anthropic-version": "2023-06-01",
        }
        params = {
            "starting_at": _iso(period_start),
            "ending_at": _iso(period_end),
        }

        cost_usd = _sum_cost(headers, params)
        tokens = _sum_tokens(headers, params)

        return VendorReport(
            vendor=self.name,
            tool=self.tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=cost_usd,
            active_users=None,
            licensed_seats=None,
            tokens_or_requests=tokens,
            pricing_model="token",
            notes="Cost from cost_report; tokens are input+output across messages.",
        )


def _iso(d: date) -> str:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _sum_cost(headers: dict[str, str], params: dict[str, str]) -> float:
    total = 0.0
    for body in _paginate(_COST_URL, headers, params):
        for bucket in _safe_list(body.get("data")):
            for result in _safe_list(bucket.get("results")):
                amount = _coerce_amount(result.get("amount"))
                if amount is not None:
                    total += amount
    return round(total, 2)


def _sum_tokens(headers: dict[str, str], params: dict[str, str]) -> int:
    total = 0
    for body in _paginate(_USAGE_URL, headers, params):
        for bucket in _safe_list(body.get("data")):
            for result in _safe_list(bucket.get("results")):
                for field in (
                    "uncached_input_tokens",
                    "cache_creation_input_tokens",
                    "cache_read_input_tokens",
                    "output_tokens",
                ):
                    total += _coerce_int(result.get(field))
    return total


def _paginate(url: str, headers: dict[str, str], params: dict[str, str]):
    """Yield response bodies as dicts, following next_page links. A non-dict body
    (e.g., a JSON string error payload) ends pagination instead of crashing."""
    next_page: str | None = None
    while True:
        page_params = dict(params)
        if next_page:
            page_params["page"] = next_page
        r = httpx.get(url, headers=headers, params=page_params, timeout=60)
        r.raise_for_status()
        body = _safe_dict(r.json())
        yield body
        next_page = body.get("next_page") if isinstance(body.get("next_page"), str) else None
        if not next_page:
            break


def _safe_dict(value: object) -> dict:
    """Return value if it is a dict, otherwise an empty dict. Guards against API
    responses where the JSON root isn't an object (the source of the original
    `'str' object has no attribute 'get'` crash)."""
    return value if isinstance(value, dict) else {}


def _safe_list(value: object) -> list[dict]:
    """Return value if it is a list of dicts, otherwise []. Anthropic occasionally
    returns wrapper-only payloads on edge cases; this prevents `'str' has no attribute
    'get'` from crashing the run."""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _coerce_amount(value: object) -> float | None:
    """Anthropic's cost_report has returned `amount` as either a top-level number/string
    or a nested {"value": ...} object across versions. Handle both."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    if isinstance(value, dict):
        return _coerce_amount(value.get("value"))
    return None


def _coerce_int(value: object) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
