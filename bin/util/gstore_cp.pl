#!/usr/bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::GStore;
use Getopt::Long;
use Data::Dumper;

my $force = 0;
my $mode = "test";
my $default_file = "/etc/resolv.conf";

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();

$result = GetOptions (  "f|file=s" => \$file, 
                        "h|help"  => \$usage,      # function
			"d|debug"  => \$debug);    # flag

my $gs = new SC6::Cam::GStore();

if ( ! $file ) {
    $file = $default_file; 
}

my $dir = $config->{GStore}->{'CurrentDir'};
print $gs->cp($file, $dir);
print "\n", $gs->web_url($dir, $file), "\n";

exit;

