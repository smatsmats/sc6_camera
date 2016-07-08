#!/usr/bin/perl

use DateTime;
use Time::ParseDate;
use Getopt::Long;

my $rut = "/home/willey/sc6_camera/data/cam_images";
my $run_flag = "/tmp/redo_run_flag";
my $dryrun;
my $date;
my $debug;

my $start = DateTime->new( year => 2015,  month => 2, day => 16,
                           hour  => 12, minute => 0, second => 0,
                           time_zone => 'America/Los_Angeles' );

my $result = GetOptions (  "n|dry-run" => \$dryrun,
                        "h|help"  => \&usage,
                        "t|date=s"  => \$date,
                        "d|debug+"  => \$debug);

my ($seconds, $error) = parsedate($date);
if ( not $seconds ) {
    print "Error can't parse date: $date : $error\n";
    exit;
}
else {
    print $seconds, "\n" if ( $debug );
    $start = DateTime->from_epoch(  epoch => $seconds, time_zone => 'America/Los_Angeles');
}

while () {
    print "time is: ", scalar localtime(), "\n";
    if ( ! -e $run_flag ) {
        print "missing run flag: $run_flag\n";
        exit;
    }
    my $dd = $rut . "/" . $start->strftime('%Y%m%d');
    print $start, "\t", $start->strftime('%Y%m%d'), "\t", $dd, "\n";
    if ( ! -e $dd ) {
        print "$dd doesn't exist, quitting\n";
        exit;
    }
    print `./build_time_lapse.pl --date $start --debug`;
    $start->add( days => -1 );
}
#$start->add( days => -1 );
#my $now = DateTime->now();
#my $duration = $now->delta_days( $epoch );
#print $duration->delta_days(), "\n";

exit;

opendir my $dh, $rut or die "Could not open '$rut' for reading: $!\n";
while (my $thing = readdir $dh) {

    if ($thing eq '.' or $thing eq '..') {
        next;
    }
    if ($thing eq 'on_data' ) {
        next;
    }
    my $dd = $rut . "/" . $thing;
    my $public = $dd . "/public";
    my $orig = $dd . "/orig";
#    print $dd, "\n";
    if ( ! -e $public ) { 
        print "going to ln -s $orig $public\n";
        symlink($orig, $public) or die "Can't symlink($orig, $public): $!\n";
    }
    
}

