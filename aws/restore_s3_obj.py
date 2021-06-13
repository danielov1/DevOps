#!/usr/bin/python3

import boto3
import botocore
import sys
import datetime


client = boto3.client('s3')
s3 = boto3.resource('s3')

bucket = s3.Bucket('<bucket-name>')

i = 0

s3_log = open("s3.log", "a")
now = datetime.datetime.now()

for obj in bucket.objects.all():
    try:
        if obj.key.startswith('/'):
            continue
        else:
            now = datetime.datetime.now()
            response = client.restore_object(
            Bucket='<bucket-name>',
            Key=obj.key,
            RestoreRequest={'Days': 7, 'GlacierJobParameters': {'Tier': 'Standard'}})
            print(now, " ", obj.key, file=open("s3.log", "a"))
            i = i + 1
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] != "RestoreAlreadyInProgress":
            raise error
            continue

now = datetime.datetime.now()
print(now, " ", "finished", file=open("s3.log", "a"))
print(now, " ", "total files count is:", i, file=open("s3.log", "a"))
