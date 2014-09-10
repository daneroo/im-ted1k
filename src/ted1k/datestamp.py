import calendar
import time

# start reorganizing dat/format manipulations
# Notes:
# These are inverses of each other:
#  -time.gmtime(secs) and calendar.timegm(tuple)
#  -time.localtime(secs) and time.mktime(t)

# dt is in GMT (necessary?)
def datetimeToSecs(dt):
    return calendar.timegm(dt.timetuple())

def formatTimeForJSON(secs):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(secs))

# return secs
def startOfDayGMT(secs,offsetInDays):
    # code adapted from Summarize
    secsTuple = time.gmtime(secs)
    startOfDayWithOffsetTuple = (secsTuple[0],secsTuple[1],secsTuple[2]+offsetInDays,0,0,0,0,0,-1)
    startOfDayWithOffsetSecs  = calendar.timegm(startOfDayWithOffsetTuple)
    return startOfDayWithOffsetSecs

# generator for tuples of [startOfDaySecs,endOfDaySecs)
# could generalize for direction, GMT/Local boundary conditions
def dayGeneratorGMT(startSecs,stopSecs):
    # Initial Values
    start = startOfDayGMT(startSecs,0)
    stop = startOfDayGMT(stopSecs,0)

    current=start
    watt=0;
    while True:
        if (current>stop):
            return  # termination of generator
        next = startOfDayGMT(current,+1)
        yield (current,next)
        current=next


# return secs
def startOfDayLocal(secs,offsetInDays):
    # code from Summarize
    # don't keep DST flag in converting with offset..(unlike hour,minute)
    secsTuple = time.localtime(secs)
    startOfDayWithOffsetTuple = (secsTuple[0],secsTuple[1],secsTuple[2]+offsetInDays,0,0,0,0,0,-1)
    startOfDayWithOffsetSecs  = time.mktime(startOfDayWithOffsetTuple)
    return startOfDayWithOffsetSecs

# generator for tuples of [startOfDaySecs,endOfDaySecs)
# could generalize for direction, GMT/Local boundary conditions
def dayGeneratorLocal(startSecs,stopSecs):
    # Initial Values
    start = startOfDayLocal(startSecs,0)
    stop = startOfDayLocal(stopSecs,0)

    current=start
    watt=0;
    while True:
        if (current>stop):
            return  # termination of generator
        next = startOfDayLocal(current,+1)
        yield (current,next)
        current=next

