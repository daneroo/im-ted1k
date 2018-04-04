package ted1k

import (
	"database/sql"
	"fmt"
	"log"
	"reflect"
	"time"

	"github.com/tarm/serial"
)

const fmtRFC3339NoZ = "2006-01-02T15:04:05"

type entry struct {
	stamp string // now.UTC().Format(fmtRFC3339NoZ) no timezone for db insert
	watts int
	volts float32
}

// StartLoop performs the read loop:
// - Take a measurement from serial port (poll()),
// - Store to the database,
// - Calculate delay to make loop every second (with offset)
// TODO(daneroo): move discovery (invocation) out to main
// TODO(daneroo): Create a New method to store state/config (sql.DB,serial.Port,decoderState{escapeFlag,buffer})
func StartLoop(db *sql.DB) error {

	serialName, err := findSerialDevice(nil)
	if err != nil {
		return err
	}
	log.Printf("Discovered serial port: %s", serialName)

	// ReadTimeout: makes the port.Read() non-blocking, causing a more sophisticated readRresponse()
	//  smallest possible value: 0.1s time.Millisecond * 100,  1 deciSecond
	c := &serial.Config{Name: serialName, Baud: 19200, ReadTimeout: time.Millisecond * 100}
	s, err := serial.OpenPort(c)
	if err != nil {
		return err
	}
	log.Printf("Connected to serial port: %s", serialName)

	state := &decoderState{buffer: nil, escapeFlag: false}
	state.show("-")
	for {
		loopStart := time.Now().UTC()
		stamp := time.Now().UTC().Format(fmtRFC3339NoZ) // stamp is set to second (before poll() is called)
		entries, err := state.poll(s)
		if err != nil {
			return err
		}
		state.show("+")
		if len(entries) == 0 {
			log.Printf("warning: skipping entry (no entry from poll)\n")
		} else {
			if len(entries) > 1 {
				log.Printf("warning: multiple entries: %d (keeping last)", len(entries))
			}
			entry := entries[len(entries)-1]

			// Call insert in goroutine. (This was sometime holding up the main loop.)
			go insertEntry(db, stamp, entry.watts)

			log.Printf("%s watts: %d volts: %.1f\n", stamp, entry.watts, entry.volts)
		}

		if delay := time.Since(loopStart); delay > time.Second {
			log.Printf("warning: skipping entry (loop took %v>1s)\n", delay)
		}
		offset := 10 * time.Millisecond // used to be 0.1s
		time.Sleep(delayUntilNextSecond(time.Now(), offset))
	}
}

// conditional on database connection type - Yay SQL
// This is one approaches to the dialect specific queries
// TODO(daneroo): Can we call this just once on setup?
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
func insertEntry(db *sql.DB, stamp string, watts int) error {
	// const insertSQLFormat = "INSERT INTO watt (stamp, watt) VALUES ('%s',%d)"
	insertSQLFormat := insertSQLFormat(db)
	insertSQL := fmt.Sprintf(insertSQLFormat, stamp, watts)
	_, err := db.Exec(insertSQL)
	if err != nil {
		log.Println(err)
		return err
	}

	return nil
}
