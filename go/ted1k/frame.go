package ted1k

import (
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"log"

	"github.com/tarm/serial"
)

type frame []byte // represents a decoded frame: most likely always len=278

type decoderState struct {
	// stamp        string // now.UTC().Format(fmtRFC3339NoZ) no timezone for db insert
	buffer     []byte
	escapeFlag bool
}

// TODO(daneroo): remove
func (state *decoderState) show(msg string) {
	if state.escapeFlag || len(state.buffer) > 0 {
		log.Printf("%sstate: escape=%v buf=%d %s\n", msg, state.escapeFlag, len(state.buffer), hex.EncodeToString(state.buffer))
	}
}

func (state *decoderState) poll(s *serial.Port) ([]entry, error) {
	err := writeRequest(s)
	if err != nil {
		return nil, err
	}
	raw, err := readResponse(s)
	if err != nil {
		return nil, err
	}

	frames := state.decode(raw)

	return extractEntriesFromFrames(frames), nil
}

// extract entry from each frame, ignore any bad frames (bad length)
func extractEntriesFromFrames(frames []frame) []entry {
	entries := make([]entry, 0, len(frames))
	for _, frame := range frames {
		entry, err := extractEntryFromFrame(frame)
		if err != nil {
			log.Printf("warning: %s", err)
		} else {
			entries = append(entries, entry)
		}
	}
	return entries
}

// extract one entry from one frame, return error if length not supported
func extractEntryFromFrame(frame frame) (entry, error) {
	if len(frame) != 278 {
		return entry{}, fmt.Errorf("Unsupported packet length: %d!=278", len(frame))
	}
	/*
		original: http://svn.navi.cx/misc/trunk/python/ted.py

		see [this](https://docs.python.org/2/library/struct.html) to decode python format in ted.py
			_protocol_len = 278
			# Offset,  name,             fmt,     scale
			(82,       'kw_rate',        "<H",    0.0001),
			(108,      'house_code',     "<B",    1),
			(247,      'kw',             "<H",    0.01),
			(251,      'volts',          "<H",    0.1),

		see also (more fields): https://github.com/mloebl/mqtt-ted1000/blob/master/ted.py
	*/
	watts := int(binary.LittleEndian.Uint16(frame[247:249]) * 10)
	volts := float32(binary.LittleEndian.Uint16(frame[251:253])) / 10
	return entry{watts: watts, volts: volts}, nil
}

// Can accumulate bytes (in state.buffer) corresponding to more than one serial read.
func (state *decoderState) decode(raw []byte) []frame {
	const escapeByte byte = 0x10
	const packetBegin byte = 0x04
	const packetEnd byte = 0x03

	var frames = make([]frame, 0, 1)
	for _, b := range raw {
		if state.escapeFlag {
			state.escapeFlag = false
			if b == escapeByte {
				if state.buffer != nil {
					state.buffer = append(state.buffer, b)
				}
			} else if b == packetBegin {
				state.buffer = make([]byte, 0, 278) // set expected capacity
				// state.stamp = time.Now().UTC().Format(fmtRFC3339NoZ)
			} else if b == packetEnd {
				if state.buffer != nil {
					frames = append(frames, state.buffer)
					state.buffer = nil
					// state.stamp = ""
				}
			} else {
				panic(fmt.Sprintf("Unknown escape byte %x", b))
			}
		} else if b == escapeByte {
			state.escapeFlag = true
		} else {
			state.buffer = append(state.buffer, b)
		}
	}
	return frames
}