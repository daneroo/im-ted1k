package main // import "github.com/daneroo/im-ted1k/go/cmd/capture"

import (
	"fmt"
	"log"
	"time"

	"github.com/daneroo/im-ted1k/go/ted1k"
)

type logWriter struct {
}

func (writer logWriter) Write(bytes []byte) (int, error) {
	return fmt.Print(time.Now().UTC().Format("2006-01-02T15:04:05.0000Z") + " - " + string(bytes))
}

func main() {
	log.SetFlags(0)
	log.SetOutput(new(logWriter))
	log.Printf("Starting TED1K capture\n") // version,buildDate
	ted1k.StartLoop()
}
