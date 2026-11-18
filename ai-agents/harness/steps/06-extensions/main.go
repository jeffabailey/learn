// harness talks to a model through an OpenAI-compatible Chat Completions API.
package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"time"
)

const (
	maxSteps        = 25               // tool rounds allowed per user message
	maxOutputBytes  = 10_000           // longest tool result sent back to the model
	commandTimeout  = 60 * time.Second // longest a shell command may run
	maxHistoryBytes = 20_000           // about 5,000 tokens; compact the history past this
	maxSummaryInput = 2_000            // longest message excerpt sent to the summarizer
	sessionFile     = ".harness-session.json"
	summaryHeading  = "\n\nSummary of the conversation so far:\n"
)

var (
	input      = bufio.NewScanner(os.Stdin)
	httpClient = &http.Client{Timeout: 5 * time.Minute}
	workspace  string // the folder the agent may touch, set in main
)

// Message is one entry in the conversation, in the OpenAI-compatible format.
type Message struct {
	Role       string     `json:"role"`
	Content    string     `json:"content"`
	ToolCalls  []ToolCall `json:"tool_calls,omitempty"`
	ToolCallID string     `json:"tool_call_id,omitempty"`
}

// ToolCall is the model asking the harness to run a tool.
type ToolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function FunctionCall `json:"function"`
}

type FunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"` // a JSON object, encoded as a string
}

// ToolDef describes a tool to the model: its name, purpose, and arguments.
type ToolDef struct {
	Type     string      `json:"type"`
	Function FunctionDef `json:"function"`
}

type FunctionDef struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Parameters  map[string]any `json:"parameters"`
}

type chatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Tools    []ToolDef `json:"tools,omitempty"`
	Stream   bool      `json:"stream"`
}

// chatChunk is one server-sent event of a streamed reply. Each carries a
// small delta: a few tokens of text, or a piece of a tool call.
type chatChunk struct {
	Choices []struct {
		Delta struct {
			Content   string `json:"content"`
			ToolCalls []struct {
				Index    int          `json:"index"`
				ID       string       `json:"id"`
				Function FunctionCall `json:"function"`
			} `json:"tool_calls"`
		} `json:"delta"`
	} `json:"choices"`
}

func main() {
	var err error
	workspace, err = os.Getwd()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}

	history := loadSession()
	fmt.Printf("Agent ready in %s. Type /reset to start over, /quit to exit.\n", workspace)
	for {
		fmt.Print("\nyou> ")
		if !input.Scan() {
			saveSession(history)
			return
		}
		line := strings.TrimSpace(input.Text())
		switch line {
		case "":
			continue
		case "/quit":
			saveSession(history)
			return
		case "/reset":
			history = []Message{{Role: "system", Content: systemPrompt()}}
			fmt.Println("History cleared.")
			continue
		}

		if compacted, err := compact(history); err != nil {
			fmt.Fprintln(os.Stderr, "warning: could not compact the history:", err)
		} else {
			history = compacted
		}
		history = append(history, Message{Role: "user", Content: line})
		history, err = runTurn(history)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
		}
	}
}

// chat sends the conversation and tools to the model, streams any text it
// writes to out as it arrives, and returns the complete message.
func chat(messages []Message, tools []ToolDef, out io.Writer) (Message, error) {
	body, err := json.Marshal(chatRequest{
		Model:    env("HARNESS_MODEL", "gemma4:e2b"),
		Messages: messages,
		Tools:    tools,
		Stream:   true,
	})
	if err != nil {
		return Message{}, err
	}

	url := env("HARNESS_BASE_URL", "http://localhost:11434/v1") + "/chat/completions"
	req, err := http.NewRequest("POST", url, bytes.NewReader(body))
	if err != nil {
		return Message{}, err
	}
	req.Header.Set("Content-Type", "application/json")
	if key := os.Getenv("HARNESS_API_KEY"); key != "" {
		req.Header.Set("Authorization", "Bearer "+key)
	}

	resp, err := httpClient.Do(req)
	if err != nil {
		return Message{}, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return Message{}, fmt.Errorf("model server returned %s", resp.Status)
	}
	return readStream(resp.Body, out)
}

