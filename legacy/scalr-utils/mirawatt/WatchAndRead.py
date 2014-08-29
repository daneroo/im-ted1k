# This is example code to perpetually read
# a directory with changing logs
#   logdir: prefix*.log
# One of theese files is growing
# as input to this script: use
# while true; do echo `date +%Y-%m-%dT%H:%M:%S%z` "Content in the file" >> PFX`date +%Y%m%dT%H%M00%z`.log; sleep 2; done
#
#  Two parts, 
#  -find and order candidate files
#  -read a file (until some timeout event..)
# The loop is
#  find all files, for each 
#      read each line until EOF
#      check for new files
#      if not more files, keep reading this one
#  
# so to do that can we iterate over a changing vector ?

import os.path
import sys
import time

import datetime
import fileinput
import getopt
import iso8601
import os
import pickle
import re
import string
from xml.dom import minidom

def findPrefixedLogs(path, prefix='CC', includeCompressed=False):
    """
    Finds files (recursively) in the directory tree starting at 'path'
    who's basenames start with prefix
    and who's siffix is .log (or.og.bz2 if includeCOmpressed is True)

    The returnd filepaths are sorted by basename

    Returns a sequence of paths for files found.
    """
    matcherList = [(lambda s: os.path.basename(s).startswith(prefix))]
    if includeCompressed:
        matcherList.append((lambda s: s.endswith('.log') or s.endswith('.log.bz2') or s.endswith('.log.gz')))
    else:
        matcherList.append((lambda s: s.endswith('.log')))

    fileList = ffind(path, namefs=matcherList, relative=False)
    fileList.sort(key=(lambda s: os.path.basename(s)))
    return fileList

# From: http://muharem.wordpress.com/2007/05/18/python-find-files-and-search-inside-them-find-grep/
class ScriptError(Exception): pass
def ffind(path, namefs=None, relative=True):
    """
    Finds files in the directory tree starting at 'path' (filtered by the
    functions in the optional 'namefs' sequence); if the 'relative'
    flag is not set, the result sequence will contain absolute paths.

    Returns a sequence of paths for files found.
    """
    if not os.access(path, os.R_OK):
        raise ScriptError("cannot access path: '%s'" % path)

    fileList = [] # result list
    try:
        for dir, subdirs, files in os.walk(path):
            fileList.extend('%s%s%s' % (dir, os.sep, f) for f in files)
        if not relative: fileList = map(os.path.abspath, fileList)
        if namefs: 
            for ff in namefs: fileList = filter(ff, fileList)
    except Exception, e: raise ScriptError(str(e))
    return(fileList)

# return a copy of logFileList, which need processing according to progress
def removeUnchanged(logFileList, progress): # Remove items which are unchanged in progress.
    activeFileList = [];
    for filename in  logFileList:
        newPI = ProgressItem(filename)
        #localtimeModStr : not used for date comparisons, just output logging
        localtimeModStr = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(newPI.lastMod))
        ago = time.time()-newPI.lastMod
        #print " checking: %s  len:%08d ago:%ds. mod:%s md5:%s" % (os.path.basename(newPI.fileName),newPI.fileSize,ago,localtimeModStr,newPI.md5)
        oldPI = None
        if (filename in progress):
            oldPI = progress[filename]
        if (not oldPI): # new file: seed progress, calc md5, appent to active file list
            newPI.calcmd5()
            progress[filename] = newPI
            activeFileList.append(filename)
            print "# NEW: %s  len:%08d ago:%ds. mod:%s md5:%s" % (os.path.basename(newPI.fileName), newPI.fileSize, ago, localtimeModStr, newPI.md5)
        elif (newPI.fileSize != oldPI.fileSize or newPI.lastMod != oldPI.lastMod):
            # current file is in progress, but size/date has changed
            # update info in progress, add to active List (calc md5)
            # make sure we preserve le lastLineRead (high water mark)
            newPI.calcmd5()
            newPI.lastLineRead = oldPI.lastLineRead
            # replace with new progress item
            progress[filename] = newPI
            activeFileList.append(filename)
            print "# MOD: %s  len:%08d ago:%ds. mod:%s md5:%s" % (os.path.basename(newPI.fileName), newPI.fileSize, ago, localtimeModStr, newPI.md5)
        else:
            #print "# SKP: %s  len:%08d ago:%ds. mod:%s md5:%s" % (os.path.basename(oldPI.fileName),oldPI.fileSize,ago,localtimeModStr,oldPI.md5)
            pass

    return activeFileList

