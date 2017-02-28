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

my $force = 0;
my $dryrun = 0;
my $current_bluecode;
our $mode = "prod";

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();
print "\n***** STARTING *****\n" if ( $debug );

$result = GetOptions (  "n|dry-run" => \$dryrun,
                        "f|force"  => \$force,
                        "h|help"  => \&usage,
                        "m|mode=s"  => \$mode,
                        "d|debug+"  => \$debug);

# prime bluecode
my $bcr = new SC6::Cam::BlueCodeState($mode, $dryrun);

print "current bluecode is: ", $bcr->getBluecode(), "\n";
exit;

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

while() {
    my $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
    if ( $s->is_sun($dt) || $force ) {  # inefficient to do this everytime, but who cares
        print "Sun is up! $dt\n";
        $sun_status = 1;
        $fetch_sleep = $sleep_time;

        # fetch an image
        my $current_image = new SC6::Cam::Image($dt, $mode, $dryrun, $s);
        my $result = $current_image->fetch();

        if ( ! $result ) {
            print "Image fetch failed!!!!!\n";
            $fetch_sleep = 0;  # skip sleeping
            $prev_failed_start = $dt->epoch();
        }
        else {
            $current_image->getBluecode();
            $current_image->make_public_version();
            $current_image->do_image_overlays();
            $current_image->resizes_and_links();
            
            # normal sleep, but prune sleep time to account for processing
            $end_time = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
            if ( $prev_failed_start != 0 ) {
                $fetch_sleep = $sleep_time - ($end_time->epoch() - $prev_failed_start);
            } 
            else {
                $fetch_sleep = $sleep_time - ($end_time->epoch() - $dt->epoch());
            }
            $prev_failed_start = 0;
            
            # file and dir locations
            # this directory crap is a mess, fix it.  
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

            # check blue code and push blue file maybe
            if ( $bcr->checkBluecode($current_image) == 1 ) {
                print "new blue\n";
                $gstore->cp_fs2bucket($public_image_orig, $blue_bucket);
                $gstore->cp_fs2bucket($public_image_50pct, $blue_bucket);
            }
            else {
                print "old blue\n";
            }

            # push the images to gstore
            # this should really be a seperate loop or even process, but for now it's here
            if ( $last_gstore_push + $gstore_interval < $end_time->epoch() ) { 
                $gstore->cp_fs2bucket($www_image_orig, $current);
    # skip copying up 50pct images
    #            $gstore->cp_fs2bucket($www_image_50pct, $current);
    
                $gstore->cp_fs2bucket($public_image_orig, $public);
    # skip copying up 50pct images
    #            $gstore->cp_fs2bucket($public_image_50pct, $public);
    
                $last_gstore_push = $end_time->epoch();
            }
            else {
                print "No gstore push until ", $last_gstore_push + $gstore_interval, "\n";
            }
    
        }

    }
    else {
        print "Sun is down! $dt\n";
        $fetch_sleep = $sleep_time_night;

        # do some things during the first hour the sun is down, but only once
        if ( $s->is_hour_after_dusk($dt) && $sun_status == 1 ) {
            $sun_status = 0;
            $prev_failed_start = 0;   # make sure this doesn't carry over from the previous day
            $last_gstore_push = 0;
 
            # cp blueist to current
            my $current_dir = $config->{GStore}->{'CurrentDir'};
            my $blueist_dir = $config->{GStore}->{'BlueistDir'};
            my $public_dir = $config->{GStore}->{'PublicDir'};
            my $blueist_image_orig = $blueist_dir . "/" . $config->{Image}->{File}->{orig};
            my $blueist_image_50pct = $blueist_dir . "/" . $config->{Image}->{File}->{'50pct'};
            $gstore->cp_bucket2bucket($blueist_image_orig, $current_dir);
            $gstore->cp_bucket2bucket($blueist_image_orig, $public_dir);
# lets not dork with 50pct rigth now
#            $gstore->cp_bucket2bucket($blueist_image_50pct, $current_dir);
        }
    }

    if ( $fetch_sleep >= 0 ) {
#        print "fetch_sleep: $fetch_sleep  prev_failed_start: $prev_failed_start sleep_time: $sleep_time end_time: ", $end_time->epoch(), "\n" if ( $debug );
        print "Gonna sleep: $fetch_sleep\n\n" if ( $debug );
        sleep $fetch_sleep;
        print "done sleeping; sleep: $fetch_sleep\n\n" if ( $debug );
    }
    else {
        print "WTF! fetch_sleep: $fetch_sleep  prev_failed_start: $prev_failed_start sleep_time: $sleep_time end_time: ", $end_time->epoch(), "\n";
        exit 1;
    }
}

sub usage
{
    print "usage: $0 [-d|--debug] [-f|--force] [-h|--help] [-n|--dry-run] [-m|mode=mode]\n";
    print "\t-f|--force   - Force collecting of the  files\n";
    print "\t-h|--help    - This message\n";
    print "\t-n|--dry-run - perform a trial run with no changes made\n";
    print "\t-m|--mode    - mode, prod or test\n";
    exit(1);

}

