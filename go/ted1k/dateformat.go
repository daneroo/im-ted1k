package ted1k

// RFC3339NoZ format is used for UTC time, formatted without timezone, for insertion into mysql
const RFC3339NoZ = "2006-01-02T15:04:05"

// RFC3339Millli format is used for UTC time as in ISO8601, with fractional ms (always even if 0)
// It is similar to time.RFC3339Nano, but with only 3 digits, and 0 (always), instad of 9's (trailing 0's removed)
// Not currently used, but could be used to Marshal JSON time.Time fields, for now default is fine
const RFC3339Millli = "2006-01-02T15:04:05.000Z07:00"
