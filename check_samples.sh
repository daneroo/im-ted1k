#!/usr/bin/env bash

date -u +'%Y-%m-%dT%H:%M:%SZ Checking Samples'

run_query(){
  title=$1
  query=$2
  # echo $query
  echo '-=-=' $1 '=-=-'
  docker run --rm -it mysql mysql -h euler.imetrical.com ted -e "$query"
}

run_query 'Missing samples in last day' 'select count(*) as samples, 86400-count(*) as missing from watt where stamp>DATE_SUB(NOW(), INTERVAL 24 HOUR)'

# missing in day
run_query 'Missing in days of last week' 'select concat(substring(stamp,1,11),"00:00:00") as day, round(avg(watt),0), count(*) as samples,86400-count(*) as missing from watt where stamp>DATE_SUB(NOW(), INTERVAL 7 DAY) group by day having missing>0'
# missing in hour
run_query 'Missing in hours of last day' 'select concat(substring(stamp,1,14),"00:00") as hour, round(avg(watt),0), count(*) as samples,3600-count(*) as missing from watt where stamp>DATE_SUB(NOW(), INTERVAL 24 HOUR) group by hour having missing>0'
# missing in minute
run_query 'Missing in minutes of last day' 'select concat(substring(stamp,1,17),"00") as minute, round(avg(watt),0), count(*) as samples,60-count(*) as missing from watt where stamp>DATE_SUB(NOW(), INTERVAL 24 HOUR) group by minute having missing>0'