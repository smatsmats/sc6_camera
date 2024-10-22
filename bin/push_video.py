#!/usr/bin/python

import sys
sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_bucket_shiz

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
