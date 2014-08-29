# Extract from http://aria.dl.sologlobe.com:9090/DashboardData
# derived from SummarizeCC.py keep this around for validating
# arithmetic and lookup logic -- so we can clean up SummarizeCC

import sys
import string
import math
import getopt
import datetime
import time
import urllib 
from xml.dom import minidom  

def parseLocaltimeToSecs(stampStrNoTZ):
	# date format: 2009-07-02T19:08:12
	ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
	stampSecs = time.mktime(time.strptime(stampStrNoTZ,ISO_DATE_FORMAT))
	return stampSecs
def formatGMTForMysql(stampSecs):
	ISO_DATE_FORMAT_MYSQL = '%Y-%m-%d %H:%M:%S'
	gmtStr =  time.strftime(ISO_DATE_FORMAT_MYSQL,time.gmtime(stampSecs))
	return gmtStr

def formatLocal(stampSecs):
	ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
	gmtStr =  time.strftime(ISO_DATE_FORMAT,time.localtime(stampSecs))
	return gmtStr

def roundHour(stampStr,deltaHours):
	# round hours, index back by scope
	hourStamp = stampStr[:13]+':00:00'
	hourSecs = parseLocaltimeToSecs(hourStamp)
	hourStampOffsetByDelta = formatLocal(hourSecs+deltaHours*3600)
	#print "%s <-- Hour  %s  %05d" % ( hourStampOffsetByDelta,hourStamp, deltaHours )
	return hourStampOffsetByDelta

def roundDay(stampStr,deltaDays,secondsOffset):
	# NOT DST Safe
	# add second offset and round again
	stampSecsPreSecondOffset = parseLocaltimeToSecs(stampStr[:19])
	stampStrOffsetBySeconds = formatLocal(stampSecsPreSecondOffset+secondsOffset)

	# round hours, index back by scope
	#dayStamp = stampStr[:11]+'00:00:00'
	dayStamp = stampStrOffsetBySeconds[:11]+'00:00:00'
	daySecs = parseLocaltimeToSecs(dayStamp)

	
	# now do the deltaDays
	dayStampOffsetByDelta = formatLocal(daySecs+deltaDays*24*3600)
	#print "%s <-- Day  %s  %05d" % ( dayStampOffsetByDelta,dayStamp, deltaDays )
	return dayStampOffsetByDelta

summaryHours = {}
def accumulateHours(stampStr, scopeIndex, scopeValue ):
	# round hours, index back by scope
	# scopeIndex is OFF BY 4 : h004 is really the sum just calculated
	# i.e. sum of last two hours
	scopeIndexCORRECTION=4
	hourStampOffsetByIndex = roundHour(stampStr,-scopeIndex+scopeIndexCORRECTION)
	newValue = scopeValue/2*1000; # kWh/2h -> watt
	if (hourStampOffsetByIndex in summaryHours):
		oldValue = summaryHours[hourStampOffsetByIndex]
		if (oldValue!=newValue):
			print "Hour %s replacing %f with %f" % (hourStampOffsetByIndex,summaryHours[hourStampOffsetByIndex],newValue)
	summaryHours[hourStampOffsetByIndex]=newValue;

averageHours = {}
def averageForHours(stampStr, scopeValue ):
	hourStamp = roundHour(stampStr,0)
	if (hourStamp in averageHours):
		averageHours[hourStamp][0]=averageHours[hourStamp][0]+scopeValue
		averageHours[hourStamp][1]=averageHours[hourStamp][1]+1
	else:
		averageHours[hourStamp]=[scopeValue,1];

def showHours():
	print "-=-=-=-=-= Average Hours"
	sortedKeys = averageHours.keys()
	sortedKeys.sort()
	for h in sortedKeys:
		print "Hour Average: %s  %f    (%f, %d)" % (h, averageHours[h][0]/averageHours[h][1],averageHours[h][0],averageHours[h][1])
	print "-=-=-=-=-= Summary Hours"
	sortedKeys = summaryHours.keys()
	sortedKeys.sort()
	for hh in sortedKeys:
		h1 = roundHour(hh,-2)
		h2 = roundHour(hh,-1)
		v1=0
		v2=0
		avg=0
		errPercent=0
		if ((h1 in averageHours) and (h2 in averageHours)):
			v1 = averageHours[h1][0]/averageHours[h1][1];
			v2 = averageHours[h2][0]/averageHours[h2][1];
			avg=(v1+v2)/2.0
			errPercent = (avg-summaryHours[hh])/avg*100
		print "Hour Summary: %s  %8.2f  avg: %8.2f [%5.2f %%]= (%8.2f +%8.2f)/2 [%s,%s]" % (hh, summaryHours[hh],avg,errPercent,v1,v2,h1,h2)
		#print "CSV Hour Summary, %s,  %8.2f,   %8.2f" % (hh, summaryHours[hh],avg)

