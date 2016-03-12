#!/usr/bin/env bash
#simulate docker env linking for cantor's host mysql instance
# now using the docker-compose name: teddb
MYSQL_PORT_3306_TCP_ADDR='teddb'
MYSQL_PORT_3306_TCP_PORT='3306'
MYSQL_ENV_MYSQL_DATABASE='ted'
LOOP_PERIOD_SECONDS=30

unset sleepPID
trap 'echo TERMinated; kill $sleepPID; exit' TERM

while true; do
  date  +"  %Y-%m-%d %H:%M:%S     %Z publish (localtime)"
  php feeds.php >tmp.xml
  curl -s -m 30 -F "owner=daniel" -F "content=@tmp.xml;type=text/xml"  http://imetrical.appspot.com/post
  sleep ${LOOP_PERIOD_SECONDS} & sleepPID=$!; wait
  echo;
done
