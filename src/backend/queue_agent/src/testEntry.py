# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import os
import signal
import sys
import uuid
import boto3
import time

from runtimes import comfyui

# Logging configuration
logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger("queue-agent")
logger.propagate = False

## comfyUI setup
COMFYUI_ENDPOINT='comfyui-lb-1023792722.us-east-1.elb.amazonaws.com'

server_address = COMFYUI_ENDPOINT
client_id = str(uuid.uuid4())

api_base_url = server_address

# Check current runtime type
runtime_type = os.getenv("RUNTIME_TYPE", "").lower
s3_bucket = os.getenv("S3_BUCKET")

runtime_type = "comfyui"
s3_bucket = "s3://"

# For graceful shutdown
shutdown = False

dynamic_sd_model = False

def test_workflow():
    try:
        workflowfile = './runtimes/test_workflow_api.json'
        with open(workflowfile, 'r', encoding="utf-8") as workflowfile_data:
            return json.load(workflowfile_data)
    except FileNotFoundError:
        print(f"The file {workflowfile} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"The file {workflowfile} contains invalid JSON.")
        return None

def main():

    if runtime_type == "comfyui":
        comfyui.check_readiness(api_base_url)

    task_id = "test"
    payload = test_workflow()
    response = {}

    while True:
        if shutdown:
            logger.info('Received SIGTERM, shutting down...')
            break

        if runtime_type == "comfyui":
            response = comfyui.handler(api_base_url, task_id, payload)
            if response["success"]:
                images = response["image"]
                idx = 1
                for image_data in images:
                        OUTPUT_LOCATION = "./outputs/comfyui/{}_{}.png".format(task_id, idx)
                        with open(OUTPUT_LOCATION, "wb") as binary_file:
                            # Write bytes to file
                            binary_file.write(image_data)
                        idx = idx + 1
                        print("{} DONE!!!".format(OUTPUT_LOCATION))
            break
        time.sleep(1)

def signalHandler(signum, frame):
    global shutdown
    shutdown = True

if __name__ == '__main__':
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
        signal.signal(sig, signalHandler)
    main()