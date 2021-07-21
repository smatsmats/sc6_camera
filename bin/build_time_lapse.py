#!/usr/bin/python3

#  todo
#  - Concurrance locking
#  - deal with building / pushing a date other than today
#  - make collect_metadata meaningful
#  - trickle, do we need trickle?

import sys
import os
import fcntl
from datetime import *
import argparse
import yaml
import errno
import logging
import logging.config
import pprint

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_bucket_shiz
import sc6_sun
import sc6_general
import sc6_config


def today_video_name():
    vdir = config['BucketShiz']['VideoDir']
    t_name = config['BucketShiz']['TodayVideoName']
    out = vdir + "/" + t_name
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
    except KeyError:
        cache_timeout = \
            config['BucketShiz']['Cache']['MaxAge']['default_video']
    cachecontrol_val = "'" + cache_control + ", max-age=" + \
        str(cache_timeout) + "'"
    bshiz.set_blob_cachecontrol(dest_name, cachecontrol_val)


class Vmeta:
    def __init__(self):
        self.title = "test title"
        self.tags = "test tags"
        self.description = "test description"
        self.date = "test date"


def collect_metadata():
    h = {}
    h['title'] = "test title"
    h['tags'] = "test tags"
    h['description'] = "test description"
    h['date'] = "test date"

    return h


def make_moovie(dt, size, mode, args):
    image_dir = 'public'
    out = sc6_general.get_video_file(dt, size, 'avi', mode)

    if args.directory:
        image_dir = args.directory
    else:
        image_dir = sc6_general.get_image_dir(dt, image_dir, mode)

    if args.fps:
        fps = args.fps
    else:
        fps = config['FPS']

    files_in = 'mf://{}/*_{}.jpg'.format(image_dir, size)
    mf = 'w={}:h={}:type={}:fps={}'.format(config['Sizes'][size]['width'],
                                           config['Sizes'][size]['height'],
                                           config['Type'],
                                           fps)

    cmd = ["mencoder", "-msglevel", "all=1",
           "-nosound", "-noskip", "-oac", "copy",
           "-ovc", "copy", "-o", out, "-mf", mf, files_in]
    logger.debug(" ".join(cmd))

    if not args.dryrun:
        return(sc6_general.run_cmd(cmd, debug))


def compress_moovie(dt, size, mode, metadata, args):
    infile = sc6_general.get_video_file(dt, size, 'avi', mode)
    outfile = sc6_general.get_video_file(dt, size, 'mp4', mode)

    cmd = [config['Bins']['ffmpeg'], "-y", "-loglevel",
           config['FFMpegLogLevel'], "-i", infile]
    for k in metadata.keys():
        cmd.append("-metadata")
        cmd.append(k + "='" + metadata[k] + "'")
    the_rest = ["-r", "25", "-s", "1920x1080", "-vcodec",
                "libx264", "-b:v", "30000k", outfile]
    cmd = cmd + the_rest

    if debug:
        print(" ".join(cmd))
    logger.debug(" ".join(cmd))

    if not args.dryrun:
        return(sc6_general.run_cmd(cmd, debug))


def cleanup(size, mode, args):

    # don't delete video files if we were asked to keep them
    if args.keep:
        return

    if config['Video']['Daily']['Disposable']:
        out = sc6_general.get_video_file(dt, size, 'mp4', mode)
        try:
            os.unlink(out)
        except OSError as error:
            print("Can't remove {}: {}".format(out, error))
            pass
        out = sc6_general.get_video_file(dt, size, 'avi', mode)
        try:
            os.unlink(out)
        except OSError as error:
            print("Can't remove {}: {}".format(out, error))
            pass


if __name__ == '__main__':

#  lock
#  try:
#         lokky = open(lock_file, 'w+')
#         fcntl.flock(lokky, fcntl.LOCK_EX | fcntl.LOCK_NB)
#         break
#  except IOError as e:
#         # raise on unrelated IOErrors
#         if e.errno != errno.EAGAIN:
#             raise
#         else:
#
#             time.sleep(0.1)
#  fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)

    argparser = argparse.ArgumentParser(description='build time lapse video.')
    argparser.add_argument("--file", dest="file",
                           required=False,
                           help="Video file to upload")
    argparser.add_argument("--directory", dest="directory",
                           default=None,
                           help="a directory")
    argparser.add_argument("--fps", dest="fps", help="frames per second")
    argparser.add_argument("--mode", dest="mode", help="prod, test, dev",
                           default="prod")
    argparser.add_argument("--date", dest="date_in", help="override date")
