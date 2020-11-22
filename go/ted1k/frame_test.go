package ted1k

import (
	"reflect"
	"testing"
)

func TestFrameDecode(t *testing.T) {
	var data = []struct {
		raw []byte // input
		// expected
		rawLen int
		decLen int
	}{
		{
			raw:    []byte("\x10\x04\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\x9e\x04\x05\x00\xb4\x04\x02\x00[\x04U\xab\x05U`\x00\x05\x002\x04A\x00\xc5\x10\x10\x00\x00\x89\x1b\x00\x00\x8d\x9d\x00\x000\x15\x05\x03\x95\xce\xd6\x01\x05W\t\xdc\x03\xf6\x02X\tw\x04v\x03Y\tE\x04M\x03Z\t\xe5\x03\xfd\x02[\t\xb5\x03\xd5\x02J\t\x8a\x03\xb2\x02K\tE\x03\x86\x02L\t\xb9\x03\xd9\x02Q\t\xe7\x03\xff\x02R\t-\x049\x03S\t\xf9\x03\x0e\x03T\t%\x042\x03(\x00\x02\x00\xae\x04\x8c\x02\xb0\x02\x88\x03\x04$a\x00\x00\x00\x00\x00\x00Σh\x00\x00\x00\x00\x00\x1c\x02\x10\x03"),
			rawLen: 283,
			decLen: 278,
		},
		{
			raw:    []byte("\x10\x04\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\xa3\x04v\x03\xe0\x04\x9e\x00a\x04Q\xb0\x05B\x8e\x02'\x00g\x05T\x00\x99\xf2\b\x009\xb1\x0e\x00?n\x00\x00@+c\x02\x1f4t\x01\x06z\t\xea\x04\xd5\x03{\t0\x04;\x03|\t\x91\x04\x8c\x03\x81\t\xa1\x04\x99\x03\x82\t\xac\x04\xa2\x03\x83\t\xd3\x03\xee\x02r\x81\xd0\x01\xa4\x01s\t\xa9\x01\x8c\x01t\t\xe6\x03\xfe\x02u\t\xb0\x03\xd2\x02v\t\x8b\x04\x87\x03w\t\xb1\x04\xa6\x03_\x00\x05\x00\xb2\x04 \x02\v\x03\x1e\x04\x04\xa7\xe6\x00\x00\x00\x00\x00\x002\xeeh\x00\x00\x00\x00\x00\x1c\x02\x10\x03"),
			rawLen: 282,
			decLen: 278,
		},
	}
	for _, tt := range data {

		if rawLen := len(tt.raw); rawLen != tt.rawLen {
			t.Errorf("Expected length of %d, but it was %d instead.", tt.rawLen, rawLen)
		}

		state := &decoderState{buffer: nil, escapeFlag: false}
		frames := state.decode(tt.raw)
		if len(frames) == 0 {
			t.Errorf("Expected frames length > 0, but it was %d instead.", len(frames))
		} else {
			frame := frames[0]
			if decLen := len(frame); decLen != tt.decLen {
				t.Errorf("Expected decoded length of %d, but it was %d instead.", tt.decLen, decLen)
			}

		}
	}
}

