2009-05-29 Update from subclipse
2008-12-18 TODO
  -doSQLDump : see /home/daniel/java/solochain/heads/wdel/ext_resources/masterslave/doSqlDumpOnSlave as example

    Could also remote slave from solaris box at office...

    Watch while dumping:
         while true; do mysql ted -e "select stamp as 'stamp@watt',watt from watt order by stamp desc limit 20"; sleep 1; done
         while true; do mysql ted -e "select stamp as 'stamp@native',watt from ted_native order by stamp desc limit 20"; sleep 1; done

     to see if they lock while taking a dump...

     seems NOT to lock the inserts although the dump stops at moment of start.
     does seem to lock_out the Summarizing.

      45 secs: time mysqldump --opt ted >ted.sql
      95 secs: time mysqldump --opt --extended-insert=0  ted >ted.sql

     Could dump just once a day..
.
  +Turn Summarize into a forever loop (sleep 10.2 secs)
  +Invoke ReadTedNative --forever, and SUmmarize --forever (--duration )
    -into wdog daemons:
      make config file (for summarize first)
      redirect output and error?

  --Rethink 
      watt + ted_native duplication, 
      Secondary ouput of ReadTEDNative (files (sql,xml,cvs))

  -Reseed TED.db > watt, (? and ted_service ? - or ted_footprints)
  -Refactor all code (rename scalr? classes..., make installer ?) 

2008-12-17 Native interface... WORKING
   ReadTedNative.py : read device directly
      modeled after ReadTEDService.py, and ted.py

2008-11-14 Inventory and new plan.

-=-= Overview:
   Flow:  when and who
     to feed: ReadTEDService.py loads every second into watt, and ted_service
     to overwrite: HOWTO Incremental to Reload TED.db over watt
     to compare,     TED.db, ted_service(,aztech_service) , watt
     to summarize

   Script Names
          SQLiteToMysql???.py <- Incremental.py
          ReadTedNative.py 
          ReadTEDService.py
          Summarize.py

   DB tables: (dbname ted->wattrical not yet)
         watt : (stamp,watt)
         watt_tensec
         watt_minute
         watt_hour
         watt_day 
         ted_service
         ted_native
     -owner ? multiple accounts ? only on gae or morph


-=-= Objective (short):
   -Python daemon 
     -Exception Proof (see below)
     -Cron (all parts) 
         packaging for deployment into /archive/mirror (remove scalr.py ?)

   -Historical data (billing) into watt_day

   -HOWTO for Incremental.py invocation
   -HOWTO for copying ted_service back over watt ?
   -HOWTO for Summarize.py invocation (continuous+after reload)

   -Compare feeds (perhaps as we refill tensec,minute,hour)
        watt vs TED.db vs ted_service

   -API for wattrical.php feeds (for iphone)
      dtd , url map

   -Excpetion Proof: ReadTEDService: output to log
  File "ReadTEDService.py", line 88, in ?
    (stamp, watts,volts) = getTimeWattsAndVoltsFromTedService()
  File "ReadTEDService.py", line 28, in getTimeWattsAndVoltsFromTedService
    usock = urllib.urlopen(TED_DASHBOARDDATA_URL)
  IOError: [Errno socket error] (-2, 'Name or service not known')
     

-=-= Objective (mid):
  -Python daemon summarizes 'second' data into:
     tensec,minute,tenminute,halfhour,hour,day,month summary tables
     -possibly have accumulation table for mainting averaging state


  -Alternative feed xml format: GData
  -GAppEngine repository (mirrors local daemon data (through synch/push))
  -Groovy repository (ibid)
  -GoogleDocs Spreadsheet repository

  -Objective-C binding for GData on iPhone
    
-=-= Inventory:
Bash cron:
  doMirror:
    copy cifs mounted ted directory's TED.db sqlite db
      requires:  mount -t cifs //aria/ted /ted
    compress and archive as per usual.
    installed as cron for daniel:
00 * * * *    cd /archive/mirror/ted; ./doMirror >>tedmirror.log 2>&1

Python
 Incremental.py: will be renamed as Pump
     use --all or 
         --secs,--minutes,--hours,--days
         --start  [--stop]
     sqlite.teddb > mysql text out.
          add params --days X, --hours Y, etc

ReadTEDService.py
   Reads and prints ted: watt, volt : and current client-time
   added --duration and --forever params
   added a precise 1 second timing loop

Summarize.py:  (renamed from hierTed.py
  calculates summary tables: watt_day,watt_hour,watt_minute,watt_tensec.


Python GDATA:
  DON'T FORGET 
  export PYTHONPATH=~/python/lib/python/;
  showGDATA.py: List SpreadSheet, WorkSheet, Data
    python showGDATA.py --user daniel.lauzon --pw BLABLA
   or (for GDATA-TED Spreadseet/Worksheet-1
    python showGDATA.py --user daniel.lauzon --pw BLABLA --key pEzZl0NxQ-0gFzvkp3oJsew --sheet od6

  appendToGDATA.py: insert watt data into GDATA-TED Spreadsheet
    python appendToGDATA.py --user=daniel.lauzon --pw=BLABLA --watt=125
    python appendToGDATA.py --user daniel.lauzon --pw BLABLA --watt 126 --stamp '2008-11-16 23:34:55'

Java
 WinTime.java:
    Time Experiments to convert TED sqlite time format to java



















