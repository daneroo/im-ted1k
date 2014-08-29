#!/usr/bin/python
# validate basic datetime manipulations
# especialy related to timezones
#
# requirements 
# 1-parse
#  2009-09-24T15::34:56-0400
# but eventually also
#  2009-09-24T15::34:56-0400
#  2009-09-24T15::34:56Z
#  2009-09-24 15::34:56-0400
#  2009-09-24 15::34:56Z
# 2-Format Local/UTC
# 3-Rounding with pre/post offset, local/UTC ?
#  (year,month,day,hour,halfhour,tenminute,minute,halfminute,tenseconds,second)
#  We will first parse an ISO Format

import datetime

def roundHour():
    dt=datetime.datetime.now()
    print "date under test: %s" % dt
    dt = dt.replace(minute=0,second=0)
    print "rounded to hour: %s" % dt

def examineNow():
    # datetime.datetime.now() return None in tzinfo
    # strftime with %z and %Z return emtpy strings on mac
    dt=datetime.datetime.now()
    print "date under test: %s" % dt
    print "tzinfo: %s" % dt.tzinfo
    print "strftime with %%z and %%Z: |%s|" % dt.strftime("%z %Z")

import sys

if __name__ == "__main__":
    print "Starting datetime tests"
    examineNow()
    #roundHour()
