#!/usr/bin/perl
open(FILE, ">$ARGV[0]") || die " Can't open $ARGV[0]: $!\n";
select FILE; $| = 1;
select STDOUT; $| = 1;

while (1) {
    $rv = sysread(STDIN, $c, 1);
    if ( defined($rv)) {
	if ( $rv ) {
	    print STDOUT $c;
	    print FILE $c;
	}
	else { exit(0); }
    }
    else { die "Read failed: !?\n"; }
}
