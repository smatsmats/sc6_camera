#!/usr/bin/perl

# cnks one directory of files to anothr adjusting the image interval.
#
# obviously we can only increase the interval, not decrease it
#

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use Getopt::Long;
use Data::Dumper;
use Time::ParseDate;

my $mode = "prod";
my $date;
my $interval = 45;

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();

my $result = GetOptions (  "h|help"  => \&usage,
                        "t|date=s"  => \$date,
                        "D|destination=s"  => \$destination,
                        "i|new_interval=i"  => \$interval,
                        "d|debug+"  => \$debug);

my $dt;
if ( $date ) {
    print $date, "\n" if ( $debug );
    my ($seconds, $error) = parsedate($date);
    if ( not $seconds ) {
        print "Error can't parse date: $date : $error\n";
        exit(1);
    }
    else {
        print $seconds, "\n" if ( $debug );
        $dt = DateTime->from_epoch(  epoch => $seconds, time_zone => $config->{'General'}->{'Timezone'} );
    }
    $date_from_args = 1;
}
else {
    print "Date is required\n";
    usage();
    exit;
}

if ( ! $destination ) {
    print "Destination dir is required\n";
    usage();
    exit;
}

if ( ! -d $destination ) {
    print "Destination dir ($destination) has to exist\n";
    exit;
}

my $d = get_image_dir($dt, "orig", $mode);

opendir(my $dh, $d) || die;

my $last = 0;
my @files = readdir $dh;
foreach my $f ( sort @files ) {
    next if ( $f eq "." );
    next if ( $f eq ".." );

    my $n = $f;
    $n =~ s/image(\d+)_orig.jpg/$1/; 
    $last = $n if ( $last == 0 );
    if ( $n - $last <= $interval ) {
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

sub usage
{
    print "usage: $0 [-d|--debug] [-t|--date=date] [-i|--gap=interval] [-h|--help] \n";
    print "\t-t|--date     - Date of files to check\n";
    print "\t-h|--help     - This message\n";
    print "\t-i|--gap      - OK gap in images\n";
    print "\t--debug       - print extra debugging information (debug trumps silent)\n";
    exit(1);

}
