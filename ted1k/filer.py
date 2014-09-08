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
    # def __del__(self):
    #     logInfo('Destroying Filer')

    def updateFile(self,secs):
        newFileName = formatTimeForOutputFilename(secs)
        if newFileName != self.filename:
            logInfo('filename: %s -> %s' % (self.filename,newFileName))
            if self.file !=None:
                self.file.close()
            self.file = open(newFileName, 'a')
            self.filename=newFileName

    def store(self,stamp,watt):
        secs = datetimeToSecs(stamp);
        obj = {"stamp": formatTimeForJSON(secs), "watt":watt}
        self.updateFile(secs)
        json.dump(obj,self.file)
        self.file.write('\n')

    #  for use with with!
    def __enter__(self):
        # logInfo('Entering Filer')
        return self
    def __exit__(self, type, value, traceback):
        # logInfo('Exiting Filer')
        if self.file !=None:
            self.file.close()
        self.file=None
        self.filename=None
