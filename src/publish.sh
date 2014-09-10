#!/usr/bin/env bash
#simulate docker env linking for cantor's host mysql instance
MYSQL_PORT_3306_TCP_ADDR='172.17.42.1'
MYSQL_PORT_3306_TCP_PORT='3306'
MYSQL_ENV_MYSQL_DATABASE='ted'

while true; do
  date  +"  %Y-%m-%d %H:%M:%S     %Z publish (localtime)"
  php feeds.php >tmp.xml
  curl -s -m 30 -F "owner=daniel" -F "content=@tmp.xml;type=text/xml"  http://imetrical.appspot.com/post
  sleep 10
  echo;
done
