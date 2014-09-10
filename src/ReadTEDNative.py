# Modified version of ted.py
#
# The most recent version of this module can be obtained at:
#   http://svn.navi.cx/misc/trunk/python/ted.py
#
# Copyright (c) 2008 Micah Dowty <micah@navi.cx>
# run as
#  while true; do echo `date` Restarted ReadTEDNative | tee -a TEDNative.log; python ReadTEDNative.py --forever --device /dev/ttyUSB0; sleep 1; done
#
#

import sys
import string
import math
import getopt
from scalr import logInfo,logWarn,logError
import datetime
import time
import MySQLdb
########################### START of ted.py Stuff

import serial
import binascii
import struct

# Special bytes

PKT_REQUEST = "\xAA"
ESCAPE      = "\x10"
PKT_BEGIN   = "\x04"
PKT_END     = "\x03"

class ProtocolError(Exception):
    pass


class TED(object):
    def __init__(self, device):
        self.port = serial.Serial(device, 19200, timeout=0)
        self.escape_flag = False

        # None indicates that the packet buffer is invalid:
        # we are not receiving any valid packet at the moment.
        self.packet_buffer = None

    def poll(self):
        """Request a packet from the RDU, and flush the operating
           system's receive buffer. Any complete packets we've
           received will be decoded. Returns a list of Packet
           instances.

           Raises ProtocolError if we see anything from the RDU that
           we don't expect.
           """

        # Request a packet. The RDU will ignore this request if no
        # data is available, and there doesn't seem to be any harm in
        # sending the request more frequently than once per second.
        self.port.write(PKT_REQUEST)

        return self.decode(self.port.read(4096))

    def decode(self, raw):
        """Decode some raw data from the RDU. Updates internal
           state, and returns a list of any valid Packet() instances
           we were able to extract from the raw data stream.
           """

        packets = []

        # The raw data from the RDU is framed and escaped. The byte
        # 0x10 is the escape byte: It takes on different meanings,
        # depending on the byte that follows it. These are the
        # escape sequence I know about:
        #
        #    10 10: Encodes a literal 0x10 byte.
        #    10 04: Beginning of packet
        #    10 03: End of packet
        #
        # This code illustrates the most straightforward way to
        # decode the packets. It's best in a low-level language like C
        # or Assembly. In Python we'd get better performance by using
        # string operations like split() or replace()- but that would
        # make this code much harder to understand.

        for byte in raw:
            if self.escape_flag:
                self.escape_flag = False
                if byte == ESCAPE:
                    if self.packet_buffer is not None:
                        self.packet_buffer += ESCAPE
                elif byte == PKT_BEGIN:
                    self.packet_buffer = ''
                elif byte == PKT_END:
                    if self.packet_buffer is not None:
                        packets.append(Packet(self.packet_buffer))
                        self.packet_buffer = None
                else:
                    raise ProtocolError("Unknown escape byte %r" % byte)

            elif byte == ESCAPE:
                self.escape_flag = True
            elif self.packet_buffer is not None:
                self.packet_buffer += byte

        return packets


class Packet(object):
    """Decoder for TED packets. We use a lookup table to find individual
       fields in the packet, convert them using the 'struct' module,
       and scale them. The results are available in the 'fields'
       dictionary, or as attributes of this object.
       """
    
    # We only support one packet length. Any other is a protocol error.
    _protocol_len = 278

    _protocol_table = (
        # TODO: Fill in the rest of this table.
        #
        # It needs verification on my firmware version, but so far the
        # offsets in David Satterfield's code match mine. Since his
        # code does not handle packet framing, his offsets are 2 bytes
        # higher than mine. These offsets start counting at the
        # beginning of the packet body. Packet start and packet end
        # codes are omitted.

        # Offset,  name,             fmt,     scale
        (82,       'kw_rate',        "<H",    0.0001),
        (108,      'house_code',     "<B",    1),
        (247,      'kw',             "<H",    0.01),
        (251,      'volts',          "<H",    0.1),
        )

    def __init__(self, data):
        self.data = data
        self.fields = {}
        if len(data) != self._protocol_len:
            raise ProtocolError("Unsupported packet length %r" % len(data))

        for offset, name, fmt, scale in self._protocol_table:
            size = struct.calcsize(fmt)
            field = data[offset:offset+size]
            value = struct.unpack(fmt, field)[0] * scale

            setattr(self, name, value)
            self.fields[name] = value



