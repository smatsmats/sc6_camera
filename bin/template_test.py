#!/usr/bin/python

import sys
import os
import re
import getopt
import time
from time import sleep
import string
from string import Template
import urllib
import urllib2
import gdata.youtube
import gdata.youtube.service
import xml.parsers.expat
from stat import *
from datetime import *

from gdata.media import YOUTUBE_NAMESPACE
from atom import ExtensionElement

def getDateString(days):
  today = date.today()
  someday = today - timedelta(days)
  return someday.isoformat()

def getVidDateTime():
  vdate = os.stat(video_file).st_mtime
  return datetime.fromtimestamp(vdate)


import yaml
gconfig = yaml.load(file("/usr/local/cam/conf/push2youtube_config.yml"))
config_root = yaml.load(file("/usr/local/cam/conf/config.yml"))
config = config_root['Root1']

# set the path for the video file binary
video_file = gconfig['Root1']['Paths']['video_file']

vid_selector = "Daily"
print config['Video'][vid_selector]

#title = Template

date_string = getDateString(0)
d = dict([('date', date_string), ('underbar_date', date_string.replace('-', '_')), ('video_created', str(getVidDateTime())), ('video_uploaded', str(datetime.now()))])

title = Template(config['Video'][vid_selector]['TitleTemplate']).safe_substitute(d)
print title
d['title'] = title
titletag = Template(config['Video'][vid_selector]['TitleTagTemplate']).safe_substitute(d)
print titletag
description = Template(config['Video'][vid_selector]['DescriptionTemplate']).safe_substitute(d)
print description

