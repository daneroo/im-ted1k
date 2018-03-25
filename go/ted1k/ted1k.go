package ted1k

import (
	"encoding/binary"
	"fmt"
	"io/ioutil"
	"log"
	"path"
	"strings"
	"time"

	"github.com/tarm/serial"
)

var serialDeviceBaseDirs = []string{"/hostdev", "/dev"}

const packetRequestByte byte = 0xaa
const escapeByte byte = 0x10
const packetBegin byte = 0x04
const packetEnd byte = 0x03

type entry struct {
	watts int
	volts float32
}

// StartLoop performs the read loop:
// - Take a measurement from serial port,
// - Store to the database,
// - Calculate delay to make loop every second
func StartLoop() error {

	serialName, err := findSerialDevice(serialDeviceBaseDirs)
	log.Printf("Using serial port: %s", serialName)

	// omitted ReadTimeout: e.g.: time.Millisecond * 500
	// c := &serial.Config{Name: "/hostdev/ttyUSB0", Baud: 19200}
	c := &serial.Config{Name: serialName, Baud: 19200}
	s, err := serial.OpenPort(c)
	if err != nil {
		return err
	}
	log.Printf("Connected to serial port: %s", serialName)

	for {
		entry, err := fetchAndReadValues(s)
		if err != nil {
			return err
		}
		now := time.Now()
		stamp := now.UTC().Format(time.RFC3339)
		if entry != nil {
			log.Printf("%s watts: %d volts: %.1f\n", stamp, entry.watts, entry.volts)
		}
		sleepUntilNextSecondWithOffset(now)
	}
}

// TODO:daneroo what if we are betweem (0,desiredOffet]?
func sleepUntilNextSecondWithOffset(now time.Time) {
	desiredOffsetNanos := 100000000 // .1s
	nanosUntilNextSecondPlusOffset := time.Duration(1000000000 - now.Nanosecond() + desiredOffsetNanos)
	time.Sleep(nanosUntilNextSecondPlusOffset)
}

func fetchAndReadValues(s *serial.Port) (*entry, error) {
	raw, err := fetchAndReadBuffer(s)
	if err != nil {
		return nil, err
	}
	entry := decodeValues(raw)
	if entry == nil {
		log.Printf("warning: skipping entry |raw|=%d |decoded|=%d\n", len(raw), len(decodeBuffer(raw)))

	}
	return entry, nil
}

func fetchAndReadBuffer(s *serial.Port) ([]byte, error) {
	n, err := s.Write([]byte{packetRequestByte})
	if err != nil {
		return nil, err
	}

	raw := make([]byte, 4096)
	n, err = s.Read(raw)
	if err != nil {
		return nil, err
	}
	raw = raw[:n]
	// log.Printf("raw: n:%d raw[:n]:%q", n, raw[:n])
	return raw, nil
}

func decodeValues(raw []byte) *entry {
	decoded := decodeBuffer(raw)
	if len(decoded) != 278 {
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

func decodeBuffer(raw []byte) []byte {
	decoded := make([]byte, 0)
	escapeFlag := false
	for _, b := range raw {
		switch {
		case escapeFlag:
			escapeFlag = false
			switch b {
			case escapeByte:
				// log.Println("Double Escape")
				decoded = append(decoded, b)
			case packetBegin:
				// log.Println("Reset packetBegin")
				decoded = make([]byte, 0)
			case packetEnd:
				// log.Println("Reset packetEnd")
				// decoded = make([]byte)
			default:
				panic(fmt.Sprintf("Unknown escape byte %x", b))
			}
		case b == escapeByte:
			// log.Printf("Escape %x", b)
			escapeFlag = true
		default:
			// log.Printf("Append %x", b)
			decoded = append(decoded, b)
		}
	}

	// log.Printf("decoded: n:%d decoded[]:%q\n", len(decoded), decoded)
	return decoded
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
	return "", fmt.Errorf("Unable to find serial device in %q", baseDirs)
}
