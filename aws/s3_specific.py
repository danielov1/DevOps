#!/usr/bin/python3

import boto3
import botocore
import sys
import datetime


client = boto3.client('s3')
s3 = boto3.resource('s3')

bucket = s3.Bucket('test-cldze')
start_foldernum = '1000'
end_foldernum = '1004'

start_int = int(start_foldernum)
end_int = int(end_foldernum)

file_loc = "logzio-ec-aws-logs-archive/s3.log"

s3_log = open("s3.log", "a")
now = datetime.datetime.now()

i = 0

for obj in bucket.objects.all():
    try:
        for obj_num in range(start_int,end_int):
            if obj.key.startswith(str(obj_num)) and not obj.key.endswith('/'):
                now = datetime.datetime.now()
                print(now, " ", obj.key, file=open(file_loc, "a"))
                response = client.restore_object(
                Bucket='logzio-ec-aws-logs-archive',
                Key=obj.key,
                RestoreRequest={'Days': 7, 'GlacierJobParameters': {'Tier': 'Standard'}})
                i = i + 1
            else:
                continue
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] != "RestoreAlreadyInProgress":
            raise error
            continue

now = datetime.datetime.now()
print(now, " ", "finished", file=open(file_loc, "a"))
print(now, " ", "total files count is:", i, file=open(file_loc, "a"))