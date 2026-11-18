package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

// streamReply sends msg the way an OpenAI-compatible server streams it:
// text split across two events, and each tool call's arguments split in two.
func streamReply(w http.ResponseWriter, msg Message) {
	w.Header().Set("Content-Type", "text/event-stream")
	send := func(delta map[string]any) {
		data, _ := json.Marshal(map[string]any{"choices": []map[string]any{{"delta": delta}}})
		fmt.Fprintf(w, "data: %s\n\n", data)
	}
	if half := len(msg.Content) / 2; msg.Content != "" {
		send(map[string]any{"role": "assistant", "content": msg.Content[:half]})
		send(map[string]any{"content": msg.Content[half:]})
	}
	for i, c := range msg.ToolCalls {
		half := len(c.Function.Arguments) / 2
		send(map[string]any{"tool_calls": []map[string]any{{"index": i, "id": c.ID, "type": "function",
			"function": map[string]any{"name": c.Function.Name, "arguments": c.Function.Arguments[:half]}}}})
		send(map[string]any{"tool_calls": []map[string]any{{"index": i,
			"function": map[string]any{"arguments": c.Function.Arguments[half:]}}}})
	}
	fmt.Fprint(w, "data: [DONE]\n\n")
}

// fakeModel starts a model server that answers each request with reply(req).
func fakeModel(t *testing.T, reply func(chatRequest) Message) *int {
	t.Helper()
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var req chatRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			t.Errorf("bad request body: %v", err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		if !req.Stream {
			t.Error("request did not ask for a streamed reply")
		}
		calls++
		streamReply(w, reply(req))
	}))
	t.Cleanup(server.Close)
	t.Setenv("HARNESS_BASE_URL", server.URL)
	return &calls
}

func findTool(name string) Tool {
	for _, t := range toolbox {
		if t.Name == name {
			return t
		}
	}
	panic("no tool " + name)
}

func TestSafePathKeepsAgentInsideWorkspace(t *testing.T) {
	workspace = t.TempDir()

	for _, p := range []string{"notes.txt", "src/main.go", ".", "a/../b.txt"} {
		if _, err := safePath(p); err != nil {
			t.Errorf("safePath(%q) refused a path inside the workspace: %v", p, err)
		}
	}
	outside := filepath.Join(filepath.Dir(workspace), "secrets.txt")
	for _, p := range []string{"..", "../secrets.txt", "a/../../b.txt", outside} {
		if _, err := safePath(p); err == nil {
			t.Errorf("safePath(%q) allowed a path outside the workspace", p)
		}
	}
}

