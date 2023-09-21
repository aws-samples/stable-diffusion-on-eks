import boto3
import json
import requests
import logging
import sys
import argparse
import time
import os
logger = logging.getLogger(__name__)

pid = os.getpid()


logging.basicConfig(level=logging.INFO, format='From Client: %(asctime)s - %(process)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

url = '<api gw url>'


json_data = {
    "alwayson_scripts": {
        "task": "text-to-image",
        "sd_model_checkpoint": "135643.safetensors",
        "id_task": "16869",
        "uid": "123",
        "save_dir": "outputs"
    },
    "prompt": "A dog",
    "steps": 20,
    "width": 768,
    "height": 768
}
    
headers = {'Content-Type': 'application/json','x-api-key': '<api key>'}
json_data = json.dumps(json_data)
response = requests.post(url, data=json_data,headers = headers)
logger.info(f"response for request {response}")

    



