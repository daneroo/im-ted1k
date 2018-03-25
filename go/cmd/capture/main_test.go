package main

import "testing"

func TestSmoke(t *testing.T) {
	if 1 != 1 {
		t.Errorf("Basic test should always pass")
	}
}
