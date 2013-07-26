#!/usr/bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use Getopt::Long;
use Data::Dumper;

my $mode = "prod";

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();

my $dt = DateTime->now(  time_zone => 'America/Los_Angeles' );
#my $d = "/data/cam_images/20130209/orig";
my $d = get_image_dir($dt, "orig", $mode);

opendir(my $dh, $d) || die;
$ok_gap = 35;

my $last_was_big = 0;
my $last = 0;
my @files = readdir $dh;
foreach my $f ( sort @files ) {
    next if ( $f eq "." );
    next if ( $f eq ".." );
    my $n = $f;
    $n =~ s/image(\d+)_orig.jpg/$1/; 
    $last = $n if ( $last == 0 );
#image1360089169_orig.jpg
    if ( $n - $last <= $ok_gap ) {
        $last_was_big = 0;
    }
    else {
        print "$f $n";
        print " Big gap: ", $n - $last, " ", scalar localtime($n);
        if ( $last_was_big ) {
            print " prior was also big\n";
        }
        else {
            print "\n";
        }
        $last_was_big = 1;
    }
    $last = $n;
}

#    my $new =  $d . "/" . $_;
#    $new =~ s/.jpg$//;
#    $new .= "_orig.jpg";
#    print "mv $d/$_ $new\n";
closedir $dh;