// readStream assembles a streamed reply. Text is printed as it arrives; tool
// calls arrive in pieces keyed by index and are joined before anything runs.
func readStream(body io.Reader, out io.Writer) (Message, error) {
	reply := Message{Role: "assistant"}
	var text strings.Builder
	events := bufio.NewScanner(body)
	events.Buffer(make([]byte, 0, 64*1024), 1<<20) // a single event can exceed the 64 KB default
	for events.Scan() {
		data, ok := strings.CutPrefix(events.Text(), "data: ")
		if !ok {
			continue // blank separators and comments
		}
		if data == "[DONE]" {
			break
		}
		var chunk chatChunk
		if err := json.Unmarshal([]byte(data), &chunk); err != nil {
			return Message{}, fmt.Errorf("bad stream event: %w", err)
		}
		if len(chunk.Choices) == 0 {
			continue
		}
		delta := chunk.Choices[0].Delta
		if delta.Content != "" {
			if text.Len() == 0 {
				fmt.Fprint(out, "agent> ")
			}
			fmt.Fprint(out, delta.Content)
			text.WriteString(delta.Content)
		}
		for _, d := range delta.ToolCalls {
			for len(reply.ToolCalls) <= d.Index {
				reply.ToolCalls = append(reply.ToolCalls, ToolCall{Type: "function"})
			}
			call := &reply.ToolCalls[d.Index]
			if d.ID != "" {
				call.ID = d.ID
			}
			call.Function.Name += d.Function.Name
			call.Function.Arguments += d.Function.Arguments
		}
	}
	if err := events.Err(); err != nil {
		return Message{}, err
	}
	if text.Len() > 0 {
		fmt.Fprintln(out)
	}
	reply.Content = text.String()
	return reply, nil
}

// env reads an environment variable, falling back to a default.
func env(name, fallback string) string {
	if v := os.Getenv(name); v != "" {
		return v
	}
	return fallback
}

// runTurn is the agent loop: call the model, run any tools it asks for,
// send the results back, and repeat until the model answers in plain text
// or the step budget runs out.
func runTurn(history []Message) ([]Message, error) {
	for step := 0; step < maxSteps; step++ {
		reply, err := chat(history, toolDefs(), os.Stdout)
		if err != nil {
			return history, err
		}
		history = append(history, reply)

		if len(reply.ToolCalls) == 0 {
			return history, nil
		}

		for _, call := range reply.ToolCalls {
			fmt.Printf("  [tool] %s %s\n", call.Function.Name, call.Function.Arguments)
			history = append(history, Message{
				Role:       "tool",
				ToolCallID: call.ID,
				Content:    truncate(runTool(call)),
			})
		}
	}
	return history, fmt.Errorf("stopped after %d tool rounds; ask again to continue", maxSteps)
}

// runTool finds the tool by name, decodes its arguments, asks for approval
// when the tool is risky, and runs it. Errors go back to the model as text.
func runTool(call ToolCall) string {
	for _, t := range toolbox {
		if t.Name != call.Function.Name {
			continue
		}
		var args map[string]string
		if err := json.Unmarshal([]byte(call.Function.Arguments), &args); err != nil {
			return "error: bad arguments: " + err.Error()
		}
		if t.Risky && !approve(call) {
			return "error: the user denied this action. Do not retry it; ask the user what to do instead."
		}
		out, err := t.Run(args)
		if err != nil {
			return "error: " + err.Error()
		}
		return out
	}
	return "error: unknown tool " + call.Function.Name
}

// Tool pairs what the model sees (name, description, parameters)
// with what the harness does (Run). Risky tools need the user's approval.
type Tool struct {
	Name        string
	Description string
	Params      map[string]string // argument name -> description
	Risky       bool
	Run         func(args map[string]string) (string, error)
}

