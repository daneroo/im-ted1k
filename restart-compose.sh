#!/usr/bin/env bash

# should be cron'd with
# 9 */4 * * *  cd /home/daniel/im-ted1k; ./restart-compose.sh >>restart-compose.log 2>&1
date -u +'%Y-%m-%dT%H:%M:%SZ Restarting docker-compose (up -d)'

/usr/local/bin/docker-compose up -d

date -u +'%Y-%m-%dT%H:%M:%SZ Done'
