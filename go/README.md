# Go port for im-ted1k

Just read the serial port for now.

For discussion of serial port access, see [this article](http://reprage.com/post/using-golang-to-connect-raspberrypi-and-arduino/).
And try to use:

- good https://github.com/tarm/serial
- previous https://github.com/tarm/goserial
- old fork of above https://github.com/huin/goserial
- also: https://github.com/edartuz/go-serial

## Vendoring - vgo and hellogopher
- [hellogopher](https://github.com/cloudflare/hellogopher)
- [vgo-tour (usage)](https://research.swtch.com/vgo-tour)
```
go get -u golang.org/x/vgo
```

Just build:
```
vgo build ${VERSION_FLAGS} ./cmd/capture
```

Build, injecting version and buildTime
```
VERSION=$(git describe --tags --always --dirty="-dev")
DATE=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
VERSION_FLAGS=--ldflags="-X main.Version=${VERSION} -X main.BuildTime=${DATE}"
vgo build "${VERSION_FLAGS}" ./cmd/capture
```

Cross compiling for linux
```
VERSION=$(git describe --tags --always --dirty="-dev")
DATE=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
VERSION_FLAGS=--ldflags="-X main.Version=${VERSION} -X main.BuildTime=${DATE}"
GOOS=linux GORACH=amd64 vgo build "${VERSION_FLAGS}" ./cmd/capture
```
The system I had was using `govend`: `vendor.yml`, `vendor/`
- I added an import comment to `main.go:` 
```
package main // import "github.com/daneroo/im-ted1k/go"
```
- running `vgo build` produces a go.mod file.
- I then replaced the vgo require for tarm/serial to match the govend vendored copy. (which I can update later)
```
// actual time: 2015-11-13T21:30:10Z
require "github.com/tarm/serial" v0.0.0-20151113213010-edb665337295
```

## Docker dev
For dev in docker, mounting local directory, and cwd to /usr/src/ted1k

cd go
docker run -it --rm --privileged -v /dev:/hostdev -v `pwd`:/usr/src/ted1k -w /usr/src/ted1k  golang


see [this](https://docs.python.org/2/library/struct.html) to decode python format in ted.py

    _protocol_len = 278

    # Offset,  name,             fmt,     scale
    (82,       'kw_rate',        "<H",    0.0001),
    (108,      'house_code',     "<B",    1),
    (247,      'kw',             "<H",    0.01),
    (251,      'volts',          "<H",    0.1),

