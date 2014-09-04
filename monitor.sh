#!/usr/bin/env bash
#simulate docker env linking for cantor's host mysql instance
MYSQL_PORT_3306_TCP_ADDR='172.17.42.1'
MYSQL_PORT_3306_TCP_PORT='3306'
MYSQL_ENV_MYSQL_DATABASE='ted'
while true; do   
done
while true; do
  for i in watt_day watt_hour watt_minute watt_tensec watt ; do
    echo `mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" $MYSQL_ENV_MYSQL_DATABASE -N -B -e "select now(),'--',stamp,watt from $i order by stamp desc limit 1"` $i;
  done;
  sleep 9; 
  echo;
done