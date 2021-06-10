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
            "bucket_shiz: File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )

    def cp_in_bucket(self, src_name, dst_name):
        src_blob = self.bucket.blob(src_name)
        new_blob = self.bucket.copy_blob(src_blob, self.bucket, dst_name)
        print("bucket_shiz: File copied")
        pp.pprint(new_blob)

    def list_bucket(self):
        b = self.storage_client.list_blobs(self.bucket_name)
        print("bucket_shiz: File list:")
        for item in b:
            pp.pprint(item)

    def set_blob_metadata(self, blob_name, metadata):

        blob = self.bucket.get_blob(blob_name)
        pp.pprint(metadata)
        mdict = {metadata[0]: metadata[1]}
        pp.pprint(mdict)

    # metadata={'color': 'Red', 'name': 'Test'}
        blob.metadata = mdict
        blob.patch()

        print("bucket_shiz: The metadata for the blob {} is {}".format(blob.name, blob.metadata))

    def get_blob_metadata(self, blob_name):

        blob = self.bucket.get_blob(blob_name)

        print("bucket_shiz: blob metadata:")
        print("Blob: {}".format(blob.name))
        print("Bucket: {}".format(blob.bucket.name))
        print("Storage class: {}".format(blob.storage_class))
        print("ID: {}".format(blob.id))
        print("Size: {} bytes".format(blob.size))
        print("Updated: {}".format(blob.updated))
        print("Generation: {}".format(blob.generation))
        print("Metageneration: {}".format(blob.metageneration))
        print("Etag: {}".format(blob.etag))
        print("Owner: {}".format(blob.owner))
        print("Component count: {}".format(blob.component_count))
        print("Crc32c: {}".format(blob.crc32c))
        print("md5_hash: {}".format(blob.md5_hash))
        print("Cache-control: {}".format(blob.cache_control))
        print("Content-type: {}".format(blob.content_type))
        print("Content-disposition: {}".format(blob.content_disposition))
        print("Content-encoding: {}".format(blob.content_encoding))
        print("Content-language: {}".format(blob.content_language))
        print("Metadata: {}".format(blob.metadata))
        print("Custom Time: {}".format(blob.custom_time))
        print(
            "Temporary hold: ",
            "enabled" if blob.temporary_hold else "disabled")
        print(
            "Event based hold: ",
            "enabled" if blob.event_based_hold else "disabled")
        if blob.retention_expiration_time:
            print(
                "retentionExpirationTime: {}".format(
                    blob.retention_expiration_time)
            )


def testme():
    mybuck = MyBucket()
    mybuck.list_bucket()
    sample_file = "/usr/local/cam/data/cam_images/2021/06/08/public/image1623187155_orig.jpg"
    mybuck.upload_blob(sample_file, "test/image_orig.jpg")
    mybuck.cp_in_bucket("test/image_orig.jpg", "test/image_orig2.jpg")
    mybuck.set_blob_metadata('test/image_orig.jpg',
                             {'Cache-Control': 'public, max-age=300'})
    mybuck.get_blob_metadata('test/image_orig.jpg')


if __name__ == '__main__':

    mybuck = MyBucket()

    parser = argparse.ArgumentParser(description='mess with goog buckets.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--test", dest="do_test", required=False,
                       action='store_true',
                       help="just run the test", default=False)
    group.add_argument("--upload", dest="do_upload", required=False,
                       action='store_true',
                       help="Do an upload", default=False)
    group.add_argument("--copy", dest="do_copy", required=False,
                       action='store_true',
                       help="Do a copy", default=False)
    group.add_argument("--list", dest="do_list", required=False,
                       action='store_true',
                       help="Do an upload", default=False)
    group.add_argument("--get_metadata", dest="do_get_metadata",
                       required=False,
                       action='store_true',
                       help="Get blob metadata", default=False)
    group.add_argument("--set_metadata", dest="do_set_metadata",
                       required=False,
                       action='store_true',
                       help="Set blob metadata", default=False)
    parser.add_argument("--file", dest="file", default=None,
                        required=False,
                        help="Image file to upload")
    parser.add_argument("--dst_name", dest="dst_name",
                        help="Folder and filename for destination",
                        required=False)
    parser.add_argument("--src_name", dest="src_name",
                        help="Source folder and filename",
                        required=False)
    parser.add_argument("--blob_name", dest="blob_name",
                        help="Blob name for metadata",
                        required=False)
    parser.add_argument("--metadata", dest="metadata", nargs=2,
                        help="Metadata to set on blob",
                        required=False)
    args = parser.parse_args()

    if args.do_test:
        testme()
    elif args.do_list:
        mybuck.list_bucket()
    elif args.do_upload:
        if args.file is None:
            print("Need filename")
            sys.exit(0)
        if args.dst_name is None:
            print("Need destination name")
            sys.exit(0)
        mybuck.upload_blob(args.file, args.dst_name)
    elif args.do_copy:
        if args.src_name is None:
            print("Need source name")
            sys.exit(0)
        if args.dst_name is None:
            print("Need destination name")
            sys.exit(0)
        mybuck.cp_in_bucket(args.src_name, args.dst_name)
    elif args.do_get_metadata:
        if args.blob_name is None:
            print("Need blob name")
            sys.exit(0)
        mybuck.get_blob_metadata(args.blob_name)
    elif args.do_set_metadata:
        if args.blob_name is None:
            print("Need blob name")
            sys.exit(0)
        if args.metadata is None:
            print("Need metadata")
            sys.exit(0)
        mybuck.set_blob_metadata(args.blob_name, args.metadata)
