#!/usr/bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::WX;
use Getopt::Long;
use Data::Dumper;

my $force = 0;
my $mode = "test";

my $c = new SC6::Cam::Config();
our $config = $c->getConfig();
our $debug = $c->getDebug();

$result = GetOptions (  "length=i" => \$length,    # numeric
                        "f|force"  => \$force,     # flag
                        "h|help"  => \$usage,      # function
			"d|debug"  => \$debug);    # flag

my $wx = new SC6::Cam::WX();
print "Rain today: ", $wx->rain_today(), "\n";
