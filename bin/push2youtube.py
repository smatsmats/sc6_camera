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

import yaml
gconfig_root = yaml.load(file("/usr/local/cam/conf/push2youtube_config.yml"))
gconfig = gconfig_root['Root1']
config_root = yaml.load(file("/usr/local/cam/conf/config.yml"))
config = config_root['Root1']

# this will soon come from command line or somewhere
vid_selector = "Daily"

# set the path for the video file binary
video_file = gconfig['Paths']['video_file']

def PrintEntryDetails(entry):
  print 'Video title: %s' % entry.media.title.text
  print 'Video published on: %s ' % entry.published.text
  print 'Video description: %s' % entry.media.description.text
  print 'Video category: %s' % entry.media.category[0].text
  print 'Video tags: %s' % entry.media.keywords.text
  print 'Video watch page: %s' % entry.media.player.url
  print 'Video flash player URL: %s' % entry.GetSwfUrl()
  print 'Video duration: %s' % entry.media.duration.seconds

  # non entry.media attributes
  print 'Video geo location: %s' % entry.geo.location()
  print 'Video view count: %s' % entry.statistics.view_count
  print 'Video rating: %s' % entry.rating.average

  # show alternate formats
  for alternate_format in entry.media.content:
    if 'isDefault' not in alternate_format.extension_attributes:
      print 'Alternate format: %s | url: %s ' % (alternate_format.type,
                                                 alternate_format.url)

  # show thumbnails
  for thumbnail in entry.media.thumbnail:
    print 'Thumbnail url: %s' % thumbnail.url

def PrintVideoFeed(feed):
  for entry in feed.entry:
    print "in for entry in feed.entry in PrintVideoFeed"
    PrintEntryDetails(entry)

def DeleteEntry(entry):
  print "***** Gonna delete ", entry.media.title.text, "updated:", entry.published.text
  response = yt_service.DeleteVideoEntry(entry)
  if response:
    print 'Old video successfully deleted'

def Vid2Nuke(feed):
  for entry in feed.entry:
    if entry.media.title.text == title:
      return(entry)

def getDateString(days):
  today = date.today()
  someday = today - timedelta(days)
  return someday.isoformat()

def getVidDateTime():
  vdate = os.stat(video_file).st_mtime
  return datetime.fromtimestamp(vdate)

# 3 handler functions for parsing responce
def start_element(name, attrs):
#  print 'Start element:', name, attrs
  if ( name == 'ns4:content' ):
#    print "+++++ found one", name
#    print "+++>", attrs, "<+++"
    vid_url = attrs['url']
    print ">>>>>>>>", str(vid_url), "<<<<<<<"
    f = open('/var/www/bib/camera/tl_url', 'w')
    f.write(vid_url)
    f.close
def end_element(name):
    pass
#    print 'End element:', name
def char_data(data):
    pass
#    print 'Character data:', repr(data)

# create the service
yt_service = gdata.youtube.service.YouTubeService()
# Turn on HTTPS/SSL access.
yt_service.ssl = True
yt_service.developer_key = gconfig['Google']['YT']['dev_key']
yt_service.client_id = gconfig['Google']['YT']['client_id']

# login
yt_service.email = gconfig['Google']['YT']['service_email']
yt_service.password = gconfig['Google']['YT']['service_password']
yt_service.source = gconfig['Google']['YT']['service_source']
yt_service.ProgrammaticLogin()

# titles and stuff for video
date_string = getDateString(0)
# first build dictionary of substitutions
d = dict([('date', date_string), ('underbar_date', date_string.replace('-', '_')), ('video_created', str(getVidDateTime())), ('video_uploaded', str(datetime.now()))])

title = Template(config['Video'][vid_selector]['TitleTemplate']).safe_substitute(d)
d['title'] = title # make the title available for later substitution
title_tag = Template(config['Video'][vid_selector]['TitleTagTemplate']).safe_substitute(d)
description = Template(config['Video'][vid_selector]['DescriptionTemplate']).safe_substitute(d)

## why doesn't this work?
#developer_tag_uri = 'http://gdata.youtube.com/feeds/videos/-/%7Bhttp%3A%2F%2Fgdata.youtube.com%2Fschemas%2F2007%2Fdevelopertags.cat%7D' + title_tag
#print "developer_tag_uri:", developer_tag_uri
#print
#PrintVideoFeed(yt_service.GetYouTubeVideoFeed(developer_tag_uri))

# prepare a media group object to hold our video's meta-data
my_media_group = gdata.media.Group(
  title=gdata.media.Title(text=title),
  description=gdata.media.Description(description_type='plain', text=description),
  category=[gdata.media.Category(text='Travel', scheme='http://gdata.youtube.com/schemas/2007/categories.cat')],
  keywords=gdata.media.Keywords(text='travel'),
  player=None
)
#  private=gdata.media.Private(),

# prepare a geo.where object to hold the geographical location
# of where the video was recorded
where = gdata.geo.Where()
where.set_location((37.0,-122.0))

# if you want video unlisted, replace attributes line with this:
#    "attributes": {'action': 'list', 'permission': 'denied'},
kwargs = {
    "namespace": YOUTUBE_NAMESPACE,
    "attributes": {'action': 'list', 'permission': 'allowed'},
}
extension = ([ExtensionElement('accessControl', **kwargs)])

# create the gdata.youtube.YouTubeVideoEntry
video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group,
    geo=where, extension_elements=extension)

# add developer tag
print "title", title
print "title tag", title_tag
developer_tags = [title_tag]
video_entry.AddDeveloperTags(developer_tags)

# look for my videos
username = 'default'
uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % username
# remember old one
old_video = Vid2Nuke(yt_service.GetYouTubeVideoFeed(uri))

# add it
print "Uploading video"
new_entry = yt_service.InsertVideoEntry(video_entry, video_file)
if new_entry:
  print 'Video upload sucessful, being processed'

# check status
upload_status = yt_service.CheckUploadStatus(new_entry)
if upload_status is not None:
  print "state:", upload_status[0]
  print "detailed:", upload_status[1]

# build parser for responce
p = xml.parsers.expat.ParserCreate()
p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

# parse responce - including writing-out video url
p.Parse(str(new_entry))

# remove old video
DeleteEntry(old_video)
