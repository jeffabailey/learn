// harness talks to a model through an OpenAI-compatible Chat Completions API.
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"sort"
	"strings"
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
	var history []Message
	input := bufio.NewScanner(os.Stdin)

	fmt.Println("Agent ready. Type /quit to exit.")
	for {
		fmt.Print("\nyou> ")
		if !input.Scan() {
			return
		}
		line := strings.TrimSpace(input.Text())
		if line == "" {
			continue
		}
		if line == "/quit" {
			return
		}

		history = append(history, Message{Role: "user", Content: line})
		var err error
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

	resp, err := http.DefaultClient.Do(req)
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
// send the results back, and repeat until the model answers in plain text.
func runTurn(history []Message) ([]Message, error) {
	for {
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
				Content:    runTool(call),
			})
		}
	}
}

// runTool finds the tool by name, decodes its arguments, and runs it.
// Errors go back to the model as text, so it can read them and adjust.
func runTool(call ToolCall) string {
	for _, t := range toolbox {
		if t.Name != call.Function.Name {
			continue
		}
		var args map[string]string
		if err := json.Unmarshal([]byte(call.Function.Arguments), &args); err != nil {
			return "error: bad arguments: " + err.Error()
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
// with what the harness does (Run).
type Tool struct {
	Name        string
	Description string
	Params      map[string]string // argument name -> description
	Run         func(args map[string]string) (string, error)
}

var toolbox = []Tool{
	{
		Name:        "list_files",
		Description: "List the files and folders in a directory.",
		Params:      map[string]string{"path": "Directory to list. Use . for the current directory."},
		Run: func(args map[string]string) (string, error) {
			entries, err := os.ReadDir(args["path"])
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
		Description: "Read a text file and return its contents.",
		Params:      map[string]string{"path": "Path to the file."},
		Run: func(args map[string]string) (string, error) {
			data, err := os.ReadFile(args["path"])
			return string(data), err
		},
	},
	{
		Name:        "write_file",
		Description: "Create or overwrite a text file with the given content.",
		Params:      map[string]string{"path": "Path to the file.", "content": "The full new contents of the file."},
		Run: func(args map[string]string) (string, error) {
			err := os.WriteFile(args["path"], []byte(args["content"]), 0o644)
			if err != nil {
				return "", err
			}
			return fmt.Sprintf("wrote %d bytes to %s", len(args["content"]), args["path"]), nil
		},
	},
	{
		Name:        "run_command",
		Description: "Run a shell command and return its combined output.",
		Params:      map[string]string{"command": "The command line to run."},
		Run: func(args map[string]string) (string, error) {
			shell, flag := "sh", "-c"
			if runtime.GOOS == "windows" {
				shell, flag = "cmd", "/C"
			}
			out, err := exec.Command(shell, flag, args["command"]).CombinedOutput()
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
