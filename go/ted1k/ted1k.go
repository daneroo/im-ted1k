package ted1k

import (
	"encoding/binary"
	"fmt"
	"log"

	"github.com/tarm/serial"
)

const verbose = true
const PKT_REQUEST byte = 0xaa
const ESCAPE byte = 0x10
const PKT_BEGIN byte = 0x04
const PKT_END byte = 0x03

// Doit does it
func Doit() {
	if verbose {
		log.Printf("const PKT_REQUEST: %q", PKT_REQUEST)
		log.Printf("const ESCAPE: %x", ESCAPE)
		log.Printf("const PKT_BEGIN: %x", PKT_BEGIN)
		log.Printf("const PKT_END: %x", PKT_END)

	}

	// omitted ReadTimeout: e.g.: time.Millisecond * 500
	// c := &serial.Config{Name: "/hostdev/ttyUSB0", Baud: 19200}
	c := &serial.Config{Name: "/dev/ttyUSB0", Baud: 19200}
	s, err := serial.OpenPort(c)
	if err != nil {
		log.Fatal(err)
	}

	n, err := s.Write([]byte{PKT_REQUEST})
	if err != nil {
		log.Fatal(err)
	}

	// log.Printf("c %q", c)
	// raw := []byte("\x10\x04\x1a\x02\xc3\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x1d\x01\x00\x00\x84\x03\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x02\xdd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\b\x05\x00\xe8\x03\x00\xd3\x00\x00TED \x00\x00\x00\x00\x00\xb7\v\x0f'\x0f'\x0f'\xe8\x03\xdc\x05\x9e\x04\x05\x00\xb4\x04\x02\x00[\x04U\xab\x05U`\x00\x05\x002\x04A\x00\xc5\x10\x10\x00\x00\x89\x1b\x00\x00\x8d\x9d\x00\x000\x15\x05\x03\x95\xce\xd6\x01\x05W\t\xdc\x03\xf6\x02X\tw\x04v\x03Y\tE\x04M\x03Z\t\xe5\x03\xfd\x02[\t\xb5\x03\xd5\x02J\t\x8a\x03\xb2\x02K\tE\x03\x86\x02L\t\xb9\x03\xd9\x02Q\t\xe7\x03\xff\x02R\t-\x049\x03S\t\xf9\x03\x0e\x03T\t%\x042\x03(\x00\x02\x00\xae\x04\x8c\x02\xb0\x02\x88\x03\x04$a\x00\x00\x00\x00\x00\x00Σh\x00\x00\x00\x00\x00\x1c\x02\x10\x03")
	// n = len(raw)
	raw := make([]byte, 4096)
	n, err = s.Read(raw)
	if err != nil {
		log.Fatal(err)
	}
	raw = raw[:n]
	if verbose {
		log.Printf("raw: n:%d raw[:n]:%q", n, raw[:n])
	}
	decoded := make([]byte, 0)
	escape_flag := false
	for _, b := range raw {
		switch {
		case escape_flag:
			escape_flag = false
			switch b {
			case ESCAPE:
				if verbose {
					log.Println("Double Escape")
				}
				decoded = append(decoded, b)
			case PKT_BEGIN:
				if verbose {
					log.Println("Reset PKT_BEGIN")
				}
				decoded = make([]byte, 0)
			case PKT_END:
				if verbose {
					log.Println("Reset PKT_END")
				}
				// decoded = make([]byte)
			default:
				panic(fmt.Sprintf("Unknown escape byte %x", b))
			}
		case b == ESCAPE:
			if verbose {
				log.Printf("Escape %x", b)
			}
			escape_flag = true
		default:
			if verbose {
				log.Printf("Append %x", b)
			}
			decoded = append(decoded, b)
		}
	}

	if verbose {
		log.Printf("decoded: n:%d decoded[]:%q\n", len(decoded), decoded)
	}
	/*
		   see [this](https://docs.python.org/2/library/struct.html) to decode python format in ted.py

		       _protocol_len = 278

		       # Offset,  name,             fmt,     scale
		       (82,       'kw_rate',        "<H",    0.0001),
		       (108,      'house_code',     "<B",    1),
		       (247,      'kw',             "<H",    0.01),
					 (251,      'volts',          "<H",    0.1),

					 where <H is little endian, unsigned short, 2 bytes
					 https://play.golang.org/p/G_4-t_NwoV9
	*/
	watts := binary.LittleEndian.Uint16(decoded[247:249]) * 10
	volts := float32(binary.LittleEndian.Uint16(decoded[251:253])) / 10
	log.Printf("watts:%d volts:%.1f |decoded|=%d |raw|=%d \n", watts, volts, len(decoded), len(raw))
}
