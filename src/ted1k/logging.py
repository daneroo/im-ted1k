# should probably include a timestamp, with local/UTC convention
import sys

def logError(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
def logWarn(msg):
    logError(msg)
def logInfo(msg):
    logError(msg)
