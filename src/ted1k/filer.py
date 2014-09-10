import time
import json
import os
from ted1k.logging import logInfo,logWarn,logError
from ted1k.datestamp import datetimeToSecs, formatTimeForJSON

# Append json entry to outputfile (jsonl format)
#   {"stamp": "2008-07-30T00:04:40Z", "watt": 540}
#   {"stamp": "2008-07-30T00:04:41Z", "watt": 540}

# TODO 
# check for existence of file: overwrite vs append...

OUTPUTLOGDIR="/data/jsonl"
DEVICEALIAS="TED1k"

def formatTimeForOutputFilename(secs):
    SUFFIX="jsonl"
    # this is the name of the current logrotated file
    #OUTPUTSTAMPFORMAT="%Y%m%dT%H%M00Z" # by Minute
    OUTPUTSTAMPFORMAT="%Y%m%dT000000Z" # by Day
    stamp =  time.strftime(OUTPUTSTAMPFORMAT,time.gmtime(secs))
    return "%s/%s-%s.%s" %(OUTPUTLOGDIR,DEVICEALIAS,stamp,SUFFIX)

def formatOutputLine(secs,watt):
    obj = {"stamp": formatTimeForJSON(secs), "watt":watt}
    line = json.dumps(obj)+'\n'
    return line

# return (filename,line) - grouped to avoid double conversion to secs
def filenameAndLine(stamp,watt):
    secs = datetimeToSecs(stamp);
    filename = formatTimeForOutputFilename(secs)
    line = formatOutputLine(secs,watt)
    return (filename,line)

def ensure_dir():
    if not os.path.exists(OUTPUTLOGDIR):
        logInfo('Creating directory: %s' % OUTPUTLOGDIR)
        os.makedirs(OUTPUTLOGDIR)

class Filer:
    def __init__(self):
        logInfo('Setting up Filer')
        self.file=None
        self.filename=None
        ensure_dir()

    def updateFile(self,filename):
        if filename != self.filename:
            logInfo('filename: %s -> %s' % (self.filename,filename))
            if self.file !=None:
                self.file.close()
            self.file = open(filename, 'a')
            self.filename=filename

    def store(self,stamp,watt):
        (filename,line) = filenameAndLine(stamp,watt)
        self.updateFile(filename)
        self.file.write(line)

    # Cache many lines - flush with writeLines (faster)
    def storeMany(self,rows):
        pendingLines = [];

        # logInfo('-storeMany %d' % len(rows))
        for (stamp,watt) in rows:
            (filename,line) = filenameAndLine(stamp,watt)

            # flush pending lines (before updateFile is called)
            if filename != self.filename:
                # logInfo('+storeMany flush %d' % len(pendingLines))
                if len(pendingLines)>0:
                    self.file.writelines(pendingLines)
                    pendingLines=[]
                self.updateFile(filename)
            pendingLines.append(line)

        # flush all remaining lines
        # logInfo('+storeMany flush %d' % len(pendingLines))
        self.file.writelines(pendingLines)
        pendingLines=[];
        
    #  for use with with! Allows cleaning up the last opened file...
    def __enter__(self):
        # logInfo('Entering Filer')
        return self
    def __exit__(self, type, value, traceback):
        # logInfo('Exiting Filer')
        if self.file !=None:
            self.file.close()
        self.file=None
        self.filename=None
