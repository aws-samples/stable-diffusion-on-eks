# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import sys
import uuid

from modules import s3_action
from runtimes import sdwebui

# Logging configuration
logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger("queue-agent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.propagate = False

api_base_url = 'http://172.31.33.229:8000/sdapi/v1/'
task_id = "test2"
task_type = "image-to-image"
body = json.loads("""
{
    "alwayson_scripts": {
      "image_link": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png"
    },
    "prompt": "A dog",
    "steps": 16,
    "width": 512,
    "height": 512
}
""")
dynamic_sd_model = False
s3_bucket = "sdoneksstack-outputs3bucket9fe85b9f-mjpz1dptybka"
prefix = "output"
context = {}

def main():
    sdwebui.check_readiness(api_base_url, dynamic_sd_model)

    response = {}

    response = sdwebui.handler(api_base_url, task_type, task_id, body, dynamic_sd_model)

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

if __name__ == '__main__':
    main()