def md5OfFileContent(fileName): # if bz2 or gz md5 of uncompressed content
    mode = 'r'
    #fp = open(fileName,mode) #fileinput.hook_compressed(fileName, mode)
    fp = fileinput.hook_compressed(fileName, mode)

    #md5 = hashlib.md5()
    md5 = None
    try:
        import hashlib
        md5 = hashlib.md5()
    except:
        import md5
        md5 = md5.md5()

    try:
        while 1:
            data = fp.read(8096) #buffer at a time
            if not data:
                break
            md5.update(data)
    finally:
        fp.close()
    return md5.hexdigest()

class ProgressItem:
    def __init__(self, fileName):
        self.fileName = fileName
        stats = os.stat(fileName)
        self.fileSize = stats[6]
        self.lastMod = stats[8]
        self.md5 = 'UNSET'
        self.lastLineRead = 0

    def calcmd5(self):
        self.md5 = md5OfFileContent(self.fileName)

def loadProgressFromPickle():
    try:
        if (os.path.exists(Settings.progressStateFilename)):
            print "# STATE Reading persited from: %s" % Settings.progressStateFilename
            pckfp = open(Settings.progressStateFilename, 'rb')
            nuprogress, nuaverages = pickle.load(pckfp)
            pckfp.close()
            return (nuprogress, nuaverages)
    except Exception, e:
        print "# STATE Error reading from: %s : %s" % (Settings.progressStateFilename, e)
    return ({}, {}) # empty progress,averages

def saveProgressToPickle(saveprogress, saveaverages):
    print "# STATE peristed to: %s" % Settings.progressStateFilename
    pckfp = open(Settings.progressStateFilename, 'wb')
    pickle.dump((saveprogress, saveaverages), pckfp)
    pckfp.close()

def onepass(progress, averages):
    # renew the list
    logFileList = findPrefixedLogs(Settings.logPathRoot, prefix=Settings.logPrefix, includeCompressed=True)
    activeFileList = removeUnchanged(logFileList, progress)
    if (len(activeFileList) <= 0):
        #print "No files to process"
        return

    #for line in fileinput.input(activeFileList):
    for line in fileinput.input(activeFileList, openhook=fileinput.hook_compressed):
        if (fileinput.filelineno() <= progress[fileinput.filename()].lastLineRead):
            #print "skip  %06d from:%s" % (fileinput.filelineno(),fileinput.filename())
            continue

        # indicate progress (before or after actual processing ?
        progress[fileinput.filename()].lastLineRead = fileinput.filelineno()

        if (fileinput.isfirstline()):
            truncateAverages()

        # actually process the line
        handleLine(line)

        if (fileinput.filelineno() % 1000 == 0):
            pass #print "file:%s:%06d  -mod:%s" % (os.path.basename(fileinput.filename()),fileinput.filelineno(),lastModDate)
        #print "file:%s:%06d" % (os.path.basename(fileinput.filename()),fileinput.filelineno())

    truncateAverages()
    writeXML()
    saveProgressToPickle(progress, averages)

    # only print active listed logs
    #for fileName in sorted(progress.keys(), key=(lambda s: os.path.basename(s))):
    for fileName in sorted(activeFileList, key=(lambda s: os.path.basename(s))):
        print "# PROGRESS line %5d %s in %s" % (progress[fileName].lastLineRead, os.path.basename(fileName), os.path.dirname(fileName))

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

lastPrintedWarning = None # stamp of last drift warning, so we can warn only every two hours (MAX)
def warnDrift(stamp, ccfragment):
    matchTime = re.search("<time>(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})</time>", ccfragment)
    if (not matchTime): return
    ccstamp = stamp.replace(hour=int(matchTime.group('hour')),
        minute=int(matchTime.group('minute')),
        second=int(matchTime.group('second')))
    delta = ccstamp - stamp
    drift = delta.days * 86400 + delta.seconds #+delta.microseconds/1000000.0
    if (drift > 43200):
        drift = -86400 + drift
    elif (drift < -43200):
        drift = 86400 + drift
    if (abs(drift) > 600):
        global lastPrintedWarning
        if (lastPrintedWarning):
            timeSinceLastWarning = (stamp-lastPrintedWarning)
            if (timeSinceLastWarning > datetime.timedelta(hours=2)):
                print "# WARNING clock drift: %f seconds @ %s" % (drift, stamp)
                lastPrintedWarning = stamp
        else:
            lastPrintedWarning = stamp

