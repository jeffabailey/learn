"""Minimal MCP client.

Spawns the server in `server.py` over stdio, initializes a session, lists
the server's tools, resources, and prompts, and calls one tool. The
defaults call `summarize_text` with a short sample sentence.

Run:
    python client.py
    python client.py "Summarize: arbitrary input text here"
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DEFAULT_MESSAGE = "Summarize: MCP standardizes how AI hosts talk to external tools."


def server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command="python",
        args=["server.py"],
    )


def first_text(content) -> str:
    """Pull the first text item out of a CallToolResult's content list."""
    for item in content:
        text = getattr(item, "text", None)
        if text:
            return text
    return "<no text reply>"


async def call_summarize(message: str) -> None:
    async with stdio_client(server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            resources = (await session.list_resources()).resources
            prompts = (await session.list_prompts()).prompts

            print(f"Discovered {len(tools)} tool(s):")
            for tool in tools:
                print(f"  tool: {tool.name} -- {tool.description}")
            for resource in resources:
                print(f"  resource: {resource.uri}")
            for prompt in prompts:
                print(f"  prompt: {prompt.name}")

            result = await session.call_tool(
                "summarize_text", {"text": message}
            )
            print()
            print(f"[via {SERVER_LABEL}] {first_text(result.content)}")


SERVER_LABEL = "Summarizer MCP Server"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal MCP client over stdio")
    parser.add_argument("message", nargs="?", default=DEFAULT_MESSAGE)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    asyncio.run(call_summarize(args.message))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
