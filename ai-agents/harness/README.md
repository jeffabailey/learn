# Agent harness from scratch (Go)

Companion code for the blog post **Agent Harness Tutorial: Build a Coding Agent in Go** at
<https://jeffbailey.us/blog/2026/11/17/how-do-i-build-an-agent-harness/>.

A coding agent in one Go file and the standard library: a chat loop, an agent
loop that runs tools, four tools (list, read, write, run), and guardrails.
It talks to any OpenAI-compatible Chat Completions endpoint, and defaults to
a local [Ollama](https://ollama.com) server so it runs free and offline.

## Layout

Steps 1 to 5 are complete, runnable programs, identical to the `main.go` you have
after following that step of the tutorial. Step 6 goes past the tutorial. Diff two neighbors to see exactly
what a step adds.

```
go.mod
steps/
  01-hello/        send one message, print the reply
  02-chat/         a chat loop that keeps the conversation history
  03-first-tool/   one tool (read_file) and the agent loop
  04-toolbox/      list_files, read_file, write_file, run_command
  05-guardrails/   workspace fence, approvals, timeouts, output limits,
                   step budget, system prompt; main_test.go (the tutorial's
                   tests) and more_test.go (two extra tests)
  06-extensions/   the tutorial's five suggested extensions, with tests:
                   streamed replies, edit_file, saved sessions,
                   history compaction, symlink-aware workspace fence
```

```bash
diff steps/02-chat/main.go steps/03-first-tool/main.go
```

## Run

Requires Go 1.22 or newer and Ollama.

```bash
ollama pull gemma4:e2b
go run ./steps/01-hello "What is the capital of France?"
go run ./steps/05-guardrails
go run ./steps/06-extensions
```

Steps 4 to 6 can write files and run commands. Run them from a scratch
folder, for example:

```bash
go build -o harness ./steps/05-guardrails
mkdir -p /tmp/agent-playground && cd /tmp/agent-playground
/path/to/harness
```

## Extensions (step 6)

```bash
diff steps/05-guardrails/main.go steps/06-extensions/main.go
```

* **Stream replies.** Requests set `"stream": true`. `readStream` prints text
  as it arrives and joins tool calls, which arrive in pieces, before running them.
* **Edit instead of overwrite.** `edit_file` replaces one exact snippet and
  refuses if it appears zero times or more than once. It asks for approval.
* **Save sessions.** `/quit` (or Ctrl+D) writes the history to
  `.harness-session.json` in the workspace, and the next start resumes it. The
  file can hold file contents the agent read, so it is readable only by you.
  Delete it, or type `/reset` before `/quit`, to start fresh.
* **Compact the history.** Before a turn, if the history is over 20,000 bytes,
  the model summarizes it and the summary replaces everything but the system
  prompt.
* **Close the symlink gap.** `safePath` resolves symbolic links, including the
  parent folder of a file that doesn't exist yet, and refuses broken links.
  `run_command` is still fenced only by your approval.

## Configure

| Variable           | Default                     | Purpose                               |
| ------------------ | --------------------------- | ------------------------------------- |
| `HARNESS_BASE_URL` | `http://localhost:11434/v1` | Any OpenAI-compatible endpoint        |
| `HARNESS_MODEL`    | `gemma4:e2b`                | Model name; it must support tools     |
| `HARNESS_API_KEY`  | (empty)                     | Sent as a Bearer token when set       |

## Test

```bash
go test ./...
```

The tests use a fake model server, so they pass without Ollama.

CI runs `gofmt`, `go vet`, these tests with `-race` on Go 1.22 and the
latest Go, and a build of every step for macOS, Linux, and Windows. See the
`harness-tests` job in `.github/workflows/test-coverage.yml`.

## Ship

```bash
go build -ldflags="-s -w" -o harness ./steps/05-guardrails
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o harness.exe ./steps/05-guardrails
GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o harness-linux-arm64 ./steps/05-guardrails
```
