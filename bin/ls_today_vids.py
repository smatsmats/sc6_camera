#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time

import yaml
import errno
import re
import getopt
from time import sleep
import string
from string import Template
import urllib
import urllib2
import xml.parsers.expat
import pprint
from stat import *
from datetime import *
from atom import ExtensionElement

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
from optparse import OptionParser

gconfig_root = yaml.load(file("/usr/local/cam/conf/push2youtube_config.yml"))
gconfig = gconfig_root['Prod']
config_root = yaml.load(file("/usr/local/cam/conf/config.yml"))
config = config_root['Root1']

# this will soon come from command line or somewhere
vid_selector = "Daily"

# set the path for the video file binary
video_file = gconfig['Paths']['video_file']

youtube = None

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# CLIENT_SECRETS_FILE, name of a file containing the OAuth 2.0 information for
# this application, including client_id and client_secret. You can acquire an
# ID/secret pair from the API Access tab on the Google APIs Console
#   http://code.google.com/apis/console#access
# For more information about using OAuth2 to access Google APIs, please visit:
#   https://developers.google.com/accounts/docs/OAuth2
# For more information about the client_secrets.json file format, please visit:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
# Please ensure that you have enabled the YouTube Data API for your project.
CLIENT_SECRETS_FILE = gconfig['Google']['Auth']['client_secrets_file']

# soemt things still need developer key
DEVELOPER_KEY = gconfig['Google']['Auth']['api_key']

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
# A limited OAuth 2 access scope that allows for uploading files, but not other
# types of account access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Helpful message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console
https://code.google.com/apis/console#access

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage(gconfig['Google']['Auth']['oauth_token_file'])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    print flow
    credentials = run(flow, storage)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def getVidDateTime():
  vdate = os.stat(video_file).st_mtime
  return datetime.fromtimestamp(vdate)

def writeUrl(vid_url):
  url_file = config['Video'][vid_selector]['URL_file']
  try:
    f = open(url_file, 'w')
    f.write(vid_url)
    f.close
  except IOError, ioex:
    print 'errno:', ioex.errno
    print 'err code:', errno.errorcode[ioex.errno]
    print 'err message:', os.strerror(ioex.errno)

def search_todays_videos(options):
  search_options = options
  options.max_results = 50
  options.q = options.title
#  options.q = "SeaCrest 6 2015-04-21"
#  options.q = ""
  return youtube_search(options)

def youtube_search(search_options):
  global youtube
  youtube_public = youtube 
#  youtube_public = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#        developerKey=DEVELOPER_KEY)

  print "Searching for: " + search_options.q
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube_public.search().list(
    q=search_options.q,
    part="id,snippet",
    type="video",
    maxResults=search_options.max_results
  ).execute()

  videos = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      print "id: %s Title: %s Date / Time: %s" % (search_result["id"]["videoId"], search_result["snippet"]["title"], search_result["snippet"]["publishedAt"])
      videos.append(search_result["id"]["videoId"])

  return videos

def remove_old_video(id):
#  youtube_public = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#        developerKey=DEVELOPER_KEY)

  global youtube
  youtube2 = get_authenticated_service()
  print "going to remove: " + id
  res = youtube2.videos().delete(id=id).execute()
  print res

def initialize_upload(options):
  global youtube

  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  insert_request = youtube.videos().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
        title=options.title,
        description=options.description,
        tags=tags,
        categoryId=options.category
      ),
      status=dict(
        privacyStatus=options.privacyStatus
      )
    ),
    # chunksize=-1 means that the entire file will be uploaded in a single
    # HTTP request. (If the upload fails, it will still be retried where it
    # left off.) This is usually a best practice, but if you're using Python
    # older than 2.6 or if you're running on App Engine, you should set the
    # chunksize to something like 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  return resumable_upload(insert_request)


def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      status, response = insert_request.next_chunk()
      if 'id' in response:
        print "'%s' (video id: %s) was successfully uploaded." % (
          options.title, response['id'])
      else:
        exit("The upload failed with an unexpected response: %s" % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)

  return response


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("--file", dest="file", help="Video file to upload")
  parser.add_option("--title", dest="title", help="Video title",
    default="Test Title")
  parser.add_option("--description", dest="description",
    help="Video description",
    default="Test Description")
  parser.add_option("--category", dest="category",
    help="Numeric video category. " +
      "See https://developers.google.com/youtube/v3/docs/videoCategories/list",
          #youtube.videos().delete(id=ID).execute()
    default="22")
  parser.add_option("--keywords", dest="keywords",
    help="Video keywords, comma separated", default="")
  parser.add_option("--privacyStatus", dest="privacyStatus",
    help="Video privacy status: public, private or unlisted",
    default="public")
  (options, args) = parser.parse_args()

  # file
  options.file = gconfig['Paths']['video_file']

  # titles and stuff for video
  date_string = date.today().isoformat()
  # first build dictionary of substitutions
  d = dict([('date', date_string), ('underbar_date', date_string.replace('-', '_')), ('video_created', getVidDateTime().ctime()), ('video_uploaded', datetime.now().ctime())])
  
  options.title = Template(config['Video'][vid_selector]['TitleTemplate']).safe_substitute(d)
  d['title'] = options.title # make the title available for later substitution
  options.developer_tag = Template(config['Video'][vid_selector]['TitleTagTemplate']).safe_substitute(d)
  options.description = Template(config['Video'][vid_selector]['DescriptionTemplate']).safe_substitute(d)

  youtube = get_authenticated_service()

  search_todays_videos(options)
