package ted1k

import (
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"path"
	"strings"
	"time"

	"github.com/tarm/serial"
)

var defaultSerialDeviceBaseDirs = []string{"/hostdev", "/dev"}

// Travers directories, and look for usb serial devices (Linux and MacOS)
func findSerialDevice(baseDirs []string) (string, error) {
	if len(baseDirs) == 0 {
		baseDirs = defaultSerialDeviceBaseDirs
	}
	for _, baseDir := range baseDirs {
		contents, _ := ioutil.ReadDir(baseDir)

		// Look for what is mostly likely the Arduino device
		for _, f := range contents {
			if strings.Contains(f.Name(), "tty.usbserial") ||
				strings.Contains(f.Name(), "ttyUSB") {
				return path.Join(baseDir, f.Name()), nil
			}
		}
	}
	// Have not been able to find a USB device that 'looks'
	// like an Arduino.
	return "", fmt.Errorf("Unable to find a serial device in %q", baseDirs)
}

// write the request packet to the serial port
func writeRequest(s *serial.Port) error {
	const packetRequestByte byte = 0xaa
	_, err := s.Write([]byte{packetRequestByte})
	return err
}

// Read available response frm the serial port
// Now that the serial port is non-blocking, we accumulate the response
// Termination condition is read:n==0
// We account for the fact that the first response bytes might take a while to come:
// - First sleep for 300ms
// - If we get a read:n==0 we only return if we have already started receiving bytes
// - Otherwise we can attempt up to zeroLengthTerminationCount times
// We return the accumulated read bytes.
func readResponse(s *serial.Port) ([]byte, error) {
	delayBeforeFirstRead := time.Millisecond * 300
	zeroLengthTerminationCount := 4
	zeroLengthTimeouts := 0

	// Sleep before first Read
	time.Sleep(delayBeforeFirstRead)

	// returned output bytes
	out := make([]byte, 0)
	// buffer for reading (inner loop) re-used, only allocated once
	raw := make([]byte, 4096)
	for {
		n, err := s.Read(raw)
		if err != nil && err != io.EOF { // zero bytes will produce an EOF error
			return nil, err
		}
		if n == 0 { // might also break if accumulated>282,283, or as soon as decode is integrated
			zeroLengthTimeouts++
			if zeroLengthTimeouts > 1 { // tone down debug logging
				log.Printf("debug: s.Read break (n=0) #%d out:%d", zeroLengthTimeouts, len(out))
			}
			if len(out) > 0 || zeroLengthTimeouts > zeroLengthTerminationCount {
				break
			}
		} else {
			out = append(out, raw[:n]...)
			// wait before we read again
			time.Sleep(time.Millisecond * 50)
		}
	}

	return out, nil
}
