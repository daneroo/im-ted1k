# Modified version of ted.py
#
# The most recent version of this module can be obtained at:
#   http://svn.navi.cx/misc/trunk/python/ted.py
#
# Copyright (c) 2008 Micah Dowty <micah@navi.cx>
# run as
#  while true; do echo `date` Restarted ReadTEDNative | tee -a TEDNative.log; python ReadTEDNative.py --forever --device /dev/ttyUSB0; sleep 1; done
#
#

import sys
import string
import math
import getopt
import datetime
import time
from ted1k.logging import logInfo,logWarn,logError
from ted1k.ted import TED
from ted1k.mysql import MySQL
# from ted1k.filer import Filer


def getGMTTimeWattsAndVoltsFromTedNative(packet):
    ISO_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    #isodatestr = datetime.datetime.now().strftime(ISO_DATE_FORMAT) 
    isodatestr = time.strftime(ISO_DATE_FORMAT,time.gmtime(time.time())) 

    #for name, value in packet.fields.items():
    #        print "%s = %s" % (name, value)
    # -- kw_rate = 0.054
    # -- volts = 122.0
    # -- house_code = 211
    # -- kw = 1.0

    kWattStr = packet.fields["kw"]
    voltStr = packet.fields["volts"]
    #print "%s\t%s\t%s" % (isodatestr, kWattStr, voltStr) 
    watts = string.atof(kWattStr)*1000.0
    volts  = string.atof(voltStr)
    return (isodatestr , watts,volts)

# catch SIGTERM signal, So we can terminate gracefully (set global duration to 0)
def sigterm_handler(signum, frame):
    global duration
    print 'Signal caught (%d): Exiting' % signum
    duration=0

if __name__ == "__main__":

    signal.signal(signal.SIGTERM, sigterm_handler)
    db = MySQL();

    usage = 'python %s  ( --duration <secs> | --forever) [--device /dev/ttyXXXX]' % sys.argv[0]
    
    # tablenames: watt, ted_native
    # insert into BOTH tables
    tablenames=['watt','ted_native']

    for tablename in tablenames:
        db.checkOrCreateTable(tablename);

    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["duration=", "forever", "device="])
    except getopt.error, msg:
        logError('error msg: %s' % msg)
        logError(usage)
        sys.exit(2)

    # default value (forever -> duration=-1
    duration=-1
    #default value /dev/ttyUSB0
    device = "/dev/ttyUSB0"

    for o, a in opts:
        if o == "--duration":
            duration = string.atol(a)
        elif o == "--forever":
            duration = -1
        elif o == "--device":
            device = a

    print "duration is %d" % duration
    start = time.time()

    print "Instantiating TED object using device: %s" % device
    tedObject = TED(device)

    
    while True:
        datetimenow = datetime.datetime.now()
        now=time.time()
        if duration>=0 and (now-start)>duration:
            break

        for packet in tedObject.poll():
            (stamp, watts,volts) = getGMTTimeWattsAndVoltsFromTedNative(packet)
            print "%s --- %s\t%d\t%.1f" % (datetimenow,stamp, watts, volts) 

            # insert into BOTH tables
            for tablename in tablenames:
                sql = "INSERT IGNORE INTO %s (stamp, watt) VALUES ('%s', '%d')" % (
                        tablename,stamp,watts)
                #print " exe: %s" % sql
                db.executeQuery(sql)

        now=time.time()
        if duration>0 and (now-start)>duration:
                break
        # sleep to hit the second on the nose:
        (frac,dummy) = math.modf(now)
        desiredFractionalOffset = .1
        delay = 1-frac + desiredFractionalOffset
        time.sleep(delay)

print "Done; lasted %f" % (time.time()-start)

