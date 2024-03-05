import boto3
import aioboto3
import datetime
import uuid
import logging

logger = logging.getLogger("queue-agent")
s3Res = boto3.resource('s3')

ab3_session = aioboto3.Session()

def upload_file(object_bytes, bucket, folder, file_name=None, suffix=None):
    try:
        if suffix == 'out':
            content_type = f'application/json'
            if file_name is None:
                file_name = f"response-{uuid.uuid4()}"
        else:
            suffix = 'png'
            content_type = f'image/{suffix}'
            if file_name is None:
                file_name = datetime.datetime.now().strftime(
                    f"%Y%m%d%H%M%S-{uuid.uuid4()}")

        bucket = s3Res.Bucket(bucket)
        logger.info(f"Uploading s3://{bucket}/{folder}/{file_name}.{suffix}")
        bucket.put_object(
            Body=object_bytes, Key=f'{folder}/{file_name}.{suffix}', ContentType=content_type)

        return f's3://{bucket}/{folder}/{file_name}.{suffix}'
    except Exception as error:
        logger.error('Failed to upload content to S3', exc_info=True)
        raise error


async def async_upload(object_bytes, bucket, folder, file_name=None, suffix=None):
    try:
        async with ab3_session.resource("s3") as s3:
            if suffix == 'out':
                content_type = f'application/json'
                if file_name is None:
                    file_name = f"response-{uuid.uuid4()}"
            else:
                suffix = 'png'
                content_type = f'image/{suffix}'
                if file_name is None:
                    file_name = datetime.datetime.now().strftime(
                        f"%Y%m%d%H%M%S-{uuid.uuid4()}")

            bucket = await s3.Bucket(bucket)
            await bucket.put_object(
                Body=object_bytes, Key=f'{folder}/{file_name}.{suffix}', ContentType=content_type)

            return f's3://{bucket}/{folder}/{file_name}.{suffix}'
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