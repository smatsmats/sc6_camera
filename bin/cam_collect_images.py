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
import logging
import logging.config
from time import sleep

sys.path.append('/usr/local/cam/lib/pythonlib')
import bucket_shiz
import sc6_sun

# TODO
# startup mail


# use SC6::Cam::General
# use SC6::Cam::BlueCodeState
# use SC6::Cam::Config
# use SC6::Cam::Image
# use SC6::Cam::Sun
# use SC6::Cam::GStore

with open('/usr/local/cam/conf/config.yml', 'r') as file:
    config_root = yaml.safe_load(file)
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger('build_timelapse')

debug = config['Debug']
if debug:
    print("***** STARTING *****")
    logger.debug("***** STARTING *****")


# force = 0
# mode = "prod"
# dryrun = 0
# current_bluecode
# $result = GetOptions (  "n|dry-run" => \$dryrun,
#                         "f|force"  => \$force,
#                         "h|help"  => \&usage,
#                         "m|mode=s"  => \$mode,
#                         "d|debug+"  => \$debug)
#     print "usage: $0 [-d|--debug] [-f|--force] [-h|--help] [-n|--dry-run] [-m|mode=mode]\n"
#     print "\t-f|--force   - Force collecting of the  files\n"
#     print "\t-h|--help    - This message\n"
#     print "\t-n|--dry-run - perform a trial run with no changes made\n"
#     print "\t-m|--mode    - mode, prod or test\n"

# # startup mail
# startup_mail()

# # prime bluecode
# push_to_google = config['BucketShiz']['Enable']
# bcr = new SC6::Cam::BlueCodeState($mode, $dryrun)

# print "primed bluecode is: ", $bcr->getBluecode(), "\n" if ( $debug )
# our $gstore = new SC6::Cam::GStore()

# initialize some timing things
sleep_time = config['General']['ImageInterval']['SunUp']
sleep_time_night = config['General']['ImageInterval']['SunDown']
fetch_sleep = None
last_gstore_push = 0
gstore_interval = config['BucketShiz']['PushInterval']['SunUp']
prev_failed_start = 0
mysun = sc6_sun.SC6Sun()
end_time = None
sun_status = None
force = False

while True:
    dt = mysun.maybenewday()  
    if mysun.is_sun() or force:
        print("Sun is up! {}".format(dt))
        sun_status = 1
        fetch_sleep = sleep_time

        # fetch an image
        image_set = new SC6::Cam::Image($dt, $mode, $dryrun, $s)
        result = image_set->fetch()
#        result = True

#         if ( ! $result ) {
#             print "Image fetch failed!!!!!\n"
#             $fetch_sleep = 0;  # skip sleeping
#             $prev_failed_start = $dt->epoch()
#         ]
#         else {
#             image_set->getBluecode()
#             image_set->make_public_version()
#             image_set->do_image_overlays()
#             image_set->resizes_and_links()
#
#             # normal sleep, but prune sleep time to account for processing
#             $end_time = DateTime->now(  time_zone => config['General']['Timezone'} )
#             if ( $prev_failed_start != 0 ) {
#                 $fetch_sleep = $sleep_time - ($end_time->epoch() - $prev_failed_start)
#             } 
#             else {
#                 $fetch_sleep = $sleep_time - ($end_time->epoch() - $dt->epoch())
#             ]
#             $prev_failed_start = 0
#
#             # file and dir locations
#             # this directory crap is a mess, fix it.  
#             current = config['BucketShiz']['CurrentDir']
#             www_dir = get_www_dir($size, $mode)
#             www_image_orig = $www_dir . config['Image']['File']['orig]
#             www_image_50pct = $www_dir . config['Image']['File']['50pct']
#             public = config['BucketShiz']['PublicDir']
#             public_image_orig = image_set.www_public_image_orig
#             public_image_50pct = image_set.www_public_image_50pct
#             blue_bucket = $main::config->{BucketShiz']['BlueistDir']
#             blueist_file_50pct = get_www_dir("", $main::mode) . $main::config->{BlueCode']['BlueistImage'} . "_50pct"
#             blueist_file_orig = get_www_dir("", $main::mode) . $main::config->{BlueCode']['BlueistImage'} . "_orig"

#             # check blue code and push blue file maybe
#             if ( $bcr->checkBluecode(image_set) == 1 ) {
#                 print "new blue\n"
#                 $gstore->cp_fs2bucket($public_image_orig, $blue_bucket)
#                 $gstore->cp_fs2bucket($public_image_50pct, $blue_bucket)
#             ]
#             else {
#                 print "old blue\n"
#             ]

#             # push the images to gstore
#             # this should really be a seperate loop or even process, but for now it's here
#             if ( $last_gstore_push + $gstore_interval < $end_time->epoch() ) { 
#                 $gstore->cp_fs2bucket($www_image_orig, $current)
#     # skip copying up 50pct images
#     #            $gstore->cp_fs2bucket($www_image_50pct, $current)
#     
#                 $gstore->cp_fs2bucket($public_image_orig, $public)
#     # skip copying up 50pct images
#     #            $gstore->cp_fs2bucket($public_image_50pct, $public)
#     
#                 $last_gstore_push = $end_time->epoch()
#             ]
#             else {
#                 print "No gstore push until ", scalar localtime($last_gstore_push + $gstore_interval), "\n"
#             ]
#     
#         ]

#     ]
    else:
        print("Sun is down! {}".format(dt))
        fetch_sleep = sleep_time_night

#         # do some things during the first hour the sun is down, but only once
#         if ( $s->is_hour_after_dusk($dt) && $sun_status == 1 ) {
#             $sun_status = 0
#             $bcr->clear();  # clear bluecode
#             $prev_failed_start = 0;   # make sure this doesn't carry over from the previous day
#             $last_gstore_push = 0
#  
#             # cp blueist to current
#             current_dir = config['BucketShiz']['CurrentDir']
#             blueist_dir = config['BucketShiz']['BlueistDir']
#             public_dir = config['BucketShiz']['PublicDir']
#             blueist_image_orig = $blueist_dir . "/" . config['Image']['File']['orig]
#             blueist_image_50pct = $blueist_dir . "/" . config['Image']['File']['50pct']
#             $gstore->cp_bucket2bucket($blueist_image_orig, $current_dir)
#             $gstore->cp_bucket2bucket($blueist_image_orig, $public_dir)
# # lets not dork with 50pct rigth now
# #            $gstore->cp_bucket2bucket($blueist_image_50pct, $current_dir)
#         ]
#     ]

#     if ( $fetch_sleep < 0 ) {
#         print "WTF! fetch_sleep: $fetch_sleep  prev_failed_start: $prev_failed_start sleep_time: $sleep_time end_time: ", $end_time->epoch(), "\n"
#         print "setting fetch_sleep to sleep_time: $sleep_time\n"
#         $fetch_sleep = $sleep_time
#     ]
#     print "Gonna sleep: $fetch_sleep\n\n" if ( $debug )
    sleep(fetch_sleep)
#     print "done sleeping; sleep: $fetch_sleep\n\n" if ( $debug )
# ]


# ]

# sub startup_mail {
#     mail_message = $0 . " started"
#     mail_recip = config['General']['MailRecipient']
#     send_mail($mail_message, $mail_recip)
# ]

# sub send_mail {
#     my($mess, $recip) = @_

#     mail_cmd = config['General']['MailCommand']
#     cmd = "$mail_cmd -s \"$mess\" $recip"
#     print $cmd, "\n"
#     open MAIL, "| $cmd" or die "Can't open $mail_cmd: $!\n"
#     print MAIL $mess
#     close MAIL
# ]