func TestFrameExtract(t *testing.T) {
	var data = []struct {
		frame []byte // input
		// expected
		err   string
		watts int     // expected result
		volts float32 // expected result
	}{
		{
			frame: []byte("\x10\x04\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\x9e\x04\x05\x00\xb4\x04\x02\x00[\x04U\xab\x05U`\x00\x05\x002\x04A\x00\xc5\x10\x10\x00\x00\x89\x1b\x00\x00\x8d\x9d\x00\x000\x15\x05\x03\x95\xce\xd6\x01\x05W\t\xdc\x03\xf6\x02X\tw\x04v\x03Y\tE\x04M\x03Z\t\xe5\x03\xfd\x02[\t\xb5\x03\xd5\x02J\t\x8a\x03\xb2\x02K\tE\x03\x86\x02L\t\xb9\x03\xd9\x02Q\t\xe7\x03\xff\x02R\t-\x049\x03S\t\xf9\x03\x0e\x03T\t%\x042\x03(\x00\x02\x00\xae\x04\x8c\x02\xb0\x02\x88\x03\x04$a\x00\x00\x00\x00\x00\x00Σh\x00\x00\x00\x00\x00\x1c\x02\x10\x03"),
			err:   "Unsupported packet length: 283!=278",
		}, {
			frame: []byte("\x10\x04\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\xa3\x04v\x03\xe0\x04\x9e\x00a\x04Q\xb0\x05B\x8e\x02'\x00g\x05T\x00\x99\xf2\b\x009\xb1\x0e\x00?n\x00\x00@+c\x02\x1f4t\x01\x06z\t\xea\x04\xd5\x03{\t0\x04;\x03|\t\x91\x04\x8c\x03\x81\t\xa1\x04\x99\x03\x82\t\xac\x04\xa2\x03\x83\t\xd3\x03\xee\x02r\x81\xd0\x01\xa4\x01s\t\xa9\x01\x8c\x01t\t\xe6\x03\xfe\x02u\t\xb0\x03\xd2\x02v\t\x8b\x04\x87\x03w\t\xb1\x04\xa6\x03_\x00\x05\x00\xb2\x04 \x02\v\x03\x1e\x04\x04\xa7\xe6\x00\x00\x00\x00\x00\x002\xeeh\x00\x00\x00\x00\x00\x1c\x02\x10\x03"),
			err:   "Unsupported packet length: 282!=278",
		}, {
			frame: []byte("\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\x9e\x04\x05\x00\xb4\x04\x02\x00[\x04U\xab\x05U`\x00\x05\x002\x04A\x00\xc5\x10\x00\x00\x89\x1b\x00\x00\x8d\x9d\x00\x000\x15\x05\x03\x95\xce\xd6\x01\x05W\t\xdc\x03\xf6\x02X\tw\x04v\x03Y\tE\x04M\x03Z\t\xe5\x03\xfd\x02[\t\xb5\x03\xd5\x02J\t\x8a\x03\xb2\x02K\tE\x03\x86\x02L\t\xb9\x03\xd9\x02Q\t\xe7\x03\xff\x02R\t-\x049\x03S\t\xf9\x03\x0e\x03T\t%\x042\x03(\x00\x02\x00\xae\x04\x8c\x02\xb0\x02\x88\x03\x04$a\x00\x00\x00\x00\x00\x00Σh\x00\x00\x00\x00\x00\x1c\x02"),
			watts: 400, volts: 119.8,
		}, {
			frame: []byte("\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\xa3\x04v\x03\xe0\x04\x9e\x00a\x04Q\xb0\x05B\x8e\x02'\x00g\x05T\x00\x99\xf2\b\x009\xb1\x0e\x00?n\x00\x00@+c\x02\x1f4t\x01\x06z\t\xea\x04\xd5\x03{\t0\x04;\x03|\t\x91\x04\x8c\x03\x81\t\xa1\x04\x99\x03\x82\t\xac\x04\xa2\x03\x83\t\xd3\x03\xee\x02r\x81\xd0\x01\xa4\x01s\t\xa9\x01\x8c\x01t\t\xe6\x03\xfe\x02u\t\xb0\x03\xd2\x02v\t\x8b\x04\x87\x03w\t\xb1\x04\xa6\x03_\x00\x05\x00\xb2\x04 \x02\v\x03\x1e\x04\x04\xa7\xe6\x00\x00\x00\x00\x00\x002\xeeh\x00\x00\x00\x00\x00\x1c\x02"),
			watts: 950, volts: 120.2,
		},
	}

	for _, tt := range data {
		entry, err := extractEntryFromFrame(tt.frame)

		if tt.err != "" && err.Error() != tt.err {
			t.Errorf("Expected error to be %v, but it was %v instead.", tt.err, err)
		}
		if entry.Watts != tt.watts {
			t.Errorf("Expected watts to be %d, but it was %d instead.", tt.watts, entry.Watts)
		}
		if entry.Volts != tt.volts {
			t.Errorf("Expected volts to be %f, but it was %f instead.", tt.volts, entry.Volts)
		}
	}
}

func TestFrameExtractMultiple(t *testing.T) {
	frames := []frame{
		[]byte("\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\x9e\x04\x05\x00\xb4\x04\x02\x00[\x04U\xab\x05U`\x00\x05\x002\x04A\x00\xc5\x10\x00\x00\x89\x1b\x00\x00\x8d\x9d\x00\x000\x15\x05\x03\x95\xce\xd6\x01\x05W\t\xdc\x03\xf6\x02X\tw\x04v\x03Y\tE\x04M\x03Z\t\xe5\x03\xfd\x02[\t\xb5\x03\xd5\x02J\t\x8a\x03\xb2\x02K\tE\x03\x86\x02L\t\xb9\x03\xd9\x02Q\t\xe7\x03\xff\x02R\t-\x049\x03S\t\xf9\x03\x0e\x03T\t%\x042\x03(\x00\x02\x00\xae\x04\x8c\x02\xb0\x02\x88\x03\x04$a\x00\x00\x00\x00\x00\x00Σh\x00\x00\x00\x00\x00\x1c\x02"),
		[]byte("discarded because not of length 278"),
		[]byte("\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\xa3\x04v\x03\xe0\x04\x9e\x00a\x04Q\xb0\x05B\x8e\x02'\x00g\x05T\x00\x99\xf2\b\x009\xb1\x0e\x00?n\x00\x00@+c\x02\x1f4t\x01\x06z\t\xea\x04\xd5\x03{\t0\x04;\x03|\t\x91\x04\x8c\x03\x81\t\xa1\x04\x99\x03\x82\t\xac\x04\xa2\x03\x83\t\xd3\x03\xee\x02r\x81\xd0\x01\xa4\x01s\t\xa9\x01\x8c\x01t\t\xe6\x03\xfe\x02u\t\xb0\x03\xd2\x02v\t\x8b\x04\x87\x03w\t\xb1\x04\xa6\x03_\x00\x05\x00\xb2\x04 \x02\v\x03\x1e\x04\x04\xa7\xe6\x00\x00\x00\x00\x00\x002\xeeh\x00\x00\x00\x00\x00\x1c\x02"),
	}
	t.Log("Expect log warning: Unsupported packet length: 35!=278")
	entries := extractEntriesFromFrames(frames)
	// t.Logf("entry:%#v \n", entries)
	expected := []Entry{
		{Watts: 400, Volts: 119.8},
		{Watts: 950, Volts: 120.2},
	}
	if !reflect.DeepEqual(expected, entries) {
		t.Errorf("Expected entries to be %v, but it was %v instead.", expected, entries)

	}
}
