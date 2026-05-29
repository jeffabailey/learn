#!/usr/bin/env bash
# Boots the MCP client, which in turn spawns the server over stdio,
# lists capabilities, and calls one tool. Requires `uv` to be installed.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${HERE}"

uv sync --quiet

uv run --no-sync python "${HERE}/client.py" \
    "Summarize: MCP lets an AI host call tools, read resources, and reuse prompts over a single standard protocol."
