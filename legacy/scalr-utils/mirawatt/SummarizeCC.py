# reading loop for captured log files
#  
# accumulates history, and produces
#  current state of same

import math
import sys
import time

import datetime
import getopt
import string
import urllib
from xml.dom import minidom
  

def parseLocaltimeToSecs(stampStrNoTZ):
    # date format: 2009-07-02T19:08:12
    ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
    stampSecs = time.mktime(time.strptime(stampStrNoTZ, ISO_DATE_FORMAT))
    return stampSecs
def formatGMTForXML(stampSecs):
    ISO_DATE_FORMAT_XML = '%Y-%m-%dT%H:%M:%SZ'
    gmtStr = time.strftime(ISO_DATE_FORMAT_XML, time.gmtime(stampSecs))
    return gmtStr

def formatLocal(stampSecs):
    ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
    gmtStr = time.strftime(ISO_DATE_FORMAT, time.localtime(stampSecs))
    return gmtStr

def roundTensec(stampStr):
    # round to tensec
    tensecStamp = stampStr[:18] + '0'
    tensecSecs = parseLocaltimeToSecs(tensecStamp)
    tensecStamp = formatLocal(tensecSecs)
    #print "%s <-- Tensec  %s" % ( tensecStamp,stampStr )
    return tensecStamp

def roundMinute(stampStr):
    # round to minute
    minuteStamp = stampStr[:16] + ':00'
    minuteSecs = parseLocaltimeToSecs(minuteStamp)
    minuteStamp = formatLocal(minuteSecs)
    #print "%s <-- Minute  %s" % ( minuteStamp,stampStr )
    return minuteStamp

def roundHour(stampStr, deltaHours):
    # round hours, index back by scope
    hourStamp = stampStr[:13] + ':00:00'
    hourSecs = parseLocaltimeToSecs(hourStamp)
    hourStampOffsetByDelta = formatLocal(hourSecs + deltaHours * 3600)
    #print "%s <-- Hour  %s  %05d" % ( hourStampOffsetByDelta,hourStamp, deltaHours )
    return hourStampOffsetByDelta

def roundDay(stampStr, deltaDays, secondsOffset):
    # NOT DST Safe
    # add second offset and round again
    stampSecsPreSecondOffset = parseLocaltimeToSecs(stampStr[:19])
    stampStrOffsetBySeconds = formatLocal(stampSecsPreSecondOffset + secondsOffset)

    # round hours, index back by scope
    #dayStamp = stampStr[:11]+'00:00:00'
    dayStamp = stampStrOffsetBySeconds[:11] + '00:00:00'
    daySecs = parseLocaltimeToSecs(dayStamp)

        
    # now do the deltaDays
    dayStampOffsetByDelta = formatLocal(daySecs + deltaDays * 24 * 3600)
    #print "%s <-- Day  %s  %05d" % ( dayStampOffsetByDelta,dayStamp, deltaDays )
    return dayStampOffsetByDelta

averageTensecs = {}
def averageForTensecs(stampStr, scopeValue):
    tensecStamp = roundTensec(stampStr)
    if (tensecStamp in averageTensecs):
        averageTensecs[tensecStamp][0] = averageTensecs[tensecStamp][0] + scopeValue
        averageTensecs[tensecStamp][1] = averageTensecs[tensecStamp][1] + 1
    else:
        averageTensecs[tensecStamp] = [scopeValue, 1];

def showTensecs():
    print "-=-=-=-=-= Average Tensecs (%d)" % len(averageTensecs)
    howManyToShow = 30
    sortedKeys = averageTensecs.keys()
    sortedKeys.sort()
    for d in sortedKeys[-howManyToShow:]:
        print "Tensec Average: %s  %f    (%f, %d)" % (d, averageTensecs[d][0] / averageTensecs[d][1], averageTensecs[d][0], averageTensecs[d][1])

averageMinutes = {}
def averageForMinutes(stampStr, scopeValue):
    minuteStamp = roundMinute(stampStr)
    if (minuteStamp in averageMinutes):
        averageMinutes[minuteStamp][0] = averageMinutes[minuteStamp][0] + scopeValue
        averageMinutes[minuteStamp][1] = averageMinutes[minuteStamp][1] + 1
    else:
        averageMinutes[minuteStamp] = [scopeValue, 1];

