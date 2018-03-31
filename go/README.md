# Go port for im-ted1k

- Loop every second
- Take a measurement from serial port
- Store to the database

## TODO
- move getDB to startLoop(creds)
- `.netrc` still required for vgo based build (GitHub API token)
- Reorganize this document (vgo,docker,..)
    - vgo and vscode (with `vendor/` and `$GOPATH`)
- Integrate into `go-ted1k` repo.
- `vgo` pinned version for mysql driver

## References
For discussion of serial port access, see [this article](http://reprage.com/post/using-golang-to-connect-raspberrypi-and-arduino/).
And try to use:

- good https://github.com/tarm/serial
- previous https://github.com/tarm/goserial
- old fork of above https://github.com/huin/goserial
- also: https://github.com/edartuz/go-serial

## Docker
```
docker build -t capture:latest .
docker run --rm -it --name capture capture:latest
```

This is a way to build and extract the executable (capture) from the container without starting it:
```
docker build -t capture:latest .
docker create --name capture capture:latest
docker cp capture:/capture ./capture-linux-amd64
docker rm capture
scp -p capture-linux-amd64  daniel@euler:Code/iMetrical/im-ted1k/
```

### Skip Analysis
```
docker run --rm -it mysql bash
mysql -h euler.imetrical.com ted -e 'select concat(left(stamp,18),"0") as pertensec,count(*) from watt where stamp>DATE_SUB(NOW(), INTERVAL 3 minute) group by pertensec'
mysql -h euler.imetrical.com ted -e 'select concat(left(stamp,16),":00") as permin,count(*) from watt where stamp>DATE_SUB(NOW(), INTERVAL 15 minute) group by permin'
```
## Vendoring - vgo and hellogopher
- [hellogopher](https://github.com/cloudflare/hellogopher)
- [vgo-tour (usage)](https://research.swtch.com/vgo-tour)
Install vgo
```
go get -u golang.org/x/vgo
```

This is to allow vscode to see vendor'd directory:
```
.vscode:   "go.gopath": "/Users/daniellauzon/Code/iMetrical/im-ted1k/go/.GOPATH"

vgo vendor
```

Just build:
```
vgo build ./cmd/capture
```

Just test:
```
vgo test -v ./cmd/capture/ ./ted1k/
```

Cross compiling for linux
```
GOOS=linux GOARCH=amd64 vgo build ./cmd/capture
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

