#!/usr/bin/python3

# Imports the Google Cloud client library
from google.cloud import storage

import argparse
import sys
import logging
import logging.config
import pprint
import yaml

pp = pprint.PrettyPrinter(indent=4)

class MyBucket:
    def __init__(self):
        with open('/usr/local/cam/conf/push2bucket_config.yml', 'r') as file:
            gconfig_root = yaml.safe_load(file)
        gconfig = gconfig_root['prod']
        with open('/usr/local/cam/conf/config.yml', 'r') as file:
            config_root = yaml.safe_load(file)
        config = config_root['prod']
        
        with open(config['Logging']['LogConfig'], 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)
        
        # create logger
        self.logger = logging.getLogger('push2bucket')
        
        # Explicitly use service account credentials by specifying the private key
        # file.
        self.storage_client = storage.Client.from_service_account_json(
                gconfig['Google']['Auth']['service_key_secrets'])
        
        # The name for the new bucket
        self.bucket_name = config['GStore']['ImageBucket']
        self.bucket = self.storage_client.bucket(self.bucket_name)
    
    def upload_blob(self, source_file_name, destination_blob_name):
    
        blob = self.bucket.blob(destination_blob_name)
    
        blob.upload_from_filename(source_file_name)
    
        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )


    def cp_in_bucket(self, src_name, dst_name):    
        src_blob = self.bucket.blob(src_name)
        new_blob = self.bucket.copy_blob(src_blob, self.bucket, dst_name)
        pp.pprint(new_blob)

    def list_bucket(self):    
        b = self.storage_client.list_blobs(self.bucket_name)
        for item in b:
          pp.pprint(item)


def testme():
    mybuck = MyBucket()
    mybuck.list_bucket()
    sample_file = "/usr/local/cam/data/cam_images/2021/06/08/public/image1623187155_orig.jpg"
    mybuck.upload_blob(sample_file, "current/image_orig.jpg")
    mybuck.cp_in_bucket("current/image_orig.jpg", "blueist/image_orig.jpg")


if __name__ == '__main__':

    mybuck = MyBucket()

    parser = argparse.ArgumentParser(description='mess with goog buckets.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--upload", dest="do_upload", required=False, action='store_true',
                        help="Do an upload", default=False)
    group.add_argument("--copy", dest="do_copy", required=False, action='store_true',
                        help="Do a copy", default=False)
    group.add_argument("--list", dest="do_list", required=False, action='store_true',
                        help="Do an upload", default=False)
    parser.add_argument("--file", dest="file", default = None, required=False, help="Image file to upload")
    parser.add_argument("--dst_name", dest="dst_name",
                        help="Folder and filename for destination",
                        required = False)
    parser.add_argument("--src_name", dest="src_name",
                        help="Source folder and filename if we're copying within bucket",
                        required = False)
    args = parser.parse_args()

    # file
    if args.do_list:
        mybuck.list_bucket()
    if args.do_upload:
        if args.file == None:
            print("Need filename")
            sys.exit(0)
        if args.dst_name == None:
            print("Need destination name")
            sys.exit(0)
        mybuck.upload_blob(args.file, args.dst_name)
    if args.do_copy:
        if args.src_name == None:
            print("Need source name")
            sys.exit(0)
        if args.dst_name == None:
            print("Need destination name")
            sys.exit(0)
        mybuck.cp_in_bucket(args.src_name, args.dst_name)

