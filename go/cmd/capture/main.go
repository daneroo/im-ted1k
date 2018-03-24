package main // import "github.com/daneroo/im-ted1k/go/cmd/capture"

import (
	"log"

	"github.com/daneroo/im-ted1k/go/ted1k"
)

var (
	// Version describes the git version (injected)
	Version = "N/A"
	// BuildTime is the UTC stamp at build (injected)
	BuildTime = "N/A"
)

func main() {
	log.Printf("Starting TED1K capture. Version: %s, BuildTime: %s\n", Version, BuildTime)
	ted1k.Doit()
}
