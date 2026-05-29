#!/usr/bin/env bash
# Boots both agents, sends a delegated request through the router, and tears
# everything down. Requires `uv` to be installed; the script runs every Python
# entry point through `uv run`, which syncs the project virtualenv on demand.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${HERE}"
LOG_DIR="${HERE}/.demo-logs"
mkdir -p "${LOG_DIR}"

cleanup() {
    pkill -P $$ || true
}
trap cleanup EXIT

# Sync once up front so the agents below do not race on the first install.
uv sync --quiet

echo "Starting summarizer on :9001 ..."
uv run --no-sync python "${HERE}/summarizer_agent.py" > "${LOG_DIR}/summarizer.log" 2>&1 &
SUMMARIZER_PID=$!

echo "Starting router on :9002 ..."
uv run --no-sync python "${HERE}/router_agent.py" > "${LOG_DIR}/router.log" 2>&1 &
ROUTER_PID=$!

# Wait for both agent cards to become reachable.
for url in "http://localhost:9001/.well-known/agent-card.json" \
           "http://localhost:9002/.well-known/agent-card.json"; do
    for attempt in $(seq 1 30); do
        if curl -fsS "${url}" > /dev/null 2>&1; then
            break
        fi
        sleep 0.3
    done
done

echo
echo "Calling router (which will delegate to summarizer) ..."
uv run --no-sync python "${HERE}/client.py" \
    "Summarize: A2A lets agents from different vendors discover each other and exchange tasks."

echo
echo "Logs: ${LOG_DIR}"
