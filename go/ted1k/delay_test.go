package ted1k

import (
	"testing"
	"time"
)

func TestDelayUntilNextSecond(t *testing.T) {
	fromStamp := func(stamp string) time.Time { t, _ := time.Parse(time.RFC3339Nano, stamp); return t }
	var data = []struct {
		reference time.Time     // input
		offset    time.Duration // should be <1second
		// expected
		delay time.Duration
	}{
		{
			reference: fromStamp("1966-05-16T01:23:45.000Z"),
			offset:    100 * time.Millisecond,
			delay:     100 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.000Z"),
			offset:    100 * time.Millisecond,
			delay:     100 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.050Z"),
			offset:    100 * time.Millisecond,
			delay:     50 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.100Z"),
			offset:    100 * time.Millisecond,
			delay:     1000 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.200Z"),
			offset:    100 * time.Millisecond,
			delay:     900 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.450Z"),
			offset:    100 * time.Millisecond,
			delay:     650 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.000Z"),
			offset:    200 * time.Millisecond,
			delay:     200 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.100Z"),
			offset:    200 * time.Millisecond,
			delay:     100 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.200Z"),
			offset:    200 * time.Millisecond,
			delay:     1000 * time.Millisecond,
		},
		{
			reference: fromStamp("2018-03-29T15:46:31.300Z"),
			offset:    200 * time.Millisecond,
			delay:     900 * time.Millisecond,
		},
	}
	for _, tt := range data {

		if delay := delayUntilNextSecond(tt.reference, tt.offset); delay != tt.delay {
			t.Errorf("Expected delay of %q, but it was %q instead.", tt.delay, delay)
		}

	}
}
