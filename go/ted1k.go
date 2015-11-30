package main

import (
	"log"

	"github.com/tarm/serial"
)

func main() {
	// omitted ReadTimeout: e.g.: time.Millisecond * 500
	c := &serial.Config{Name: "/hostdev/ttyUSB0", Baud: 19200}
	s, err := serial.OpenPort(c)
	if err != nil {
		log.Fatal(err)
	}

	n, err := s.Write([]byte("\xAA"))
	if err != nil {
		log.Fatal(err)
	}

	buf := make([]byte, 4096)
	n, err = s.Read(buf)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("n:%d buf[:n]:%q", n, buf[:n])
}
