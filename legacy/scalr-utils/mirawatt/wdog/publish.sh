#!/bin/bash                                                                                             
# This pushes the summrized feed into the cloud

USERNAME="jean"
FEEDFILE="/mirawatt/feeds.xml"

# -s: silent  : disble progress meter and errors
# -S : show error, when used with -s, re-enables error logging

while true; do  
    curl -s -S -m 30 -F "owner=${USERNAME}" -F "content=@${FEEDFILE};type=text/xml"  http://imetrical.appspot.com/post; 
    sleep 60;
done