# could validate entire DTD, hist version,sample version
msgintegrity = re.compile('<msg>.*</msg>')
chwattpattern = re.compile('<(?P<ch>ch[0-9])><watts>(?P<watt>[0-9]+)</watts></(?P=ch)>')
def extractWattsRE(stampStr, ccfragment):  # return sum of watt channels - could be 1,2,3 channels
    ok  = msgintegrity.search(ccfragment)
    if (not ok):
        print "# XML Error: %s : %s" % (stampStr, 'RE: Incomplete fragment')
        return None

    pairs = chwattpattern.findall(ccfragment)
    # e.g.: [('ch1', '00769'), ('ch2', '00400')]
    if (pairs):
        sumwatts = 0
        for ch, watt in pairs:
            sumwatts += int(watt)
        #print "RE  %s W = sum(%s)" % (sumwatts,pairs)
        return sumwatts
    else:
        return None

# <msg><hist><data><sensor>X</sensor><[hdm](YYY)>VVV</[hdm](YYY)>/data></hist></msg>
# - inside history: repeating data elements
# - inside data:    sensor + repeating hmd elements
msghistpattern = re.compile('<msg>.*(?P<hist><hist>.*</hist>).*</msg>')
datapattern = re.compile('(?P<data><data><sensor>(?P<sensorid>[0-9]+)</sensor>.*?</data>)')
hdmdatapattern = re.compile('<(?P<scope>[hmd][0-9]+)>(?P<value>[0-9]+[.][0-9]+)</(?P=scope)>')
def extractHistoryRE(stampStr, ccfragment):  # return sum of watt channels - could be 1,2,3 channels
    #this should be moved up and include hist|data detection
    ok  = msgintegrity.search(ccfragment)
    if (not ok):
        print "# XML Error: %s : %s" % (stampStr, 'RE: Incomplete fragment')
        return None
    isHist  = msghistpattern.findall(ccfragment)
    history = [] # tuples of (scopePrefix,scopeIndex,scopeValue)
    if (isHist):
        #print "History: %s : %s" % (stampStr, isHist[0])
        # isHit[0] contains the hist element
        dataElements = datapattern.findall(isHist[0])
        if (not dataElements): return None
        for data in dataElements:
            # data[0] is the whole data element, data[1] is the sensorid
            sensorid = int(data[1])
            #print " Data: %s : %s" % (stampStr, data)
            # only do sensor 0
            if (sensorid == 0):
                #print " Sensor 0: %s : %s" % (stampStr, data)
                hdms = hdmdatapattern.findall(data[0])
                for hdm in hdms:
                    #print "   scope,value: %s : %s" % (stampStr, hmd)
                    scopePrefix = hdm[0][:1]             # h|d|m
                    scopeIndex = string.atoi(hdm[0][1:]) # 4 in h004 or 2 in m002
                    scopeValue = string.atof(hdm[1]);
                    #print "   %s: %04d -> %f" % (scopePrefix,scopeIndex,scopeValue)
                    history.append((scopePrefix, scopeIndex, scopeValue))
        return history
    else:
        return None



def extractWattsXML(stampStr, ccfragment):  # return sum of watt channels - could be 1,2,3 channels
    try:
        ccdom = minidom.parseString(ccfragment)
        sumwatts = 0
        wattarray = []
        for wattnode in ccdom.getElementsByTagName('watts'):
            watt = string.atol(wattnode.childNodes[0].nodeValue)
            wattarray.append(watt)
            sumwatts += watt
        #print "XML %s W = sum(%s)" % (sumwatts,wattarray)
        return sumwatts
    except Exception, e:
        print "# XML Error: %s : %s" % (stampStr, e)

    return None

