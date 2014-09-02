import sys
import getopt
from scalr import logInfo,logWarn,logError
import MySQLdb
import time
import calendar
import json


def executeQuery(conn, query):
     cursor = conn.cursor()
     cursor.execute(query)
     rows = cursor.fetchall()
     cursor.close()
     return rows

def getOneRow(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    if row is None: return None
    return row

def startOfDay(secs,offsetInDays):
    # code from Summarize
    # don't keep DST flag in converting with offset..(unlike hour,minute)
    secsTuple = time.localtime(secs)
    startOfDayWithOffsetTuple = (secsTuple[0],secsTuple[1],secsTuple[2]+offsetInDays,0,0,0,0,0,-1)
    startOfDayWithOffsetSecs  = time.mktime(startOfDayWithOffsetTuple)
    return startOfDayWithOffsetSecs

def datetimeToSecs(dt):
    return calendar.timegm(dt.timetuple())

def formatTimeForMySQL(secs):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(secs))

def formatTimeForOutputFilename(secs):
    # OUTPUTLOGDIR="/data/jsonl"
    OUTPUTLOGDIR="/data"
    DEVICEALIAS="TED1k"
    SUFFIX="jsonl"
    # this is the name of the current logrotated file
    #OUTPUTSTAMPFORMAT="%Y%m%dT%H%M00Z" # by Minute
    OUTPUTSTAMPFORMAT="%Y%m%dT000000Z" # by Day
    stamp =  time.strftime(OUTPUTSTAMPFORMAT,time.gmtime(secs))
    return "%s/%s-%s.%s" %(OUTPUTLOGDIR,DEVICEALIAS,stamp,SUFFIX)

def formatTimeForJSON(secs):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(secs))

# generator for tuples of [startOfDaySecs,endOfDaySecs)
# could generalize for direction, boundary conditions
def dayGenerator(startSecs,stopSecs):
    # Initial Values
    start = startOfDay(startSecs,0)
    stop = startOfDay(stopSecs,0)

    current=start
    watt=0;
    while True:
        if (current>stop):
            return  # termination of generator
        next = startOfDay(current,+1)
        yield (current,next)
        current=next

# Generator to fetch all 'watt' table entries by querying for each day
# stamp is a datetime.datetime, watt is an integer
def getAllByDate():
    # get datetime.datetime tuple
    (startDT,stopDT) = getOneRow("select min(stamp),max(stamp) from watt")
    # convert to secs
    startSecs = datetimeToSecs(startDT)
    stopSecs = datetimeToSecs(stopDT)

    for (current,next) in dayGenerator(startSecs,stopSecs):
        startOfDay = formatTimeForMySQL(current)
        endOfDay   = formatTimeForMySQL(next)
        query = "select stamp,watt from watt where stamp>='%s' and stamp<'%s' order by stamp asc" % (startOfDay,endOfDay)
        print "query: %s" % query
        rows = executeQuery(conn,query)
        if not rows: 
            print "No data for %s" % (startOfDay)
            # break
        for row in rows:
            yield row;

# append json entry to outputfile
# TODO 
# create directory
# check for existence of file: overwrite vs append...
# maybe cache outputfile descriptor
def store(stamp,watt):
    secs = datetimeToSecs(stamp);
    filename = formatTimeForOutputFilename(secs)
    with open(filename, 'a') as f:
        obj = {"stamp": formatTimeForJSON(secs), "watt":watt}
        # print(filename,json.dumps(obj))
        json.dump(obj,f)


if __name__ == "__main__":

    usage = 'python %s --verify --dump PFX)' % sys.argv[0]

    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["verify", "dump="])
    except getopt.error, msg:
        logError('error msg: %s' % msg)
        logError(usage)
        sys.exit(2)

    # default values 
    verify=False;
    # (forever-> duration=-1)
    dump=False;
    dumpPrefix=""

    for o, a in opts:
        if o == "--verify":
            verify = True
        elif o == "--dump":
            dump=True
            dumpPrefix = a


    logInfo("Verification %s" % verify)
    logInfo("Dump %s, prefix %s" % (dump,dumpPrefix))

    conn = MySQLdb.connect (host = "172.17.0.5",db="ted")

    startTime = time.time()
    records=0
    for (stamp,watt) in getAllByDate():

        records += 1
        if records%10000 == 0:
            elapsed = (time.time()-startTime)
            rate = records/elapsed
            print "%d records in %f seconds: rate: %f" % (records,elapsed,rate)
        store(stamp,watt)

    elapsed = (time.time()-startTime)
    rate = records/elapsed
    print "== %d records in %f seconds: rate: %f" % (records,elapsed,rate)

    conn.close()
