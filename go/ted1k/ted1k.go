package ted1k

import (
	"database/sql"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"path"
	"reflect"
	"strings"
	"time"

	"github.com/tarm/serial"
)

var serialDeviceBaseDirs = []string{"/hostdev", "/dev"}

const fmtRFC3339NoZ = "2006-01-02T15:04:05"

type entry struct {
	stamp string // now.UTC().Format(fmtRFC3339NoZ) no timezone for db insert
	watts int
	volts float32
}

// TODO(daneroo): remove
func showState(msg string, state *state) {
	if state.escapeFlag || len(state.packetBuffer) > 0 {
		log.Printf("%sstate: escape=%v buf=%d %s\n", msg, state.escapeFlag, len(state.packetBuffer), hex.EncodeToString(state.packetBuffer))
	}
}

// StartLoop performs the read loop:
// - Take a measurement from serial port (poll()),
// - Store to the database,
// - Calculate delay to make loop every second (with offset)
// TODO(daneroo): move discovery (invocation) out to main
func StartLoop(db *sql.DB) error {

	serialName, err := findSerialDevice(serialDeviceBaseDirs)
	if err != nil {
		return err
	}
	log.Printf("Using serial port: %s", serialName)

	// ReadTimeout: makes the port.Read() non-blocking, causing a more sophisticated readRresponse()
	//  smallest possible value: 0.1s time.Millisecond * 100,  1 deciSecond
	c := &serial.Config{Name: serialName, Baud: 19200, ReadTimeout: time.Millisecond * 100}
	s, err := serial.OpenPort(c)
	if err != nil {
		return err
	}
	log.Printf("Connected to serial port: %s", serialName)

	state := &state{packetBuffer: nil, escapeFlag: false}
	showState("-", state)
	for {
		stamp := time.Now().UTC().Format(fmtRFC3339NoZ) // stamp is set to second (before poll() is called)
		entry, err := poll(s, state)
		if err != nil {
			return err
		}
		showState("+", state)

		// stamp should be before calling poll?
		if entry != nil {
			log.Printf("%s watts: %d volts: %.1f\n", stamp, entry.watts, entry.volts)
			insertEntry(db, stamp, entry.watts)
		} else {
			log.Printf("warning: skipping entry (nil)\n")
		}
		offset := 10 * time.Millisecond // used to be 0.1s
		time.Sleep(delayUntilNextSecond(time.Now(), offset))
	}
}

// TODO(daneroo): Create a New method to store state (serial.Port,escapeFlag,packetBuffer)
func poll(s *serial.Port, state *state) (*entry, error) {
	err := writeRequest(s)
	if err != nil {
		return nil, err
	}
	raw, err := readResponse(s)
	if err != nil {
		return nil, err
	}
	entry := extract(raw, state)
	if entry == nil {
	}
	return entry, nil
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

func extract(raw []byte, state *state) *entry {
	packets := decode(raw, state)
	if len(packets) == 0 {
		return nil
	}
	if len(packets) > 1 {
		log.Printf("warning: extract got multiple packets: %d", len(packets))
	}
	decoded := packets[0]
	if len(decoded) != 278 {
		log.Printf("raw: %d %s", len(raw), hex.EncodeToString(raw))
		return nil
	}
	/*
		see [this](https://docs.python.org/2/library/struct.html) to decode python format in ted.py
			_protocol_len = 278
			# Offset,  name,             fmt,     scale
			(82,       'kw_rate',        "<H",    0.0001),
			(108,      'house_code',     "<B",    1),
			(247,      'kw',             "<H",    0.01),
			(251,      'volts',          "<H",    0.1),
	*/
	watts := int(binary.LittleEndian.Uint16(decoded[247:249]) * 10)
	volts := float32(binary.LittleEndian.Uint16(decoded[251:253])) / 10
	return &entry{watts: watts, volts: volts}
}

type state struct {
	stamp        string // now.UTC().Format(fmtRFC3339NoZ) no timezone for db insert
	packetBuffer []byte
	escapeFlag   bool
}

// TODO(daneroo): perhaps this should be a channel writer...
// Can accumulate bytes corresponding to more than one frame
func decode(raw []byte, state *state) [][]byte {
	const escapeByte byte = 0x10
	const packetBegin byte = 0x04
	const packetEnd byte = 0x03

	var packets = make([][]byte, 0, 1)
	for _, b := range raw {
		if state.escapeFlag {
			state.escapeFlag = false
			if b == escapeByte {
				if state.packetBuffer != nil {
					state.packetBuffer = append(state.packetBuffer, b)
				}
			} else if b == packetBegin {
				state.packetBuffer = make([]byte, 0, 278) // set expected capacity
				state.stamp = time.Now().UTC().Format(fmtRFC3339NoZ)
			} else if b == packetEnd {
				if state.packetBuffer != nil {
					packets = append(packets, state.packetBuffer)
					state.packetBuffer = nil
					state.stamp = ""
				}
			} else {
				panic(fmt.Sprintf("Unknown escape byte %x", b))
			}
		} else if b == escapeByte {
			state.escapeFlag = true
		} else {
			state.packetBuffer = append(state.packetBuffer, b)
		}
	}
	return packets
}

// conditional on database connection type - Yay SQL
// This is one approach to the dialect specific queries
func insertSQLFormat(db *sql.DB) string {
	const insertSQLFormatMySQL = "INSERT IGNORE INTO watt (stamp, watt) VALUES ('%s',%d)"
	const insertSQLFormatSQLITE = "INSERT OR IGNORE INTO watt (stamp, watt) VALUES ('%s',%d)"

	driverName := reflect.ValueOf(db.Driver()).Type().String()
	// log.Printf("db.Driver.Name: %s\n", driverName)
	switch driverName {
	case "*mysql.MySQLDriver":
		return insertSQLFormatMySQL
	case "*sqlite3.SQLiteDriver":
		return insertSQLFormatSQLITE
	default:
		log.Fatalf("Could not create insert statement for unknown driver: %s", driverName)
		return ""
	}

}

// insertEntry inserts one entry - ignores if duplicate key (stamp)
func insertEntry(db *sql.DB, stamp string, watts int) error {
	// const insertSQLFormat = "INSERT INTO watt (stamp, watt) VALUES ('%s',%d)"
	insertSQLFormat := insertSQLFormat(db)
	insertSQL := fmt.Sprintf(insertSQLFormat, stamp, watts)
	_, err := db.Exec(insertSQL)
	if err != nil {
		// TODO(daneroo): Second option to dialect problem is to catch, the insert duplicate
		// and safely ignore the error in this case (insert [or] ignore)
		// MySQL:  Error 1062: Duplicate entry '1966-05-16 01:23:45' for key 'PRIMARY'
		// Sqlite: UNIQUE constraint failed: watt.stamp
		log.Println(err)
		return err
	}

	return nil
}

func findSerialDevice(baseDirs []string) (string, error) {
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
