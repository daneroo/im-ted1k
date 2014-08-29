#!/bin/bash                                                                                             
# This pushes the summrized feed into the cloud

while true; do  
    cat /mirawatt/logs/CC2*log | /usr/bin/python -OO /mirawatt/wdog/summarizeCC.py
    sleep 60;
done
