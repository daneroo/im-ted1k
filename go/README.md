# Go port for im-ted1k

Just read the port for now.

See [this article](http://reprage.com/post/using-golang-to-connect-raspberrypi-and-arduino/).
And try to use:

- good https://github.com/tarm/serial
- previous https://github.com/tarm/goserial
- old fork of above https://github.com/huin/goserial
- also: https://github.com/edartuz/go-serial

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