func TestSafePathFollowsSymlinks(t *testing.T) {
	workspace = t.TempDir()
	outside := t.TempDir()
	if err := os.WriteFile(filepath.Join(outside, "secret.txt"), []byte("s"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.Mkdir(filepath.Join(workspace, "real"), 0o755); err != nil {
		t.Fatal(err)
	}
	links := map[string]string{
		"escape":   outside,                               // a folder outside
		"dangling": filepath.Join(outside, "missing.txt"), // a file that doesn't exist yet
		"alias":    filepath.Join(workspace, "real"),      // a folder inside
	}
	for name, target := range links {
		if err := os.Symlink(target, filepath.Join(workspace, name)); err != nil {
			t.Skipf("cannot create symbolic links here: %v", err)
		}
	}

	for _, p := range []string{"escape", "escape/secret.txt", "escape/new.txt", "dangling"} {
		if _, err := safePath(p); err == nil {
			t.Errorf("safePath(%q) followed a link out of the workspace", p)
		}
	}
	if _, err := safePath("alias/new.txt"); err != nil {
		t.Errorf("safePath refused a link that stays inside the workspace: %v", err)
	}
}

func TestReadStreamJoinsToolCallPieces(t *testing.T) {
	stream := strings.Join([]string{
		`data: {"choices":[{"delta":{"content":"Let me "}}]}`,
		`data: {"choices":[{"delta":{"content":"look."}}]}`,
		`data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"a","function":{"name":"read_file","arguments":"{\"pa"}}]}}]}`,
		`data: {"choices":[{"delta":{"tool_calls":[{"index":1,"id":"b","function":{"name":"list_files","arguments":"{\"path\":\".\"}"}}]}}]}`,
		`data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"th\":\"x\"}"}}]}}]}`,
		`data: [DONE]`,
	}, "\n\n")
	var printed strings.Builder

	reply, err := readStream(strings.NewReader(stream), &printed)
	if err != nil {
		t.Fatal(err)
	}
	if printed.String() != "agent> Let me look.\n" {
		t.Errorf("printed %q", printed.String())
	}
	want := []ToolCall{
		{ID: "a", Type: "function", Function: FunctionCall{Name: "read_file", Arguments: `{"path":"x"}`}},
		{ID: "b", Type: "function", Function: FunctionCall{Name: "list_files", Arguments: `{"path":"."}`}},
	}
	if reply.Content != "Let me look." || !reflect.DeepEqual(reply.ToolCalls, want) {
		t.Errorf("got %+v", reply)
	}
}

// TestAgentLoopRunsToolThenAnswers fakes a model server that asks for
// read_file once, then answers with what the tool returned.
func TestAgentLoopRunsToolThenAnswers(t *testing.T) {
	workspace = t.TempDir()
	if err := os.WriteFile(filepath.Join(workspace, "go.mod"), []byte("module demo\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	calls := fakeModel(t, func(req chatRequest) Message {
		last := req.Messages[len(req.Messages)-1]
		if last.Role == "tool" {
			return Message{Role: "assistant", Content: "The file says: " + last.Content}
		}
		return Message{Role: "assistant", ToolCalls: []ToolCall{{
			ID:       "call_1",
			Type:     "function",
			Function: FunctionCall{Name: "read_file", Arguments: `{"path":"go.mod"}`},
		}}}
	})

	history, err := runTurn([]Message{{Role: "user", Content: "What is in go.mod?"}})
	if err != nil {
		t.Fatal(err)
	}
	if *calls != 2 {
		t.Errorf("expected 2 model calls (tool request, then answer), got %d", *calls)
	}
	final := history[len(history)-1]
	if !strings.Contains(final.Content, "module demo") {
		t.Errorf("final answer did not include the tool result: %q", final.Content)
	}
}

func TestEditFileReplacesOneExactSnippet(t *testing.T) {
	workspace = t.TempDir()
	path := filepath.Join(workspace, "app.py")
	edit := findTool("edit_file").Run
	write := func(s string) {
		if err := os.WriteFile(path, []byte(s), 0o644); err != nil {
			t.Fatal(err)
		}
	}

	write("a = 1\nb = 2\n")
	if _, err := edit(map[string]string{"path": "app.py", "old_text": "b = 2", "new_text": "b = 3"}); err != nil {
		t.Fatal(err)
	}
	if got, _ := os.ReadFile(path); string(got) != "a = 1\nb = 3\n" {
		t.Errorf("file is %q", got)
	}

	write("x\nx\n")
	for old, want := range map[string]string{"x": "appears 2 times", "y": "not found", "": "empty"} {
		_, err := edit(map[string]string{"path": "app.py", "old_text": old, "new_text": "z"})
		if err == nil || !strings.Contains(err.Error(), want) {
			t.Errorf("old_text %q: got %v, want an error containing %q", old, err, want)
		}
	}
	if got, _ := os.ReadFile(path); string(got) != "x\nx\n" {
		t.Errorf("a refused edit changed the file to %q", got)
	}
}

func TestSessionSurvivesRestart(t *testing.T) {
	workspace = t.TempDir()
	history := []Message{
		{Role: "system", Content: systemPrompt()},
		{Role: "user", Content: "My name is Inigo Montoya."},
		{Role: "assistant", ToolCalls: []ToolCall{{ID: "1", Type: "function", Function: FunctionCall{Name: "read_file", Arguments: `{"path":"x"}`}}}},
		{Role: "tool", ToolCallID: "1", Content: "contents"},
	}

	saveSession(history)
	if got := loadSession(); !reflect.DeepEqual(got, history) {
		t.Errorf("loaded %+v", got)
	}

	if err := os.WriteFile(filepath.Join(workspace, sessionFile), []byte("not json"), 0o600); err != nil {
		t.Fatal(err)
	}
	if got := loadSession(); len(got) != 1 || got[0].Role != "system" {
		t.Errorf("a corrupt session file should start fresh, got %+v", got)
	}
}

func TestCompactSummarizesLongHistory(t *testing.T) {
	workspace = t.TempDir()
	calls := fakeModel(t, func(req chatRequest) Message {
		if len(req.Tools) != 0 {
			t.Error("the summary request offered tools")
		}
		return Message{Role: "assistant", Content: "User is building fizz.py."}
	})
	short := []Message{{Role: "system", Content: systemPrompt()}, {Role: "user", Content: "hi"}, {Role: "assistant", Content: "hello"}}

	if got, err := compact(short); err != nil || !reflect.DeepEqual(got, short) || *calls != 0 {
		t.Fatalf("a short history should pass through untouched: %v, %d calls", err, *calls)
	}

	long := append(short, Message{Role: "tool", Content: strings.Repeat("x", maxHistoryBytes)})
	got, err := compact(long)
	if err != nil {
		t.Fatal(err)
	}
	if len(got) != 1 || got[0].Role != "system" || !strings.HasSuffix(got[0].Content, summaryHeading+"User is building fizz.py.") {
		t.Errorf("got %+v", got)
	}

	// A second compaction replaces the old summary instead of stacking another.
	again, err := compact(append(got, Message{Role: "user", Content: strings.Repeat("y", maxHistoryBytes)}))
	if err != nil {
		t.Fatal(err)
	}
	if strings.Count(again[0].Content, summaryHeading) != 1 {
		t.Errorf("summaries stacked: %q", again[0].Content)
	}
}

func TestTruncateLimitsToolOutput(t *testing.T) {
	short := "hello"
	if got := truncate(short); got != short {
		t.Errorf("truncate changed short output: %q", got)
	}
	long := strings.Repeat("x", maxOutputBytes+500)
	got := truncate(long)
	if !strings.HasPrefix(got, strings.Repeat("x", maxOutputBytes)) || !strings.Contains(got, "[truncated 500 bytes]") {
		t.Errorf("truncate did not cut and label long output, got %d bytes", len(got))
	}
}

func TestUnknownToolReturnsErrorToModel(t *testing.T) {
	got := runTool(ToolCall{Function: FunctionCall{Name: "delete_everything", Arguments: "{}"}})
	if !strings.HasPrefix(got, "error: unknown tool") {
		t.Errorf("expected an unknown-tool error, got %q", got)
	}
}
