"""OpenAI admin API adapter.

Docs: https://platform.openai.com/docs/api-reference/usage
The /organization/costs endpoint returns daily cost buckets in USD cents.
The /organization/usage/completions endpoint returns daily token counts.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import httpx

from .base import VendorAdapter, VendorReport

_COSTS_URL = "https://api.openai.com/v1/organization/costs"
_USAGE_URL = "https://api.openai.com/v1/organization/usage/completions"


class OpenAIAdapter(VendorAdapter):
    name = "OpenAI"
    tool = "OpenAI API (GPT, o-series)"

    def is_configured(self, env: dict[str, str]) -> bool:
        return bool(env.get("OPENAI_ADMIN_KEY"))

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        if not self.is_configured(env):
            return VendorReport.skipped(self.name, self.tool, "OPENAI_ADMIN_KEY missing", period_start, period_end)

        headers = {"Authorization": f"Bearer {env['OPENAI_ADMIN_KEY']}"}
        start_unix = _to_unix(period_start)
        end_unix = _to_unix(period_end)

        cost_usd = _sum_cost(headers, start_unix, end_unix)
        tokens = _sum_tokens(headers, start_unix, end_unix)

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
            notes="Cost from /organization/costs (USD); tokens are input+output across completions.",
        )


def _to_unix(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def _sum_cost(headers: dict[str, str], start: int, end: int) -> float:
    total = 0.0
    page: str | None = None
    while True:
        params = {"start_time": start, "end_time": end, "bucket_width": "1d", "limit": 31}
        if page:
            params["page"] = page
        r = httpx.get(_COSTS_URL, headers=headers, params=params, timeout=60)
        r.raise_for_status()
        body = r.json()
        for bucket in body.get("data", []):
            for result in bucket.get("results", []):
                amount = result.get("amount", {})
                value = amount.get("value")
                if value is not None:
                    total += float(value)
        if not body.get("has_more"):
            break
        page = body.get("next_page")
        if not page:
            break
    return round(total, 2)


def _sum_tokens(headers: dict[str, str], start: int, end: int) -> int:
    total = 0
    page: str | None = None
    while True:
        params = {"start_time": start, "end_time": end, "bucket_width": "1d", "limit": 31}
        if page:
            params["page"] = page
        r = httpx.get(_USAGE_URL, headers=headers, params=params, timeout=60)
        r.raise_for_status()
        body = r.json()
        for bucket in body.get("data", []):
            for result in bucket.get("results", []):
                total += int(result.get("input_tokens", 0))
                total += int(result.get("output_tokens", 0))
        if not body.get("has_more"):
            break
        page = body.get("next_page")
        if not page:
            break
    return total
