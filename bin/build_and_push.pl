#!/usr/bin/perl

use strict;
use Getopt::Long;

my $aaargs = join(" ", @ARGV);
my $debug;
my $date;
my $result = GetOptions ( "d|debug+"  => \$debug,
                          "t|date=s"  => \$date);

if ( $debug ) {
    print "starting build and parse\n";
}

my $cmd = "trickle -s -u 200 /usr/local/cam/bin/build_time_lapse.pl $aaargs";
my $ret = `$cmd`;
my $exit_code = $?;
if ( $exit_code != 0 ) {
    print "exit: ", $exit_code, "\nret: ", $ret, "\n";
    exit(1);
}
if ( $debug ) {
    print $ret;
    print "exit code from build_time_lapse.pl: ", $exit_code, "\n";
    #print $ret;
    print "ending build and parse\n";
}
exit($exit_code);
