"""Summarizer MCP server.

A minimal Model Context Protocol (MCP) server that exposes:

  - Two tools: `summarize_text` and `word_count`.
  - One resource: `doc://about`, a short static description.
  - One prompt template: `summarize_with_focus`.

Tool implementations are kept as pure functions (`summarize`, `count_words`)
so they can be unit tested without spinning up the MCP transport. The
FastMCP decorators only wire the protocol to those functions.

Run:
    python server.py
    # or:
    uv run python server.py
"""

from __future__ import annotations

import textwrap

from mcp.server.fastmcp import FastMCP

SERVER_NAME = "Summarizer MCP Server"
SUMMARY_WIDTH = 160
ABOUT_DOC = (
    "Summarizer MCP Server. Exposes one summarization tool, one counting "
    "tool, a static `doc://about` resource, and a reusable "
    "`summarize_with_focus` prompt template."
)


def summarize(text: str) -> str:
    """Collapse arbitrary input text into a single-line summary.

    Whitespace runs are flattened to a single space, then the result is
    truncated to `SUMMARY_WIDTH` characters with an ellipsis placeholder.
    """
    flattened = " ".join(text.split())
    return textwrap.shorten(flattened, width=SUMMARY_WIDTH, placeholder="...")


def count_words(text: str) -> int:
    """Count whitespace-separated words in the input."""
    return len(text.split())


mcp = FastMCP(SERVER_NAME)


@mcp.tool()
def summarize_text(text: str) -> str:
    """Collapse arbitrary input text into a single-line summary."""
    return summarize(text)


@mcp.tool()
def word_count(text: str) -> int:
    """Count whitespace-separated words in the input."""
    return count_words(text)


@mcp.resource("doc://about")
def about_doc() -> str:
    """Return a short description of this server's capabilities."""
    return ABOUT_DOC


@mcp.prompt()
def summarize_with_focus(focus: str, text: str) -> str:
    """Reusable prompt: summarize text, focused on a particular topic."""
    return (
        f"Summarize the following text, focusing on: {focus}\n\n{text}"
    )


if __name__ == "__main__":
    mcp.run()
