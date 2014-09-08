import calendar
import time

#start reorganizing dat/format manipulations

def datetimeToSecs(dt):
    return calendar.timegm(dt.timetuple())

def formatTimeForJSON(secs):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(secs))
