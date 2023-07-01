# iMetrical-Energy TED1K

- _2023-06-30 darwin: modified for `docker compose` and debian stretch archive_
- _2019-08-21 euler died, move to darwin: go modules, pinned base image to python2.7.15 and use php7_
- _2018-04-04 Moved to go (vgo) based capture_
- _2016-09-17 Adjusted monitoring and docker-compose v2_
- _2016-03-12 Moving back to x86 (euler, old cantor/goedel)_
- _We lost data from ( 2016-02-14 21:24:21 , 2016-03-12 06:35:35 ]_

## TODO

- Remove dependencies on debian stretch/mysql5.7/php
- Move to php7 (`feeds.php`)
- Remove python or move to `python3`
- Merge with `git@github.com:daneroo/go-ted1k.git` in `~/Code/Go/src/github.com/daneroo/go-ted1k`
- ~~Older below~~
- Restore (at least 2016-.. into database frm last cantor snapshot (and other all day tables?))
- Should run as another user (mysql creds?)
- Ability to move volume easily; i.e. another disk
- Will do incremental dumps to .jsonl.gz files
- Will eventually write to .jsonl file concurrently
- Will eventually port to go and consolidate parts
- Makefile and Dockerfile(s) in go directory

## Counts

- mysql
  | Year | Min Date | Max Date | Count |
  | ---- | ------------------- | ------------------- | -------- |
  | 2007 | 2007-08-28 00:02:18 | 2007-08-28 20:56:22 | 75026 |
  | 2016 | 2016-03-12 06:35:35 | 2016-12-31 23:59:59 | 24957526 |
  | 2017 | 2017-01-01 00:00:00 | 2017-12-31 23:59:59 | 29321718 |
  | 2018 | 2018-01-01 00:00:00 | 2018-12-31 23:59:59 | 30758853 |
  | 2019 | 2019-01-01 00:00:00 | 2019-12-31 23:59:59 | 30639015 |
  | 2020 | 2020-01-01 00:00:00 | 2020-12-31 23:59:59 | 31478859 |
  | 2021 | 2021-01-01 00:00:00 | 2021-12-31 23:59:59 | 31401094 |
  | 2022 | 2022-01-01 00:00:00 | 2022-12-31 23:59:59 | 31425006 |
  | 2023 | 2023-01-01 00:00:00 | 2023-07-01 02:56:04 | 15336517 |

- timescale
  | Year | Min Date (GMT) | Max Date (GMT) | Count |
  | ---- | ------------------- | ------------------- | -------- |
  | 2022 | 2022-12-29 21:56:41 | 2022-12-31 23:59:59 | 180131 |
  | 2023 | 2023-01-01 00:00:00 | 2023-07-01 03:03:24 | 15424260 |

## 2023-06-30 debian stretch end-of-life

Changed the Debian sources to use the archive URLs for stretch version, and remove security and stretch-updates

Testing new build from M2

```bash
docker buildx build --platform linux/amd64 -t py2-7-15-strech-archive .
```

## 2019-08-21 euler died, move to darwin

- python image fails to build
  - python 2.7
- replace `vgo` with `go modules`

### Restore database

```bash
# not -it but -i
# on darwin 2023-06-30: took ~47m
time cat ted.watt.20230630.2142Z.sql |docker exec -i im-ted1k-teddb-1 mysql ted
time bzcat ted.watt.20190818.0554Z.sql.bz2 | docker exec -i im-ted1k-teddb-1 mysql ted

docker exec -it im-ted1k-teddb-1 bash

mysqladmin proc
mysql ted -e 'select min(stamp),max(stamp) from watt;'
mysql ted -e 'select * from watt where stamp>DATE_SUB(NOW(), INTERVAL 1 HOUR)'
```

### Re-Summarize

- Restore Summaries, after restore (darwin) 5448 days since 2008-07-30 as of 2023-06-30

```bash
docker exec -it im-ted1k-summarize-1 bash
time python summarize.py --days 6000 --duration 1
```

## Backups

We backup ted.watt table, compress and send to dirac:/archive/mirror/ted for Backblaze

_Note:_ If your tables are InnoDB, using the --single-transaction option will start a transaction before running. Rather than locking the entire database, this will let mysqldump retrieve the binlog position without locking the tables at all.

