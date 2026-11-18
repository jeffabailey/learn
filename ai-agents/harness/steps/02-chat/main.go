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
	Role    string `json:"role"`
	Content string `json:"content"`
}

type chatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
}

type chatResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

func main() {
	var history []Message
	input := bufio.NewScanner(os.Stdin)

	fmt.Println("Chat with the model. Type /quit to exit.")
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
		reply, err := chat(history)
		if err != nil {
			fmt.Fprintln(os.Stderr, "error:", err)
			history = history[:len(history)-1]
			continue
		}
		history = append(history, reply)
		fmt.Println("model>", reply.Content)
	}
}

// chat sends the whole conversation to the model and returns its next message.
func chat(messages []Message) (Message, error) {
	body, err := json.Marshal(chatRequest{
		Model:    env("HARNESS_MODEL", "gemma4:e2b"),
		Messages: messages,
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
