// harness talks to a model through an OpenAI-compatible Chat Completions API.
package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
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
	maxSteps       = 25               // tool rounds allowed per user message
	maxOutputBytes = 10_000           // longest tool result sent back to the model
	commandTimeout = 60 * time.Second // longest a shell command may run
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
}

type chatResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

func main() {
	var err error
	workspace, err = os.Getwd()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}

	history := []Message{{Role: "system", Content: systemPrompt()}}
	fmt.Printf("Agent ready in %s. Type /reset to start over, /quit to exit.\n", workspace)
	for {
		fmt.Print("\nyou> ")
		if !input.Scan() {
			return
		}
		line := strings.TrimSpace(input.Text())
		switch line {
		case "":
			continue
		case "/quit":
			return
		case "/reset":
			history = history[:1]
			fmt.Println("History cleared.")
			continue
		}

		history = append(history, Message{Role: "user", Content: line})
		history, err = runTurn(history)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
		}
	}
}

// chat sends the whole conversation to the model and returns its next message.
func chat(messages []Message) (Message, error) {
	body, err := json.Marshal(chatRequest{
		Model:    env("HARNESS_MODEL", "gemma4:e2b"),
		Messages: messages,
		Tools:    toolDefs(),
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

	var out chatResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return Message{}, err
	}
	if len(out.Choices) == 0 {
		return Message{}, fmt.Errorf("model returned no choices")
	}
	return out.Choices[0].Message, nil
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
		reply, err := chat(history)
		if err != nil {
			return history, err
		}
		history = append(history, reply)

		if len(reply.ToolCalls) == 0 {
			fmt.Println("agent>", reply.Content)
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
		Description: "Create or overwrite a text file inside the workspace.",
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

// safePath resolves a path against the workspace and refuses anything outside it.
func safePath(p string) (string, error) {
	full := p
	if !filepath.IsAbs(p) {
		full = filepath.Join(workspace, p)
	}
	rel, err := filepath.Rel(workspace, full)
	if err != nil || !filepath.IsLocal(rel) {
		return "", fmt.Errorf("%s is outside the workspace %s", p, workspace)
	}
	return filepath.Join(workspace, rel), nil
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
	if len(s) <= maxOutputBytes {
		return s
	}
	return s[:maxOutputBytes] + fmt.Sprintf("\n[truncated %d bytes]", len(s)-maxOutputBytes)
}

func systemPrompt() string {
	return fmt.Sprintf(`You are a coding agent running on %s.
Your workspace is %s. Every path is relative to it.
Use the tools to look at files and run commands instead of guessing.
When a tool returns an error, read it and try a different approach.
Keep answers short and say which files you changed.`, runtime.GOOS, workspace)
}