```bash
# on darwin - in docker ~ 13min - we shouldn't lock anymore!
time docker exec -it im-ted1k-teddb-1 mysqldump --single-transaction --opt ted watt >ted.watt.`date -u +%Y%m%d.%H%MZ`.sql
# LEGACY: previously (on euler) - in docker: ~4m33s
time docker exec -it im-ted1k-teddb-1 mysqldump --opt ted watt >ted.watt.`date -u +%Y%m%d.%H%MZ`.sql
```

Now compress and archive it: ~12m13s (data from 2016ish to 2023-06-30)

```bash
time bzip2 ted.watt.*.sql
scp -p ted.watt.*.sql.bz2 galois:/Volumes/Space/archive/mirror/ted
```

## To run

```bash
docker compose build --pull
docker compose up -d
```

## 2016-02-20 moving to raspberry pi

Other/Previous [Notes in Evernote](https://www.evernote.com/shard/s60/nl/1773032759/ae1b9921-7e85-4b75-a21b-86be7d524295/).

## Operation

on `pi@pi`:

```bash
cd Code/iMetrical/im-ted1k
# build (move `./data/` out of way ?)
docker compose build
# run
docker compose up -d
```

-Minimal changes, mysql will also be in docker
-add ssh key pi@pi for github
-Dockerfile from hypriot/rpi-python
-add teddb mysql server and config in `docker compose`
-so teddb is now the hostname instead of 172.17.0.1
-mysql data volume in ./data/mysql; later in /data/ted/mysql

## Rebuild cantor

As I rebuild cantor, and wanting to preserve data capture, I decided to consolidate som previous code. We are going to [Docker](https://www.docker.com/)ize all the things.

### Notes

- HOST IP changed from 172.17.42.1 to 172.17.0.1
- The database is still run on the HOST: 172.17.42.1:3306/ted
- Cron restarts the containers every 4 hours

## TODO2

- finish verify/dump add to compose
- ttyusb discovery : instead of `/hostdev/ttyUSB0`
- move data directory out ( into /archive/production ?)
- tone console logging waaaaay down
- SIGTERM handling for Summary and shell [scripts monitor and publish](http://lists.gnu.org/archive/html/help-bash/2013-04/msg00062.html)
- version specifier in requirements.txt (use ~= x.y instead of == x.y.z)
- python refactoring (modules)

[Editing files in a container (Samba)](https://groups.google.com/forum/#!topic/docker-user/UubYr7b4fMI)

### Done

- SIGTERM Handler for capture
- mv src to subfolder
- Cleanup unneeded src
- Fix config for MYSQL: Summarize, monitor, publish
  - use 172.17.42.1:3306/ted (implicitly root@container)
  - works on cantor:guests because of GRANT ALL PRIVILEGES ON _._ TO 'root'@'%' WITH GRANT OPTION
  - works on boot2docker guests if mysql's port 3306 is redirected
  - default to aviso@172.17.42.1/ted for cantor:host
- Include ReadTEDNative.py -> capture.py in docker-compose
  - Note move to <https://github.com/scanlime/navi-misc/blob/master/python/ted.py>

## Components

- Capture
- Summarize
- Publish
- Monitor

## Docker

- Use of docker-compose (previously fig)
- (directory layout)

### Single command (verify/dump)

Run a single command, and attach data volume, e.g.:

```bash
docker run -it --rm  -v $(pwd)/data:/data im-ted1k-monitor bash
time python verify.py
```

## Legacy consolidation

Have gathered the code I'm obsoleting into the legacy folder for convenient reference.

- Old startup instructions for `cantor`
- TEDNative.log
- snookr-gcode-svn/green/scalr-utils/
  - php - feeds.php - getJSON.php
  - CurrentCost|mirawatt (SheevaPlug code)
- imetrical-couch (not yet moved ?)

## Dev notes

Run a mysql (OSX/boot2docker)

- Restore Summaries, on init (dirac) 2231 days since 2008-07-30 as of 2014-08-06

```bash
fig run --rm summarize bash
time python Summarize.py --days 2500 --duration 1
```

- Run the database on dirac:
  Databse port is exposed so all containers so we can talk to 172.17.42.1:3306/ted without linking.

We can also currently talk to (192.168.5.132) cantor.imetrical.com:3306/ted from dirac...

Pick an image: [dockerfile/mysql](https://registry.hub.docker.com/u/dockerfile/mysql/) (dropped [centurylink/mysql](https://registry.hub.docker.com/u/centurylink/mysql/))

```bash
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
```
