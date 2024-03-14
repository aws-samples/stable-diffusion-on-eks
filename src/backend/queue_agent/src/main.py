# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import os
import signal
import sys
import uuid

import boto3
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core.models.trace_header import TraceHeader
from modules import s3_action, sns_action, sqs_action
from runtimes import comfyui, sdwebui

patch_all()

# Logging configuration
logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger("queue-agent")
logger.propagate = False
logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Set current logger as global
logger = logging.getLogger("queue-agent")

# Get base environment variable
aws_default_region = os.getenv("AWS_DEFAULT_REGION")
sqs_queue_url = os.getenv("SQS_QUEUE_URL")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
s3_bucket = os.getenv("S3_BUCKET")

api_base_url = ""

# Check current runtime type
runtime_type = os.getenv("RUNTIME_TYPE", "").lower()

# Runtime type should be specified
if runtime_type == "":
    logger.error(f'Runtime type not specified')
    raise RuntimeError

# Init for SD Web UI
if runtime_type == "sdwebui":
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8080/sdapi/v1/")
    dynamic_sd_model_str = os.getenv("DYNAMIC_SD_MODEL", "false")
    if dynamic_sd_model_str.lower() == "false":
        dynamic_sd_model = False
    else:
        dynamic_sd_model = True

# TODO: Add some init for ComfyUI
if runtime_type == "comfyui":
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8080/")
    client_id = str(uuid.uuid4())
    # Change here to ComfyUI's base URL
    # You can specify any required environment variable here

sqsRes = boto3.resource('sqs')
snsRes = boto3.resource('sns')

SQS_WAIT_TIME_SECONDS = 20

# For graceful shutdown
shutdown = False

def main():
    # Initialization:
    # 1. Environment parameters;
    # 2. AWS services resources(sqs/sns/s3);
    # 3. SD API readiness check, current checkpoint cached;
    print_env()

    queue = sqsRes.Queue(sqs_queue_url)
    topic = snsRes.Topic(sns_topic_arn)

    if runtime_type == "sdwebui":
        sdwebui.check_readiness(api_base_url, dynamic_sd_model)

    if runtime_type == "comfyui":
        comfyui.check_readiness(api_base_url)

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

        received_messages = sqs_action.receive_messages(queue, 1, SQS_WAIT_TIME_SECONDS)

        for message in received_messages:
            with xray_recorder.in_segment('Queue-Agent') as segment:
                # Retrieve x-ray trace header from SQS message
                traceHeaderStr = message.attributes['AWSTraceHeader']
                sqsTraceHeader = TraceHeader.from_header_str(traceHeaderStr)
                # Update current segment to link with SQS
                segment.trace_id = sqsTraceHeader.root
                segment.parent_id = sqsTraceHeader.parent
                segment.sampled = sqsTraceHeader.sampled

                # Process received message
                payload = json.loads(json.loads(message.body)['Message'])
                metadata = payload["metadata"]
                task_id = metadata["id"]

                logger.info(f"Received task {task_id}, processing")

                if "prefix" in metadata.keys():
                    if metadata["prefix"][-1] == '/':
                        prefix = metadata["prefix"] + str(task_id)
                    else:
                        prefix = metadata["prefix"] + "/" + str(task_id)
                else:
                    prefix = str(task_id)

                if "tasktype" in metadata.keys():
                    tasktype = metadata["tasktype"]

                if "context" in metadata.keys():
                    context = metadata["context"]
                else:
                    context = {}

                body = payload["content"]
                logger.debug(body)

                response = {}

                if runtime_type == "sdwebui":
                    response = sdwebui.handler(api_base_url, tasktype, task_id, body, dynamic_sd_model)

                if runtime_type == "comfyui":
                    response = comfyui.handler(api_base_url, task_id, body)

                result = []
                rand = str(uuid.uuid4())[0:4]

                if response["success"]:
                    idx = 0
                    if len(response["image"]) > 0:
                        for i in response["image"]:
                            idx += 1
                            result.append(s3_action.upload_file(i, s3_bucket, prefix, str(task_id)+"-"+rand+"-"+str(idx)))

                output_url = s3_action.upload_file(response["content"], s3_bucket, prefix, str(task_id)+"-"+rand, ".out")

                sns_response = {'id': task_id,
                                'result': response["success"],
                                'image_url': result,
                                'output_url': output_url,
                                'context': context}

                # Put response handler to SNS and delete message
                sns_action.publish_message(topic, json.dumps(sns_response))
                sqs_action.delete_message(message)

def print_env() -> None:
    logger.info(f'AWS_DEFAULT_REGION={aws_default_region}')
    logger.info(f'SQS_QUEUE_URL={sqs_queue_url}')
    logger.info(f'SNS_TOPIC_ARN={sns_topic_arn}')
    logger.info(f'S3_BUCKET={s3_bucket}')
    logger.info(f'RUNTIME_TYPE={runtime_type}')

def signalHandler(signum, frame):
    global shutdown
    shutdown = True

if __name__ == '__main__':
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
        signal.signal(sig, signalHandler)
    main()
