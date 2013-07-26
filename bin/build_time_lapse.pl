#!/usr//bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::Sun;
use Getopt::Long;
use Data::Dumper;

my $force = 0;
my $mode = "prod";
my $dryrun = 0;
my $sleep_time = 30;

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = $c->getDebug();

$result = GetOptions (  "n|dry-run" => \$dryrun,
                        "f|force"  => \$force,
                        "h|help"  => \&usage,
                        "m|mode=s"  => \$mode,
#                        "d+"  => \$debug,
                        "d|debug+"  => \$debug);
if ( ! $result ) {
    usage();
    exit;
}

my $dt = DateTime->now(  time_zone => 'America/Los_Angeles' );
my $s = new SC6::Cam::Sun();
print "Now: $dt\n" if ( $debug );
if ( $force ) {
    print "We're forced to do this\n" if ( $debug );
}
else {
    if ( $s->is_sun($dt) ) {
        print "Sun is up!\n";
    }
    elsif ( $s->is_hour_after_dusk($dt) ) {
        print "Sun is down, but for less than an hour!\n";
    }
    else  {
        print "Sun is down!\n";
        exit;
    }
}

if ( $dryrun ) {
    print "This is a dry run, not doing anything\n";
}

$format = 'orig';
make_moovie($format, $mode);
compress_moovie($format, $mode);
push_to_youtube();

print "buh bye\n";

sub make_moovie {
    my ($format, $mode) = @_;

    my $out = get_video_file($dt, $format, 'avi', $mode);
    my $in = "'mf://" . get_image_dir($dt, $format, $mode) . "/*_" . $format . ".jpg'";
    my $mf = "w=" . $config->{'Sizes'}->{$format}->{'width'} . 
        ":h=" . $config->{'Sizes'}->{$format}->{'height'} . 
        ":type=" . $config->{'Type'} . 
        ":fps=" . $config->{'FPS'};

    my $cmd = "mencoder -msglevel all=1 -nosound -noskip -oac copy -ovc copy -o $out -mf $mf $in";
    do_cmd($cmd, $dryrun);
}

sub compress_moovie {
    my ($format, $mode) = @_;
    my $in = get_video_file($dt, $format, 'avi', $mode);
    my $out = get_video_file($dt, $format, 'mp4', $mode);
    my $ll =  $config->{'FFMpegLogLevel'};
#    my $cmd = "ffmpeg -y -loglevel $ll -i $in -r 25 -s 1920x1080 -vcodec libx264 -b:v 30000k $out 2> /dev/null";
    my $cmd = "avconv -y -loglevel $ll -i $in -r 25 -s 1920x1080 -vcodec libx264 -b:v 30000k $out";
    do_cmd($cmd, $dryrun);
}

sub usage
{
    print "usage: $0 [-d|--debug] [-f|--force] [-h|--help] [-n|--dry-run] [-m|mode=mode]\n";
    print "\t-f|--force   - Force building of the video files\n";
    print "\t-h|--help    - This message\n";
    print "\t-n|--dry-run - perform a trial run with no changes made\n";
    print "\t-m|--mode    - mode, prod or test\n";
    exit(1);

}

sub push_to_youtube {
    my $cmd = $config->{'Bins'}->{'push2youtube'};
    do_cmd($cmd, $dryrun);
}