var toolbox = []Tool{
	{
		Name:        "list_files",
		Description: "List the files and folders in a directory inside the workspace.",
		Params:      map[string]string{"path": "Directory to list, relative to the workspace. Use . for the workspace root."},
		Run: func(args map[string]string) (string, error) {
			dir, err := safePath(args["path"])
			if err != nil {
				return "", err
			}
			entries, err := os.ReadDir(dir)
			if err != nil {
				return "", err
			}
			var b strings.Builder
			for _, e := range entries {
				name := e.Name()
				if e.IsDir() {
					name += "/"
				}
				b.WriteString(name + "\n")
			}
			return b.String(), nil
		},
	},
	{
		Name:        "read_file",
		Description: "Read a text file inside the workspace and return its contents.",
		Params:      map[string]string{"path": "Path to the file, relative to the workspace."},
		Run: func(args map[string]string) (string, error) {
			path, err := safePath(args["path"])
			if err != nil {
				return "", err
			}
			data, err := os.ReadFile(path)
			return string(data), err
		},
	},
	{
		Name:        "write_file",
		Description: "Create a new text file inside the workspace, or replace one completely. To change part of an existing file, use edit_file.",
		Params:      map[string]string{"path": "Path to the file, relative to the workspace.", "content": "The full new contents of the file."},
		Risky:       true,
		Run: func(args map[string]string) (string, error) {
			path, err := safePath(args["path"])
			if err != nil {
				return "", err
			}
			if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
				return "", err
			}
			if err := os.WriteFile(path, []byte(args["content"]), 0o644); err != nil {
				return "", err
			}
			return fmt.Sprintf("wrote %d bytes to %s", len(args["content"]), args["path"]), nil
		},
	},
	{
		Name:        "edit_file",
		Description: "Change part of a text file inside the workspace by replacing one exact snippet. Read the file first; old_text must appear exactly once.",
		Params: map[string]string{
			"path":     "Path to the file, relative to the workspace.",
			"old_text": "The exact text to replace, including whitespace. Include enough lines to make it unique.",
			"new_text": "The text to put in its place.",
		},
		Risky: true,
		Run: func(args map[string]string) (string, error) {
			path, err := safePath(args["path"])
			if err != nil {
				return "", err
			}
			data, err := os.ReadFile(path)
			if err != nil {
				return "", err
			}
			oldText := args["old_text"]
			switch n := strings.Count(string(data), oldText); {
			case oldText == "":
				return "", errors.New("old_text is empty")
			case n == 0:
				return "", errors.New("old_text was not found; read the file and copy the snippet exactly")
			case n > 1:
				return "", fmt.Errorf("old_text appears %d times; include more surrounding lines so it appears once", n)
			}
			edited := strings.Replace(string(data), oldText, args["new_text"], 1)
			if err := os.WriteFile(path, []byte(edited), 0o644); err != nil {
				return "", err
			}
			return "edited " + args["path"], nil
		},
	},
	{
		Name:        "run_command",
		Description: "Run a shell command in the workspace and return its combined output.",
		Params:      map[string]string{"command": "The command line to run."},
		Risky:       true,
		Run: func(args map[string]string) (string, error) {
			shell, flag := "sh", "-c"
			if runtime.GOOS == "windows" {
				shell, flag = "cmd", "/C"
			}
			ctx, cancel := context.WithTimeout(context.Background(), commandTimeout)
			defer cancel()

			cmd := exec.CommandContext(ctx, shell, flag, args["command"])
			cmd.Dir = workspace
			out, err := cmd.CombinedOutput()
			if errors.Is(ctx.Err(), context.DeadlineExceeded) {
				return string(out) + "\nerror: command timed out after " + commandTimeout.String(), nil
			}
			if err != nil {
				return string(out) + "\n" + err.Error(), nil
			}
			return string(out), nil
		},
	},
}

// toolDefs converts the toolbox into the JSON schema the model expects.
func toolDefs() []ToolDef {
	var defs []ToolDef
	for _, t := range toolbox {
		props := map[string]any{}
		var required []string
		for name, desc := range t.Params {
			props[name] = map[string]any{"type": "string", "description": desc}
			required = append(required, name)
		}
		sort.Strings(required)
		defs = append(defs, ToolDef{
			Type: "function",
			Function: FunctionDef{
				Name:        t.Name,
				Description: t.Description,
				Parameters:  map[string]any{"type": "object", "properties": props, "required": required},
			},
		})
	}
	return defs
}

// safePath resolves a path against the workspace, follows any symbolic links,
// and refuses anything whose real location is outside the workspace.
func safePath(p string) (string, error) {
	full := p
	if !filepath.IsAbs(p) {
		full = filepath.Join(workspace, p)
	}
	root, err := filepath.EvalSymlinks(workspace)
	if err != nil {
		return "", err
	}
	real, err := resolveLinks(full)
	if err != nil {
		return "", fmt.Errorf("%s: %w", p, err)
	}
	rel, err := filepath.Rel(root, real)
	if err != nil || !filepath.IsLocal(rel) {
		return "", fmt.Errorf("%s is outside the workspace %s", p, workspace)
	}
	return real, nil
}

