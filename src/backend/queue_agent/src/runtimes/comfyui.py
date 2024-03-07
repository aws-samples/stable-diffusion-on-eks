# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# TODO: ComfyUI support

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import threading
import time
import datetime
import json
import logging
import traceback
import asyncio
import uuid
import urllib.request
import urllib.parse
from aws_xray_sdk.core import xray_recorder
# from modules import http_action, misc, s3_action

logger = logging.getLogger("queue-agent-comfyui")

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class comfyuiCaller(object):

    def __init__(self):
        # self.wss = wsClient()
        self.wss = websocket.WebSocket()
        self.client_id = str(uuid.uuid4())
        pass

    def setUrl(self, api_base_url:str):
        self.api_base_url = api_base_url

    def wss_connect(self):
       self.wss.connect("ws://{}/ws?clientId={}".format(self.api_base_url, self.client_id))
        # self.wss.Connect("ws://{}/ws?clientId={}".format(self.api_base_url, self.client_id))
       
    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.api_base_url, prompt_id)) as response:
            return json.loads(response.read())

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(self.api_base_url), data=data)
        return json.loads(urllib.request.urlopen(req).read())
    
    def get_image(self, filename,  subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.api_base_url, url_values)) as response:
            return response.read()
        
    def get_images(self, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        logger.info("prompt_id:" + prompt_id)
        output_images = {}
        while True:
            out = self.wss.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    logger.info(data)
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                time.sleep(1)
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for o in history['outputs']:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                # image branch
                if 'images' in node_output:
                    images_output = []
                    for image in node_output['images']:
                        image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        images_output.append(image_data)
                    output_images[node_id] = images_output
                # video branch
                if 'videos' in node_output:
                    videos_output = []
                    for video in node_output['videos']:
                        video_data = self.get_image(video['filename'], video['subfolder'], video['type'])
                        videos_output.append(video_data)
                    output_images[node_id] = videos_output

        return output_images
        
    def parse_worflow(self, prompt_data):
        logger.debug(prompt_data)
        return self.get_images(prompt_data)
            

def check_readiness(api_base_url: str, dynamic_sd_model: bool) -> bool:
    while True:
        cf = comfyuiCaller()
        cf.setUrl(api_base_url)
        cf.wss_connect()
        break
    return True


def handler(api_base_url: str, payload: dict, s3_bucket, dynamic_sd_model: bool) -> str:
    try:
        images = invoke_pipeline(api_base_url, payload)
        # write to s3
        post_invocations(s3_bucket, None, images, 80)       
    except Exception as e:
        pass

    content = {"code": 200}
    return content

def invoke_pipeline(api_base_url: str, body, header = None) -> str:
    cf = comfyuiCaller()
    cf.setUrl(api_base_url)
    return cf.parse_worflow(body)

def post_invocations(s3_bucket, folder, images, quality):
    defaultFolder = datetime.date.today().strftime("%Y-%m-%d")
    if not folder:
        folder = defaultFolder

    if len(images) > 0:
        idx = 1
        for node_id in images:
            for image_data in images[node_id]:
                from PIL import Image
                import io
                OUTPUT_LOCATION = "./outputs/comfyui/{}_{}.png".format(folder, idx)
                with open(OUTPUT_LOCATION, "wb") as binary_file:
                    # Write bytes to file
                    binary_file.write(image_data)
                idx = idx + 1
                print("{} DONE!!!".format(OUTPUT_LOCATION))
                
        # results = [s3_action.upload_file(i, s3_bucket, folder, None, 'png') for i in images]