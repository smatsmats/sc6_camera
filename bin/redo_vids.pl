#!/usr/bin/perl

use DateTime;
use Time::ParseDate;
use Getopt::Long;
use SC6::Cam::Config;
use Data::Dumper;
use strict;

#two different scripts:
my $build_and_push_cmd = "/home/willey/sc6_camera/bin/build_time_lapse.pl";

my $rut = "/home/willey/sc6_camera/data/cam_images";
my $run_flag = "/tmp/redo_run_flag.yml";
my $dryrun;
my $date;
my $debug;
my $default_fail_sleep_interval = (10 * 60); # how long to wait if we can't run a built 
my $default_ok_sleep_interval = (10 * 60); # how long to wait if we can't run a built 

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

    
    my ($stop_seconds, $stop_error);
    my $stop;
    if ( defined $conf->{'StopTime'} ) {
        ($stop_seconds, $stop_error) = parsedate($conf->{'StopTime'});
        if ( not $stop_seconds ) {
            print "Error can't parse end date/time: ", $conf->{'StopTime'}, ": $stop_error\n";
            exit;
        }
        $stop = DateTime->from_epoch(  epoch => $stop_seconds, time_zone => 'America/Los_Angeles');
        $conf->{'StopTimeDecoded'} = $stop->ymd . " " . $stop->hms;
        print "I will stop at ", $conf->{'StopTime'}, " a.k.a. $stop_seconds, ", $stop, "\n";
        if ( time >= $stop_seconds ) {
            print "Time to stop!\n";
            print scalar localtime(), "\n";
            exit;
        }
    }

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


    my $cmd = $build_and_push_cmd . " --trickle --date $start --debug";
    print "are we going to trickle: ", $conf->{'Trickle'}, "\n";
    if ( $conf->{'Trickle'} eq "False" || $conf->{'Trickle'} == 0 ) {
        $cmd = $build_and_push_cmd . " --date $start --debug";
    }
    print $cmd, "\n";
    print `$cmd`;
    my $ret_code = $?;
    print "return code is $ret_code\n";
    my $fail = 0;
    if ($ret_code > 0) {
        print "fail from $cmd : $!\n";
        print scalar localtime(), "\n";
        $fail = 1;
    }
    else {
        # update the config and write it out
        $start->add( days => -1 );
        $conf->{'StartDate'} = $start->strftime('%m/%d/%Y');
    }
    $conf->{'BailAfter'} = $counter - 1;
    write_config();
    $count++;

    if ( $fail == 1 ) {
        my $sleep_interval = $default_fail_sleep_interval;
        if ( defined $conf->{'SleepIntervalFail'} ) {
            $sleep_interval = $conf->{'SleepIntervalFail'};
        }
        print "sleeping between failures: $sleep_interval\n";
        sleep $sleep_interval;
    }
    else {
        my $sleep_interval = $default_ok_sleep_interval;
        if ( defined $conf->{'SleepIntervalOK'} ) {
            $sleep_interval = $conf->{'SleepIntervalOK'};
        }
        print "sleeping between sucesses: $sleep_interval\n";
        sleep $sleep_interval;
    }
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
    if ( $new->{'BailAfter'} - 1 != $conf->{'BailAfter'} ) {
        print "updating BailAfter.  Was going to be: ", $conf->{'BailAfter'}, " now will be: ", $new->{'BailAfter'} - 1, "\n";
        $new->{'BailAfter'} = $new->{'BailAfter'} - 1;
    }
    else {
        $new->{'BailAfter'} = $conf->{'BailAfter'};
    }
    if ( $new->{'BailAfter'} <= 0 ) {
        print "looks like the config changed while I was running and you asked me to stop, so I will.\n";
    }
    $new->{'StartDate'} = $conf->{'StartDate'};

    if ( defined $conf->{'StopTime'} ) {
        if ( $new->{'StopTime'} != $conf->{'StopTime'} ) {
            print "looks like the config changed while I was running I'll use your new Stop Time.\n";
        }
        else {
            $new->{'StopTime'} = $conf->{'StopTimeDecoded'};
            $new->{'StopTimeDecoded'} = $conf->{'StopTimeDecoded'};
        }
    }
    $c->writeConfig($new);
}
