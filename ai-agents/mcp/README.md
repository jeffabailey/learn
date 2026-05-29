# MCP (Model Context Protocol) Working Examples

Companion code for the blog post **How Do I Implement an MCP Server?** at
<https://jeffbailey.us/blog/2026/05/22/how-do-i-implement-an-mcp-server/>.

A minimal Model Context Protocol (MCP) server in Python that exposes:

- **Tools**: `summarize_text` (collapse text to one line) and `word_count`
  (count whitespace-separated words).
- **Resource**: `doc://about`, a short static description of the server.
- **Prompt**: `summarize_with_focus`, a reusable prompt template.

A small `client.py` spawns the server over stdio, lists its capabilities,
and calls one of the tools.

## Layout

```
python/
  pyproject.toml          mcp, optional pytest
  server.py               FastMCP server (tools, resource, prompt)
  client.py               Minimal MCP client over stdio
  run-demo.sh             Boots the server and runs the client
  tests/
    test_server.py        Unit tests for the pure functions
```

## Run

Requires [uv](https://docs.astral.sh/uv/). `uv sync` provisions Python 3.11
and installs the project in editable mode into a managed `.venv`.

```bash
cd python
uv sync
./run-demo.sh
```

You should see the server's tools listed, then a `Summary:` line from
the `summarize_text` tool.

## Test

```bash
cd python
uv sync --extra test
uv run --no-sync pytest
```

## See also

- The blog post above for the implementation walkthrough.
- The companion explanation: **What Is MCP?** at
  <https://jeffbailey.us/blog/2026/01/15/what-is-mcp/>.