summaryDays = {}
def accumulateDays(stampStr, scopeIndex, scopeValue ):
	# round days, index back by scope
	dayStampOffsetByIndex = roundDay(stampStr,-scopeIndex,3600)
	newValue = scopeValue/24*1000; # kWh/24h -> watt
	if (dayStampOffsetByIndex in summaryDays):
		oldValue = summaryDays[dayStampOffsetByIndex]
		if (oldValue!=newValue):
			print "Day %s replacing  %f was %f (%s - %dd)" % (dayStampOffsetByIndex,newValue,oldValue,stampStr,scopeIndex)
		#else:
		#	print "Day %s preserving %f was %f (%s - %dd)" % (dayStampOffsetByIndex,newValue,oldValue,stampStr,scopeIndex)
	#else:
		#print "Day %s setting    %f        (%s - %dd)" % (dayStampOffsetByIndex,newValue,stampStr,scopeIndex)
	summaryDays[dayStampOffsetByIndex]=newValue;

averageDays = {}
def averageForDays(stampStr, scopeValue ):
	dayStamp = roundDay(stampStr,0,0)
	if (dayStamp in averageDays):
		averageDays[dayStamp][0]=averageDays[dayStamp][0]+scopeValue
		averageDays[dayStamp][1]=averageDays[dayStamp][1]+1
	else:
		averageDays[dayStamp]=[scopeValue,1];

def showDays():
	print "-=-=-=-=-= Average Days"
	sortedKeys = averageDays.keys()
	sortedKeys.sort()
	for d in sortedKeys:
		print "Day Average: %s  %f    (%f, %d)" % (d, averageDays[d][0]/averageDays[d][1],averageDays[d][0],averageDays[d][1])
	print "-=-=-=-=-= Summary Days"
	sortedKeys = summaryDays.keys()
	sortedKeys.sort()
	for dd in sortedKeys:
		d1 = roundHour(dd,0)
		avg=0
		errPercent=0
		if (d1 in averageDays):
			avg = averageDays[d1][0]/averageDays[d1][1];
			errPercent = (avg-summaryDays[dd])/avg*100
		print "Day Summary: %s  %8.2f  avg: %8.2f [%5.2f %%]" % (dd, summaryDays[dd],avg,errPercent)
		#print "CSV Day Summary, %s,  %8.2f,   %8.2f" % (hh, summaryDays[hh],avg)

def doHistNode(stampStr,histNode):
	# msg/hist/data/sensor(0)/../[h|d]???
	# for all data nodes
	# find first sensor child, only handle sensor0
	#  handle all it's (h|d|m)XXX siblings
	for dataNode in histNode.getElementsByTagName('data'):
		sensor = string.atol(dataNode.getElementsByTagName('sensor')[0].childNodes[0].nodeValue)
		#print "Found sensor: %d" % sensor
		if (sensor==0):
			#print "Handling sensor: %d" % sensor
			for hdm in dataNode.childNodes:
				#print "tag: %s" % hdm.tagName
				if ("sensor"==hdm.tagName):
					continue
				scopePrefix=hdm.tagName[:1]             # h|d|m
				scopeIndex=string.atoi(hdm.tagName[1:]) # 4 in h004 or 2 in m002
				scopeValue=string.atof(hdm.childNodes[0].nodeValue);
				if ("h"==scopePrefix):
					#print "%s Hour  %05d %10.5f" % ( stampStr, scopeIndex, scopeValue )
					accumulateHours(stampStr, scopeIndex, scopeValue )
				if ("d"==scopePrefix):
					#print "%s Day  %05d %10.5f" % ( stampStr, scopeIndex, scopeValue )
					accumulateDays(stampStr, scopeIndex, scopeValue )
				if ("m"==scopePrefix):
					print "%s Month  %05d %10.5f" % ( stampStr, scopeIndex, scopeValue )
					#summaryMonth(stampStr, scopeIndex, scopeValue )
		#else:
		#	pass
		#	print "Ignoring sensor: %d" % sensor

