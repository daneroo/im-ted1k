# Extract from http://aria.dl.sologlobe.com:9090/DashboardData
# <DashboardData>
#   ...
#   <VrmsNowDsp>124.7</VrmsNowDsp>
#   ...
#   <KWNow>0.560</KWNow>
#   ...
# </DashboardData>
# run as 
#   while true; do  python ReadTEDService.py ; sleep 1; done
# until this is turned into a timing loop.

import sys
import string
import math
import getopt
from scalr import logInfo,logWarn,logError
import datetime
import time
import urllib 
from xml.dom import minidom  
import MySQLdb

def tableExists(tablename):
        exists = getScalar("show tables like '%s'" % tablename) is not None
        return exists
    
def checkOrCreateTable(tablename):
        exists = tableExists(tablename)
        if exists:
                logInfo(" Table %s is OK" % (tablename))
                return

        # I removed table dropping code (safety)

        ddl = """CREATE TABLE %s (
stamp datetime NOT NULL default '1970-01-01 00:00:00',
watt int(11) NOT NULL default '0',
PRIMARY KEY %sByStamp (stamp)
);
""" % (tablename,tablename)
        cursor.execute(ddl)
        logInfo(" Created %s table" % (tablename))

def getScalar(sql):
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None: return None
    return row[0]

def getGMTTimeWattsAndVoltsFromTedService():
	#TED_DASHBOARDDATA_URL = 'http://aria.dl.sologlobe.com:9090/DashboardData'
	TED_DASHBOARDDATA_URL = 'http://192.168.5.14:9090/DashboardData'
	ISO_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
	usock = urllib.urlopen(TED_DASHBOARDDATA_URL)
	xmldoc = minidom.parse(usock)                              
	usock.close()                                              

	#isodatestr = datetime.datetime.now().strftime(ISO_DATE_FORMAT) 
	isodatestr = time.strftime(ISO_DATE_FORMAT,time.gmtime(time.time())) 

	kWattStr = xmldoc.getElementsByTagName('KWNow')[0].childNodes[0].nodeValue
	voltStr = xmldoc.getElementsByTagName('VrmsNowDsp')[0].childNodes[0].nodeValue
	#print "%s\t%s\t%s" % (isodatestr, kWattStr, voltStr) 
	watts = string.atof(kWattStr)*1000.0
	volts  = string.atof(voltStr)
	return (isodatestr , watts,volts)

if __name__ == "__main__":
        usage = 'python %s  ( --duration <secs> | --forever)' % sys.argv[0]
        conn = MySQLdb.connect (host = "127.0.0.1",
                                user = "aviso",
                                passwd = "",
                                db = "ted")
        cursor = conn.cursor ()
        
        # tablenames: watt, ted_service
        # insert into BOTH tables
        tablenames=['watt','ted_service']

        for tablename in tablenames:
                checkOrCreateTable(tablename);


        # parse command line options
        try:
                opts, args = getopt.getopt(sys.argv[1:], "", ["duration=", "forever"])
        except getopt.error, msg:
                logError('error msg: %s' % msg)
                logError(usage)
                sys.exit(2)

        # default value (forever-> duration=-1
        duration=1

        for o, a in opts:
                if o == "--duration":
                        duration = string.atol(a)
                elif o == "--forever":
                        duration = -1

        print "duration is %d" % duration
        start = time.time()

        while True:
                datetimenow = datetime.datetime.now()
                now=time.time()
                if duration>0 and (now-start)>duration:
                        break
                (stamp, watts,volts) = getGMTTimeWattsAndVoltsFromTedService()
                print "%s --- %s\t%d\t%.1f" % (datetimenow,stamp, watts, volts) 

                # insert into BOTH tables
                for tablename in tablenames:
                        sql = "INSERT IGNORE INTO %s (stamp, watt) VALUES ('%s', '%d')" % (
                                tablename,stamp,watts)
                        cursor.execute(sql)

                now=time.time()
                if duration>0 and (now-start)>duration:
                        break
                # sleep to hit the second on the nose:
                (frac,dummy) = math.modf(now)
                desiredFractionalOffset = .1
                delay = 1-frac + desiredFractionalOffset
                time.sleep(delay)

print "Done; lasted %f" % (time.time()-start)


cursor.close ()
conn.close ()

