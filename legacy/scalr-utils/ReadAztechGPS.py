# run as
# Talk to Aztech IHD through serial device /dev/ttyUSB1
#

import sys
import string
import math
import getopt
from scalr import logInfo,logWarn,logError
import datetime
import time
#import MySQLdb
########################### START of ted.py Stuff

import serial
import binascii
import struct

def getGPS():
    line = "GPS Unavailable"
    try:
        f = open('/tmp/gps.txt')
    except(IOError), e:
        pass
    else:
        try:
            line = f.readline()
            line = line.rstrip()
        finally:
            f.close()
    return line


def oneIteration(device,doCommand):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    ser = serial.Serial(device,38400,timeout=60,rtscts=0,dsrdtr=0,xonxoff=0)
    if (doCommand):
        ser.write("DEBUGON\r\n")

    zeroAttempts=0
    while True:
        resp = ser.readline()
        if (len(resp)==0):
            zeroAttempts+=1
        #if (zeroAttempts>3000):
        #    break

        stamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        gps = getGPS()
        # leading whitespace on OSX beacause of readline cr+lf mismatch ?
        resp = resp.lstrip() # remove leading whitespace
        resp = resp.rstrip() # remove trailing whitespace
        if (len(resp)>0 and resp.find("[R]")>=0):
            print "%s,%s,%s" % (stamp,resp,gps)
        elif (len(resp)>0):
            logInfo("%s |Response|=%4d : %s" % (stamp,len(resp),resp))
        else:
            #differentate between 0 from timeout and 0 from empty line: 2 before strip
            pass

    ser.close()
    logInfo("Exited loop")
    
if __name__ == "__main__":
        usage = 'python %s  ( --duration <secs> | --forever) [--device /dev/ttyXXXX]' % sys.argv[0]

        try:
                opts, args = getopt.getopt(sys.argv[1:], "", ["duration=", "forever", "device="])
        except getopt.error, msg:
                logError('error msg: %s' % msg)
                logError(usage)
                sys.exit(2)

        # default value (forever-> duration=-1
        duration=1
        #default value /dev/ttyUSB0
        device = "/dev/ttyUSB1"

        for o, a in opts:
                if o == "--duration":
                        duration = string.atol(a)
                elif o == "--forever":
                        duration = -1
                elif o == "--device":
                        device = a

        logInfo("Using device: %s" % device)

        while True:
            oneIteration(device,True)
        


