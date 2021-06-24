#!/usr/bin/python3

#
#use SC6::Cam::General
#use SC6::Cam::Config
#use SC6::Cam::Sun

mode = "prod"
dryrun = 0
sleep_time = 30

import sys
sys.path.append('/usr/local/cam/lib/pythonlib')
import bucket_shiz

import os
from datetime import *
import argparse
import yaml
import errno
import xml.parsers.expat
from stat import *
import logging
import logging.config

gconfig_root = yaml.safe_load(file("/usr/local/cam/conf/push_video_config.yml"))
gconfig = gconfig_root['prod']
config_root = yaml.safe_load(file("/usr/local/cam/conf/config.yml"))
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger('push_video')


def today_video_name():
    vdir = config['BucketShiz']['VideoDir']
    t_name = config['BucketShiz']['TodayVideoName']
    out = "%s/%s" % (vdir,
                     t_name)
    return(out)


def get_dest_name():
    vdir = config['BucketShiz']['VideoDir']
    dt = datetime.today()
    fname_template = config['BucketShiz']['VideoNameTemplate']
    fname_w_date = dt.strftime(fname_template)
    suffix = config['BucketShiz']['VideoNameSuffix']
    out = "%s/%s/%s/%s/%s%s" % (vdir,
                                dt.strftime("%Y"),
                                dt.strftime("%m"),
                                dt.strftime("%d"),
                                fname_w_date,
                                suffix)
    return(out)


def set_cache_timeout(dest_name):
    fbase = os.path.basename(dest_name)
    cache_control = config['BucketShiz']['Cache']['CacheControl']
    try:
        cache_timeout = config['BucketShiz']['Cache']['MaxAge'][fbase]
    except:
        cache_timeout = config['BucketShiz']['Cache']['MaxAge']['default_video']
    cachecontrol_val = "'" + cache_control + ", max-age=" + str(cache_timeout) + "'"
    bshiz.set_blob_cachecontrol(dest_name, cachecontrol_val)



