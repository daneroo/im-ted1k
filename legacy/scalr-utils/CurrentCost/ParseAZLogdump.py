# -Extract Aztech LOGDUMP Hourly output from stdin
#
# Aztech LOGDMP Format:
#  2008/09/24 22:01:00 Total = 23177200, Used Watts = 1790,Cost = 9666, tier = 0
#  2008/09/24 23:01:00 Total = 23179450, Used Watts = 2250,Cost = 12150, tier = 0
#  ..
#  2009/07/06 23:01:00 Total = 33557040, Used Watts = 2000,Cost = 10800, tier = 0

import sys
import string
import math
import getopt
import datetime
import time
import re

def parseLocaltimeToSecs(stampStrNoTZ):
	# date format: 2009-07-02T19:08:12
	ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
	stampSecs = time.mktime(time.strptime(stampStrNoTZ,ISO_DATE_FORMAT))
	return stampSecs
def formatGMTForMysql(stampSecs):
	ISO_DATE_FORMAT_MYSQL = '%Y-%m-%d %H:%M:%S'
	gmtStr =  time.strftime(ISO_DATE_FORMAT_MYSQL,time.gmtime(stampSecs))
	return gmtStr


def handleLine(line):
	# line format
	# 2009/07/06 23:01:00 Total = 33557040, Used Watts = 2000,Cost = 10800, tier = 0
	#stampStr = line[:19]
	# date format: 2009/07/06 23:01:00 
	# Date is EDT: GMT-0400 no daylight stuff in Aztech

	#lineRE = '(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) Total = (\d+), Used Watts = (\d+),Cost = \d+, tier = \d+'
	# force date to be: XX;01:00
	lineRE = '(\d{4}/\d{2}/\d{2} \d{2}:01:00) Total = (\d+), Used Watts = (\d+),Cost = \d+, tier = \d+'
	match = re.match(lineRE, line)
	if match:
		stampStr = match.group(1)
		readingWh = match.group(2)
		watt = match.group(3)

		stampStr = stampStr.replace('/','-')
		stampStr = stampStr.replace(':01:00',':00:00')

		#gmtStampStrExpr = "CONVERT_TZ('%s','America/Montreal','GMT')"%(stampStr)
		gmtStampStrExpr = "CONVERT_TZ('%s','-04:00','GMT') "% ( stampStr)
		sql = "INSERT IGNORE INTO az_hour_logdump(stamp,readingWh,wattPrecedingHour) VALUES (%s,%s,%s);" % (gmtStampStrExpr, readingWh, watt)
		print sql
		#print "%s wh=%s diff=%s" %(stampStr,readingWh,watt)
	else:
		pass
		#print "NOMATCH : %s" % ( line )

if __name__ == "__main__":
        usage = 'python %s' % sys.argv[0]
	totallines=0;
	# read line by line
        while True:
		line = sys.stdin.readline()         # read a one-line string
		if not line:                        # or an empty string at EOF
			break

		totallines+=1
		handleLine(line)
		if (totallines>10000):
			break
                # (stamp, watts,volts) = getGMTTimeWattsAndVoltsFromTedService()


sys.stderr.write("Done; counted %d lines\n" % (totallines))


