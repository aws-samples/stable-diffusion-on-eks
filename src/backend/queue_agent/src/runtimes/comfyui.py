# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import traceback
import urllib.parse
import urllib.request
import uuid

import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
from aws_xray_sdk.core import xray_recorder

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
        try:
            p = {"prompt": prompt, "client_id": self.client_id}
            data = json.dumps(p).encode('utf-8')
            # print(data)
            req =  urllib.request.Request("http://{}/prompt".format(self.api_base_url), data=data)
            output = urllib.request.urlopen(req)
            return json.loads(output.read())
        except Exception as e:
            logger.error(e)
            return None

    def get_image(self, filename,  subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.api_base_url, url_values)) as response:
            return response.read()

    def track_progress(self, prompt, prompt_id):
        logger.info("prompt_id:" + prompt_id)
        node_ids = list(prompt.keys())
        finished_nodes = []

        while True:
            out = self.wss.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'progress':
                    data = message['data']
                    current_step = data['value']
                    logger.info('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
                if message['type'] == 'execution_cached':
                    data = message['data']
                    for itm in data['nodes']:
                        if itm not in finished_nodes:
                            finished_nodes.append(itm)
                            logger.info('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] not in finished_nodes:
                        finished_nodes.append(data['node'])
                        logger.info('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')

                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue
        return

    def get_images(self, prompt):
        output = self.queue_prompt(prompt)
        if output is None:
            raise("internal error")
        prompt_id = output['prompt_id']
        output_images = {}
        self.track_progress(prompt, prompt_id)

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


def check_readiness(api_base_url: str) -> bool:
    while True:
        cf = comfyuiCaller()
        cf.setUrl(api_base_url)
        cf.wss_connect()
        break
    return True


def handler(api_base_url: str, task_id: str, payload: dict) -> str:
    response = {}

    try:
        images = invoke_pipeline(api_base_url, payload)
        # write to s3
        imgOutputs = post_invocations(images)
        content = '{"code": 200}'
        response["success"] = True
        response["image"] = imgOutputs
        response["content"] = content
        logger.info(f"End process pipeline task with ID: {task_id}")
    except Exception as e:
        logger.error(f"Pipeline task with ID: {task_id} finished with error")
        traceback.print_exc()
        response["success"] = False
        response["content"] = '{"code": 500}'

    return response

def invoke_pipeline(api_base_url: str, body) -> str:
    cf = comfyuiCaller()
    cf.setUrl(api_base_url)
    return cf.parse_worflow(body)

def post_invocations(image):
    img_bytes = []

    if len(image) > 0:
        for node_id in image:
            for image_data in image[node_id]:
                img_bytes.append(image_data)

    return img_bytes