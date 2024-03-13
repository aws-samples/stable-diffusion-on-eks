# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import uuid

from modules import s3_action
from runtimes import comfyui

# Logging configuration
logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger("queue-agent")
logger.propagate = False

## comfyUI setup
COMFYUI_ENDPOINT='172.31.33.229:8000'

server_address = COMFYUI_ENDPOINT
client_id = str(uuid.uuid4())

api_base_url = server_address

runtime_type = "comfyui"
s3_bucket = "sdoneksstack-outputs3bucket9fe85b9f-mjpz1dptybka"
task_id = "test4"
prefix = "output"
context = {}

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
    comfyui.check_readiness(api_base_url)
    payload = test_workflow()
    response = comfyui.handler(api_base_url, task_id, payload)
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

    print(json.dumps(sns_response))


"""     if response["success"]:
        images = response["image"]
        idx = 1
        for image_data in images:
                OUTPUT_LOCATION = "./outputs/comfyui/{}_{}.png".format(task_id, idx)
                with open(OUTPUT_LOCATION, "wb") as binary_file:
                    # Write bytes to file
                    binary_file.write(image_data)
                idx = idx + 1
                print("{} DONE!!!".format(OUTPUT_LOCATION)) """

if __name__ == '__main__':
    main()