#!/usr/bin/python
#
# Copyright (C) 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'api.laurabeth@gmail.com (Laura Beth Lincoln)'


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


class Shower:
  
  def __init__(self, email, password, key, sheet):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Spreadsheets GData Sample'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = key
    self.curr_wksht_id = sheet
    self.list_feed = None
    
  def _ValidateKey(self):
    try:
      self._ListWorksheet()
    except gdata.service.RequestError:
      print "Hello Error on key"
      self._ListSpreadsheet()
      sys.exit(0)

  def _ValidateSheet(self):
    try:
      self._ValidateKey()
      self._ListGetAction()
    except gdata.service.RequestError:
      print "Hello Error on sheet"

  def _ListSpreadsheets(self):
    # Get the list of spreadsheets
    feed = self.gd_client.GetSpreadsheetsFeed()
    self._PrintFeed(feed)
    
  def _ListWorksheets(self):
    try:
      # Get the list of worksheets
      feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
      self._PrintFeed(feed)
    except gdata.service.RequestError, msg:
      print " --Error on ListWorksheets : %s\n Listing Spreadshets" % msg
      self._ListSpreadsheets()
      sys.exit(0)
  
  def _ShowCells(self):
    try :
      # Get the list feed
      self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
      self._PrintFeed(self.list_feed)
    except gdata.service.RequestError, msg:
      print " --Error on ShowCells : %s\n Listing Worksheets" % msg
      self._ListWorksheets()
      sys.exit(0)
    
  def _ListDeleteAction(self, index):
    self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
    print 'Deleted!'
    
  def _PrintFeed(self, feed):
    for i, entry in enumerate(feed.entry):
      if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
        print '%s %s\n' % (entry.title.text, entry.content.text)
      elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        #print '%s %s %s\n' % (i, entry.title.text.encode('UTF-8'), entry.content.text.encode('UTF-8'))
        print '%s %s %s' % (i, entry.title.text, entry.content.text)
      elif isinstance(feed, gdata.spreadsheet.SpreadsheetsWorksheetsFeed):
        id_parts = feed.entry[i].id.text.split('/')
        print '  %s : --sheet %s rows: %s' % (entry.title.text, id_parts[len(id_parts) - 1],entry.row_count.text)
      elif isinstance(feed, gdata.spreadsheet.SpreadsheetsSpreadsheetsFeed):
        id_parts = feed.entry[i].id.text.split('/')
        print '  %s : --key %s ' % (entry.title.text, id_parts[len(id_parts) - 1])
      else:
        print "Feed of type: %s" % feed.__class__.__name__
        print '%s %s' % (i, entry.title.text)
        #print '%s' % ( entry)
        
  def Run(self):
    self._ShowCells()


def main():
  usage = 'python %s --user [username] --pw [password] --key [key] --sheet [sheet]' % sys.argv[0]
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw=","key=","sheet="])
  except getopt.error, msg:
    print usage
    sys.exit(2)
  
  user = ''
  pw = ''
  key = ''
  sheet = ''
  # Process options
  for o, a in opts:
    if o == "--user":
      user = a
    elif o == "--pw":
      pw = a
    elif o == "--key":
      key = a
    elif o == "--sheet":
      sheet = a

  if user == '' or pw == '':
    print usage
    sys.exit(2)
        
  sample = Shower(user, pw, key, sheet)
  sample.Run()


if __name__ == '__main__':
  main()
