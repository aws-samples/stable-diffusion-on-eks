# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging

from runtimes import sdwebui

# Logging configuration
logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

logger = logging.getLogger("queue-agent")
logger.setLevel(logging.INFO)
logger.propagate = False

api_base_url = 'http://172.31.33.229:8000/sdapi/v1/'
task_id = "test"
task_type = "text-to-image"
body = json.loads("""
{
    "alwayson_scripts": {
        "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors"
    },
    "prompt": "A dog",
    "steps": 16,
    "width": 512,
    "height": 512
}
""")
dynamic_sd_model = False


def main():
    sdwebui.check_readiness(api_base_url, dynamic_sd_model)

    response = {}

    response = sdwebui.handler(api_base_url, task_type, task_id, body, dynamic_sd_model)
    if response["success"]:
        images = response["image"]
        idx = 1
        for image_data in images:
                OUTPUT_LOCATION = "./outputs/sdwebui/{}_{}.png".format(task_id, idx)
                with open(OUTPUT_LOCATION, "wb") as binary_file:
                    # Write bytes to file
                    binary_file.write(image_data)
                idx = idx + 1
                print("{} DONE!!!".format(OUTPUT_LOCATION))
        print(json.dumps(response["content"]))


if __name__ == '__main__':
    main()