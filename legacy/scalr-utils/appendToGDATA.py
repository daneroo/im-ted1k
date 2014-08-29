#!/usr/bin/python
#
__author__ = 'Daniel Lauzon'


try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string
import time

def main():
  usage = 'python %s --user [username] --pw [password] --watt [watts]  (--secs [secs] --stamp [\'2008-12-31 23:59:59\'])' % sys.argv[0]

  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw=","secs=","watt=","stamp="])
  except getopt.error, msg:
    print 'error msg: %s' % msg
    print usage
    sys.exit(2)
  
  user = ''
  pw = ''
  watt = ''
  secs = ''
  stamp = ''

  # Process options
  for o, a in opts:
    if o == "--user":
      user = a
    elif o == "--pw":
      pw = a
    elif o == "--watt":
      watt = a
    elif o == "--secs":
      secs = a
    elif o == "--stamp":
      stamp = a

  if user == '' or pw == '' or watt == '':
    print usage
    sys.exit(2)

  if stamp == '':
    try:
      stamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(string.atol(secs)))
    except ValueError:
      stamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

  print 'user: %s @ %s : watt=%s' % (user,stamp,watt)

  gd_client = gdata.spreadsheet.service.SpreadsheetsService()
  gd_client.email = user
  gd_client.password = pw
  gd_client.source = 'GDATA-TED Appender Script'
  gd_client.ProgrammaticLogin()
  curr_key = 'o05258885899204507155.8893627254848474629'
  curr_wksht_id = 'od6'
  dict = {}
  dict['watt']=watt
  dict['stamp']=stamp
  entry = gd_client.InsertRow(dict, curr_key, curr_wksht_id)
  if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
    print 'Inserted!'
  
if __name__ == '__main__':
  main()
