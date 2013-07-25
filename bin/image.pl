#!/usr/bin/perl

use SC6::Cam::BlueCodeState;
use SC6::Cam::Config;
use SC6::Cam::Image;
use SC6::Cam::Sun;
use Getopt::Long;
use Data::Dumper;
use DateTime;
use GD;

my $mode = "test";
my $dryrun = 0;
my $force = 0;

my $c = new SC6::Cam::Config();
our $config = $c->getConfig();
our $debug = $c->getDebug();
$debug++;
#print Dumper($config);
#print "test config: ", $real_config->{Overlay}->{Clock}->{Overlay}, "\n";

my $s = new SC6::Cam::Sun();
$dt = DateTime->now(  time_zone => 'America/Los_Angeles' );

$result = GetOptions (  "n|dry-run" => \$dryrun,
                        "f|force"  => \$force,
                        "h|help"  => \&usage,
                        "m|mode=s"  => \$mode,
                        "d|debug+"  => \$debug);

my $now = time();

if ( $force ) {
    print "We're forced to do this\n" if ( $debug );
}
else {
    if ( $s->is_sun($dt) ) {
        print "Sun is up!\n";
    }
    elsif ( $s->is_hour_after_dusk($dt) ) {
        print "Sun is down, but for less than an hour!\n";
    }
    else  {
        print "Sun is down!\n";
        exit;
    }
}

my $cim = new SC6::Cam::Image($dt, $mode, $dryrun, $s);
my $result = $cim->fetch();

my $bcr = new SC6::Cam::BlueCodeState();
print "primed bluecode is: ", $bcr->getBluecode(), "\n";
    if ( $result ) {
        $cim->getBluecode();
        $cim->do_image_overlays();
        $cim->resizes_and_links();
        $bcr->checkBluecode($cim);
    }
    else {
        print "Image fetch failed!!!!!\n";
        $fetch_sleep = 0;  # skip sleeping
        $prev_failed_start = $dt->epoch();
    }
exit;
