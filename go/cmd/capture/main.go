package main // import "github.com/daneroo/im-ted1k/go/cmd/capture"

import (
	"database/sql"
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
	return fmt.Print(time.Now().UTC().Format("2006-01-02T15:04:05.0000Z") + " - " + string(bytes))
}

func main() {
	log.SetFlags(0)
	log.SetOutput(new(logWriter))
	log.Printf("Starting TED1K capture\n") // version,buildDate
	db := getDB()
	if db == nil {
		log.Println("Unable to open database")
		os.Exit(-1)
	}
	defer db.Close()

	err := ted1k.StartLoop(db)
	if err != nil {
		log.Println(err)
		// just to prevent rapid container reatart!
		time.Sleep(2 * time.Second)
		os.Exit(-1)
	}
}

func getDB() *sql.DB {
	// log.Println(sql.Drivers())

	// db, err := sql.Open("sqlite3", "./ted.db")
	// db, err := sql.Open("mysql", "ted:secret@tcp(0.0.0.0:3306)/ted")
	db, err := sql.Open("mysql", "root@tcp(0.0.0.0:3306)/ted")
	// db, err := sql.Open("mysql", "root@tcp(teddb:3306)/ted")

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
	// err = ted1k.InsertEntry(db, "1966-05-16T01:23:45", 1234)
	// if err != nil {
	// 	log.Printf("%q\n", err)
	// }
	return db
}
