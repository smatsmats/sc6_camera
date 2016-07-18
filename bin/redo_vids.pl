#!/usr/bin/perl

use DateTime;
use Time::ParseDate;
use Getopt::Long;
use SC6::Cam::Config;
use Data::Dumper;
use strict;

my $rut = "/home/willey/sc6_camera/data/cam_images";
my $run_flag = "/tmp/redo_run_flag.yml";
my $dryrun;
my $date;
my $debug;
my $sleep_interval = (20 * 60); # how long to wait if we can't run a built 

my $start = DateTime->new( year => 2015,  month => 2, day => 16,
                           hour  => 12, minute => 0, second => 0,
                           time_zone => 'America/Los_Angeles' );

my $result = GetOptions (  "n|dry-run" => \$dryrun,
                        "h|help"  => \&usage,
                        "t|date=s"  => \$date,
                        "d|debug+"  => \$debug);

my $conf;
my $count = 0;
while () {
    print "time is: ", scalar localtime(), "\n";
    $conf = reread_conf();

    $date = $conf->{'StartDate'};
    my $counter = $conf->{'BailAfter'};
    if ($counter <= 0 ) {
        print "did as many as I'm going to do: $count\n";
        exit;
    }
    my ($seconds, $error) = parsedate($date);
    if ( not $seconds ) {
        print "Error can't parse date: $date : $error\n";
        exit;
    }
    else {
        print $seconds, "\n" if ( $debug );
        $start = DateTime->from_epoch(  epoch => $seconds, time_zone => 'America/Los_Angeles');
    }
    
    my $dd = $rut . "/" . $start->strftime('%Y%m%d');
    print $start, "\t", $start->strftime('%Y%m%d'), "\t", $dd;
    print " counter: ", $counter, "\n";
    if ( ! -e $dd ) {
        print "$dd doesn't exist, quitting\n";
        exit;
    }


    my $cmd = "./build_time_lapse.pl --date $start --debug";
    print $cmd, "\n";
    print `$cmd`;
    print "return code is $?\n";
    if ($? > 0) {
        print "fail from $cmd : $!\n";
        print "sleeping: $sleep_interval\n";
        sleep $sleep_interval;
    }
    else {
        # update the config and write it out
        $start->add( days => -1 );
        $conf->{'StartDate'} = $start->strftime('%m/%d/%Y');
    }
    $conf->{'BailAfter'} = $counter - 1;
    write_config();
    $count++;
}

sub reread_conf {
    if ( ! -e $run_flag ) {
        print "missing run flag: $run_flag\n";
        exit;
    }
    my $c = new SC6::Cam::Config($run_flag);
    return $c->getConfig();
}

sub write_config {
    my $c = new SC6::Cam::Config($run_flag);
    my $new = $c->getConfig();
    # re-read the config and see if the BailAfter went down.  
    if ( $new->{'BailAfter'} < $conf->{'BailAfter'} ) {
         $conf->{'BailAfter'} = $new->{'BailAfter'} - 1;
    }
    if ( $new->{'BailAfter'} <= 0 ) {
        print "looks like the config changed while I was running and you asked me to stop, so I will.\n";
    }
    $c->writeConfig($conf);
}
