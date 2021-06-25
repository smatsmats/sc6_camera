#!/usr/bin/python3

#
#use SC6::Cam::General
#use SC6::Cam::Config
#use SC6::Cam::Sun

# todo
# - Concurrance locking
# - deal with building / pushing a date other than today

mode = "prod"
dryrun = 0
sleep_time = 30

import sys
sys.path.append('/usr/local/cam/lib/pythonlib')
import bucket_shiz

import os
import fcntl
from datetime import *
import argparse
import yaml
import errno
import xml.parsers.expat
from stat import *
import logging
import logging.config


with open('/usr/local/cam/conf/push_video_config.yml', 'r') as file:
    gconfig_root = yaml.safe_load(file)
gconfig = gconfig_root['prod']
with open('/usr/local/cam/conf/config.yml', 'r') as file:
    config_root = yaml.safe_load(file)
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger('build_timelapse')


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
def push_to_bucket():

    # deal with date

    out = get_video_file(dt, format, 'mp4', mode)
    cmd = " --file " + out
#    rcode = my_do_cmd($cmd, $dryrun)
#    return $rcode


class Vmeta:
    def __init__(self):
        self.title = "test title"
        self.tags = "test tags"
        self.description = "test description"
        self.date = "test date"


if __name__ == '__main__':

# TODO
#    # lock 
#    try:
#        lokky = open(lock_file, 'w+')
#        fcntl.flock(lokky, fcntl.LOCK_EX | fcntl.LOCK_NB)
#        break
#    except IOError as e:
#        # raise on unrelated IOErrors
#        if e.errno != errno.EAGAIN:
#            raise
#        else:
#
#            time.sleep(0.1)
#    fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)


    argparser = argparse.ArgumentParser(description='build time lapse video.')
    argparser.add_argument("--file", dest="file", help="Video file to upload")
    argparser.add_argument("--directory", dest="directory", help="a directory")
    argparser.add_argument("--fps", dest="fps", help="frames per second")
    argparser.add_argument("--mode", dest="mode", help="prod, test, dev", 
                           default="prod")
    argparser.add_argument("--date", dest="date_in", help="override date")
# how we implement something like trickle and throttleing?  
#    argparser.add_argument("--trickle", dest="trickle",  action='store_true',
#                           default=False,
#                           help="trickle the data in")
#    argparser.add_argument("--trickle-cmd", dest="trickle_cmd",  
#                           default="trickle -s -u 200",
#                           help="trickle the data in")
    argparser.add_argument("--dry-run", action='store_true', dest='dryrun',
                           help="don't actually do anything")
    argparser.add_argument("--force", action='store_true', dest='force',
                           help="force thigns to happen")
    argparser.add_argument("--videoDate", dest="videoDate", default="",
                           help="video is for some other date than today")
    argparser.add_argument("--keep", action='store_true',
                           default=False,
                           help="keep video, don't delete")
    argparser.add_argument("--silent", action='store_true', dest='silent',
                           default=False,
                           help="no output")
    argparser.add_argument("--debug", action='store_true', dest='debug',
                           help="lots of output",
                           default=config['Debug'])
    argparser.add_argument("--dontUpload", action='store_true',
                           help="for testing, don't actually do the upload")
    args = argparser.parse_args()

    # debug trumps silent
    if args.debug && args.silent:
        args.silent = False

    # file
    if args.file is None:
        args.file = gconfig['Paths']['video_file']

    # titles and stuff for video
    if args.videoDate:
        date_string = args.videoDate
    else:
        date_string = date.today().isoformat()

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

#    # release lock
#    fcntl.flock(x, fcntl.LOCK_UN)
