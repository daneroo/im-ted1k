#!/bin/bash                                                                                                           
# This program tests if we can test for emtpy lines, to limit captureCC.sh' output

stampline() {
    echo read : "|$1| ${#1}"
    if [ "${#1}" -gt "0" ]; then
	echo `date +%Y-%m-%dT%H:%M:%S%z` $1;
    else
	echo "  This line was EMPTY -- ||=0"
    fi
}

while true; do
    while read -t 10 line; do
	stampline "$line"
    done
done
