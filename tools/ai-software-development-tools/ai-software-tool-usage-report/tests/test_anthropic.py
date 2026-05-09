"""Tests for vendors.anthropic.

These exist primarily as regression tests for the
"'str' object has no attribute 'get'" crash that surfaced in the May 2026
report run, plus general happy-path coverage.
"""
from __future__ import annotations

from datetime import date

import pytest

from vendors import anthropic as adapter_mod
from vendors.anthropic import AnthropicAdapter


PERIOD_START = date(2026, 5, 1)
PERIOD_END = date(2026, 5, 31)


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return self._payload


def _stub_httpx(monkeypatch, payloads_by_url: dict[str, list[object]]):
    """Replace httpx.get with one that pops the next payload for each URL."""
    queues = {url: list(items) for url, items in payloads_by_url.items()}

    def fake_get(url, headers=None, params=None, timeout=None):
        for known_url, queue in queues.items():
            if url.startswith(known_url):
                if not queue:
                    raise AssertionError(f"no more stubbed payloads for {url}")
                return _FakeResponse(queue.pop(0))
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(adapter_mod.httpx, "get", fake_get)


def test_skipped_when_admin_key_missing():
    report = AnthropicAdapter().fetch({}, PERIOD_START, PERIOD_END)
    assert report.notes.startswith("SKIPPED:")
    assert report.monthly_cost_usd is None
    assert report.tokens_or_requests is None


def test_happy_path_aggregates_cost_and_tokens(monkeypatch):
    cost_payload = {
        "data": [
            {"results": [{"amount": {"value": 10.5}}, {"amount": "2.25"}]},
            {"results": [{"amount": 1}]},
        ]
    }
    usage_payload = {
        "data": [
            {
                "results": [
                    {
                        "uncached_input_tokens": 100,
                        "cache_creation_input_tokens": 10,
                        "cache_read_input_tokens": 5,
                        "output_tokens": 20,
                    }
                ]
            }
        ]
    }
    _stub_httpx(
        monkeypatch,
        {
            "https://api.anthropic.com/v1/organizations/cost_report": [cost_payload],
            "https://api.anthropic.com/v1/organizations/usage_report/messages": [usage_payload],
        },
    )

    report = AnthropicAdapter().fetch({"ANTHROPIC_ADMIN_KEY": "sk-x"}, PERIOD_START, PERIOD_END)

    assert report.monthly_cost_usd == pytest.approx(13.75)
    assert report.tokens_or_requests == 135
    assert report.pricing_model == "token"
    assert not report.notes.startswith("SKIPPED")


def test_string_body_does_not_crash(monkeypatch):
    """Regression: when the API returns a JSON string at the root (e.g. an error
    body), the adapter must not raise `'str' object has no attribute 'get'`."""
    _stub_httpx(
        monkeypatch,
        {
            "https://api.anthropic.com/v1/organizations/cost_report": ["unauthorized"],
            "https://api.anthropic.com/v1/organizations/usage_report/messages": ["unauthorized"],
        },
    )

    report = AnthropicAdapter().fetch({"ANTHROPIC_ADMIN_KEY": "sk-x"}, PERIOD_START, PERIOD_END)

    assert report.monthly_cost_usd == 0.0
    assert report.tokens_or_requests == 0
    assert not report.notes.startswith("SKIPPED")


def test_non_dict_buckets_and_results_are_skipped(monkeypatch):
    cost_payload = {
        "data": [
            "garbage-bucket",  # ignored
            {"results": ["garbage-result", {"amount": 5}]},
        ]
    }
    usage_payload = {"data": [{"results": [{"output_tokens": "7"}]}]}
    _stub_httpx(
        monkeypatch,
        {
            "https://api.anthropic.com/v1/organizations/cost_report": [cost_payload],
            "https://api.anthropic.com/v1/organizations/usage_report/messages": [usage_payload],
        },
    )

    report = AnthropicAdapter().fetch({"ANTHROPIC_ADMIN_KEY": "sk-x"}, PERIOD_START, PERIOD_END)

    assert report.monthly_cost_usd == 5.0
    assert report.tokens_or_requests == 7


def test_pagination_follows_next_page(monkeypatch):
    page_one_cost = {"data": [{"results": [{"amount": 1}]}], "next_page": "p2"}
    page_two_cost = {"data": [{"results": [{"amount": 2}]}]}
    page_one_usage = {"data": [{"results": [{"output_tokens": 10}]}], "next_page": "p2"}
    page_two_usage = {"data": [{"results": [{"output_tokens": 20}]}]}
    _stub_httpx(
        monkeypatch,
        {
            "https://api.anthropic.com/v1/organizations/cost_report": [page_one_cost, page_two_cost],
            "https://api.anthropic.com/v1/organizations/usage_report/messages": [page_one_usage, page_two_usage],
        },
    )

    report = AnthropicAdapter().fetch({"ANTHROPIC_ADMIN_KEY": "sk-x"}, PERIOD_START, PERIOD_END)

    assert report.monthly_cost_usd == 3.0
    assert report.tokens_or_requests == 30


def test_amount_shapes_are_coerced(monkeypatch):
    cost_payload = {
        "data": [
            {
                "results": [
                    {"amount": None},
                    {"amount": "not-a-number"},
                    {"amount": {"value": "0.5"}},
                    {"amount": 4},
                ]
            }
        ]
    }
    _stub_httpx(
        monkeypatch,
        {
            "https://api.anthropic.com/v1/organizations/cost_report": [cost_payload],
            "https://api.anthropic.com/v1/organizations/usage_report/messages": [{"data": []}],
        },
    )

    report = AnthropicAdapter().fetch({"ANTHROPIC_ADMIN_KEY": "sk-x"}, PERIOD_START, PERIOD_END)

    assert report.monthly_cost_usd == pytest.approx(4.5)


def test_non_string_next_page_does_not_loop(monkeypatch):
    """If `next_page` comes back as a non-string truthy value, treat it as
    end-of-pagination instead of feeding garbage back into the next request."""
    cost_payload = {"data": [{"results": [{"amount": 1}]}], "next_page": True}
    _stub_httpx(
        monkeypatch,
        {
            "https://api.anthropic.com/v1/organizations/cost_report": [cost_payload],
            "https://api.anthropic.com/v1/organizations/usage_report/messages": [{"data": []}],
        },
    )

    report = AnthropicAdapter().fetch({"ANTHROPIC_ADMIN_KEY": "sk-x"}, PERIOD_START, PERIOD_END)

    assert report.monthly_cost_usd == 1.0
