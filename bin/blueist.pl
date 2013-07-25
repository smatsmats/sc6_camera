#!/usr//bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::BlueCode;
use Getopt::Long;
use Data::Dumper;
use GD;

my $debug = 0;
my $force = 0;
my $mode = "prod";
my $dryrun = 0;
my $sleep_time = 30;

my $config = get_config($mode, $debug);

my $most_blue = 0;
my $most_blue_f = "";
my $somedir = "/data/cam_images/20130219/50pct";
opendir(my $dh, $somedir) || die;
while(readdir $dh) {
        next if ( $_ eq '.' );
        next if ( $_ eq '..' );
        my $f = $somedir . "/" . $_;
        my $tc = $_;
        $tc =~ s/^image([0-9]+)_50pct.jpg/\1/;
        print `ls -l $f`;
        my $b = get_blue($f, 1);
#        my $new_code = $l * $b; 
#        print "trip $tc ", scalar localtime($tc), " $b $d $l $new_code\n";
        print "trip $tc ", scalar localtime($tc), " $b\n";
        if ( $b > $most_blue ) {
            $most_blue = $b;
            $most_blue_f = $f;
        }
}
closedir $dh;
print "most blue: ", $most_blue_f, " which scored: $most_blue\n";

