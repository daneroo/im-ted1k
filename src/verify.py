import sys
import getopt
import MySQLdb
import time
import calendar
from ted1k.logging import logInfo,logWarn,logError
from ted1k.filer import Filer
from ted1k.datestamp import datetimeToSecs, formatTimeForJSON
from ted1k.datestamp import dayGeneratorGMT
from ted1k.mysql import MySQL

db = MySQL();
# format in GMT
def formatTimeForMySQL(secs):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(secs))

# Generator to fetch all 'watt' table entries by querying for each day
# return rows=[(stamp,watt)] for each (GMT) Day
# stamp is a datetime.datetime, watt is an integer
def getAllEntriesByDay():
    # get datetime.datetime tuple
    (startDT,stopDT) = db.getOneRow("select min(stamp),max(stamp) from watt")
    # convert to secs
    startSecs = datetimeToSecs(startDT)
    stopSecs = datetimeToSecs(stopDT)

    for (current,next) in dayGeneratorGMT(startSecs,stopSecs):
        startOfDay = formatTimeForMySQL(current)
        endOfDay   = formatTimeForMySQL(next)
        query = "select stamp,watt from watt where stamp>='%s' and stamp<'%s' order by stamp asc" % (startOfDay,endOfDay)
        print "query: %s" % query
        rows = db.executeQuery(query)
        # if not rows: 
        #     print "No data for %s" % (startOfDay)
        #     # break
        yield rows

def getAllEntries():
    for rows in getAllEntriesByDay():
        for row in rows:
            yield row;


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

    startTime = time.time()
    records=0

    # Fast dump
    with Filer() as filer:    
        for rows in getAllEntriesByDay():
            filer.storeMany(rows);
            records += len(rows)
            elapsed = (time.time()-startTime)
            rate = records/elapsed
            print "%d records in %f seconds: rate: %f" % (records,elapsed,rate)
            # if records>1000000: break;

    # Slower verify...
    # with Filer() as filer:    
    #     for (stamp,watt) in getAllEntries():
    #         if records>1000000: break;
    #         records += 1
    #         if records%100000 == 0:
    #             elapsed = (time.time()-startTime)
    #             rate = records/elapsed
    #             print "%d records in %f seconds: rate: %f" % (records,elapsed,rate)
    #         filer.store(stamp,watt)

    elapsed = (time.time()-startTime)
    rate = records/elapsed
    print "== %d records in %f seconds: rate: %f" % (records,elapsed,rate)

    db.close()
