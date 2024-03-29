#!/usr/bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use Getopt::Long;
use Data::Dumper;
use Time::ParseDate;

my $mode = "prod";
my $date;
my $ok_gap = 45;
my $only_last_hour;
my $ONE_HOUR = (60*60);

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();
my $d;

my $result = GetOptions (  "h|help"  => \&usage,
                        "t|date=s"  => \$date,
                        "D|directory=s"  => \$d,
                        "m|mode=s"  => \$mode,
                        "o|only-last-hour"  => \$only_last_hour,
                        "i|gap=i"  => \$ok_gap,
                        "d|debug+"  => \$debug);

my $now = time();

if ( ! $d ) {
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
    }
    else {
        $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
    }
    
    $d = get_image_dir($dt, "orig", $mode);
}

opendir(my $dh, $d) || die;

my $last_was_big = 0;
my $last = 0;
my @files = readdir $dh;
foreach my $f ( sort @files ) {
    next if ( $f eq "." );
    next if ( $f eq ".." );
    my $n = $f;
    $n =~ s/image(\d+)_orig.jpg/$1/; 
    $last = $n if ( $last == 0 );
    if ( $n - $last <= $ok_gap ) {
        $last_was_big = 0;
    }
    else {
        if ( ! $only_last_hour || $now - $n < $ONE_HOUR ) {
	    my $all_secs = $n - $last;
	    my $mins;
	    my $t_string = "$all_secs seconds";
	    if ( $all_secs >= 60 ) {
	        $mins = ( $all_secs / 60 ) % 60;
		if ( $mins == 1 ) {
		    $min_word = "minute";
		}
		else {
		    $min_word = "minutes";
		}
                $seconds = $all_secs % 60; 
		$t_string = "$mins $min_word $seconds seconds ($all_secs secs)";
	    }
            print "Big gap: ", $t_string, " at ", scalar localtime($n);
            if ( $last_was_big ) {
                print " prior was also big\n";
            }
            else {
                print "\n";
            }
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
    print "\t-t|--date                - date of files to check\n";
    print "\t-D|--directory           - directory to check (overrules date based directory)\n";
    print "\t-h|--help                - This message\n";
    print "\t-i|--gap                 - OK gap in images\n";
    print "\t-m|--mode                - set mode (prod is default)\n";
    print "\t-o|--only-last-hour      - only report issues from tha last hour\n";
    print "\t--debug                  - print extra debugging information\n";
    exit(1);

}