def showMinutes():
    print "-=-=-=-=-= Average Minutes (%d)" % len(averageMinutes)
    howManyToShow = 60
    sortedKeys = averageMinutes.keys()
    sortedKeys.sort()
    for d in sortedKeys[-howManyToShow:]:
        print "Minute Average: %s  %f    (%f, %d)" % (d, averageMinutes[d][0] / averageMinutes[d][1], averageMinutes[d][0], averageMinutes[d][1])

summaryHours = {}
def accumulateHours(stampStr, scopeIndex, scopeValue):
    # round hours, index back by scope
    # scopeIndex is OFF BY 4 : h004 is really the sum just calculated
    # i.e. sum of last two hours
    scopeIndexCORRECTION = 4
    hourStampOffsetByIndex = roundHour(stampStr, -scopeIndex + scopeIndexCORRECTION)
    newValue = scopeValue / 2 * 1000; # kWh/2h -> watt
    if (hourStampOffsetByIndex in summaryHours):
        oldValue = summaryHours[hourStampOffsetByIndex]
        if (oldValue != newValue):
            print "Hour %s replacing %f with %f" % (hourStampOffsetByIndex, summaryHours[hourStampOffsetByIndex], newValue)
    summaryHours[hourStampOffsetByIndex] = newValue;

averageHours = {}
def averageForHours(stampStr, scopeValue):
    hourStamp = roundHour(stampStr, 0)
    if (hourStamp in averageHours):
        averageHours[hourStamp][0] = averageHours[hourStamp][0] + scopeValue
        averageHours[hourStamp][1] = averageHours[hourStamp][1] + 1
    else:
        averageHours[hourStamp] = [scopeValue, 1];

def showHours():
    print "-=-=-=-=-= Average Hours"
    sortedKeys = averageHours.keys()
    sortedKeys.sort()
    for h in sortedKeys:
        print "Hour Average: %s  %f    (%f, %d)" % (h, averageHours[h][0] / averageHours[h][1], averageHours[h][0], averageHours[h][1])
    print "-=-=-=-=-= Summary Hours"
    sortedKeys = summaryHours.keys()
    sortedKeys.sort()
    for hh in sortedKeys:
        h1 = roundHour(hh, -2)
        h2 = roundHour(hh, -1)
        v1 = 0
        v2 = 0
        avg = 0
        errPercent = 0
        if ((h1 in averageHours) and (h2 in averageHours)):
            v1 = averageHours[h1][0] / averageHours[h1][1];
            v2 = averageHours[h2][0] / averageHours[h2][1];
            avg = (v1 + v2) / 2.0
            errPercent = (avg-summaryHours[hh]) / avg * 100
        print "Hour Summary: %s  %8.2f  avg: %8.2f [%5.2f %%]= (%8.2f +%8.2f)/2 [%s,%s]" % (hh, summaryHours[hh], avg, errPercent, v1, v2, h1, h2)
        #print "CSV Hour Summary, %s,  %8.2f,   %8.2f" % (hh, summaryHours[hh],avg)

summaryDays = {}
def accumulateDays(stampStr, scopeIndex, scopeValue):
    # round days, index back by scope
    dayStampOffsetByIndex = roundDay(stampStr, -scopeIndex, 3600)
    newValue = scopeValue / 24 * 1000; # kWh/24h -> watt
    if (dayStampOffsetByIndex in summaryDays):
        oldValue = summaryDays[dayStampOffsetByIndex]
        if (oldValue != newValue):
            print "Day %s replacing  %f was %f (%s - %dd)" % (dayStampOffsetByIndex, newValue, oldValue, stampStr, scopeIndex)
        #else:
        #        print "Day %s preserving %f was %f (%s - %dd)" % (dayStampOffsetByIndex,newValue,oldValue,stampStr,scopeIndex)
    #else:
        #print "Day %s setting    %f        (%s - %dd)" % (dayStampOffsetByIndex,newValue,stampStr,scopeIndex)
    summaryDays[dayStampOffsetByIndex] = newValue;

averageDays = {}
def averageForDays(stampStr, scopeValue):
    dayStamp = roundDay(stampStr, 0, 0)
    if (dayStamp in averageDays):
        averageDays[dayStamp][0] = averageDays[dayStamp][0] + scopeValue
        averageDays[dayStamp][1] = averageDays[dayStamp][1] + 1
    else:
        averageDays[dayStamp] = [scopeValue, 1];

