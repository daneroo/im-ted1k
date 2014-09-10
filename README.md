# iMetrical-Energy TED1K

As I rebuild cantor, and wanting to preserve data capture, I decided to consolidate som previous code. We are going to [Docker](https://www.docker.com/)ize the components.

Previous Notes in Evernote for now. 

## Operation
on `cantor`:

      cd im-ted1k
      # build (move `./data/` out of way ?)
      fig build
      # run
      fig up -d

## TODO
* move data directory out ( into /archive/production ?)
* tone console logging waaaaay down
* finish verify/dump add to fig
* install [nsenter](https://github.com/jpetazzo/nsenter) on `cantor`
* python refactoring (modules)
* second publish to Firebase
* figure out restart strategy for capture
* include ReadTEDNative.py -> CaptureTED1k.py in fig
    * Note move to https://github.com/scanlime/navi-misc/blob/master/python/ted.py

[Editing files in a container (Samba)](https://groups.google.com/forum/#!topic/docker-user/UubYr7b4fMI)
### Done
* mv src to subfolder
* Cleanup unneeded src
* Fix config for MYSQL: Summarize, monitor, publish
    * use 172.17.42.1:3306/ted (implicitly root@container)
    * works on cantor:guests because of GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION
    * works on boot2docker guests if mysql's port 3306 is redirected
    * default to aviso@172.17.42.1/ted for cantor:host

## Components

* Capture
* Summarize
* Publish
* Monitor

## Docker

* Use of fig : install 0.5.2 as root on cantor
* (directory layout)

Run a single command, and attach data volume, e.g.:

    docker run -it --rm  -v $(pwd)/data:/data imted1k_monitor bash
    time python verify.py

## Legacy consolidation
Have gathered the code I'm obsoleting into the legacy folder for convenient reference.

* Old startup instructions for `cantor`
* TEDNative.log
* snookr-gcode-svn/green/scalr-utils/
    * php - feeds.php - getJSON.php
    * CurrentCost|mirawatt (SheevaPlug code)
* imetrical-couch (not yet moved ?)

# Dev notes
Run a mysql (OSX/boot2docker)

* Restore Summaries, on init (dirac) 2231 days since 2008-07-30 as of 2014-08-06

    fig run --rm summarize bash
    time python Summarize.py --days 2500 --duration 1


* Run the database on dirac:
Databse port is exposed so all containers so we can talk to 172.17.42.1:3306/ted without linking.

We can also currently talk to (192.168.5.132) cantor.imetrical.com:3306/ted from dirac...

Pick an image: [dockerfile/mysql](https://registry.hub.docker.com/u/dockerfile/mysql/) (dropped [centurylink/mysql](https://registry.hub.docker.com/u/centurylink/mysql/))


    # run the database: the port is exposed
    docker run -d --name mysql -p 3306:3306 dockerfile/mysql

    # copy some files over (OSX)
    scp -i ~/.ssh/id_boot2docker ~/Downloads/TED1K-backup/ted.watt.20140806.0016.sql.bz2 docker@$(/usr/local/bin/boot2docker ip 2>/dev/null):~

    #restore a database (binding /home/docker in vm to /backup)
    docker run -it --rm --link mysql:mysql -v /home/docker:/backup dockerfile/mysql bash
    # or run the clien directly
    docker run -it --rm --link mysql:mysql -v /home/docker:/backup dockerfile/mysql bash -c 'mysql -h $MYSQL_PORT_3306_TCP_ADDR'

    # create the database (now that we are usin docerfile/mysql)
    mysqladmin -h $MYSQL_PORT_3306_TCP_ADDR create ted
    # restore took 12 minutes
    time bzcat /backup/ted.watt.20140806.0016.sql.bz2 |mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" ted

    mysqladmin -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" proc

    #run a mysql client
    docker run -it --rm --link mysql:mysql dockerfile/mysql sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" ted'


