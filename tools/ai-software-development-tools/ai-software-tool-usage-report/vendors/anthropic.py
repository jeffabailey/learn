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
    next_page: str | None = None
    while True:
        page_params = dict(params)
        if next_page:
            page_params["page"] = next_page
        r = httpx.get(_COST_URL, headers=headers, params=page_params, timeout=60)
        r.raise_for_status()
        body = r.json()
        for bucket in body.get("data", []):
            for result in bucket.get("results", []):
                amount = result.get("amount", {})
                value = amount.get("value")
                if value is not None:
                    total += float(value)
        next_page = body.get("next_page")
        if not next_page:
            break
    return round(total, 2)


def _sum_tokens(headers: dict[str, str], params: dict[str, str]) -> int:
    total = 0
    next_page: str | None = None
    while True:
        page_params = dict(params)
        if next_page:
            page_params["page"] = next_page
        r = httpx.get(_USAGE_URL, headers=headers, params=page_params, timeout=60)
        r.raise_for_status()
        body = r.json()
        for bucket in body.get("data", []):
            for result in bucket.get("results", []):
                total += int(result.get("uncached_input_tokens", 0))
                total += int(result.get("cache_creation_input_tokens", 0))
                total += int(result.get("cache_read_input_tokens", 0))
                total += int(result.get("output_tokens", 0))
        next_page = body.get("next_page")
        if not next_page:
            break
    return total