#  how we implement something like trickle and throttleing?
#     argparser.add_argument("--trickle", dest="trickle",  action='store_true',
#                            default=False,
#                            help="trickle the data in")
#     argparser.add_argument("--trickle-cmd", dest="trickle_cmd",
#                            default="trickle -s -u 200",
#                            help="trickle the data in")
    argparser.add_argument("--dryrun", action='store_true', dest='dryrun',
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
                           default=False)
    argparser.add_argument("--dontUpload", action='store_true',
                           help="for testing, don't actually do the upload")
    args = argparser.parse_args()

    cfg = sc6_config.Config(mode = args.mode)
    config = cfg.get_config()

    #  create logger
    logger = logging.getLogger('build_timelapse')

    # either from the cmd line or config    
    debug = args.debug or config['Debug']

    # debug trumps silent
    if debug and args.silent:
        args.silent = False

    if debug:
        print("Debug output on")

    mysun = sc6_sun.SC6Sun(config)
    dt = mysun.get_dt()

    # titles and stuff for video
    if args.videoDate:
        date_string = args.videoDate
    else:
        date_string = dt.strftime("%Y%m%d")

#    date_from_args = False
#    if date:
#        if debug:
#            print date, "\n"
#        my (seconds, error) = parsedate($date)
#        if ! seconds:
# 	   print "Error can't parse date: $date : $error\n"
#            exit(1)
#        else:
# 	   print seconds, "\n" if ( debug )
#            dt = DateTime->from_epoch(
#                    epoch => $seconds, time_zone =>
#                    config['General']['Timezone'] )
#        force = 1
#        date_from_args = 1
#    else:
#        dt = mysun.get_dt()

    if debug:
        print("Now: ", dt)

    if args.directory:
        print(" We hav a direcotry to process: ", args.directory)
        # maybe check the directory
        # specified directory implies force
        args.force = True
    elif args.force:
        if debug:
            print(" We're forced to do this")
    elif mysun.is_sun():
        if debug:
            print(" Sun is up!")
    elif mysun.is_hour_after_dusk():
        if debug:
            print(" Sun is down, but for less than an hour!")
    else:
        if debug:
            print(" Sun is down!")
        sys.exit()

    if args.dryrun and not args.silent:
        print("This is a dry run, not doing anything")

    # make sure we have the directory we're going to work with
    if args.directory:
        image_dir = args.directory
    else:
        image_dir = sc6_general.get_image_dir(dt, "public", args.mode)
    if not os.path.exists(image_dir) or len(os.listdir(image_dir) ) == 0:
        print("directory {} missing or empty, quitting".format(image_dir))
        sys.exit()

    size = 'orig'
    make_moovie(dt, size, args.mode, args)

    metadata = collect_metadata()
    compress_moovie(dt, size, args.mode, metadata, args)

    bshiz = sc6_bucket_shiz.MyBucket(config)

    logger.debug("upload logic")
    if args.file:
        if not os.path.exists(args.file):
            exit("Please specify a valid file using the --file= parameter.")
        vid_file = args.file
    else:
        vid_file = sc6_general.get_video_file(dt, size, 'mp4', args.mode)
        dest_name = get_dest_name()
        if debug:
            print(dest_name)

        if args.dontUpload or args.dryrun:
            logger.info("dontUpload is set, we won't upload")
        else:
            # send-up the video and set cache
            logger.info("upload {} to {}".format(vid_file, dest_name))
            bshiz.upload_blob(vid_file, dest_name)
            set_cache_timeout(dest_name)

            today_name = today_video_name()
            bshiz.cp_in_bucket(dest_name, today_name)
            logger.info("going to copy {} to {}".format(dest_name, today_name))
            set_cache_timeout(today_name)

    cleanup(size, args.mode, args)

    #     # release lock
    #     fcntl.flock(x, fcntl.LOCK_UN)