# moving averages for each scope
averages = {}
def movingAverage(stamp, value):
    '''Accumulate averages for different scopes'''
    # - convert stamp to LocalTime (it probably already is
    # ***  we can not use localstamp and reverse reliably to utc
    #   but this does work for startOf Day/Month
    #  so for tensec,minute,hour, use stamp : utc
    #     for month,day use localStamp
    localStamp = iso8601.toLocalTZ(stamp)
    scopeStamps = {
        'month': iso8601.startOfMonth(localStamp),
        'day': iso8601.startOfDay(localStamp),
        'hour': iso8601.startOfHour(stamp),
        'minute': iso8601.startOfMinute(stamp),
        'tensec': iso8601.startOfTensec(stamp),
    }

    for scope in ['month', 'day', 'hour', 'minute', 'tensec']:
        scopeStamps[scope] = iso8601.toUTC(scopeStamps[scope])

    if (False): print "stamp:%s  local:%s Mo:%s DD:%s HH:%s MM:%s TS:%s" % (
        stamp, localStamp,
        scopeStamps['month'],
        scopeStamps['day'],
        scopeStamps['hour'],
        scopeStamps['minute'],
        scopeStamps['tensec'],
        )
    for scope in ['month', 'day', 'hour', 'minute', 'tensec']:
        if (scope not in averages): averages[scope] = {}
        scopeStamp = scopeStamps[scope]
        if (scopeStamp in averages[scope]):
            averages[scope][scopeStamp][0] = averages[scope][scopeStamp][0] + value
            averages[scope][scopeStamp][1] = averages[scope][scopeStamp][1] + 1
        else:
            averages[scope][scopeStamp] = [value, 1];

def historicalAverage(stamp, history):
    ''' This processes historical entries
        and potentially overwrites the observed averages.
        we may later wish to account for drift

        Special case for days: if les than
    '''
    if (not history): return
    referenceHourKey = None # so we only calculate this once
    referenceDayKey = None # so we only calculate this once
    referenceMonthKey = None # so we only calculate this once
    for ((scopePrefix, scopeIndex, scopeValue)) in history:
        #print "  history %s: %04d -> %f" % (scopePrefix,scopeIndex,scopeValue)
        if (scopePrefix == 'h'):
            minimumHourlySamples = 100 # less than this many observations use historical
            # round hour, index back by scope
            # must match the key in moving averages...
            if (not referenceHourKey):
                referenceHourKey = iso8601.startOfHour(stamp)
            # scopeIndex is OFF BY 3, : h004 is really the sum just calculated over the previous 2 hours
            # i.e. sum of last two hours or startOfHour-1 and startOfHour-2
            # we want to set this value for both hours
            for scopeIndexCORRECTION in [2, 3]:
                hourOffset = referenceHourKey + datetime.timedelta(hours=-scopeIndex + scopeIndexCORRECTION)
                newValueWatts = scopeValue / 2 * 1000; # kWh/2h -> watt
                newCount = 1000 # more than we could possibly observe every 5s==720
                newSum = newCount * newValueWatts # so we put that into running totals
                if (hourOffset not in averages['hour']):
                    #print "Hour %s %11s  %f  (%s - %d+%dh)" % (hourOffset, 'setting', newValueWatts, stamp, scopeIndex, scopeIndexCORRECTION)
                    averages['hour'][hourOffset] = [newSum, newCount]
                else:
                    (curSum, curCount) = averages['hour'][hourOffset]
                    if (curCount < minimumHourlySamples):
                        # not enough real data: override with historical
                        averages['hour'][hourOffset] = [newSum, newCount]
                        print "Hour %s %11s  %.1f  was %.1f (%d) (%s - %d+%dh)" % (hourOffset, 'replaceObs', newValueWatts, curSum / curCount, curCount, stamp, scopeIndex, scopeIndexCORRECTION)
                    elif (curCount >= newCount): # replacing a historical entry -
                        # including one that was added to after it was originally set
                        #  ic curCount<2000 above the observations after 23:00 will be added over our hostrical setting
                        if (newSum == curSum):
                            averages['hour'][hourOffset] = [newSum, newCount]
                            #print "Hour %s %11s  %.1f  was %.1f (%d) (%s - %d+%dh)" % (hourOffset, 'preserveHist', newValueWatts, curSum / curCount, curCount, stamp, scopeIndex, scopeIndexCORRECTION)
                        else:
                            averages['hour'][hourOffset] = [newSum, newCount]
                            #print "Hour %s %11s  %.1f  was %.1f (%d) (%s - %d+%dh)" % (hourOffset, 'replaceHist', newValueWatts, curSum / curCount, curCount, stamp, scopeIndex, scopeIndexCORRECTION)
                    else: # keeping observed values
                        #print "Hour %s %11s  %.1f  was %.1f (%d) (%s - %d+%dh)" % (hourOffset, 'preserveObs', newValueWatts, curSum / curCount, curCount, stamp, scopeIndex, scopeIndexCORRECTION)
                        pass
        elif (scopePrefix == 'd'):
            minimumDailySamples = 2000 # less than this many observations use historical
            # round days, index back by scope
            # must match the key in moving averages...
            if (not referenceDayKey):
                # start Of day is 23:00 in CC's history so add an hour before rounding
                referenceDayKey = iso8601.startOfDay(iso8601.toLocalTZ(stamp) + datetime.timedelta(hours=1))
            dayOffset = referenceDayKey + datetime.timedelta(days=-scopeIndex)
            newValueWatts = scopeValue / 24 * 1000; # kWh/24h -> watt
            newCount = 20000 # more than we could possibly observe every 5s==17k
            newSum = newCount * newValueWatts # so we put that into running totals
            #print "Day %s %11s  %f  (%s - %dd)" % (dayOffset,'is', newValueWatts, stamp, scopeIndex)
            if (dayOffset not in averages['day']):
                #print "Day %s %11s  %.1f  (%s - %dd)" % (dayOffset,'setting', newValueWatts, stamp, scopeIndex)
                averages['day'][dayOffset] = [newSum, newCount]
            else:
                (curSum, curCount) = averages['day'][dayOffset]
                if (curCount < minimumDailySamples):
                    # not enough real data: override with historical
                    averages['day'][dayOffset] = [newSum, newCount]
                    print "Day %s %11s  %.1f  was %.1f (%d) (%s - %dd)" % (dayOffset, 'replaceObs', newValueWatts, curSum / curCount, curCount, stamp, scopeIndex)
                elif (curCount >= newCount): # replacing a historical entry -
                    # including one that was added to after it was originally set
                    #  ic curCount<2000 above the observations after 23:00 will be added over our hostrical setting
                    if (newSum == curSum):
                        averages['day'][dayOffset] = [newSum, newCount]
                        #print "Day %s %11s  %.1f  was %.1f (%d) (%s - %dd)" % (dayOffset,'preserveHist', newValueWatts,curSum/curCount,curCount,stamp, scopeIndex)
                    else:
                        averages['day'][dayOffset] = [newSum, newCount]
                        #print "Day %s %11s  %.1f  was %.1f (%d) (%s - %dd)" % (dayOffset,'replaceHist', newValueWatts,curSum/curCount,curCount,stamp, scopeIndex)
                else: # keeping observed values
                    #print "Day %s %11s  %.1f  was %.1f (%d) (%s - %dd)" % (dayOffset,'preserveObs', newValueWatts,curSum/curCount,curCount,stamp, scopeIndex)
                    pass
        elif (scopePrefix == 'm'):
            if (not referenceMonthKey):
                referenceMonthKey = iso8601.startOfMonth(iso8601.toLocalTZ(stamp))
            monthOffset = referenceMonthKey + datetime.timedelta(days=-scopeIndex * 30)
            newValueWatts = scopeValue / 30 / 24 * 1000; # kWh/24h/30d -> watt
            #print "Month approx %s %11s  %f  (%s - %d mo)" % (monthOffset, 'ignoring', newValueWatts, stamp, scopeIndex)
            pass


