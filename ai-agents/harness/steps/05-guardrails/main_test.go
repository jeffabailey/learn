package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

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

// TestAgentLoopRunsToolThenAnswers fakes a model server that asks for
// read_file once, then answers with what the tool returned.
func TestAgentLoopRunsToolThenAnswers(t *testing.T) {
	workspace = t.TempDir()
	if err := os.WriteFile(filepath.Join(workspace, "go.mod"), []byte("module demo\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var req chatRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			t.Errorf("bad request body: %v", err)
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		calls++

		var reply Message
		last := req.Messages[len(req.Messages)-1]
		if last.Role == "tool" {
			reply = Message{Role: "assistant", Content: "The file says: " + last.Content}
		} else {
			reply = Message{Role: "assistant", ToolCalls: []ToolCall{{
				ID:       "call_1",
				Type:     "function",
				Function: FunctionCall{Name: "read_file", Arguments: `{"path":"go.mod"}`},
			}}}
		}
		json.NewEncoder(w).Encode(map[string]any{"choices": []map[string]any{{"message": reply}}})
	}))
	defer server.Close()
	t.Setenv("HARNESS_BASE_URL", server.URL)

	history, err := runTurn([]Message{{Role: "user", Content: "What is in go.mod?"}})
	if err != nil {
		t.Fatal(err)
	}
	if calls != 2 {
		t.Errorf("expected 2 model calls (tool request, then answer), got %d", calls)
	}
	final := history[len(history)-1]
	if !strings.Contains(final.Content, "module demo") {
		t.Errorf("final answer did not include the tool result: %q", final.Content)
	}
}
