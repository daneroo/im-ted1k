import sys
import getopt
from scalr import logInfo,logWarn,logError
import MySQLdb
import time

def executeQuery(conn, query):
     cur = conn.cursor()
     cur.execute(query)
     rows = cur.fetchall()
     cur.close()
     return rows


def getAll(n=1000):
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
    for (stamp,watt) in getAll():
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