# stampStr has the format: 
def parseFragment(stampStr,ccfragment):
	# date format: 2009-07-02T19:08:12-0400
	# remove the utcoffset in string
	stampStrNoTZ = stampStr[:-5]
	# reformat utcofset from -0400 to -04:00
	UTCOffset = "%s:%s" % (stampStr[-5:-2],stampStr[-2:])
	# gmtStampStrExpr = "CONVERT_TZ('%s','America/Montreal','GMT')"%(stampStrNoTZ)
	gmtStampStrExpr = "CONVERT_TZ('%s','%s','GMT') " % ( stampStrNoTZ,UTCOffset)
	# we also need actual value for csv.
	stampSecs = parseLocaltimeToSecs(stampStrNoTZ)
	gmtStr=formatGMTForMysql(stampSecs)

	try:
		ccdom = minidom.parseString(ccfragment)
	except Exception, e:
	#except:
		print "XML Error: %s : %s" % (stampStr,e)
		return

	#calculate drift
	ccTimeStr = ccdom.getElementsByTagName('time')[0].childNodes[0].nodeValue
	ccStampStr = stampStrNoTZ[:-8]+ccTimeStr
	ccTimeSecs = parseLocaltimeToSecs(ccStampStr)
	drift = ccTimeSecs - stampSecs

	histNodeList = ccdom.getElementsByTagName('hist')
	if (histNodeList):
		# confirm only one history Node ?
		#print "Detected History T: %s Drift: %f" % (stampStr,drift)
		doHistNode(stampStr,histNodeList[0])
		# use CC's time
		#doHistNode(ccStampStr,histNodeList[0])
		return

	sensor = string.atol(ccdom.getElementsByTagName('sensor')[0].childNodes[0].nodeValue)
	sensorID = string.atol(ccdom.getElementsByTagName('id')[0].childNodes[0].nodeValue)
	#print "D=%f T=%s S=%d frag=%s" % (drift,ccTimeStr,sensor,ccfragment)
	sumwatts=0
	wattarray = []
	for wattnode in ccdom.getElementsByTagName('watts'):
		watt = string.atol(wattnode.childNodes[0].nodeValue)
		#print watt
		wattarray.append(watt)
		sumwatts += watt
	#print "T=%s S=%d watts=%d walen:%d" % (ccTimeStr,sensor,sumwatts,len(wattarray))
	#sql = "INSERT IGNORE INTO cc_native (stamp, watt, sensorid, ch1watt, ch2watt, drift) VALUES (%s,'%d','%s', '%d','%d','%d');" % (gmtStampStrExpr,sumwatts,sensorID,wattarray[0],wattarray[1],drift)
	#print sql
	#csv = ','.join([gmtStr,str(sumwatts),str(sensorID),str(wattarray[0]),str(wattarray[1]),str(drift)])
	#print csv
	averageForHours(stampStr, sumwatts )
	averageForDays(stampStr, sumwatts )
	# use CC's time
	#averageForHours(ccStampStr, sumwatts )
	#averageForDays(ccStampStr, sumwatts )

MARKStamp = None #'2000-01-01T00:00:00'
MARKCheckLen = 13      # 13 for hour,16 for minute

def handleLine(line):
	if (line[:4]=="<!--"):
		return
	stampStr = line[:24]
	CCStr = line[25:-1] # to remove the newline ?
	# omit empty lines

	# Mark the logs as the stampStr advances.
	global MARKStamp
	if (stampStr[:MARKCheckLen]!=MARKStamp):
		print "# MARK -- %s" % stampStr
	MARKStamp=stampStr[:MARKCheckLen]

	if (len(CCStr)>0):
		parseFragment(stampStr,CCStr)

if __name__ == "__main__":
        usage = 'python %s' % sys.argv[0]
	totallines=0;
	# read line by line
        while True:
		line = sys.stdin.readline()         # read a one-line string
		if not line:                        # or an empty string at EOF
			break
		totallines+=1

		if ((totallines % 10000) == 0):
			sys.stderr.write("line # %d \n" % (totallines))
		
		handleLine(line)
		#if (totallines>100):
		#	break
                # (stamp, watts,volts) = getGMTTimeWattsAndVoltsFromTedService()

sys.stderr.write("Done; counted %d lines\n" % (totallines))
showHours()
showDays()
