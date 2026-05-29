# A2A (Agent2Agent) Working Examples

Companion code for the blog post **How Do I Implement A2A?** at
<https://jeffbailey.us/blog/2026/05/19/how-do-i-implement-a2a/>.

Two minimal Agent2Agent (A2A) agents in Python:

- **Summarizer Agent** -- exposes a `summarize_text` skill.
- **Router Agent** -- exposes a `triage_request` skill and, when the request
  is a summarization job, calls the Summarizer Agent over A2A.

A small `client.py` discovers either agent's card and sends a message.

## Layout

```
python/
  pyproject.toml          a2a-sdk, httpx, uvicorn
  summarizer_agent.py     A2A server on :9001
  router_agent.py         A2A server on :9002 that delegates over A2A
  client.py               Minimal A2A client
  run-demo.sh             Boots both agents and runs the client
```

## Run

Requires [uv](https://docs.astral.sh/uv/). `uv sync` provisions Python 3.11
and installs the project in editable mode into a managed `.venv`.

```bash
cd python
uv sync
./run-demo.sh
```

You should see the router's agent card, then a `Summary:` line tagged
`[via Summarizer Agent]`.

## See also

- The blog post above for the step-by-step walkthrough.
- The companion explanation: **What Is the Agent2Agent Protocol (A2A)?** at
  <https://jeffbailey.us/blog/2026/01/18/what-is-the-agent2agent-protocol-a2a/>.
