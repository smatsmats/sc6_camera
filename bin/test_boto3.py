#!/usr/local/cam/env/bin/python3

import boto3
import logging
from botocore.exceptions import ClientError

def create_bucket(bucket_name):
    region='us-west-2'

    # Create bucket
    try:
        s3_client = boto3.client('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name,
                                CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# Let's use Amazon S3
s3 = boto3.resource('s3')

app_bucket = "bucketbucket.sc6-cam"

create_bucket(app_bucket)

# Print out bucket names
for bucket in s3.buckets.all():
    print(bucket.name)

