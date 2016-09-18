#!/usr/bin/env bash
#simulate docker env linking for cantor's host mysql instance
# now using the docker-compose name: teddb
MYSQL_PORT_3306_TCP_ADDR='teddb'
MYSQL_PORT_3306_TCP_PORT='3306'
MYSQL_ENV_MYSQL_DATABASE='ted'
LOOP_PERIOD_SECONDS=60

unset sleepPID
trap 'echo TERMinated; kill $sleepPID; exit' TERM

MYCMD="mysql -h${MYSQL_PORT_3306_TCP_ADDR} -P${MYSQL_PORT_3306_TCP_PORT} $MYSQL_ENV_MYSQL_DATABASE"
while true; do
  for i in watt_day watt_hour watt_minute watt_tensec watt ; do
    STMP_WTT=`${MYCMD} -N -B -e "select watt,watt*24/1000,concat(stamp,' UTC') from $i order by stamp desc limit 1"`
    printf "  latest %12s:  %s\n"  $i "${STMP_WTT}";
  done;
  printf "  NOW %53s UTC\n" "`date -u +'%Y-%m-%d %H:%M:%S'`"
  printf "  NOW %57s\n" "`date +'%Y-%m-%d %H:%M:%S %Z'`"
  
  # Per day counts
  ${MYCMD} -e 'select left(stamp,10) as perday,count(*) from watt where stamp>DATE_SUB(NOW(), INTERVAL 7 day) group by perday';
  # Per hour counts
  ${MYCMD} -e 'select concat(left(stamp,13),":00") as perhour,count(*) from watt where stamp>DATE_SUB(NOW(), INTERVAL 12 hour) group by perhour';

  sleep ${LOOP_PERIOD_SECONDS} & sleepPID=$!; wait
done
