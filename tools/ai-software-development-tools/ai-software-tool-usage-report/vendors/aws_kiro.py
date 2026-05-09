"""AWS Kiro adapter.

AWS Kiro spend rolls into the regular AWS bill, so the cleanest source is
Cost Explorer (`ce:GetCostAndUsage`) filtered by service name. The exact
service name string can drift; verify against a recent Cost Explorer report
in your account and set AWS_KIRO_SERVICE_NAME accordingly.

Auth uses the standard AWS credential chain. Setting AWS_ACCESS_KEY_ID and
AWS_SECRET_ACCESS_KEY in .env overrides the chain. A profile or IAM role
also works (leave the env vars blank).
"""
from __future__ import annotations

from datetime import date

from .base import VendorAdapter, VendorReport


class AWSKiroAdapter(VendorAdapter):
    name = "AWS"
    tool = "Kiro (Amazon Q Developer)"

    def is_configured(self, env: dict[str, str]) -> bool:
        # We try Cost Explorer regardless; boto3 will resolve credentials from
        # env, profile, or instance role. The is_configured flag is only used
        # to skip vendors with no plausible auth at all.
        return True

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        service_name = env.get("AWS_KIRO_SERVICE_NAME") or "Amazon Kiro"
        try:
            import boto3  # type: ignore[import-not-found]
        except ImportError:
            return VendorReport.skipped(
                self.name, self.tool, "boto3 not installed (uv sync)", period_start, period_end
            )

        try:
            client = boto3.client("ce", region_name=env.get("AWS_REGION") or "us-east-1")
            resp = client.get_cost_and_usage(
                TimePeriod={"Start": period_start.isoformat(), "End": period_end.isoformat()},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                Filter={"Dimensions": {"Key": "SERVICE", "Values": [service_name]}},
            )
        except Exception as exc:  # noqa: BLE001 - report any AWS error in the CSV
            return VendorReport.skipped(
                self.name,
                self.tool,
                f"AWS Cost Explorer call failed: {type(exc).__name__}: {exc}",
                period_start,
                period_end,
            )

        cost = 0.0
        for bucket in resp.get("ResultsByTime", []):
            amount = bucket.get("Total", {}).get("UnblendedCost", {}).get("Amount")
            if amount is not None:
                cost += float(amount)

        notes = f"Cost from AWS Cost Explorer (service = {service_name!r})."
        if cost == 0.0:
            notes += " Zero result: confirm AWS_KIRO_SERVICE_NAME against a recent Cost Explorer report."

        return VendorReport(
            vendor=self.name,
            tool=self.tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=round(cost, 2),
            active_users=None,
            licensed_seats=None,
            tokens_or_requests=None,
            pricing_model="usage",
            notes=notes,
        )
