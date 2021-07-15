#!/usr/bin/python3

import sys
import os
# import fcntl
from datetime import *
import argparse
import yaml
# import errno
# import xml.parsers.expat
# from stat import *
import pprint
import logging
import logging.config
from time import sleep
import smtplib
from email.mime.text import MIMEText

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_bucket_shiz
import sc6_bluecodestate
import sc6_sun
import sc6_image
import sc6_general
import sc6_config

# TODO
# bluecode and bluecode state


parser = argparse.ArgumentParser(description='mess with goog buckets.')
parser.add_argument("--mode", dest="mode", required=False,
                    help="prod / test / maybe others?", default="prod")
parser.add_argument("--debug", dest="debug", default=False,
                    required=False,
                    action='store_true',
                    help="should we spew")
parser.add_argument("--dryrun", dest="dryrun",
                    default=False,
                    action='store_true',
                    help="Folder and filename for destination",
                    required=False)
parser.add_argument("--force", dest="force",
                    default=False,
                    action='store_true',
                    help="ignore sun and just do it",
                    required=False)
args = parser.parse_args()

cfg = sc6_config.Config(config_file='/usr/local/cam/conf/config.yml',
                        mode=args.mode)
config = cfg.get_config()

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger('cam_collect_images')
logger.setLevel(logging.DEBUG)

debug = config['Debug'] or args.debug
if debug:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.debug("***** STARTING *****")


def mail_message(subj, body):

    sender = config['Email']['From']
    receivers = (config['Email']['To'])
    msg = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(sender,
                                                       receivers,
                                                       subj,
                                                       body)
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, msg)
    except SMTPException:
        print("Error: unable to send email")
        sys.exit()
    else:
        logger.debug("Successfully sent email")


def get_cache_control(fn):
    cache_timeout = config['BucketShiz']['Cache']['MaxAge'][fn]
    cache_control = config['BucketShiz']['Cache']['CacheControl']

    cachecontrol_val = "'{}, max-age={}'".format(cache_control, cache_timeout)
    return cachecontrol_val


mail_message(__file__ + " started", __file__ + " started")

# prime bluecode
bcs = sc6_bluecodestate.BCS(config=config, debug=debug)
logger.debug("primed bluecode is: {}".format(bcs.getBluecode()))

# initialize some timing things
sleep_time = config['General']['ImageInterval']['SunUp']
sleep_time_night = config['General']['ImageInterval']['SunDown']
fetch_sleep = None
gstore_interval = config['BucketShiz']['PushInterval']['SunUp']
prev_failed_start = 0
mysun = sc6_sun.SC6Sun(config=config, debug=debug)
last_gstore_push = mysun.a_long_time_ago()
end_time = None
did_post_sun = False


# www_dir = get_www_dir($size, $mode)
# www_image_orig = $www_dir . config['Image']['File']['orig]
# www_image_50pct = $www_dir . config['Image']['File']['50pct']

fn_orig = config['Image']['File']['orig']
current_bucket_orig = os.path.join(config['BucketShiz']['CurrentDir'],
                                   fn_orig)
current_bucket_orig_cc = get_cache_control(fn_orig)

fn_50pct = config['Image']['File']['50pct']
current_bucket_50pct = os.path.join(config['BucketShiz']['CurrentDir'],
                                    fn_50pct)
current_bucket_50pct_cc = get_cache_control(fn_50pct)

public_bucket_orig = os.path.join(config['BucketShiz']['PublicDir'],
                                  fn_orig)
public_bucket_orig_cc = get_cache_control(fn_orig)

public_bucket_50pct = os.path.join(config['BucketShiz']['PublicDir'],
                                   fn_50pct)
public_bucket_50pct_cc = get_cache_control(fn_50pct)

blue_bucket_orig = os.path.join(config['BucketShiz']['BlueistDir'],
                                  fn_orig)
blue_bucket_orig_cc = get_cache_control(fn_orig)

blue_bucket_50pct = os.path.join(config['BucketShiz']['BlueistDir'],
                                   fn_50pct)
blue_bucket_50pct_cc = get_cache_control(fn_50pct)

# public = config['BucketShiz']['PublicDir']
# public_image_orig = image_set.www_public_image_orig
# public_image_50pct = image_set.www_public_image_50pct
# blue_bucket = config[BucketShiz']['BlueistDir']
# blueist_file_50pct = get_www_dir("", $main::mode) .  config[BlueCode']['BlueistImage'} . "_50pct"
# blueist_file_orig = get_www_dir("", $main::mode) . config[BlueCode']['BlueistImage'} . "_orig"

