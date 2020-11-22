package ted1k

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"reflect"
	"time"
)

// DBWriter implements EntryWriter for database connections
type DBWriter struct {
	db              *sql.DB
	insertSQLFormat string
}

// NewDBWriter is a badly named constructor
func NewDBWriter() *DBWriter {
	db := getDB()
	if db == nil {
		log.Println("Unable to open database")
		time.Sleep(5 * time.Second) // prevent rapid container restart!
		os.Exit(-1)
	}
	return &DBWriter{db, insertSQLFormat(db)}
}

func (h DBWriter) Write(e Entry) error {
	return insertEntry(h.db, e.Stamp, e.Watts)
}

// Close cleans up the database connection (not yet)
func (h DBWriter) Close() error {
	return h.db.Close()
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
func insertEntry(db *sql.DB, stamp time.Time, watts int) error {
	stampStr := stamp.Format(RFC3339NoZ)
	insertSQLFormat := insertSQLFormat(db)
	insertSQL := fmt.Sprintf(insertSQLFormat, stampStr, watts)
	_, err := db.Exec(insertSQL)
	if err != nil {
		log.Println(err)
		return err
	}

	return nil
}
