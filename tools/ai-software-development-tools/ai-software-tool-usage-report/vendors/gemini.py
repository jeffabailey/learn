"""Google Gemini adapter.

Google does not expose a single REST endpoint that aggregates Gemini API
spend or token usage across a project. Aggregate data lives in Cloud Billing
exports (BigQuery) and Cloud Monitoring time series. Wiring those up is
project-specific (a service account with bigquery.dataViewer or monitoring.viewer
plus a billing-export dataset name) and is out of scope for a one-file script.

This adapter accepts manually-entered monthly totals so Gemini still appears
on the report. Set GOOGLE_GEMINI_MONTHLY_COST_USD and / or
GOOGLE_GEMINI_MONTHLY_TOKENS in .env to populate the row.
"""
from __future__ import annotations

from datetime import date

from .base import VendorAdapter, VendorReport


class GeminiAdapter(VendorAdapter):
    name = "Google"
    tool = "Gemini API"

    def is_configured(self, env: dict[str, str]) -> bool:
        return bool(env.get("GOOGLE_GEMINI_MONTHLY_COST_USD") or env.get("GOOGLE_GEMINI_MONTHLY_TOKENS"))

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        cost_str = env.get("GOOGLE_GEMINI_MONTHLY_COST_USD")
        tokens_str = env.get("GOOGLE_GEMINI_MONTHLY_TOKENS")
        cost = float(cost_str) if cost_str else None
        tokens = int(tokens_str) if tokens_str else None

        if cost is None and tokens is None:
            return VendorReport.skipped(
                self.name,
                self.tool,
                "no GOOGLE_GEMINI_* values; pull aggregate from Cloud Billing or Monitoring and set them",
                period_start,
                period_end,
            )

        return VendorReport(
            vendor=self.name,
            tool=self.tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=cost,
            active_users=None,
            licensed_seats=None,
            tokens_or_requests=tokens,
            pricing_model="token",
            notes="Manual entry. Aggregate values come from Cloud Billing BigQuery export or Cloud Monitoring.",
        )
