#!/usr/bin/python

import StringIO
import os
import shutil
import tempfile
import time
import threading
from gslib.third_party.oauth2_plugin import oauth2_client
oauth2_client.token_exchange_lock = threading.Lock()

import boto
global token_exchange_lock


# URI scheme for Google Cloud Storage.
GOOGLE_STORAGE = 'gs'
# URI scheme for accessing local files.
LOCAL_FILE = 'file'

now = time.time()
CATS_BUCKET = 'cats-%d' % now
DOGS_BUCKET = 'dogs-%d' % now
project_id = 422002810388

for name in (CATS_BUCKET, DOGS_BUCKET):
  # Instantiate a BucketStorageUri object.
  uri = boto.storage_uri(name, GOOGLE_STORAGE)
  # Try to create the bucket.
  try:
    # If the default project is defined,
    # you do not need the headers.
    # Just call: uri.create_bucket()
    header_values = {"x-goog-api-version": "2",
      "x-goog-project-id": project_id}
    uri.create_bucket(headers=header_values)

    print 'Successfully created bucket "%s"' % name
  except boto.exception.StorageCreateError, e:
    print 'Failed to create bucket:', e
