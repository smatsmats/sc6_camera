#!/usr/bin/python

from boto import storage_uri
from gslib.third_party.oauth2_plugin import oauth2_plugin

bucket = 'cam_bucket'

#location = storage_uri(bucket).get_location()
#location = storage_uri().get_location()
location = storage_uri('gs://helloworld').get_location()
print location

content = storage_uri('gs://pub/shakespeare/rose.txt').get_contents_as_string()
print(content)
