"""Unit tests for the pure functions backing the MCP server's tools.

The tools registered with FastMCP delegate to these plain functions, so
testing the pure functions covers the business logic without spinning
up the MCP protocol stack.
"""

from __future__ import annotations

from server import (
    ABOUT_DOC,
    SUMMARY_WIDTH,
    about_doc,
    count_words,
    summarize,
    summarize_with_focus,
)


def test_summarize_collapses_whitespace_runs():
    assert summarize("hello   world\n\nthere") == "hello world there"


def test_summarize_truncates_long_input_to_width():
    long_input = " ".join(["word"] * 200)
    summary = summarize(long_input)
    assert summary.endswith("...")
    assert len(summary) <= SUMMARY_WIDTH


def test_summarize_keeps_short_input_intact():
    assert summarize("brief sentence") == "brief sentence"


def test_summarize_handles_empty_input():
    assert summarize("") == ""


def test_count_words_counts_whitespace_tokens():
    assert count_words("one two three four") == 4


def test_count_words_treats_consecutive_whitespace_as_one_separator():
    assert count_words("one   two\nthree") == 3


def test_count_words_returns_zero_for_empty_input():
    assert count_words("") == 0


def test_about_doc_returns_the_constant():
    assert about_doc() == ABOUT_DOC


def test_summarize_with_focus_embeds_topic_and_text():
    rendered = summarize_with_focus(focus="risks", text="A quarterly report.")
    assert "focusing on: risks" in rendered
    assert "A quarterly report." in rendered
