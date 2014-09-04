# iMetrical-Energy TED1K

As I rebuild cantor, and wanting to preserve data capture, I decided to consolidate som previous code. We are going to [Docker](https://www.docker.com/)ize the components.

Notes in Evernote for now. 

[Editing files in a container (Samba)](https://groups.google.com/forum/#!topic/docker-user/UubYr7b4fMI)

## Components

* Capture
* Summarize
* Publish
* Monitor

## Docker

* Use of fig : install 0.5.2 as root on cantor
* (directory layout)

## Legacy consolidation
Have gathered the code I'm obsoleting into the legacy folder for convenient reference.

* Old startup instructions for `cantor`
* TEDNative.log
* snookr-gcode-svn/green/scalr-utils/
    * php - feeds.php - getJSON.php
    * CurrentCost|mirawatt (SheevaPlug code)
* imetrical-couch

# Dev notes
Run a mysql (OSX/boot2docker)

* build my python env
    
    docker build -t daneroo/python-ted1k .
    docker run -it --rm --link mysql-ted:mysql daneroo/python-ted1k


* pick an image: mysql, centurylink/mysql, dockerfile/mysql ?


    # run the database
    docker run --name mysql-ted -d -p 3306:3306 -e MYSQL_DATABASE=ted centurylink/mysql

    # copy some files over (OSX)
    scp -i ~/.ssh/id_boot2docker backup/ted.watt.20140806.0016.sql.bz2 docker@$(/usr/local/bin/boot2docker ip 2>/dev/null):~

    #restore a database (binding /home/docker in vm to /backup)
    docker run -it --rm --link mysql-ted:mysql -v /home/docker:/backup centurylink/mysql bash

    # took 12 minutes
    time bzcat /backup/ted.watt.20140806.0016.sql.bz2 |mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" $MYSQL_ENV_MYSQL_DATABASE

    mysqladmin -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" proc

    #run a mysql client
    docker run -it --rm --link mysql-ted:mysql centurylink/mysql sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" $MYSQL_ENV_MYSQL_DATABASE'


