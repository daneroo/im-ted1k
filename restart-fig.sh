#!/usr/bin/env bash

# should be cron'd with
# 9 */4 * * *  cd /home/daniel/im-ted1k; ./restart-fig.sh >>restart-fig.log 2>&1
date -u +'%Y-%m-%dT%H:%M:%SZ Restarting fig (up -d)'

/usr/local/bin/fig up -d

date -u +'%Y-%m-%dT%H:%M:%SZ Done'
