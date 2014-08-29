
import sys
import time
import os
import random

# DON't use time.strftime with %z with gmtime!
# How about datetime instead!
ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

def log(msg):
    sys.stdout.write("%s\n"%msg)
    sys.stdout.flush()

log("Heartbeat is starting")
log("Current Working Directory is: %s " % os.getcwd())
while (True):
    #gmtStamp = time.strftime(ISO_DATE_FORMAT,time.gmtime())
    gmtStamp = time.strftime(ISO_DATE_FORMAT,time.localtime())
    log("%s heartbeat" % gmtStamp)

    # randomly die
    if (random.random()<.00001):
        log("%s heartbeat is randomly dying" % gmtStamp)
        sys.exit(0)

    # randomly wait more than 30 Secs
    if (random.random()<.00001):
        log("%s heartbeat is randomly hanging > 60 secs" % gmtStamp)
        time.sleep(60)

    time.sleep(10)

log("Heartbeat is exiting")
