# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import asyncio
import base64
import json
import logging
import time
import traceback

from aws_xray_sdk.core import xray_recorder
from modules import http_action, misc

logger = logging.getLogger("queue-agent-sdwebui")

ALWAYSON_SCRIPTS_EXCLUDE_KEYS = ['task', 'id_task', 'uid',
                                 'sd_model_checkpoint', 'image_link', 'save_dir', 'sd_vae', 'override_settings']

def check_readiness(api_base_url: str, dynamic_sd_model: bool) -> bool:
    while True:
        try:
            logger.info('Checking service readiness...')
            # checking with options "sd_model_checkpoint" also for caching current model
            opts = invoke_get_options(api_base_url)
            logger.info('Service is ready.')
            if "sd_model_checkpoint" in opts:
                if opts['sd_model_checkpoint'] != None:
                    current_model_name = opts['sd_model_checkpoint']
                    logger.info(f'Init model is: {current_model_name}.')
                else:
                    if dynamic_sd_model:
                        logger.info(f'Dynamic SD model is enabled, init model is not loaded.')
                    else:
                        logger.error(f'Init model {current_model_name} failed to load.')
            break
        except Exception as e:
            logger.debug(repr(e))
            time.sleep(1)
    return True

def handler(api_base_url: str, task_type: str, task_id: str, payload: dict, dynamic_sd_model: bool) -> dict:
    response = {}
    try:
        taskHeader = payload['alwayson_scripts']
        logger.info(f"Start process {task_type} task with ID: {task_id}")

        if dynamic_sd_model and taskHeader['sd_model_checkpoint']:
            logger.info(f'Try to switching model to: {taskHeader["sd_model_checkpoint"]}.')
            current_model_name = switch_model(api_base_url, taskHeader['sd_model_checkpoint'])
            logger.info(f'Current model is: {current_model_name}.')

        if task_type == 'text-to-image':
            task_response = invoke_txt2img(api_base_url, payload, taskHeader)
        elif task_type == 'image-to-image':
            task_response = invoke_img2img(api_base_url, payload, taskHeader)
        else:
            logger.error(f'Unsupported task type: {task_type}, ignoring')

        imgOutputs = post_invocations(task_response)
        content = json.dumps(succeed(task_id, task_response, taskHeader))
        response["success"] = True
        response["image"] = imgOutputs
        response["content"] = content
        logger.info(f"End process {task_type} task with ID: {task_id}")
    except Exception as e:
        content = json.dumps(failed(task_id, taskHeader, e))
        logger.error(f"{task_type} task with ID: {task_id} finished with error")
        traceback.print_exc()
        response["success"] = False
        response["content"] = content
    return response




@xray_recorder.capture('text-to-image')
def invoke_txt2img(api_base_url: str, body, header) -> str:
    return http_action.do_invocations(api_base_url+"txt2img", prepare_payload(body, header))

@xray_recorder.capture('image-to-image')
def invoke_img2img(api_base_url: str, body, header: dict) -> str:
    return http_action.do_invocations(api_base_url+"img2img", prepare_payload(body, header))

def invoke_set_options(api_base_url: str, options: dict) -> str:
    return http_action.do_invocations(api_base_url+"options", options)

def invoke_get_options(api_base_url: str) -> str:
    return http_action.do_invocations(api_base_url+"options")

def invoke_get_model_names(api_base_url: str) -> str:
    return sorted([x["title"] for x in http_action.do_invocations(api_base_url+"sd-models")])

def invoke_refresh_checkpoints(api_base_url: str) -> str:
    return http_action.do_invocations(api_base_url+"refresh-checkpoints", {})

def switch_model(api_base_url: str, name: str, find_closest=False) -> str:
    opts = invoke_get_options(api_base_url)
    current_model_name = opts['sd_model_checkpoint']

    if find_closest:
        name = name.lower()
        current = current_model_name.lower()
        if name in current:
            return current_model_name
    else:
        if name == current_model_name:
            return current_model_name

    # refresh then check from model list
    invoke_refresh_checkpoints(api_base_url)
    models = invoke_get_model_names(api_base_url)
    found_model = None

    # exact matching
    if name in models:
        found_model = name
    # find closest
    elif find_closest:
        max_sim = 0.0
        max_model = None
        for model in models:
            sim = misc.str_simularity(name, model.lower())
            if sim > max_sim:
                max_sim = sim
                max_model = model
        found_model = max_model

    if not found_model:
        raise RuntimeError(f'Model not found: {name}')
    elif found_model != current_model_name:
        options = {}
        options["sd_model_checkpoint"] = found_model
        invoke_set_options(api_base_url, options)
        current_model_name = found_model

    return current_model_name

# Customizable for success responses
def succeed(task_id, response, header):
    parameters = response['parameters']
    parameters['id_task'] = task_id
    parameters['image_seed'] = ','.join(
        str(x) for x in json.loads(response['info'])['all_seeds'])
    parameters['error_msg'] = ''
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }


# Customizable for failure responses
def failed(task_id, header, exception):
    parameters = {}
    parameters['id_task'] = task_id
    parameters['status'] = 0
    parameters['image_seed'] = []
    parameters['error_msg'] = repr(exception)
    parameters['reason'] = exception.response.json() if hasattr(exception, "response") else None
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }


# Customizable for request payload
def prepare_payload(body, header):
    try:
        urls = []
        offset = 0
        # img2img image link
        if 'image_link' in header:
            urls.extend(header['image_link'].split(','))
            offset = len(urls)
        # ControlNet image link
        if 'controlnet' in header:
            for x in header['controlnet']['args']:
                if 'image_link' in x:
                    urls.append(x['image_link'])
        # Generate payload including ControlNet units
        if len(urls) > 0:
            loop = asyncio.get_event_loop()
            tasks = [loop.create_task(http_action.async_get(u)) for u in urls]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            if offset > 0:
                init_images = [misc.encode_to_base64(x) for x in results[:offset]]
                body.update({"init_images": init_images})

            if 'controlnet' in header:
                for x in header['controlnet']['args']:
                    if 'image_link' in x:
                        x['input_image'] = misc.encode_to_base64(results[offset])
                        offset += 1

        # dbt compatible for override_settings
        override_settings = {}
        if 'sd_vae' in header:
            override_settings.update({'sd_vae': header['sd_vae']})
        if 'override_settings' in header:
            override_settings.update(header['override_settings'])
        if override_settings:
            if 'override_settings' in body:
                body['override_settings'].update(override_settings)
            else:
                body.update({'override_settings': override_settings})

        # dbt compatible for alwayson_scripts
        body.update({'alwayson_scripts': misc.exclude_keys(
            header, ALWAYSON_SCRIPTS_EXCLUDE_KEYS)})
    except Exception as e:
        raise e

    return body

def post_invocations(response):
    img_bytes = []

    if "images" in response.keys():
        for i in response["images"]:
            img_bytes.append(base64.b64decode(i))

    elif "image" in response.keys():
        for i in response["image"]:
            img_bytes.append(base64.b64decode(i))

    return img_bytes