########################### END of ted.py Stuff

def tableExists(tablename):
        exists = getScalar("show tables like '%s'" % tablename) is not None
        return exists
    
def checkOrCreateTable(tablename):
        exists = tableExists(tablename)
        if exists:
                logInfo(" Table %s is OK" % (tablename))
                return

        # I removed table dropping code (safety)

        ddl = """CREATE TABLE %s (
stamp datetime NOT NULL default '1970-01-01 00:00:00',
watt int(11) NOT NULL default '0',
PRIMARY KEY %sByStamp (stamp)
);
""" % (tablename,tablename)
        cursor.execute(ddl)
        logInfo(" Created %s table" % (tablename))

def getScalar(sql):
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None: return None
    return row[0]

def getGMTTimeWattsAndVoltsFromTedNative(packet):
	ISO_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
	#isodatestr = datetime.datetime.now().strftime(ISO_DATE_FORMAT) 
	isodatestr = time.strftime(ISO_DATE_FORMAT,time.gmtime(time.time())) 

        #print
        #print "%d byte packet: %r" % (len(packet.data), binascii.b2a_hex(packet.data))
        #print
        #for name, value in packet.fields.items():
        #        print "%s = %s" % (name, value)

        kWattStr = packet.fields["kw"]
        voltStr = packet.fields["volts"]
        #print "%s\t%s\t%s" % (isodatestr, kWattStr, voltStr) 
        watts = string.atof(kWattStr)*1000.0
        volts  = string.atof(voltStr)
        return (isodatestr , watts,volts)

if __name__ == "__main__":
        usage = 'python %s  ( --duration <secs> | --forever) [--device /dev/ttyXXXX]' % sys.argv[0]
        conn = MySQLdb.connect (host = "172.17.42.1", # host = "127.0.0.1",
                                user = "aviso",
                                passwd = "",
                                db = "ted")
        cursor = conn.cursor ()
        
        # tablenames: watt, ted_native
        # insert into BOTH tables
        tablenames=['watt','ted_native']

        for tablename in tablenames:
                checkOrCreateTable(tablename);


        # parse command line options
        try:
                opts, args = getopt.getopt(sys.argv[1:], "", ["duration=", "forever", "device="])
        except getopt.error, msg:
                logError('error msg: %s' % msg)
                logError(usage)
                sys.exit(2)

        # default value (forever-> duration=-1
        duration=1
        #default value /dev/ttyUSB0
        device = "/dev/ttyUSB0"

        for o, a in opts:
                if o == "--duration":
                        duration = string.atol(a)
                elif o == "--forever":
                        duration = -1
                elif o == "--device":
                        device = a

        print "duration is %d" % duration
        start = time.time()

        print "Instantiating TED object using device: %s" % device
        tedObject = TED(device)

        
        while True:
                datetimenow = datetime.datetime.now()
                now=time.time()
                if duration>0 and (now-start)>duration:
                        break

                for packet in tedObject.poll():
                        (stamp, watts,volts) = getGMTTimeWattsAndVoltsFromTedNative(packet)
                        print "%s --- %s\t%d\t%.1f" % (datetimenow,stamp, watts, volts) 

                        # insert into BOTH tables
                        for tablename in tablenames:
                                sql = "INSERT IGNORE INTO %s (stamp, watt) VALUES ('%s', '%d')" % (
                                        tablename,stamp,watts)
                                #print " exe: %s" % sql
                                cursor.execute(sql)

                now=time.time()
                if duration>0 and (now-start)>duration:
                        break
                # sleep to hit the second on the nose:
                (frac,dummy) = math.modf(now)
                desiredFractionalOffset = .1
                delay = 1-frac + desiredFractionalOffset
                time.sleep(delay)

print "Done; lasted %f" % (time.time()-start)


cursor.close ()
conn.close ()

