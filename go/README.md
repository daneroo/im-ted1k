# Go port for im-ted1k

- Loop every second
- Take a measurement from serial port
- Store to the database

## TODO

- Add Config to ted1k, use from Main
  - move getDB to startLoop(creds)
- Main Loop monitor
  - docker health?
  - internal restart
  - Test USB failover
  - DB pause/restart
- `.netrc` still required for vgo based build (GitHub API token)
- Reorganize this document (vgo,docker,..)
  - vgo and vscode (with `vendor/` and `$GOPATH`)
- Integrate into `go-ted1k` repo.
- `vgo` pinned version for mysql driver

## References

For discussion of serial port access, see [this article](http://reprage.com/post/using-golang-to-connect-raspberrypi-and-arduino/).
And try to use:

- good <https://github.com/tarm/serial>
- previous <https://github.com/tarm/goserial>
- old fork of above <https://github.com/huin/goserial>
- also: <https://github.com/edartuz/go-serial>

## Call Graph

- StartLoop
  - poll
    - writeRequwst() (error)
    - readResponse() (byte[],error)
    - extract(raw,state) (*entry)
      -decode(raw,state) ([][]byte)

Into:
    - type frame []byte (guaranteed 278 length)
    - NewSerial() *serial (port and state)
    - (*serial) poll ([]entry)
        - (*serial) writeRequest() (error)
        - (*serial) readResponse() (byte[],error)
        - (state *) decode(raw) ([]frame)
        - extract(frame) entry

## Update dependancies

```bash
go get -u ...
```

## Docker

```bash
docker build -t capture:latest .
docker run --rm -it --name capture capture:latest
```

See [this](https://docs.python.org/2/library/struct.html) to decode python format in ted.py

```text
_protocol_len = 278

# Offset,  name,             fmt,     scale
(82,       'kw_rate',        "<H",    0.0001),
(108,      'house_code',     "<B",    1),
(247,      'kw',             "<H",    0.01),
(251,      'volts',          "<H",    0.1),
```
