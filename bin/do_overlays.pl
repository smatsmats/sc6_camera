#!/usr//bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Overlay;
use SC6::Cam::Config;
use Getopt::Long;
use Data::Dumper;
use GD;

my $debug = 1;
my $force = 0;
my $mode = "prod";
my $dryrun = 0;
my $sleep_time = 30;

my $config = get_config($mode, 0);

print $ARGV[0], "\n";
my $dt = DateTime->now(  time_zone => 'America/Los_Angeles' );
do_overlays($ARGV[0], "/var/www/bib/camera/out.jpg", $dt->hour, $dt->minute, 1);
#do_overlays("current_image_orig.jpg", "out.jpg", 1);

