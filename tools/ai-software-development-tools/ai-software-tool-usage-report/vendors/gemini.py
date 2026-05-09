"""Google Gemini Code Assist adapter.

Pulls active-user counts from Cloud Monitoring's time-series API for the
"Gemini for Google Cloud" metric surface (`cloudaicompanion.googleapis.com`,
shown in Metrics Explorer as "Gemini for Google Cloud Instance"). The exact
metric type is configurable because Google's metric catalog evolves; copy
the metric type string from Metrics Explorer in the Cloud Console (it sits
under the metric's display name, e.g.
`cloudaicompanion.googleapis.com/instance/...`).

Cost is not exposed by Cloud Monitoring. For an automated cost source set up
a BigQuery billing export and replace `_manual_cost` with a query against
that table; otherwise set GOOGLE_GEMINI_MONTHLY_COST_USD by hand.

Auth uses Application Default Credentials. Locally, run
`gcloud auth application-default login` once. In CI, set
GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file. The principal
needs `roles/monitoring.viewer` on the project.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import httpx

from .base import VendorAdapter, VendorReport

_TS_URL = "https://monitoring.googleapis.com/v3/projects/{project}/timeSeries"
_SCOPE = "https://www.googleapis.com/auth/monitoring.read"


class GeminiAdapter(VendorAdapter):
    name = "Google"
    tool = "Gemini Code Assist"

    def is_configured(self, env: dict[str, str]) -> bool:
        cloud = bool(env.get("GOOGLE_GEMINI_PROJECT_ID") and env.get("GOOGLE_GEMINI_METRIC_TYPE"))
        manual = bool(env.get("GOOGLE_GEMINI_MONTHLY_COST_USD") or env.get("GOOGLE_GEMINI_MONTHLY_TOKENS"))
        return cloud or manual

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        project_id = env.get("GOOGLE_GEMINI_PROJECT_ID")
        metric_type = env.get("GOOGLE_GEMINI_METRIC_TYPE")

        active_users: int | None = None
        notes: list[str] = []

        if project_id and metric_type:
            try:
                token = _adc_token()
                active_users = _fetch_max_int(project_id, metric_type, period_start, period_end, token)
                notes.append(f"active_users from Cloud Monitoring metric {metric_type!r}")
            except Exception as exc:  # noqa: BLE001
                notes.append(f"Cloud Monitoring call failed: {type(exc).__name__}: {exc}")

        cost_str = env.get("GOOGLE_GEMINI_MONTHLY_COST_USD")
        tokens_str = env.get("GOOGLE_GEMINI_MONTHLY_TOKENS")
        cost = float(cost_str) if cost_str else None
        tokens = int(tokens_str) if tokens_str else None

        if active_users is None and cost is None and tokens is None:
            return VendorReport.skipped(
                self.name,
                self.tool,
                "no Gemini config; set GOOGLE_GEMINI_PROJECT_ID + GOOGLE_GEMINI_METRIC_TYPE for active users, "
                "and / or GOOGLE_GEMINI_MONTHLY_COST_USD for cost",
                period_start,
                period_end,
            )

        if cost is not None:
            notes.append("cost is a manual value (wire a BigQuery billing export for an automated source)")

        return VendorReport(
            vendor=self.name,
            tool=self.tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=cost,
            active_users=active_users,
            licensed_seats=None,
            tokens_or_requests=tokens,
            pricing_model="seat",
            notes="; ".join(notes) if notes else "Manual entry.",
        )


def _adc_token() -> str:
    """Return an OAuth2 access token from Application Default Credentials."""
    from google.auth import default
    from google.auth.transport.requests import Request

    credentials, _project = default(scopes=[_SCOPE])
    credentials.refresh(Request())
    return credentials.token


def _fetch_max_int(
    project_id: str,
    metric_type: str,
    period_start: date,
    period_end: date,
    token: str,
) -> int | None:
    start_dt = datetime(period_start.year, period_start.month, period_start.day, tzinfo=timezone.utc)
    end_dt = datetime(period_end.year, period_end.month, period_end.day, tzinfo=timezone.utc)
    params = {
        "filter": f'metric.type = "{metric_type}"',
        "interval.startTime": start_dt.isoformat().replace("+00:00", "Z"),
        "interval.endTime": end_dt.isoformat().replace("+00:00", "Z"),
        "view": "FULL",
    }
    r = httpx.get(
        _TS_URL.format(project=project_id),
        params=params,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    r.raise_for_status()
    body = r.json()
    max_val = 0
    for series in body.get("timeSeries", []) or []:
        for point in series.get("points", []) or []:
            value = _point_value(point)
            if value is not None:
                max_val = max(max_val, value)
    return max_val or None


def _point_value(point: dict) -> int | None:
    value = point.get("value") or {}
    if "int64Value" in value:
        return int(value["int64Value"])
    if "doubleValue" in value:
        return int(float(value["doubleValue"]))
    return None