// resolveLinks follows symbolic links in the longest existing part of path,
// so a file that doesn't exist yet resolves through its real parent folder.
func resolveLinks(path string) (string, error) {
	real, err := filepath.EvalSymlinks(path)
	if err == nil {
		return real, nil
	}
	if !errors.Is(err, fs.ErrNotExist) {
		return "", err
	}
	if _, lerr := os.Lstat(path); lerr == nil {
		// The name exists but its target doesn't: a broken link. Writing
		// through it would create the target, wherever it points.
		return "", errors.New("is a broken symbolic link")
	}
	parent := filepath.Dir(path)
	if parent == path {
		return path, nil
	}
	realParent, err := resolveLinks(parent)
	if err != nil {
		return "", err
	}
	return filepath.Join(realParent, filepath.Base(path)), nil
}

// approve asks the user before a risky tool runs.
func approve(call ToolCall) bool {
	fmt.Printf("  allow %s? [y/N] ", call.Function.Name)
	if !input.Scan() {
		return false
	}
	answer := strings.ToLower(strings.TrimSpace(input.Text()))
	return answer == "y" || answer == "yes"
}

// truncate keeps tool output from flooding the model's context window.
func truncate(s string) string {
	return clip(s, maxOutputBytes)
}

// clip cuts s to at most limit bytes and says how much it dropped.
func clip(s string, limit int) string {
	if len(s) <= limit {
		return s
	}
	return s[:limit] + fmt.Sprintf("\n[truncated %d bytes]", len(s)-limit)
}

func systemPrompt() string {
	return fmt.Sprintf(`You are a coding agent running on %s.
Your workspace is %s. Every path is relative to it.
Use the tools to look at files and run commands instead of guessing.
To change part of a file, use edit_file instead of rewriting it.
When a tool returns an error, read it and try a different approach.
Keep answers short and say which files you changed.`, runtime.GOOS, workspace)
}

// loadSession resumes the conversation saved in the workspace, or starts a new one.
func loadSession() []Message {
	fresh := []Message{{Role: "system", Content: systemPrompt()}}
	data, err := os.ReadFile(filepath.Join(workspace, sessionFile))
	if errors.Is(err, fs.ErrNotExist) {
		return fresh
	}
	var history []Message
	if err == nil {
		err = json.Unmarshal(data, &history)
	}
	if err != nil || len(history) == 0 || history[0].Role != "system" {
		fmt.Fprintf(os.Stderr, "warning: starting fresh; could not resume %s: %v\n", sessionFile, err)
		return fresh
	}
	if len(history) > 1 {
		fmt.Printf("Resumed %d messages from %s.\n", len(history)-1, sessionFile)
	}
	return history
}

// saveSession writes the conversation to the workspace so the next run can resume it.
// Tool results may include file contents, so only the owner can read the file.
func saveSession(history []Message) {
	data, err := json.MarshalIndent(history, "", "  ")
	if err == nil {
		err = os.WriteFile(filepath.Join(workspace, sessionFile), data, 0o600)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, "warning: could not save the session:", err)
	}
}

// compact replaces the conversation with a model-written summary once it
// grows past maxHistoryBytes. It runs between turns, so no tool call is left
// waiting for its result.
func compact(history []Message) ([]Message, error) {
	size := 0
	for _, m := range history {
		size += len(m.Content)
		for _, c := range m.ToolCalls {
			size += len(c.Function.Arguments)
		}
	}
	if size <= maxHistoryBytes || len(history) < 3 {
		return history, nil
	}

	// Send the summarizer plain text, not tool messages, and no tools, so it
	// answers in prose instead of calling a tool.
	var transcript strings.Builder
	if _, earlier, ok := strings.Cut(history[0].Content, summaryHeading); ok {
		fmt.Fprintf(&transcript, "summary of earlier turns: %s\n", earlier)
	}
	for _, m := range history[1:] {
		fmt.Fprintf(&transcript, "%s: %s\n", m.Role, clip(m.Content, maxSummaryInput))
		for _, c := range m.ToolCalls {
			fmt.Fprintf(&transcript, "%s called %s %s\n", m.Role, c.Function.Name, clip(c.Function.Arguments, maxSummaryInput))
		}
	}
	summary, err := chat([]Message{
		{Role: "system", Content: "Summarize this conversation between a user and a coding agent. Keep file names, decisions, and unfinished work. Use at most 200 words."},
		{Role: "user", Content: transcript.String()},
	}, nil, io.Discard)
	if err != nil {
		return history, err
	}
	fmt.Printf("  [compacted %d messages into a summary]\n", len(history)-1)
	return []Message{{
		Role:    "system",
		Content: systemPrompt() + summaryHeading + summary.Content,
	}}, nil
}