def truncateAverages():
    howMany = {
        'tensec': 90, # ~ 90*10 = 15 minutes
        'minute': 120, # ~ 2 hrs
        'hour': 48, # ~ 2 days
        'day': 60, # ~ 60 days
        'month': 84, # ~ 7 years
    }
    for scope in ['month', 'day', 'hour', 'minute', 'tensec']:
        if (scope not in averages): continue #averages[scope] = {}
        #print "scope[%s] has length:%d truncate to %d" % (scope,len(averages[scope]),howMany[scope])
        sortedKeys = averages[scope].keys()
        sortedKeys.sort()
        sortedKeys.reverse()
        for d in sortedKeys[:howMany[scope]]:
            pass # print "keep scope[%s][%s]" % (scope,d)
        for d in sortedKeys[howMany[scope]:]:
            # print "delete scope[%s][%s]" % (scope,d)
            del averages[scope][d]


def writeXML():
    if (False): # combine Archived Hours/days
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
        {'id':0, 'name':'Live', 'averages':averages['tensec'], 'howMany':30},
        {'id':1, 'name':'Hour', 'averages':averages['minute'], 'howMany':60},
        {'id':2, 'name':'Day', 'averages':averages['hour'], 'howMany':24}, #combinedHours
        {'id':3, 'name':'Week', 'averages':averages['day'], 'howMany':7}, #combinedDays
        {'id':4, 'name':'Month', 'averages':averages['day'], 'howMany':30}, #combinedDays
    ]
    f = open(Settings.outputFeedsFilename, 'w')
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

        #scopeStamp = iso8601.fmtExtendedZ(scopeStamp) unreliabls in localTZ
        scopeStamp = iso8601.fmtExtendedZ(iso8601.toUTC(scopeStamp))
        print >> f, '  <feed scopeId="%s" name="%s" stamp="%s" value="%.1f">' % (scope['id'], scope['name'], scopeStamp, scopeValue)
        for d in sortedKeys[:scope['howMany']]:
            #obsStamp = iso8601.fmtExtendedZ(d)
            obsStamp = iso8601.fmtExtendedZ(iso8601.toUTC(d)) # since we only used reversible keys
            print >> f, '    <observation stamp="%s" value="%.1f"/>' % (obsStamp, avgArray[d][0] / avgArray[d][1])
        print >> f, '  </feed>'
    print >> f, '</feeds>'
    f.close()


