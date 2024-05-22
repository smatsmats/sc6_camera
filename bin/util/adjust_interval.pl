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
my $grace = 5;
our $type = "public";
our $multi;

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();

my $result = GetOptions (  "h|help"  => \&usage,
                        "t|date=s"  => \$date,
                        "T|type=s"  => \$type,
                        "m|multi"  => \$multi,
                        "D|destination=s"  => \$destination,
                        "g|grace=i"  => \$grace,
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

my $d = get_image_dir($dt, $type, $mode);

opendir(my $dh, $d) || die;

my $last = 0;
my @files = readdir $dh;
foreach my $f ( sort @files ) {
    next if ( $f eq "." );
    next if ( $f eq ".." );

    my $n = $f;
    $n =~ s/image(\d+)_orig.jpg/$1/; 

    # first file
    if ( $last == 0 ) {
        do_link($d, $f, $destination, $f);
        $last = $n;
    }
    else {
        if ( $multi ) {
            print "for $last to $n (", $n-$last, ")\n";
            for (my $i=$last+1 ; $i < $n ; $i++ ) {
                my $this_file = "/image" . $i . "_orig.jpg";
                do_link($d, $f, $destination, $this_file);
                print $this_file, "\n";
            }
            do_link($d, $f, $destination, $f);
            $last = $n;
        }
        else {
            # link the next file that matches interval or skip it
            if ( $n >= $last + $interval - $grace ) {
                do_link($d, $f, $destination, $f);
                $last = $n;
            }
            else { 
                #skip
                print "gonna skip $f\n";
            }
        }
    } 

}

closedir $dh;

sub do_link {
    my ($old_dir, $old_file, $new_dir, $new_file) = @_;
   
    my $old = $old_dir . "/" . $old_file;
    my $new = $new_dir . "/" . $new_file;
    print "gonna link $old to $new\n";
    link $old, $new or die "Can't link $old to $new :$!\n";
}

sub usage
{
    print "usage: $0 [-d|--debug] [-t|--date=date] [-i|--gap=interval] [-h|--help] \n";
    print "\t-t|--date        - date of files to check\n";
    print "\t-T|--type        - type of image from date to pull, \"orig\", \"public\" (default), \"public_50pct\", or \"50pct\"\n";
    print "\t-m|--multi       - use multiple links to files to spread them out \n";
    print "\t-D|--destination - destination directory to check (overrules date based directory)\n";
    print "\t-h|--help        - This message\n";
    print "\t-i|--gap         - OK gap in images\n";
    print "\t-g|--grace       - how far below next interval to accept (default == 5)\n";
    print "\t--debug          - print extra debugging information (debug trumps silent)\n";
    exit(1);

}