mybuck = sc6_bucket_shiz.MyBucket(config)
while True:
    dt = mysun.maybenewday()
    if mysun.is_sun() or args.force:
        logger.debug("Sun is up! {}".format(dt))
        did_post_sun = False
        fetch_sleep = sleep_time

        # fetch an image
        image_set = sc6_image.ImageSet(config=config, debug=debug)
        result = image_set.fetch()

        if not result:
            logger.debug("Image fetch failed!!")
            fetch_sleep = 5  # skip sleeping
            prev_failed_start = dt
        else:
            image_set.getBluecode()
            image_set.make_public_version()
            image_set.do_image_overlays()
            image_set.resizes_and_links()

            # normal sleep, but prune sleep time to account for processing
            end_time = mysun.just_get_dt()
            if prev_failed_start:
                duration = (end_time - prev_failed_start).seconds
                fetch_sleep = sleep_time - duration
                prev_failed_start = 0
            else:
                duration = (end_time - dt).seconds
                fetch_sleep = sleep_time - duration


            # check blue code and push blue file maybe
#            if False:
            if bcs.checkBluecode(image_set):
                logger.debug("new blue")
                # maybe do something local with blue file?
                if config['BucketShiz']['Enable']:
                    logger.debug("pushing up new blueist")
                    mybuck.upload_blob(image_set.public_output,
                                       blue_bucket_orig)
                    mybuck.set_blob_cachecontrol(blue_bucket_orig,
                                                 blue_bucket_orig_cc)
    
                    mybuck.upload_blob(image_set.public_output_50pct,
                                       blue_bucket_50pct)
                    mybuck.set_blob_cachecontrol(blue_bucket_50pct,
                                                 blue_bucket_50pct_cc)

            # push the images to gstore
            # this should really be a seperate loop or even process,
            # but for now it's here
            if config['BucketShiz']['Enable']:
                next_push = last_gstore_push + timedelta(seconds=gstore_interval)
                if end_time >= next_push:
                    logger.debug("lets push to buckets!")
                    last_gstore_push = end_time
    
                    mybuck.upload_blob(image_set.output,
                                       current_bucket_orig)
                    mybuck.set_blob_cachecontrol(current_bucket_orig,
                                                 current_bucket_orig_cc)
    
                    mybuck.upload_blob(image_set.output_50pct,
                                       current_bucket_50pct)
                    mybuck.set_blob_cachecontrol(current_bucket_50pct,
                                                 current_bucket_50pct_cc)
    
                    mybuck.upload_blob(image_set.public_output,
                                       public_bucket_orig)
                    mybuck.set_blob_cachecontrol(public_bucket_orig,
                                                 public_bucket_orig_cc)
    
                    mybuck.upload_blob(image_set.public_output_50pct,
                                       public_bucket_50pct)
                    mybuck.set_blob_cachecontrol(public_bucket_50pct,
                                                 public_bucket_50pct_cc)
                else:
                    logger.debug("No gstore push until {}".format(str(next_push)))

    else:
        logger.debug("Sun is down! {}".format(dt))
        fetch_sleep = sleep_time_night

        # do some things during the first hour the sun is down, but only once
        if mysun.is_hour_after_dusk() and not did_post_sun:
            did_post_sun = True
            prev_failed_start = 0
            last_gstore_push = mysun.a_long_time_ago()

            bcs.clear()  # clear bluecode
            # cp blueist to current
#            current_dir = config['BucketShiz']['CurrentDir']
#            blueist_dir = config['BucketShiz']['BlueistDir']
#            public_dir = config['BucketShiz']['PublicDir']
#            blueist_image_orig = $blueist_dir . "/" . config['Image']['File']['orig]
#            blueist_image_50pct = $blueist_dir . "/" . config['Image']['File']['50pct']
#            $gstore.cp_bucket2bucket($blueist_image_orig, $current_dir)
#            $gstore.cp_bucket2bucket($blueist_image_orig, $public_dir)
# # lets not dork with 50pct rigth now
# #            $gstore.cp_bucket2bucket($blueist_image_50pct, $current_dir)

    if fetch_sleep < 0:
        print("WTF! fetch_sleep: {} prev_failed_start: {} sleep_time: {} \
            end_time: {}".format(fetch_sleep,
                                 prev_failed_start,
                                 sleep_time,
                                 end_time))
        print("setting fetch_sleep to sleep_time: {}".format(sleep_time))
        fetch_sleep = sleep_time

    logger.debug("Gonna sleep: {}".format(fetch_sleep))
    sleep(fetch_sleep)
