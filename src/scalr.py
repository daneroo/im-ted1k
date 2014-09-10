import sys
import os
import string
import time

######################################################
# logging stubs section
######################################################

def logError(msg):
	sys.stderr.write(msg)
	sys.stderr.write("\n")
def logWarn(msg):
	logError(msg)
def logInfo(msg):
	logError(msg)

######################################################
# sqlite noarch section
######################################################
def getScalar(conn,sql):
        curs = conn.cursor()
        curs.execute(sql)
        row = curs.fetchone()
        curs.close()
        return row[0]
	
def SqliteConnectNoArch(filename): # return either a sqlite3/2/1 connection
	if not os.path.exists(filename):
		logError("Could not find SQLite3 db file: %s" % filename)
		sys.exit(0);
	try:
		from pysqlite2 import dbapi2 as sqlite
		logInfo('Using sqlite-2')
		return sqlite.connect(filename)
	except:
		pass
#		logWarn("from pysqlite2 import dbapi2 failed")
	try:
		import sqlite3 as sqlite;
		logInfo('Using sqlite-3')
		return sqlite.connect(filename)
	except:
		pass
#		logWarn("import sqlite3 failed")
	try:
		import sqlite
		logInfo('Using sqlite-1')
		return sqlite.connect(filename)
	except:
		pass
#		logWarn("import sqlite failed")
	return None
	
######################################################
# TED time section
######################################################

# return a proper ted time string 
# mostly for use in building sql qualifiers on ted database
# the leading zero is important as ted sores the timestamp as a string
def secsToTed(secs):
        tedTimeLong = long( (secs+62135578800) * 1000 * 10000 )
        return "%019ld" % tedTimeLong

# returns ted time string in secs since EPOCH in UTC as time.time()
def tedToSecs(tedTimeString):
        try:
		millis = string.atol(tedTimeString)/10000
                return millis / 1000 - 62135578800;
	except ValueError:
		print "timestamp out of range: bad secs"
	except TypeError:
		print "Type Error: (%s)" % tedTimeString

def tedToGMT(tedTimeString):
	secs = tedToSecs(tedTimeString)
	return time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(secs))

def tedToLocal(tedTimeString):
	secs = tedToSecs(tedTimeString)
	return time.strftime("%Y-%m-%d %H:%M:%S %Z",time.localtime(secs))

# Ambiguous may yield DST or not 
# should only be used with caution
# so I added %Z to format string
# should probaly standardize on some
#  YYYY-MM-DDTHH:mm:ssZ+/-0500 type format
def localTimeToTed(localTimeStr):
	structTime = time.strptime(localTimeStr,"%Y-%m-%d %H:%M:%S")
	secs = time.mktime(structTime)
	return	secsToTed(secs)

if __name__ == "__main__":
	
	import sys
	import os
	if len(sys.argv) < 2:
		print "usage : %s <SQLite3 db file>" % sys.argv[0]
		sys.exit(0);
	else:
		filename = sys.argv[1]

	conn = SqliteConnectNoArch(filename)
	c = conn.cursor()
	c.execute('select * from rdu_second_data limit 10')
	for row in c:
		print "| %s | %f | %f | %f |" % row
