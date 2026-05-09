"""Cursor team admin API adapter.

Docs: https://docs.cursor.com/account/teams/admin-api
Auth is HTTP Basic with the API key as the username (empty password).
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timezone

import httpx

from .base import VendorAdapter, VendorReport

_BASE = "https://api.cursor.com"


class CursorAdapter(VendorAdapter):
    name = "Cursor"
    tool = "Cursor for Teams"

    def is_configured(self, env: dict[str, str]) -> bool:
        return bool(env.get("CURSOR_API_KEY"))

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        if not self.is_configured(env):
            return VendorReport.skipped(self.name, self.tool, "CURSOR_API_KEY missing", period_start, period_end)

        token = base64.b64encode(f"{env['CURSOR_API_KEY']}:".encode()).decode()
        headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

        spend_total, seats = _spend_and_seats(headers)
        active_users, requests = _usage(headers, period_start, period_end)

        return VendorReport(
            vendor=self.name,
            tool=self.tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=spend_total,
            active_users=active_users,
            licensed_seats=seats,
            tokens_or_requests=requests,
            pricing_model="hybrid",
            notes="Cost from /teams/spend; usage from /teams/daily-usage-data.",
        )


def _spend_and_seats(headers: dict[str, str]) -> tuple[float | None, int | None]:
    r = httpx.post(f"{_BASE}/teams/spend", headers=headers, json={}, timeout=30)
    if r.status_code >= 400:
        return None, None
    body = r.json()
    members = body.get("teamMemberSpend") or []
    if not members:
        return None, None
    total = sum(float(m.get("spendCents", 0)) for m in members) / 100.0
    return round(total, 2), len(members)


def _usage(headers: dict[str, str], start: date, end: date) -> tuple[int | None, int | None]:
    payload = {
        "startDate": _ms(start),
        "endDate": _ms(end),
    }
    r = httpx.post(f"{_BASE}/teams/daily-usage-data", headers=headers, json=payload, timeout=60)
    if r.status_code >= 400:
        return None, None
    body = r.json()
    rows = body.get("data") or []
    if not rows:
        return None, None
    users = {row.get("email") for row in rows if row.get("email")}
    requests = sum(int(row.get("totalRequests", 0)) for row in rows)
    return (len(users) or None, requests or None)


def _ms(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
