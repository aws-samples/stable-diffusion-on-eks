# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datetime
import logging
import mimetypes
import uuid

import aioboto3
import boto3
import magic

logger = logging.getLogger("queue-agent")
s3Res = boto3.resource('s3')

ab3_session = aioboto3.Session()

def upload_file(object_bytes: bytes, bucket: str, prefix: str, file_name: str=None, extension: str=None) -> str:
    if file_name is None:
        file_name = datetime.datetime.now().strftime(f"%Y%m%d%H%M%S-{uuid.uuid4()[0:5]}")

    # Auto determine file type and extension using magic
    if extension is None:
        content_type = magic.from_buffer(object_bytes, mime=True)
        extension = mimetypes.guess_extension(content_type, True)

    if extension == '.out':
        content_type = f'application/json'

    try:
        bucket = s3Res.Bucket(bucket)
        logger.info(f"Uploading s3://{bucket}/{prefix}/{file_name}{extension}")
        bucket.put_object(Body=object_bytes, Key=f'{prefix}/{file_name}{extension}', ContentType=content_type)
        return f's3://{bucket}/{prefix}/{file_name}{extension}'
    except Exception as error:
        logger.error('Failed to upload content to S3', exc_info=True)
        raise error


async def async_upload(object_bytes: bytes, bucket: str, prefix: str, file_name: str=None, extension: str=None) -> str:
    if file_name is None:
        file_name = datetime.datetime.now().strftime(f"%Y%m%d%H%M%S-{uuid.uuid4()[0:5]}")

    # Auto determine file type and extension using magic
    if extension is None:
        content_type = magic.from_buffer(object_bytes, mime=True)
        extension = mimetypes.guess_extension(content_type, True)

    if extension == '.out':
        content_type = f'application/json'

    try:
        async with ab3_session.resource("s3") as s3:
            bucket = await s3.Bucket(bucket)
            await bucket.put_object(Body=object_bytes, Key=f'{prefix}/{file_name}{extension}', ContentType=content_type)
            return f's3://{bucket}/{prefix}/{file_name}{extension}'
    except Exception as e:
        raise e

def get_bucket_and_key(s3uri):
    pos = s3uri.find('/', 5)
    bucket = s3uri[5: pos]
    key = s3uri[pos + 1:]
    return bucket, key

def get_prefix(path):
    pos = path.find('/')
    return path[pos + 1:]