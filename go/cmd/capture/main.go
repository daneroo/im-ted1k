package main // import "github.com/daneroo/im-ted1k/go/cmd/capture"

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/mattn/go-sqlite3"

	nats "github.com/nats-io/nats.go"

	"github.com/daneroo/im-ted1k/go/ted1k"
)

type logWriter struct {
}

func (writer logWriter) Write(bytes []byte) (int, error) {
	return fmt.Print(time.Now().UTC().Format("2006-01-02T15:04:05.0000Z") + " - " + string(bytes))
}

func pubNats() {
	// nats-pub im.qcic.heartbeat '{"stamp":"2020-11-20T21:00:01Z","host":"cli","text":"coco"}'
	// url := nats.DefaultURL
	// url := "nats://127.0.0.1:4222"
	url := "nats://nats.dl.imetrical.com:4222"
	nc, err := nats.Connect(url)
	if err != nil {
		log.Printf("Unable to connect to Nats: %v\n", url)
		return
	}
	nc.Publish("im.qcic.heartbeat", []byte(`{"stamp":"2020-11-20T21:00:01Z","host":"cli","text":"coco"}`))
}

func main() {
	log.SetFlags(0)
	log.SetOutput(new(logWriter))
	log.Printf("Starting TED1K capture\n") // TODO(daneroo): add version,buildDate
	log.Printf("Publishing to Nats\n")
	pubNats()
	db := getDB()
	if db == nil {
		log.Println("Unable to open database")
		time.Sleep(5 * time.Second) // prevent rapid container restart!
		os.Exit(-1)
	}
	defer db.Close()

	err := ted1k.StartLoop(db)
	if err != nil {
		log.Println(err)
		time.Sleep(5 * time.Second) // prevent rapid container restart!
		os.Exit(-1)
	}
}

func getDB() *sql.DB {
	// log.Println(sql.Drivers())

	// db, err := sql.Open("sqlite3", "./ted.db")
	// db, err := sql.Open("mysql", "ted:secret@tcp(0.0.0.0:3306)/ted")
	// db, err := sql.Open("mysql", "root@tcp(0.0.0.0:3306)/ted")
	db, err := sql.Open("mysql", "root@tcp(teddb:3306)/ted")

	if err != nil {
		log.Println(err)
		return nil
	}

	ddlStmt := `
		CREATE TABLE IF NOT EXISTS watt ( 
			stamp datetime NOT NULL DEFAULT '1970-01-01 00:00:00', 
			watt int(11) NOT NULL DEFAULT '0',  
			PRIMARY KEY (stamp) 
			);
	`
	_, err = db.Exec(ddlStmt)
	if err != nil {
		log.Printf("%q: %s\n", err, ddlStmt)
		return nil
	}
	return db
}
