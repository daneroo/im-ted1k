package main // import "github.com/daneroo/im-ted1k/go/cmd/capture"

import (
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/mattn/go-sqlite3"

	"github.com/daneroo/im-ted1k/go/ted1k"
)

type logWriter struct {
}

func (writer logWriter) Write(bytes []byte) (int, error) {
	return fmt.Print(time.Now().UTC().Format(ted1k.RFC3339Millli) + " - " + string(bytes))
}

func main() {
	log.SetFlags(0)
	log.SetOutput(new(logWriter))
	log.Printf("Starting TED1K capture\n") // TODO(daneroo): add version,buildDate

	nats := ted1k.NewNatsWriter()
	if nats == nil {
		log.Println("Unable to connect to Nats")
		return
	}
	defer nats.Close()

	// TODO(daneroo) send to different topic..
	nats.WriteMessage("Start")

	db := ted1k.NewDBWriter()
	if db == nil {
		log.Println("Unable to open database")
		time.Sleep(5 * time.Second) // prevent rapid container restart!
		os.Exit(-1)
	}
	defer db.Close()

	// Disable nats for now - Emergency - 2023-02-27
	// writers := []ted1k.EntryWriter{db, nats}
	writers := []ted1k.EntryWriter{db}
	err := ted1k.StartLoop(writers)
	if err != nil {
		log.Println(err)
		time.Sleep(5 * time.Second) // prevent rapid container restart!
		os.Exit(-1)
	}
}
