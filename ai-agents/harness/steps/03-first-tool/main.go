// harness talks to a model through an OpenAI-compatible Chat Completions API.
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
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

var tools = []ToolDef{{
	Type: "function",
	Function: FunctionDef{
		Name:        "read_file",
		Description: "Read a text file and return its contents.",
		Parameters: map[string]any{
			"type": "object",
			"properties": map[string]any{
				"path": map[string]any{"type": "string", "description": "Path to the file."},
			},
			"required": []string{"path"},
		},
	},
}}

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
		Tools:    tools,
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

// runTool executes one tool call. Errors go back to the model as text,
// so it can read them and try something else.
func runTool(call ToolCall) string {
	if call.Function.Name != "read_file" {
		return "error: unknown tool " + call.Function.Name
	}
	var args struct {
		Path string `json:"path"`
	}
	if err := json.Unmarshal([]byte(call.Function.Arguments), &args); err != nil {
		return "error: bad arguments: " + err.Error()
	}
	data, err := os.ReadFile(args.Path)
	if err != nil {
		return "error: " + err.Error()
	}
	return string(data)
}