def showDays():
    print "-=-=-=-=-= Average Days"
    sortedKeys = averageDays.keys()
    sortedKeys.sort()
    for d in sortedKeys:
        print "Day Average: %s  %f    (%f, %d)" % (d, averageDays[d][0] / averageDays[d][1], averageDays[d][0], averageDays[d][1])
    print "-=-=-=-=-= Summary Days"
    sortedKeys = summaryDays.keys()
    sortedKeys.sort()
    for dd in sortedKeys:
        d1 = roundHour(dd, 0)
        avg = 0
        errPercent = 0
        if (d1 in averageDays):
            avg = averageDays[d1][0] / averageDays[d1][1];
            errPercent = (avg-summaryDays[dd]) / avg * 100
        print "Day Summary: %s  %8.2f  avg: %8.2f [%5.2f %%]" % (dd, summaryDays[dd], avg, errPercent)
        #print "CSV Day Summary, %s,  %8.2f,   %8.2f" % (hh, summaryDays[hh],avg)

def writeXML():
    combinedHours = {}
    for k, v in summaryHours.items():
        combinedHours[k] = [v, 1]
    for k, v in averageHours.items():
        combinedHours[k] = v
    combinedDays = {}
    for k, v in summaryDays.items():
        combinedDays[k] = [v, 1]
    for k, v in averageDays.items():
        combinedDays[k] = v
    scopes = [
        {'id':0, 'name':'Live', 'averages':averageTensecs, 'howMany':30},
        {'id':1, 'name':'Hour', 'averages':averageMinutes, 'howMany':60},
        {'id':2, 'name':'Day', 'averages':combinedHours, 'howMany':24},
        {'id':3, 'name':'Week', 'averages':combinedDays, 'howMany':7},
        {'id':4, 'name':'Month', 'averages':combinedDays, 'howMany':30},
    ]
    f = open('feeds.xml', 'w')
    print >> f, '<?xml version="1.0"?>'
    print >> f, '<!DOCTYPE plist PUBLIC "-//iMetrical//DTD OBSFEEDS 1.0//EN" "http://www.imetrical.com/DTDs/ObservationFeeds-1.0.dtd">'
    print >> f, '<feeds>'
    for scope in scopes:
        avgArray = scope['averages']
        sortedKeys = avgArray.keys()
        sortedKeys.sort()
        sortedKeys.reverse()
        scopeLastValue = avgArray[sortedKeys[0]][0] / avgArray[sortedKeys[0]][1]
        scopeAverageAverage = [0.0, 0]
        for d in sortedKeys[:scope['howMany']]:
            scopeAverageAverage[0] = scopeAverageAverage[0] + avgArray[d][0]
            scopeAverageAverage[1] = scopeAverageAverage[1] + avgArray[d][1]
        scopeAverageValue = scopeAverageAverage[0] / scopeAverageAverage[1]
        scopeStamp = sortedKeys[0]
        scopeValue = scopeAverageValue
        if (scope['id'] == 0): scopeValue = scopeLastValue

        scopeStamp = formatGMTForXML(parseLocaltimeToSecs(scopeStamp))
        print >> f, '  <feed scopeId="%s" name="%s" stamp="%s" value="%.1f">' % (scope['id'], scope['name'], scopeStamp, scopeValue)
        for d in sortedKeys[:scope['howMany']]:
            obsStamp = formatGMTForXML(parseLocaltimeToSecs(d))
            print >> f, '    <observation stamp="%s-400" value="%.1f"/>' % (obsStamp, avgArray[d][0] / avgArray[d][1])
        print >> f, '  </feed>'
    print >> f, '</feeds>'
    f.close()


def doHistNode(stampStr, histNode):
    # msg/hist/data/sensor(0)/../[h|d]???
    # for all data nodes
    # find first sensor child, only handle sensor0
    #  handle all it's (h|d|m)XXX siblings
    for dataNode in histNode.getElementsByTagName('data'):
        sensor = string.atol(dataNode.getElementsByTagName('sensor')[0].childNodes[0].nodeValue)
        #print "Found sensor: %d" % sensor
        if (sensor == 0):
            #print "Handling sensor: %d" % sensor
            for hdm in dataNode.childNodes:
                #print "tag: %s" % hdm.tagName
                if ("sensor" == hdm.tagName):
                    continue
                scopePrefix = hdm.tagName[:1]             # h|d|m
                scopeIndex = string.atoi(hdm.tagName[1:]) # 4 in h004 or 2 in m002
                scopeValue = string.atof(hdm.childNodes[0].nodeValue);
                if ("h" == scopePrefix):
                    #print "%s Hour  %05d %10.5f" % ( stampStr, scopeIndex, scopeValue )
                    accumulateHours(stampStr, scopeIndex, scopeValue)
                if ("d" == scopePrefix):
                    #print "%s Day  %05d %10.5f" % ( stampStr, scopeIndex, scopeValue )
                    accumulateDays(stampStr, scopeIndex, scopeValue)
                if ("m" == scopePrefix):
                    print "%s Month  %05d %10.5f" % (stampStr, scopeIndex, scopeValue)
                    #summaryMonth(stampStr, scopeIndex, scopeValue )
        #else:
        #        pass
        #        print "Ignoring sensor: %d" % sensor

