#!/usr//bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::BlueCode;
use SC6::Cam::Config;
use Getopt::Long;
use Data::Dumper;
use GD;

my $debug = 0;
my $force = 0;
my $mode = "prod";
my $dryrun = 0;
my $sleep_time = 30;

my $config = get_config($mode, $debug);

print $ARGV[0], "\n";
get_blue($ARGV[0], 1);

