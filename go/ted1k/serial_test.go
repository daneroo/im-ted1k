package ted1k

import (
	"testing"
)

// Only tests for errors
func TestFindSerialDevice(t *testing.T) {
	var data = []struct {
		baseDirs []string // input
		err      string   // expected
	}{
		{
			baseDirs: nil,
			err:      "Unable to find a serial device in [\"/hostdev\" \"/dev\"]",
		},
		{
			baseDirs: []string{},
			err:      "Unable to find a serial device in [\"/hostdev\" \"/dev\"]",
		},
		{
			baseDirs: []string{"/notexist"},
			err:      "Unable to find a serial device in [\"/notexist\"]",
		},
	}
	for _, tt := range data {

		if _, err := findSerialDevice(tt.baseDirs); err.Error() != tt.err {
			t.Errorf("Expected error of %q, but it was %q instead.", tt.err, err.Error())
		}

	}
}
