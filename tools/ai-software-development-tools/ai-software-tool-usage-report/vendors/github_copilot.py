"""GitHub Copilot adapter.

Docs:
  - https://docs.github.com/en/rest/copilot/copilot-user-management
  - https://docs.github.com/en/rest/copilot/copilot-metrics
GitHub does not expose a Copilot cost endpoint. Cost is computed as
seats * GITHUB_COPILOT_SEAT_RATE_USD.
"""
from __future__ import annotations

from datetime import date

import httpx

from .base import VendorAdapter, VendorReport

_API_BASE = "https://api.github.com"


class GitHubCopilotAdapter(VendorAdapter):
    name = "GitHub Copilot"
    tool = "Copilot Business / Enterprise"

    def is_configured(self, env: dict[str, str]) -> bool:
        return bool(env.get("GITHUB_TOKEN") and env.get("GITHUB_ORG"))

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        if not self.is_configured(env):
            return VendorReport.skipped(
                self.name, self.tool, "GITHUB_TOKEN or GITHUB_ORG missing", period_start, period_end
            )

        headers = {
            "Authorization": f"Bearer {env['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        org = env["GITHUB_ORG"]
        rate = float(env.get("GITHUB_COPILOT_SEAT_RATE_USD") or 0)

        seats = _seat_total(headers, org)
        active_users = _active_users(headers, org, period_start, period_end)
        cost = round(seats * rate, 2) if rate and seats else None

        return VendorReport(
            vendor=self.name,
            tool=self.tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=cost,
            active_users=active_users,
            licensed_seats=seats,
            tokens_or_requests=None,
            pricing_model="seat",
            notes=f"Cost = seats * {rate} USD (override via GITHUB_COPILOT_SEAT_RATE_USD)."
            if rate
            else "Set GITHUB_COPILOT_SEAT_RATE_USD to compute cost.",
        )


def _seat_total(headers: dict[str, str], org: str) -> int | None:
    r = httpx.get(f"{_API_BASE}/orgs/{org}/copilot/billing", headers=headers, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    body = r.json()
    breakdown = body.get("seat_breakdown") or {}
    return int(breakdown.get("total", 0)) or None


def _active_users(headers: dict[str, str], org: str, start: date, end: date) -> int | None:
    """Use Copilot metrics API. Returns the max daily active users in the window."""
    r = httpx.get(
        f"{_API_BASE}/orgs/{org}/copilot/metrics",
        headers=headers,
        params={"since": start.isoformat(), "until": end.isoformat()},
        timeout=30,
    )
    if r.status_code == 404:
        return None
    r.raise_for_status()
    days = r.json()
    if not days:
        return None
    return max(int(d.get("total_active_users", 0)) for d in days) or None
