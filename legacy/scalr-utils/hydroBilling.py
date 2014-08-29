
import sys
import os
import string
import time
import getopt

############################################
### Documentation 
############################################
#  This script loads Hydro-Qc billing data into database

# Biling Data from Portal
billingData = [
	['2009-04-15', '2009-06-03', 50, 125.31, 1620, 2.51, 32.40, 'R'],
	['2009-02-10', '2009-04-14', 64, 181.50, 2340, 2.84, 36.56, 'R'],
	['2008-12-03', '2009-02-09', 69, 211.60, 2720, 3.07, 39.42, 'R'],
	['2008-10-03', '2008-12-02', 61, 190.82, 2450, 3.13, 40.16, 'R'],
	['2008-08-02', '2008-10-02', 62, 181.52, 2340, 2.93, 37.74, 'R'],
	['2008-06-03', '2008-08-01', 60, 242.31, 3070, 4.04, 51.17, 'R'],
	['2008-04-10', '2008-06-02', 54, 188.05, 2400, 3.48, 44.44, 'R'],
	['2008-02-05', '2008-04-09', 65, 281.49, 3640, 4.33, 56.00, 'E'],
	['2007-11-30', '2008-02-04', 67, 288.81, 3750, 4.31, 55.97, 'R'],
	['2007-10-02', '2007-11-29', 59, 238.95, 3080, 4.05, 52.20, 'R'],
	['2007-08-08', '2007-10-01', 55, 207.44, 2680, 3.77, 48.73, 'R'],
	['2007-06-02', '2007-08-07', 67, 270.75, 3490, 4.04, 52.09, 'R'],
	['2007-04-03', '2007-06-01', 60, 230.01, 2970, 3.83, 49.50, 'R'],
	['2007-02-02', '2007-04-02', 60, 234.61, 3080, 3.91, 51.33, 'R'],
	['2006-12-01', '2007-02-01', 63, 269.23, 3530, 4.27, 56.03, 'R'],
	['2006-09-29', '2006-11-30', 63, 236.55, 3110, 3.75, 49.37, 'R'],
	['2006-08-05', '2006-09-28', 55, 180.43, 2380, 3.28, 43.27, 'R'],
	['2006-06-02', '2006-08-04', 64, 266.03, 3490, 4.16, 54.53, 'R'],
]

#{'from':'2006-08-05', 'to':'2006-09-28' 'days':64, 'amount':180.43 'kWh':3490 'kWh/d':54.53}
#{'from':'2006-06-02', 'to':'2006-08-04' 'days':64, 'amount':266.03 'kWh':3490 'kWh/d':54.53}
def dateToSecs(dateStr):
  structTime = time.strptime(dateStr,"%Y-%m-%d");
  #print "  parsing %s yielded %s" % (dateStr,structTime)
  secs = time.mktime(structTime)
  return secs

def diffDays(dateStr1,dateStr2):  # Not inclusive midnight to midnight
  deltaSecs = dateToSecs(dateStr2) - dateToSecs(dateStr1)
  deltaDays = int(round(  deltaSecs/24.0/60/60  ))
  return deltaDays

def lineItemToBill(lineItem):
  bill = {
    'from':         lineItem[0],
    'to':           lineItem[1],
    'days':         lineItem[2],
    'amount':       lineItem[3],
    'kWh':          lineItem[4],
    'amountPerDay': lineItem[5],
    'kWhPerDay':    lineItem[6],
    }
  return bill

def isOK(cond):
  if(cond):
    return "OK"
  return "NOT OK"

def validateBill(bill):
  print "Validating bill : %s - %s" % (bill['from'],bill['to'])
  # + 1 becaus 'to' day is included
  calcDays = diffDays(bill['from'],bill['to']) +1
  print "  Days:       Expected %d - got %d   %s" % (bill['days'],calcDays,isOK((calcDays==bill['days'])))
  calcAmountPerDay = bill['amount'] / bill['days']
  deltaAmountPerDay = abs(calcAmountPerDay-bill['amountPerDay'])
  print "  Avg Amount: Expected %f - got %f   %s" % (bill['amountPerDay'],calcAmountPerDay,isOK(deltaAmountPerDay<0.01))
  calckWhPerDay = bill['kWh'] *1.0 / bill['days']
  deltakWhPerDay = abs(calckWhPerDay-bill['kWhPerDay'])
  print "  Avg kWh:    Expected %f - got %f   %s" % (bill['kWhPerDay'],calckWhPerDay,isOK(deltakWhPerDay<0.01))
  
def validateBillingData():
  nextBill = None # bill are sorted date descending..
  for lineItem in billingData:
    bill = lineItemToBill(lineItem)
    validateBill(bill)
    if (nextBill):
      deltaDays = diffDays(bill['to'],nextBill['from'])
      print "  Chaining: %s - %s   %s" % (bill['to'],nextBill['from'],isOK(deltaDays==1))
      nextBill = bill
  
# from Summarize    
def startOfDay(secs,offsetInDays):
  # don't keep DST flag in converting with offset..(unlike hour,minute)
  secsTuple = time.localtime(secs)
  startOfDayWithOffsetTuple = (secsTuple[0],secsTuple[1],secsTuple[2]+offsetInDays,0,0,0,0,0,-1)
  startOfDayWithOffsetSecs  = time.mktime(startOfDayWithOffsetTuple)
  return startOfDayWithOffsetSecs

# This is a GENERATOR not a function
# generates a sequence of 'YYYY-MM-DD' string representing the 
# start of each day between startDay and endDay (inclusive)
# and walks forwards in time
def walkDaysGenerator(startDayStr,endDayStr): # see generators docs
  # Initial Values
  startDaySecs = startOfDay(dateToSecs(startDayStr),0)
  # Termination Boundary
  endDaySecs = startOfDay(dateToSecs(endDayStr),0)
  
  while True:
    if (startDaySecs>endDaySecs): # > to include endDay, >= from exclude endDay
      return  # termination of generator
    yield time.strftime("%Y-%m-%d",time.localtime(startDaySecs))
    startDaySecs = startOfDay(startDaySecs,1)

def printBillingSQL():
  #re-invert the billing records 
  sortedBills = [];
  for lineItem in billingData:
    bill = lineItemToBill(lineItem)
    sortedBills.insert(0,bill)

  for bill in sortedBills:
    #print "Walk from %s to %s" % (bill['from'],bill['to'])
    for (aDayStr) in walkDaysGenerator(bill['from'],bill['to']):
      #print "%    -- %s" % aDayStr
      kWhPerDay = bill['kWhPerDay']
      watt = int(round(kWhPerDay/24.0*1000));
      print "REPLACE INTO watt_billing(stamp,watt) VALUES ('%s','%d');" % (aDayStr,watt)
    
def logError(msg):
        sys.stderr.write(msg)
        sys.stderr.write("\n")

def main():
  usage = 'python %s ( --validate | --sql )' % sys.argv[0]
  printUsageAndDie = True;
  if (len(sys.argv)==2):
    printUsageAndDie=False;

  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["validate", "sql"])
  except getopt.error, msg:
    logError('error msg: %s' % msg)
    printUsageAndDie=True

  if (printUsageAndDie):
    logError(usage)
    sys.exit(2)

  doSQL = False
  for o, a in opts:
    if o == "--validate":
      doSQL = False
    elif o == "--sql":
      doSQL = True


  if (doSQL):
    printBillingSQL()
  else:
    validateBillingData()

if __name__ == '__main__':
  main()
