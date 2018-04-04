package ted1k

import "time"

// delayUntilNextSecond calculates the delay after the reference time until the next second boudary + offset
// e.g. delay(2018-03-18T01:23:45.20,100ms) -> 900ms
//      delay(2018-03-18T01:23:45.00,100ms) -> 100ms
//      delay(2018-03-18T01:23:45.05,100ms) -> 50ms
func delayUntilNextSecond(reference time.Time, offset time.Duration) time.Duration {
	nanos := time.Duration(reference.Nanosecond())
	if nanos < offset {
		return offset - nanos
	}
	return offset - nanos + time.Second
}
