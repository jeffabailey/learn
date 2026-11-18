package main

import (
	"strings"
	"testing"
)

// The tutorial's main_test.go covers the workspace fence and the agent loop.
// These two tests cover the rest of Step 5's guardrails.

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
