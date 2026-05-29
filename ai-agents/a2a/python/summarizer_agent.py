"""Summarizer A2A agent.

A minimal Agent2Agent server that exposes one skill: collapse the input text into
a single line. It registers an Agent Card at /.well-known/agent-card.json, serves
JSON-RPC over HTTP, and is callable from any A2A-compatible client.

Run:
    uvicorn summarizer_agent:app --host 0.0.0.0 --port 9001
    # or:
    python summarizer_agent.py
"""

from __future__ import annotations

import textwrap

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events.event_queue import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message

HOST = "0.0.0.0"
PORT = 9001
PUBLIC_URL = f"http://localhost:{PORT}/"


class SummarizerExecutor(AgentExecutor):
    """Collapses input text to a single-line summary."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = (context.get_user_input() or "").strip()
        if not user_text:
            await event_queue.enqueue_event(
                new_agent_text_message("No input text received.")
            )
            return

        flattened = " ".join(user_text.split())
        summary = textwrap.shorten(flattened, width=160, placeholder="...")
        await event_queue.enqueue_event(
            new_agent_text_message(f"Summary: {summary}")
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise RuntimeError("Cancellation is not supported by this agent.")


def build_agent_card() -> AgentCard:
    skill = AgentSkill(
        id="summarize_text",
        name="Summarize text",
        description="Collapses arbitrary input text into a single-line summary.",
        tags=["nlp", "summarization", "demo"],
        examples=[
            "Summarize this email thread.",
            "Give me a one-line version of these release notes.",
        ],
    )
    return AgentCard(
        name="Summarizer Agent",
        description="Demo A2A agent that returns a one-line summary of any text.",
        url=PUBLIC_URL,
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )


def build_app() -> A2AStarletteApplication:
    handler = DefaultRequestHandler(
        agent_executor=SummarizerExecutor(),
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(
        agent_card=build_agent_card(),
        http_handler=handler,
    )


app = build_app().build()


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