def warnDrift(stampSecs, stampStr, ccTimeStr):
    ccStampStr = stampStr[:-13] + ccTimeStr
    ccTimeSecs = parseLocaltimeToSecs(ccStampStr)
    drift = ccTimeSecs - stampSecs
    if (drift>43200):
        drift=-86400+drift
    elif (drift<-43200):
        drift=86400+drift
    if (abs(drift)>600):
        print "WARNING clock drift: %f seconds @ %s" % (drift,stampStr)

# stampStr has the format: 
def parseFragment(stampStr, ccfragment):
    # date format: 2009-07-02T19:08:12-0400
    # remove the utcoffset in string
    stampStrNoTZ = stampStr[:-5]
    # reformat utcofset from -0400 to -04:00
    UTCOffset = "%s:%s" % (stampStr[-5:-2], stampStr[-2:])
    # gmtStampStrExpr = "CONVERT_TZ('%s','America/Montreal','GMT')"%(stampStrNoTZ)
    gmtStampStrExpr = "CONVERT_TZ('%s','%s','GMT') " % (stampStrNoTZ, UTCOffset)
    # we also need actual value for csv.
    stampSecs = parseLocaltimeToSecs(stampStrNoTZ)
    gmtStr = formatGMTForXML(stampSecs)

    try:
        ccdom = minidom.parseString(ccfragment)
    except Exception, e:
        print "XML Error: %s : %s" % (stampStr, e)
        return

    #calculate drift
    ccTimeStr = ccdom.getElementsByTagName('time')[0].childNodes[0].nodeValue
    warnDrift(stampSecs,stampStr,ccTimeStr)
    ccStampStr = stampStrNoTZ[:-8] + ccTimeStr

    histNodeList = ccdom.getElementsByTagName('hist')
    if (histNodeList):
        # confirm only one history Node ?
        #print "Detected History T: %s Drift: %f" % (stampStr,drift)
        doHistNode(stampStr, histNodeList[0])
        # use CC's time
        #doHistNode(ccStampStr,histNodeList[0])
        return

    sensor = string.atol(ccdom.getElementsByTagName('sensor')[0].childNodes[0].nodeValue)
    sensorID = string.atol(ccdom.getElementsByTagName('id')[0].childNodes[0].nodeValue)
    #print "D=%f T=%s S=%d frag=%s" % (drift,ccTimeStr,sensor,ccfragment)
    sumwatts = 0
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
    averageForHours(stampStr, sumwatts)
    averageForDays(stampStr, sumwatts)
    averageForMinutes(stampStr, sumwatts)
    averageForTensecs(stampStr, sumwatts)
    # use CC's time
    #averageForHours(ccStampStr, sumwatts )
    #averageForDays(ccStampStr, sumwatts )

MARKStamp = None #'2000-01-01T00:00:00'
MARKCheckLen = 13      # 13 for hour,16 for minute

def handleLine(line):
    if (line[:4] == "<!--"):
        return
    stampStr = line[:24]
    CCStr = line[25:-1] # to remove the newline ?
    # omit empty lines

    # Mark the logs as the stampStr advances.
    global MARKStamp
    if (stampStr[:MARKCheckLen] != MARKStamp):
        print "# MARK -- %s" % stampStr
    MARKStamp = stampStr[:MARKCheckLen]

    if (len(CCStr) > 0):
        parseFragment(stampStr, CCStr)

if __name__ == "__main__":
    usage = 'python %s' % sys.argv[0]
    totallines = 0;
        # read line by line
    while True:
        line = sys.stdin.readline()         # read a one-line string
        if not line:                        # or an empty string at EOF
            break
        totallines += 1

            #if ((totallines % 10000) == 0):
            #        sys.stderr.write("line # %d \n" % (totallines))
                
        handleLine(line)
            #if (totallines>100):
            #        break
                # (stamp, watts,volts) = getGMTTimeWattsAndVoltsFromTedService()

sys.stderr.write("Done; counted %d lines\n" % (totallines))
#showHours()
#showDays()
#showMinutes()
#showTensecs()
writeXML()
