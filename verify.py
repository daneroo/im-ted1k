import sys
import getopt
from scalr import logInfo,logWarn,logError
import MySQLdb
import time
import calendar


def executeQuery(conn, query):
     cursor = conn.cursor()
     cursor.execute(query)
     rows = cursor.fetchall()
     cursor.close()
     return rows

def getScalar(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    if row is None: return None
    return row[0]

def getOneRow(sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    if row is None: return None
    return row

def startOfDay(secs,offsetInDays):
    # don't keep DST flag in converting with offset..(unlike hour,minute)
    secsTuple = time.localtime(secs)
    startOfDayWithOffsetTuple = (secsTuple[0],secsTuple[1],secsTuple[2]+offsetInDays,0,0,0,0,0,-1)
    startOfDayWithOffsetSecs  = time.mktime(startOfDayWithOffsetTuple)
    return startOfDayWithOffsetSecs


# generator for tuples of [startOfDaySecs,endOfDaySecs)
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

# this is a generator to fetch all entries by querying for each day
def getAllByDate():
    # get datetime.datetime tuple
    (startDT,stopDT) = getOneRow("select min(stamp),max(stamp) from watt")
    # convert to secs
    startSecs = calendar.timegm(startDT.timetuple())
    stopSecs = calendar.timegm(stopDT.timetuple())
    # print 'start',type(start),start,start.timetuple(),calendar.timegm(start.timetuple())
    yield (startDT,1000)
    yield (stopDT,1001)

    for (current,next) in dayGenerator(startSecs,stopSecs):
        startOfDay = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(current))
        endOfDay   = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(next))
        query = "select stamp,watt from watt where stamp>='%s' and stamp<'%s' order by stamp asc" % (startOfDay,endOfDay)
        print "query: %s" % query
        rows = executeQuery(conn,query)
        if not rows: 
            print "No data for %s" % (startOfDay)
            # break
        for row in rows:
            yield row;





# this is a generator to fetch all entries by chunks with limit,offset
# does not seem to work
def getAll(n=1000):
    return;
    iteration=0;
    conn = MySQLdb.connect (host = "172.17.0.5",db="ted")
    while True:
        # query = "select stamp,watt from watt where stamp>'2014-01-01' order by stamp asc limit %d offset %d" % (n,n*iteration)
        query = "select stamp,watt from watt order by stamp asc limit %d offset %d" % (n,n*iteration)
        print "query: %s" % query
        rows = executeQuery(conn,query)
        if not rows: 
            print "No more data"
            break
        for row in rows:
            yield row;
        iteration+=1;

if __name__ == "__main__":

    #testStartOfPeriods()
    #sys.exit(0)

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
    # for (stamp,watt) in getAll():
    for (stamp,watt) in getAllByDate():
        records += 1
        if records%10000 == 0:
            elapsed = (time.time()-startTime)
            rate = records/elapsed
            print "%d records in %f seconds: rate: %f" % (records,elapsed,rate)
            print("stamp:{} watt:{} ".format(stamp,watt))

        # print("stamp:{:%d %b %Y} watt:{} ".format(stamp,watt))
        # print("stamp:{} watt:{} ".format(stamp,watt))

    elapsed = (time.time()-startTime)
    rate = records/elapsed
    print "== %d records in %f seconds: rate: %f" % (records,elapsed,rate)

    conn.close()
