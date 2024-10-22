#!/usr/local/cam/env/bin/python3

import datetime
import os
import sys
from dateutil.parser import parse
import argparse
import yaml
import logging
import logging.config
import time
from pytz import timezone
import smtplib, ssl

ONE_HOUR = 60 * 60

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_bucket_shiz
import sc6_bluecodestate
import sc6_sun
import sc6_image
import sc6_general
import sc6_config

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

body = ''

parser = argparse.ArgumentParser(description='check gaps in cam images.')
parser.add_argument("--mode", dest="mode", required=False,
                    help="prod / test / maybe others?", default="prod")
parser.add_argument("--debug", dest="debug", default=False,
                    required=False,
                    action='store_true',
                    help="should we spew")
parser.add_argument("--email", dest="email", default=False,
                    required=False,
                    action='store_true',
                    help="should we email")
parser.add_argument("--only-last-hour", dest="only_last_hour",
                    default=False,
                    required=False,
                    action='store_true',
                    help="only report issues from tha last hour")
parser.add_argument("--date", dest="date",
                    default=None,
                    help="date of files to check",
                    required=None)
parser.add_argument("--directory", dest="directory",
                    default=None,
                    help="directory to check (overrules date based directory)",
                    required=False)
parser.add_argument("--gap", dest="ok_gap",
                    type=int,
                    default=45,
                    help="OK gap in images",
                    required=False)
args = parser.parse_args()

email = args.email

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

now = time.time()
directory = args.directory

if directory is None:
    if args.date:
        if debug:
            print(args.date)
        try:
            seconds = parse(args.date).timestamp()
        except ValueError:
            print(f"Error can't parse date: {args.date}")
            sys.exit(1)
        if debug:
            print(seconds)
        dt = datetime.datetime.fromtimestamp(seconds, tz=timezone(config['General']['Timezone']))
    else:
        dt = datetime.datetime.now(tz=timezone(config['General']['Timezone']))
    directory = sc6_general.get_image_dir(dt, "orig", args.mode)

if debug:
    print("directory:", directory)

try:
    files = os.listdir(directory)
except OSError as e:
    print(e)
    sys.exit(1)

last_was_big = False
last = 0
for f in sorted(files):
    if f in (".", ".."):
        continue
#    if debug:
#        print(f)
    n = int(f.replace("image", "").replace("_orig.jpg", ""))
    if last == 0:
        last = n
    if n - last <= args.ok_gap:
        last_was_big = False
    else:
        if not args.only_last_hour or now - n < ONE_HOUR:
            all_secs = n - last
            mins = all_secs // 60
            secs = all_secs % 60
            if mins == 1:
                min_word = "minute"
            else:
                min_word = "minutes"
            t_string = f"{mins} {min_word} {secs} seconds ({all_secs} secs)"
            s = f"Big gap: {t_string} at {datetime.datetime.fromtimestamp(n).strftime('%c')}"
            if last_was_big:
                s += " prior was also big"
            if email:
                s += "\n"
                body += s
            else: 
                print(s)
        last_was_big = True
    last = n

if email:
    if body != '':
        mail_message("SC6 Camera: big gap(s)", body)
