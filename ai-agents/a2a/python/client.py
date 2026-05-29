"""A2A client that discovers an agent and sends a single message.

Run:
    python client.py "Summarize the news for me"
    python client.py "Summarize this" --url http://localhost:9002

Without arguments, sends a default message to the Router Agent on port 9002.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import uuid

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

DEFAULT_URL = "http://localhost:9002"
DEFAULT_MESSAGE = "Summarize: A2A standardizes how agents discover and call each other."


async def call_agent(base_url: str, user_text: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as http:
        resolver = A2ACardResolver(httpx_client=http, base_url=base_url)
        card = await resolver.get_agent_card()
        print(f"Discovered agent: {card.name} (v{card.version}) at {card.url}")
        for skill in card.skills:
            print(f"  skill: {skill.id} -- {skill.description}")

        client = A2AClient(httpx_client=http, agent_card=card)
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": user_text}],
                    "messageId": str(uuid.uuid4()),
                }
            ),
        )
        response = await client.send_message(request)
        return response.model_dump(mode="json")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal A2A client")
    parser.add_argument("message", nargs="?", default=DEFAULT_MESSAGE)
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL of the agent")
    return parser.parse_args(argv)


async def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = await call_agent(args.url, args.message)
    import json

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
