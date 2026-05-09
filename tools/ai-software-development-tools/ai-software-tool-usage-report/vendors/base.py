from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class VendorReport:
    vendor: str
    tool: str
    period_start: date
    period_end: date
    monthly_cost_usd: float | None
    active_users: int | None
    licensed_seats: int | None
    tokens_or_requests: int | None
    pricing_model: str
    notes: str = ""

    @classmethod
    def skipped(cls, vendor: str, tool: str, reason: str, period_start: date, period_end: date) -> "VendorReport":
        return cls(
            vendor=vendor,
            tool=tool,
            period_start=period_start,
            period_end=period_end,
            monthly_cost_usd=None,
            active_users=None,
            licensed_seats=None,
            tokens_or_requests=None,
            pricing_model="",
            notes=f"SKIPPED: {reason}",
        )


class VendorAdapter:
    """Base class for vendor adapters.

    Subclasses must set `name` and `tool`, and implement `fetch`.
    `is_configured` returns True when the env contains the credentials needed.
    """

    name: str = ""
    tool: str = ""

    def is_configured(self, env: dict[str, str]) -> bool:
        raise NotImplementedError

    def fetch(self, env: dict[str, str], period_start: date, period_end: date) -> VendorReport:
        raise NotImplementedError
