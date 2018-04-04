package ted1k

import (
	"testing"
)

func TestSomething(t *testing.T) {
	if 1 == 0 {
		t.Errorf("Expected 1 to be different from 0")
	}
}