def parseFragment(stampStr, ccfragment):
    # date format: 2009-07-02T19:08:12-0400
    stamp = iso8601.parse_iso8601(stampStr) 

    useDOM = False # or use RE...
    if (useDOM):
        sumwatts = extractWattsXML(stampStr, ccfragment)
    else:
        sumwatts = extractWattsRE(stampStr, ccfragment)

    if (sumwatts):
        movingAverage(stamp, sumwatts)
        #truncateAverages()

    # handle history
    history = extractHistoryRE(stamp, ccfragment)
    historicalAverage(stamp, history)

    warnDrift(stamp, ccfragment)


def usage():
    usageStr = '''
    python %s --base|-b /base/dir --logs|-l [/]log/root/PREFIX [--help|-h]
      -base dir is where the progress-state and output feed.xml files are stored
      -if log path root is empty or relative, it is taken relative to base dir
    ''' % sys.argv[0]
    print usageStr
    sys.exit(2)

class SettingsClass:
    '''Class used a s struct: see Pythom 9.7 Odds and Ends'''
    pass
Settings = SettingsClass()

def parseArgs():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:l:", ["help", "base=", "logs="])
    except getopt.error, msg:
        print 'Error msg: %s' % msg
        usage()

    # default values
    Settings.baseDir = None;
    logPathAndPrefix = None;

    for o, a in opts:
        if o in ("-b" "--base"):
            Settings.baseDir = a
        if o in ("-l" "--logs"):
            logPathAndPrefix = a
        elif o in ("-h", "--help"):
            usage()
        else:
            assert False, "Unknown option: %s" % o

    if (Settings.baseDir == None or not os.path.isdir(Settings.baseDir)):
        print "Base directory not found: %s (use --base /path/to/base)" % Settings.baseDir
        usage()
    if (logPathAndPrefix == None):
        print "Logs Root and Prefix not found (use --logs=/path/PREFIX)"
        usage()

    Settings.baseDir = os.path.abspath(Settings.baseDir)
    Settings.logPathRoot = os.path.abspath(os.path.join(Settings.baseDir, os.path.dirname(logPathAndPrefix)))
    if (not os.path.isdir(Settings.logPathRoot)):
        print "Log path root directory not found: %s (use --logs /path/to/logs)" % Settings.logPathRoot
        usage()
    Settings.logPrefix = os.path.basename(logPathAndPrefix)
    Settings.progressStateFilename = os.path.join(Settings.baseDir,'progress-state.pkl')
    Settings.outputFeedsFilename = os.path.join(Settings.baseDir,'feeds.xml')
    print "# START Base dir:   %s" % (Settings.baseDir)
    print "# START logs root:   %s/..." % (Settings.logPathRoot)
    print "# START logs prefix: %s*.log[.gz|bz2]" % (Settings.logPrefix)
    print "# START progress-state file: %s" % (Settings.progressStateFilename)
    print "# START output-feeds file: %s" % (Settings.outputFeedsFilename)

    
if __name__ == "__main__":
    parseArgs()
    progress, averages = loadProgressFromPickle() # map of file -> ProgressItem
    starttimer = time.time()
    loopcount = 0
    while (True):
        looptimer = time.time()
        loopcount += 1
        onepass(progress, averages)
        print "# ELAPSED -- loop:%08d %.1f s. (%.1f s. total)" % (loopcount, time.time()-looptimer, time.time()-starttimer)
        time.sleep(10.0)

