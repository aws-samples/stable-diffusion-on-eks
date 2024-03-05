# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import requests
import boto3
import logging
import signal
import utils
from aiohttp_client_cache import CacheBackend
from requests.adapters import HTTPAdapter, Retry
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.models.trace_header import TraceHeader

logger = logging.getLogger("queue-agent")

aws_default_region = os.getenv("AWS_DEFAULT_REGION")
sqs_queue_url = os.getenv("SQS_QUEUE_URL")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
s3_bucket = os.getenv("S3_BUCKET")
dynamic_sd_model = os.getenv("DYNAMIC_SD_MODEL")

current_model_name = ''
sqsRes = boto3.resource('sqs')
snsRes = boto3.resource('sns')

apiClient = requests.Session()
retries = Retry(
    total=3,
    connect=100,
    backoff_factor=0.1,
    allowed_methods=["GET", "POST"])
apiClient.mount('http://', HTTPAdapter(max_retries=retries))

REQUESTS_TIMEOUT_SECONDS = 60

cache = CacheBackend(
    cache_name='memory-cache',
    expire_after=600
)

shutdown = False

def main():
    # Initialization:
    # 1. Environment parameters;
    # 2. AWS services resources(sqs/sns/s3);
    # 3. SD API readiness check, current checkpoint cached;
    print_env()

    queue = sqsRes.Queue(sqs_queue_url)
    SQS_WAIT_TIME_SECONDS = 20
    topic = snsRes.Topic(sns_topic_arn)

    check_readiness()

    # TODO: Add runtime selection

    # main loop
    # 1. Pull msg from sqs;
    # 2. Translate parameteres;
    # 3. (opt)Switch model;
    # 4. (opt)Prepare inputs for image downloading and encoding;
    # 5. Call SD API;
    # 6. Prepare outputs for decoding, uploading and notifying;
    # 7. Delete msg;
    while True:
        if shutdown:
            logger.info('Received SIGTERM, shutting down...')
            break

        received_messages = utils.receive_messages(queue, 1, SQS_WAIT_TIME_SECONDS)

        for message in received_messages:
            with xray_recorder.in_segment('Queue-Agent') as segment:
                # Retrieve x-ray trace header from SQS message
                traceHeaderStr = message.attributes['AWSTraceHeader']
                sqsTraceHeader = TraceHeader.from_header_str(traceHeaderStr)
                # Update current segment to link with SQS
                segment.trace_id = sqsTraceHeader.root
                segment.parent_id = sqsTraceHeader.parent
                segment.sampled = sqsTraceHeader.sampled
                snsPayload = json.loads(message.body)
                payload = json.loads(snsPayload['Message'])
                # Todo: Add runtime choice
                utils.delete_message(message)
                logger.info(f"End process {taskType} task with ID: {taskId}")

def print_env():
    logger.info(f'AWS_DEFAULT_REGION={aws_default_region}')
    logger.info(f'SQS_QUEUE_URL={sqs_queue_url}')
    logger.info(f'SNS_TOPIC_ARN={sns_topic_arn}')
    logger.info(f'S3_BUCKET={s3_bucket}')
    logger.info(f'DYNAMIC_SD_MODEL={dynamic_sd_model}')

def signalHandler(signum, frame):
    global shutdown
    shutdown = True

if __name__ == '__main__':
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
        signal.signal(sig, signalHandler)
    main()
