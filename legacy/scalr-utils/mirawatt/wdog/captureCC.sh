#!/bin/bash                                                                                             
# This program reads a usb serial port and 
# writes all ouput to timestampled logfiles
# each output line is also prefixed with a timestamp

# check parameter here: add outputlogdir ?
# usage 
#  ./captureCC.sh /dev/ttyUSB 57600 CC1

# Log output files Directory
#OUTPUTLOGDIR="/mirawatt/logs"
OUTPUTLOGDIR="/home/daniel/netbeans-workspace/green/scalr-utils/mirawatt"
# this is the name of the current logrotated file
#OUTPUTSTAMPFORMAT="%Y%m%dT%H%M00%z" # by Minute
#OUTPUTSTAMPFORMAT="%Y%m%dT%H0000%z" # by Hour
OUTPUTSTAMPFORMAT="%Y%m%dT000000%z" # by Day
# Determines stdout MARK frequency
MARKSTAMPFORMAT="%Y%m%dT%H%M00%z" # by Minute

# this should be the /dev/ttyUSB\* pattern
INPUTTTY_PATTERN=${1:-"/dev/ttyUSB"}
INPUTTTY_DIR=`dirname ${INPUTTTY_PATTERN}`
INPUTTTY_PREFIX=`basename ${INPUTTTY_PATTERN}`
INPUTTTY=`find ${INPUTTTY_DIR} -maxdepth 1 -name ${INPUTTTY_PREFIX}\* -type c`

# use FileDescriptor 3 for input tty: (output too for Aztech)
exec 3<> "${INPUTTTY}"

TTYSPEED=${2:-"57600"}
DEVICEALIAS=${3:-"DEVICE"}
# this is the read timeout: in seconds: has  no  effect if read is not reading input from  the terminal or a pipe
READTIMEOUT=2



# - first set its params (speed)
# e.g. 
#   read:  stty -F /dev/ttyUSB1 speed
#   write: stty -F /dev/ttyUSB1 speed 57600
# check for non-zero return code: USB does not exist, perm denied...
# read each line
setupTTY(){
    echo Setting tty params for ${INPUTTTY}
    CURRENTSPEED=`stty -F ${INPUTTTY} speed`
    if [ $? -ne 0 ]; then
	echo Could not read tty params for ${INPUTTTY}
	exit 1
    fi
    echo " " Current Speed is: ${CURRENTSPEED}
    if [ "${CURRENTSPEED}" != "${TTYSPEED}" ]; then
	echo Setting new speed to ${TTYSPEED}
	NEWSPEED=`stty -F ${INPUTTTY} speed ${TTYSPEED}`
	if [ $? -ne 0 ]; then
	    echo Could not set tty speed to ${TTYSPEED} for ${INPUTTTY}
	    exit 1
	else
	    echo " " Speed was set to ${NEWSPEED} for ${INPUTTTY}
	fi
    else
	echo "Speed is alread OK"
    fi
}

# Notes
#  exit status : $?
#  open for read and write: [j]<>filename a.k.a. : exec 3<> /dev/ttyUSB1
#    read -n 4 <&3
#    echo -n . >&3
#  exec 4>&1                              # Save current "value" of stdout.


# this funcion wraps the line content (pased as argument
stampline() {
    if [ "${#1}" -gt "0" ]; then
	echo `date +%Y-%m-%dT%H:%M:%S%z` $1; 
#    else
#        echo "<!--  This line was EMPTY -- ||=0 -->"
    fi
}

rotatelog() {
    STAMP=`date +${OUTPUTSTAMPFORMAT}`
    mkdir -p "${OUTPUTLOGDIR}"
    OUTPUTFILE="${OUTPUTLOGDIR}/${DEVICEALIAS}-${STAMP}.log"
    # if file already exists, simply return
    if [ -w ${OUTPUTFILE} ]; then
	#echo file ${OUTPUTFILE} already exists and is writeable
	return;
    fi
    # touch the file make sure it exists and is writeable
    touch "${OUTPUTFILE}"
    if [ -w ${OUTPUTFILE} ]; then
	echo Creating new log file ${OUTPUTFILE}
	echo "<!-- `hostname`: `date +%Y-%m-%dT%H:%M:%S%z`: reading ${INPUTTTY} @ ${TTYSPEED}bps for device ${DEVICEALIAS} -->">>${OUTPUTFILE}
	return
    else
	# could not create outputfile: ERROR
	echo "Could Not Create Output File : ${OUTPUFILE}" >&2
	exit 1
    fi

}

#outer forever loop
setupTTY
echo DEBUGON >&3
MARKSTAMP='NOT-YET-SET'
LASTMARKSTAMP=${MARKSTAMP}
while true; do
    rotatelog
    # inner loop -- use -u fd, to read from a fd instead.
    while read -t ${READTIMEOUT} -u 3 line; do 
	stampline "$line"
	# only update the MARKSTAMP if there was output
	MARKSTAMP=`date +${MARKSTAMPFORMAT}`
    done >>"$OUTPUTFILE"
    # Mark the log every Minute: when MAARKSTAMP changes
    if [ "${MARKSTAMP}" != "${LASTMARKSTAMP}" ]; then
	echo "#MARK `hostname`: `date +%Y-%m-%dT%H:%M:%S%z`: reading ${INPUTTTY} @ ${TTYSPEED}bps for device ${DEVICEALIAS}"
    fi
    LASTMARKSTAMP=${MARKSTAMP}
done