#our $config = $c->getConfig()
#our $debug = $c->getDebug()
#my $date
#my $no_push
#my $silent = 0
#my $trickle = 0
#my $trickle_cmd = "trickle -s -u 200"
#my $keep = 0
#my $out = ""
#my $directory;   # overrides the date
#my $fps;   # overrides fps
#
#my $result = GetOptions (  "n|dry-run" => \$dryrun,
#                        "f|force"  => \$force,
#                        "h|help"  => \&usage,
#                        "k|keep"  => \$keep,
#                        "m|mode=s"  => \$mode,
#                        "t|date=s"  => \$date,
#                        "D|directory=s"  => \$directory,
#                        "np|no-push"  => \$no_push,
#                        "trickle"  => \$trickle,
#                        "fps=f"  => \$fps,
#                        "silent"  => \$silent,
#                        "d|debug+"  => \$debug)
#
#if ( ! $result ) {
#    usage()
#    exit
#}
#
## debug trumps silent
#if ( $debug && $silent ) {
#    $silent = 0
#}
#
#unless (flock(DATA, LOCK_EX|LOCK_NB)) {
#    if ( ! $silent ) {
#        print "$0 is already running. Exiting.\n"
#    }
#    exit(1)
#}
#
#my $dt
#my $date_from_args = 0
#if ( $date ) {
#    print $date, "\n" if ( $debug )
#    my ($seconds, $error) = parsedate($date)
#    if ( not $seconds ) {
#	print "Error can't parse date: $date : $error\n"
#        exit(1)
#    }
#    else {
#	print $seconds, "\n" if ( $debug )
#        $dt = DateTime->from_epoch(  epoch => $seconds, time_zone => $config->{'General'}->{'Timezone'} )
#    }
#    $force = 1
#    $date_from_args = 1
#}
#else {
#    $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} )
#}
#
#my $s = new SC6::Cam::Sun()
#print "Now: $dt\n" if ( $debug )
#if ( $directory ) {
#    print scalar localtime(), " We hav a direcotry to process: $directory\n"
#}
#elsif ( $force ) {
#    print scalar localtime(), " We're forced to do this\n" if ( $debug )
#}
#else {
#    if ( $s->is_sun($dt) ) {
#        print scalar localtime(), " Sun is up!\n" unless ( $silent)
#    }
#    elsif ( $s->is_hour_after_dusk($dt) ) {
#        print scalar localtime(), " Sun is down, but for less than an hour!\n" unless ( $silent)
#    }
#    else  {
#        print scalar localtime(), " Sun is down!\n" unless ( $silent)
#        exit
#    }
#}
#
#if ( $dryrun ) {
#    print "This is a dry run, not doing anything\n" unless ( $silent)
#}
#
#my $format = 'orig'
#make_moovie($format, $mode)
#my %metadata = collect_metadata()
#compress_moovie($format, $mode, %metadata)
#my $push_return_code
#if ( ! $no_push ) {
#    $push_return_code = push_to_youtube($format, $mode)
#}
#else {
#    $push_return_code = 0
#}
#cleanup($format, $mode)
#
#if ( $debug ) {
#    print scalar localtime(), " buh bye\n"
#    print scalar localtime(), " push still returned $push_return_code\n"
#}
#if ( $push_return_code != 0 ) {
#    exit 1
#}
#exit($push_return_code)
#
#sub make_moovie {
#    my ($format, $mode) = @_
#
#    my $image_dir = 'public'
#    my $out = get_video_file($dt, $format, 'avi', $mode)
#
#    if ( $directory ) {
#        $image_dir = $directory
#    }
#    else {
#        $image_dir = get_image_dir($dt, $image_dir, $mode)
#    }
#
#    if ( ! $fps ) {
#        $fps = $config->{'FPS'}
#    }
#
#    my $in = "'mf://" . $image_dir . "/*_" . $format . ".jpg'"
#    my $mf = "w=" . $config->{'Sizes'}->{$format}->{'width'} . 
#        ":h=" . $config->{'Sizes'}->{$format}->{'height'} . 
#        ":type=" . $config->{'Type'} . 
#        ":fps=" . $fps
#
#    my $cmd = "mencoder -msglevel all=1 -nosound -noskip -oac copy -ovc copy -o $out -mf $mf $in"
#    my $ret = my_do_cmd($cmd, $dryrun)
#    if ( $ret != 0 ) {
#        print "Failed to make a movie, maybe no images?  Return: $ret\n"
#        exit($ret)
#    }
#}
#
#sub compress_moovie {
#    my ($format, $mode, %metadata) = @_
#    my $in = get_video_file($dt, $format, 'avi', $mode)
#    my $out = get_video_file($dt, $format, 'mp4', $mode)
#    my $ll =  $config->{'FFMpegLogLevel'}
#    my $md
#    foreach my $k ( keys %metadata ) {
#	$md .= " -metadata $k='" . $metadata{$k} . "'"
#    }
#    my $cmd = $config->{'Bins'}->{'ffmpeg'}
#    $cmd .= " -y -loglevel $ll -i $in $md -r 25 -s 1920x1080 -vcodec libx264 -b:v 30000k $out"
#    my_do_cmd($cmd, $dryrun)
#}
#
#sub usage
#{
#    print "usage: $0 [-d|--debug] [-t|--date=date] [-f|--force] [-h|--help] [--silent] [--trickle] [-n|--dry-run] [-m|mode=mode]\n"
#    print "\t-f|--force     - force building of the video files\n"
#    print "\t-t|--date      - date of files to build and push\n"
#    print "\t-D|--directory - directory to build and push (overrides date)\n"
#    print "\t-h|--help      - this message\n"
#    print "\t-n|--dry-run   - perform a trial run with no changes made\n"
#    print "\t-k|--keep      - don't remove disposable video files\n"
#    print "\t-np|--no-push  - don't push to youtube\n"
#    print "\t--trickle      - use trickle to limit bandwidth\n"
#    print "\t--fps          - override frame per second\n"
#    print "\t--silent       - don't print normal amount of information\n"
#    print "\t--debug        - print extra debugging information (debug overrides silent)\n"
#    print "\t-m|--mode      - mode, prod or test\n"
#    exit(1)
#
#}
#
#sub cleanup {
#    my ($format, $mode) = @_
#
#    # don't delete video files if we were asked to keep them
#    return if ( $keep )
#
#    if ( $config->{'Video'}->{'Daily'}->{'Disposable'} ) {
#        my $out = get_video_file($dt, $format, 'mp4', $mode)
#        unlink $out or die "Can't remove $out: $!\n"
#        $out = get_video_file($dt, $format, 'avi', $mode)
#        unlink $out or die "Can't remove $out: $!\n"
#    }
#}
#
#sub push_to_youtube {
#    my ($format, $mode) = @_
#
#    my $cmd = ""
#    if ( $trickle ) {
#        $cmd = $trickle_cmd . " "
#    }
#    $cmd .= $config->{'Bins'}->{'push2youtube'} . " " . $config->{'Bins'}->{'push2youtube_args'}
#    if ( $date_from_args == 1 ) {
#        $cmd .= " " . "--videoDate=" . $dt->ymd
#    }
#    my $out = get_video_file($dt, $format, 'mp4', $mode)
#    $cmd .= " --file " . $out
#    my $rcode = my_do_cmd($cmd, $dryrun)
#    return $rcode
#}
#
#sub collect_metadata {
#    my %h
#    $h{'title'} = "test title"
#    $h{'tags'} = "test tags"
#    $h{'description'} = "test description"
#    $h{'date'} = "test date"
#
#    return %h
#}
#
#sub my_do_cmd {
#    my ($cmd, $dryrun) = @_
#    if ( $debug ) {
#        print scalar localtime(), " ", $cmd, "\n"
#    }
#    if ( ! $dryrun ) {
#        print scalar localtime(), " Start command\n" if ( $debug )
#        my  $ret = `$cmd 2>&1`
#        print $ret if ( $debug )
#        print scalar localtime(), " Stop command\n" if ( $debug )
#        return $?
#    }
#}
#
#sub new_do_cmd {
#    my $cmd = shift
#    my $wtr = gensym
#    my $rdr = gensym
#    my $err = gensym
#
#    print TMPOUT "command: $cmd\n"
#
#    my $errors
#    if( ! open3($wtr, $rdr, $err, $cmd) ) {
#        print TMPOUT "open3 of cmd $cmd failed $!"
#        $errors = 1
#        return 1
#    }
#    close $wtr
#    while(<$rdr>) {
#        print TMPOUT
#    }
#    close $rdr
#    while(<$err>) {
#        print TMPOUT
#        $errors = 1
#    }
#    close $err
#
#    return 0
#}
#

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='push video up to buckets.')
    argparser.add_argument("--file", dest="file", help="Video file to upload")
    argparser.add_argument("--videoDate", dest="videoDate", default="",
                           help="video is for some other date than today")
    argparser.add_argument("--doDeletes", action='store_true',
                           help="clenaup other uploades from today")
    argparser.add_argument("--dontUpload", action='store_true',
                           help="for testing, don't actually do the upload")
    args = argparser.parse_args()

    # file
    if args.file is None:
        args.file = gconfig['Paths']['video_file']

    # titles and stuff for video
    if args.videoDate:
        date_string = args.videoDate
    else:
        date_string = date.today().isoformat()

    bshiz = bucket_shiz.MyBucket()

    logger.debug("upload logic")
    if args.file is None or not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")
    else:
        dest_name = get_dest_name()
        print(dest_name)

        if args.dontUpload:
            logger.info("dontUpload is set, we won't upload")
        else:
            # send-up the video and set cache
            logger.info("upload")
            bshiz.upload_blob(args.file, dest_name)
            set_cache_timeout(dest_name)

            today_name = today_video_name()
            bshiz.cp_in_bucket(dest_name, today_name)
            set_cache_timeout(today_name)
