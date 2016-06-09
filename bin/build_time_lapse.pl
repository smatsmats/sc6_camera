#!/usr/bin/perl

use strict;
use warnings;
use Fcntl qw(:flock);
use Time::ParseDate;

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
my $date;
my $no_push;

my $result = GetOptions (  "n|dry-run" => \$dryrun,
                        "f|force"  => \$force,
                        "h|help"  => \&usage,
                        "m|mode=s"  => \$mode,
                        "t|date=s"  => \$date,
                        "np|no-push"  => \$no_push,
                        "d|debug+"  => \$debug);
if ( ! $result ) {
    usage();
    exit;
}

unless (flock(DATA, LOCK_EX|LOCK_NB)) {
    print "$0 is already running. Exiting.\n";
    exit(1);
}

my $dt;
my $date_from_args = 0;
if ( $date ) {
    print $date, "\n" if ( $debug );
    my ($seconds, $error) = parsedate($date);
    if ( not $seconds ) {
	print "Error can't parse date: $date : $error\n";
        exit;
    }
    else {
	print $seconds, "\n" if ( $debug );
        $dt = DateTime->from_epoch(  epoch => $seconds, time_zone => $config->{'General'}->{'Timezone'} );
    }
    $force = 1;
    $date_from_args = 1;
}
else {
    $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
}

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

my $format = 'orig';
make_moovie($format, $mode);
my %metadata = collect_metadata();
compress_moovie($format, $mode, %metadata);
if ( ! $no_push ) {
    push_to_youtube();
}

print "buh bye\n";

sub make_moovie {
    my ($format, $mode) = @_;

    my $image_dir = 'public';
    my $out = get_video_file($dt, $format, 'avi', $mode);
    my $in = "'mf://" . get_image_dir($dt, $image_dir, $mode) . "/*_" . $format . ".jpg'";
    my $mf = "w=" . $config->{'Sizes'}->{$format}->{'width'} . 
        ":h=" . $config->{'Sizes'}->{$format}->{'height'} . 
        ":type=" . $config->{'Type'} . 
        ":fps=" . $config->{'FPS'};

    my $cmd = "mencoder -msglevel all=1 -nosound -noskip -oac copy -ovc copy -o $out -mf $mf $in";
    do_cmd($cmd, $dryrun);
}

sub compress_moovie {
    my ($format, $mode, %metadata) = @_;
    my $in = get_video_file($dt, $format, 'avi', $mode);
    my $out = get_video_file($dt, $format, 'mp4', $mode);
    my $ll =  $config->{'FFMpegLogLevel'};
    my $md;
    foreach my $k ( keys %metadata ) {
	$md .= " -metadata $k='" . $metadata{$k} . "'";
    }
    my $cmd = $config->{'Bins'}->{'ffmpeg'};
    $cmd .= " -y -loglevel $ll -i $in $md -r 25 -s 1920x1080 -vcodec libx264 -b:v 30000k $out";
    do_cmd($cmd, $dryrun);
}

sub usage
{
    print "usage: $0 [-d|--debug] [-f|--force] [-h|--help] [-n|--dry-run] [-m|mode=mode]\n";
    print "\t-f|--force    - Force building of the video files\n";
    print "\t-h|--help     - This message\n";
    print "\t-n|--dry-run  - perform a trial run with no changes made\n";
    print "\t-np|--no-push - don't push to youtube\n";
    print "\t-m|--mode     - mode, prod or test\n";
    exit(1);

}

sub push_to_youtube {
    my $cmd = $config->{'Bins'}->{'push2youtube'} . " " . $config->{'Bins'}->{'push2youtube_args'};
    if ( $date_from_args == 1 ) {
        $cmd .= " " . "--videoDate=" . $dt->ymd;
    }
    do_cmd($cmd, $dryrun);
}

sub collect_metadata {
    my %h;
    $h{'title'} = "test title";
    $h{'tags'} = "test tags";
    $h{'description'} = "test description";
    $h{'date'} = "test date";

    return %h;
}

__DATA__
This exists so flock() code above works.
DO NOT REMOVE THIS DATA SECTION.
