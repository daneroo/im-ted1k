package ted1k

import (
	"log"
	"time"

	"github.com/tarm/serial"
)

// Entry represents a sensor reading at a specific time
type Entry struct {
	Stamp time.Time `json:"stamp"`
	Watts int       `json:"watt"`
	Volts float32   `json:"-"` // or "volt,omitempty"
}

// EntryWriter is the interface for "handling a single entry"
type EntryWriter interface {
	Write(e Entry) (err error)
	Close() (err error)
}

// StartLoop performs the read loop:
// - Take a measurement from serial port (poll()),
// - Store to the database,
// - Calculate delay to make loop every second (with offset)
// TODO(daneroo): move discovery (invocation) out to main
// TODO(daneroo): Create a New method to store state/config (sql.DB,serial.Port,decoderState{escapeFlag,buffer})
func StartLoop(writers []EntryWriter) error {

	serialName, err := findSerialDevice(nil)
	if err != nil {
		return err
	}
	log.Printf("Discovered serial port: %s", serialName)

	// ReadTimeout: makes the port.Read() non-blocking, causing a more sophisticated readResponse()
	// smallest possible value: 0.1s time.Millisecond * 100
	c := &serial.Config{Name: serialName, Baud: 19200, ReadTimeout: time.Millisecond * 100}
	s, err := serial.OpenPort(c)
	if err != nil {
		return err
	}
	log.Printf("Connected to serial port: %s", serialName)

	state := &decoderState{buffer: nil, escapeFlag: false}
	for {
		loopStart := time.Now().UTC()
		entries, err := state.poll(s)
		if err != nil {
			return err
		}
		// We set the time stamp associated to the polled value immediately *after* it has been read.
		// This is also truncated (rounded down) to the second
		stamp := time.Now().UTC().Truncate(time.Second)

		if len(entries) == 0 {
			log.Printf("warning: skipping entry (no entry from poll)\n")
		} else {
			if len(entries) > 1 {
				log.Printf("warning: multiple entries: %d (keeping last)", len(entries))
			}
			entry := entries[len(entries)-1]
			// state.poll does not set the stamp
			entry.Stamp = stamp
			// Call handler in goroutine. (This was sometime holding up the main loop.)
			for _, writer := range writers {
				go writer.Write(entry)
			}

			log.Printf("%s watts: %d volts: %.1f\n", stamp, entry.Watts, entry.Volts)
		}

		if delay := time.Since(loopStart); delay > time.Second {
			log.Printf("warning: skipping entry (loop took %v>1s)\n", delay)
		}
		offset := 10 * time.Millisecond // used to be 0.1s
		time.Sleep(delayUntilNextSecond(time.Now(), offset))
	}
}
