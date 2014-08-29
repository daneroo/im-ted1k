#!/bin/bash                                                                                             
# This program reads a usb serial port and 
# writes all ouput to timestampled logfiles
# each output line is also prefixed with a timestamp

# check parameter here: add outputdir ?
# usage
#  ./serialStamp.sh /dev/ttyUSB1 57600 CC1
#  ./serialStamp.sh /dev/ttyUSB0 38400 AZ2

# this is the name of the current logrotated file
#OUTPUTSTAMPFORMAT="%Y%m%dT%H%M00%z" # by Minute
#OUTPUTSTAMPFORMAT="%Y%m%dT%H0000%z" # by Hour
OUTPUTSTAMPFORMAT="%Y%m%dT000000%z" # by Day
OUTPUTFILE="DEVICE-2001-02-03T040506+0400.log"

# this should be the /dev/ttyUSBx
#INPUTTTY="../CC2-20090701T225213-0400.log"
INPUTTTY=${1:-"/dev/ttyUSB-NOTEXIST"}
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
    echo `date +%Y-%m-%dT%H:%M:%S%z` $1; 
}

rotatelog() {
    STAMP=`date +${OUTPUTSTAMPFORMAT}`
    OUTPUTFILE="${DEVICEALIAS}-${STAMP}.log"
    # if file already exists, simply return
    if [ -w ${OUTPUTFILE} ]; then
	#echo file ${OUTPUTFILE} already exists and is writeable
	return;
    fi
    # touch the file make sure it exists and is writeable
    touch "${OUTPUTFILE}"
    if [ -w ${OUTPUTFILE} ]; then
	#echo Creating new log file ${OUTPUTFILE}
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
while true; do
    rotatelog
    # inner loop -- use -u fd, to read from a fd instead.
    while read -t ${READTIMEOUT} -u 3 line; do 
	stampline "$line"
    done >>"$OUTPUTFILE"

done
