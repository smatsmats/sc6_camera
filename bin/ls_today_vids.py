#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time
from time import localtime, strftime
from time import sleep
import dateutil.parser
from pytz import timezone

import yaml
import errno
import re
import getopt
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
# from oauth2client.tools import run
from optparse import OptionParser

import logging
import logging.config

# exit codes for Nagios monitoring
EXIT_CODE_OK = 0
EXIT_CODE_WARNING = 1
EXIT_CODE_CRITICAL = 2
EXIT_CODE_UNKNOWN = 3
exit_code = EXIT_CODE_OK

gconfig_root = yaml.load(file("/usr/local/cam/conf/push2youtube_config.yml"))
gconfig = gconfig_root['Prod']
config_root = yaml.load(file("/usr/local/cam/conf/config.yml"))
config = config_root['prod']

with open(gconfig['Logging']['log_config'], 'rt') as f:
    lconfig = yaml.load(f.read())
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger('ls_today_vids')
logger.info("started")

# this will soon come from command line or somewhere
vid_select = "Daily"

youtube = None

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                        httplib.IncompleteRead,
                        httplib.ImproperConnectionState,
                        httplib.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# CLIENT_SECRETS_FILE, name of a file containing the OAuth 2.0 information for
# this application, including client_id and client_secret. You can acquire an
# ID/secret pair from the API Access tab on the Google APIs Console
# http://code.google.com/apis/console#access
# For more information about using OAuth2 to access Google APIs, please visit:
#   https://developers.google.com/accounts/docs/OAuth2
# For more information about the client_secrets.json file format, please visit:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
# Please ensure that you have enabled the YouTube Data API for your project.
CLIENT_SECRETS_FILE = gconfig['Google']['Auth']['client_secrets_file']

# soemt things still need developer key
# DEVELOPER_KEY = gconfig['Google']['Auth']['api_key']

YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
# A limited OAuth 2 access scope that allows for uploading files, but not other
# types of account access.
# YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload
# https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
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


def search_todays_videos(options):
    search_options = options
    options.max_results = 50
    options.q = options.title
    return youtube_search(options)


def list_playlists():
    global youtube

    # Retrieve the contentDetails part of the channel resource for the
    # authenticated user's channel.
    channels_response = youtube.channels().list(
        mine=True,
        part="contentDetails"
    ).execute()

    for channel in channels_response["items"]:
        # From the API response,
        # extract the playlist ID that identifies the list
        # of videos uploaded to the authenticated user's channel.
        uploads_list_id = channel["contentDetails"][
            "relatedPlaylists"]["uploads"]
        print "going to list %s" % uploads_list_id
        list_playlist(uploads_list_id)


def list_playlist(playlist_id):
    print "Videos in list %s" % playlist_id

    # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=playlist_id,
        part="snippet",
        maxResults=50
    )

    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        # Print information about each video.
        for playlist_item in playlistitems_list_response["items"]:
            # print playlist_item
            title = playlist_item["snippet"]["title"]
            video_id = playlist_item["snippet"]["resourceId"]["videoId"]
            playlist_item_id = playlist_item["id"]
            print "playlist_item_id %s (%s)" % (playlist_item_id, video_id)
            print "%s (%s)" % (title, video_id)
            # try:
            # print delete_playlist_item(playlist_item_id=playlist_item_id)
            # except:
            # pass
            # try:
            # print delete_playlist_item(playlist_item_id=video_id)
            # except:
            # pass
            print

        playlistitems_list_request = youtube.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)


def delete_playlist_item(playlist_item_id):
    global youtube

    youtube.playlistItems().delete(id=playlist_item_id).execute()


def create_playlist():
    global youtube

    # This code creates a new, private playlist in the authorized user's
    # channel.
    playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title="Test Playlist",
                description="A private playlist created"
            ),
            status=dict(
                privacyStatus="private"
            )
        )
    ).execute()


def add_to_playlist(playlist_id, video_id):
    global youtube

    # This code creates a new, private playlist in the authorized user's
    # channel.
    playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title="Test Playlist",
                description="A private playlist created"
            ),
            status=dict(
                privacyStatus="private"
            )
        )
    ).execute()


def youtube_search(search_options):
    global youtube
    global exit_code
    youtube_public = youtube
#  youtube_public = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#        developerKey=DEVELOPER_KEY)

#  print "Searching for: " + search_options.q
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube_public.search().list(
        q=search_options.q,
        part="id,snippet",
        type="video",
        maxResults=search_options.max_results
    ).execute()

    videos = []
    exit_code = EXIT_CODE_CRITICAL

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            exit_code = EXIT_CODE_OK
            # dt = new datetime

            dt = dateutil.parser.parse(search_result["snippet"]["publishedAt"])
            localPublishedAt = dt.astimezone(timezone('America/Los_Angeles'))
            print "OK - id: %s Title: %s Date / Time: %s (%s)" % (
                search_result["id"]["videoId"],
                search_result["snippet"]["title"],
                localPublishedAt,
                search_result["snippet"]["publishedAt"])
            videos.append(search_result["id"]["videoId"])

    return videos

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
                      "See https://developers.google.com/" +
                      "youtube/v3/docs/videoCategories/list",
                      # youtube.videos().delete(id=ID).execute()
                      default="22")
    parser.add_option("--keywords", dest="keywords",
                      help="Video keywords, comma separated", default="")
    parser.add_option("--privacyStatus", dest="privacyStatus",
                      help="Video privacy status: public, private or unlisted",
                      default="public")
    (options, args) = parser.parse_args()

    # titles and stuff for video
    date_string = date.today().isoformat()
    # first build dictionary of substitutions
    d = dict(
        [('date', date_string), ('underbar_date',
                                 date_string.replace('-', '_')),
            ('video_uploaded', datetime.now().ctime())])

    options.title = Template(
        config['Video'][vid_select]['TitleTemplate']).safe_substitute(d)
    d['title'] = options.title  # make the title available for later subst
    options.developer_tag = Template(
        config['Video'][vid_select]['TitleTagTemplate']).safe_substitute(d)
    options.description = Template(
        config['Video'][vid_select]['DescriptionTemplate']).safe_substitute(d)

    youtube = get_authenticated_service()

    search_todays_videos(options)
    if exit_code == EXIT_CODE_CRITICAL:
        print "CRITICAL - no videos for today"
    sys.exit(exit_code)
#  list_playlists()
#  list_playlist('PLJAbMNd9phmKLcEnYpGxjJB8gEsRDEMrB')
#  create_playlist()
#  list_playlist()

#  delete_playlist_item(playlist_item_id='UUttWSUnS1GACHB3ZJ1VLXeh5l3gT_Cidx')
#  delete_playlist_item(playlist_item_id='UUttWSUnS1GAC3GD5TCHRc3jzR1-jTy9AA')
# delete_playlist_item(playlist_item_id='PLVHBOWmyzOCkHKJNRFasWI_hYUnuvmfC_rMQEL28R03w')
#  delete_playlist_item(playlist_item_id='wLWuyrXSRWM')
