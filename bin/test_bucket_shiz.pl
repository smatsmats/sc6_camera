#!/usr//bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::BlueCodeState;
use SC6::Cam::Config;
use SC6::Cam::Image;
use SC6::Cam::Sun;
use SC6::Cam::GStore;
use Getopt::Long;
use Data::Dumper;
use File::Basename;

my $force = 0;
our $mode = "test";
my $dryrun = 0;
my $current_bluecode;

$result = GetOptions (  "n|dry-run" => \$dryrun,
                        "f|force"  => \$force,
                        "h|help"  => \&usage,
                        "m|mode=s"  => \$mode,
                        "d|debug+"  => \$debug);

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml", $mode);
our $config = $c->getConfig();
our $debug = 1;
print "\n***** STARTING *****\n" if ( $debug );


# prime bluecode
my $push_to_google = $config->{'GStore'}->{'Enable'};
my $bcr = new SC6::Cam::BlueCodeState($mode, $dryrun);

print "primed bluecode is: ", $bcr->getBluecode(), "\n" if ( $debug );
our $gstore = new SC6::Cam::GStore();

my $sleep_time = $config->{'General'}->{'ImageInterval'}->{'SunUp'};
my $sleep_time_night = $config->{'General'}->{'ImageInterval'}->{'SunDown'};
my $fetch_sleep;
my $last_gstore_push = 0;
my $gstore_interval = $config->{'GStore'}->{'PushInterval'}->{'SunUp'};
my $prev_failed_start = 0;
my $s = new SC6::Cam::Sun();
my $end_time;
my $sun_status;

my $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );

my $current_image = new SC6::Cam::Image($dt, $mode, $dryrun, $s);

my $current = $config->{GStore}->{'CurrentDir'};
my $www_dir = get_www_dir($format, $mode);
my $www_image_orig = $www_dir . $config->{Image}->{File}->{orig};
my $www_image_50pct = $www_dir . $config->{Image}->{File}->{'50pct'};
my $public = $config->{GStore}->{'PublicDir'};
my $public_image_orig = $current_image->getPublicWWWFile();
my $public_image_50pct = $current_image->getPublicWWWFile_50pct();
my $blue_bucket = $main::config->{GStore}->{'BlueistDir'};
my $blueist_file_50pct = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'BlueistImage'} . "_50pct";
my $blueist_file_orig = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'BlueistImage'} . "_orig";

# cp blueist to current
my $current_dir = $config->{GStore}->{'CurrentDir'};
my $blueist_dir = $config->{GStore}->{'BlueistDir'};
my $public_dir = $config->{GStore}->{'PublicDir'};
my $blueist_image_orig = $blueist_dir . "/" . $config->{Image}->{File}->{orig};
my $blueist_image_50pct = $blueist_dir . "/" . $config->{Image}->{File}->{'50pct'};

print ("current:\t\t$current\n");
print ("www_dir:\t\t$www_dir\n");
print ("www_image_orig:\t\t$www_image_orig\n");
print ("www_image_50pct:\t$www_image_50pct\n");
print ("public:\t\t\t$public\n");
print ("public_image_orig:\t$public_image_orig\n");
print ("public_image_50pct:\t$public_image_50pct\n");
print ("blue_bucket:\t\t$blue_bucket\n");
print ("blueist_file_50pct:\t$blueist_file_50pct\n");
print ("blueist_file_orig:\t$blueist_file_orig\n");

# cp blueist to current
print ("current_dir:\t\t$current_dir\n");
print ("blueist_dir:\t\t$blueist_dir\n");
print ("public_dir:\t\t$public_dir\n");
print ("blueist_image_orig:\t$blueist_image_orig\n");
print ("blueist_image_50pct:\t$blueist_image_50pct\n");

$gstore->cp_bucket2bucket($blueist_image_orig, $current_dir);
print("\n");
$gstore->cp_bucket2bucket($blueist_image_orig, $public_dir);
print("\n");
$gstore->cp_fs2bucket($public_image_50pct, $blue_bucket);
print("\n");
$gstore->cp_fs2bucket($public_image_orig, $blue_bucket);
print("\n");
$gstore->cp_fs2bucket($public_image_orig, $public);
print("\n");
$gstore->cp_fs2bucket($www_image_orig, $current);
my $full = $current . "/" . basename($www_image_orig);
my $cmd = "/usr/local/cam/bin/bucket_shiz.py --get_metadata --blob_name $full";
print("Going to do: ", $cmd, "\n");
print(`$cmd`);
