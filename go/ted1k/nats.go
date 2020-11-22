package ted1k

import (
	"fmt"
	"log"
	"time"

	"github.com/nats-io/nats.go"
)

// NatsWriter implements EntryWriter for a nats topic publisher
type NatsWriter struct {
	// nc *nats.Conn
	c *nats.EncodedConn
}

const natsConnectionName = "capture.ted1k"
const topic = "im.qcic.heartbeat"
const host = natsConnectionName

// NewNatsWriter is the constructor
func NewNatsWriter() *NatsWriter {
	// nats-pub im.qcic.heartbeat '{"stamp":"2020-11-20T21:00:01Z","host":"cli","text":"coco"}'
	// url := nats.DefaultURL
	// url := "nats://127.0.0.1:4222"
	url := "nats://nats.dl.imetrical.com:4222"
	nc, err := nats.Connect(url,
		// RetryOnFailedConnect is on master, ut not released
		// nats.RetryOnFailedConnect(true)
		nats.MaxReconnects(-1), // 60 is the default
		nats.Name(natsConnectionName),
	)
	if err != nil {
		log.Printf("Unable to connect to Nats: %v\n", url)
		return nil
	}
	c, _ := nats.NewEncodedConn(nc, nats.JSON_ENCODER)

	return &NatsWriter{c: c}
}

// WriteMessage publishes a message (not part of EntryWriter interface)
func (w NatsWriter) WriteMessage(text string) error {
	stamp := time.Now().UTC()
	message := message{Stamp: stamp, Host: host, Text: text}
	return w.c.Publish("im.qcic.heartbeat", message)
}

type message struct {
	Stamp time.Time `json:"stamp"`
	Host  string    `json:"host"`
	Text  string    `json:"text"` // or "volt,omitempty"
}

func (w NatsWriter) Write(e Entry) error {
	text := fmt.Sprintf("watts: %d", e.Watts)
	message := message{Stamp: e.Stamp, Host: host, Text: text}
	return w.c.Publish(topic, message)
}

// Close cleans up the EncodedConn and the underlying connection
func (w NatsWriter) Close() error {
	w.c.Close()
	return nil
}
