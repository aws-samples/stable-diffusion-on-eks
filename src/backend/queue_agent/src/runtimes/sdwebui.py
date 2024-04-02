# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import base64
import json
import logging
import time
import traceback

from aws_xray_sdk.core import xray_recorder
from jsonpath_ng import parse
from modules import http_action, misc

logger = logging.getLogger("queue-agent")

ALWAYSON_SCRIPTS_EXCLUDE_KEYS = ['task', 'id_task', 'uid',
                                 'sd_model_checkpoint', 'image_link', 'save_dir', 'sd_vae', 'override_settings']

def check_readiness(api_base_url: str, dynamic_sd_model: bool) -> bool:
    """Check if SD Web UI is ready by invoking /option endpoint"""
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
    """Main handler for SD Web UI request"""
    response = {}
    try:
        logger.info(f"Start process {task_type} task with ID: {task_id}")
        match task_type:
            case 'text-to-image':
                # Compatiability for v1alpha1: Ensure there is an alwayson_scripts
                if 'alwayson_scripts' in payload:
                    # Switch model if necessery
                    if dynamic_sd_model and payload['alwayson_scripts']['sd_model_checkpoint']:
                        new_model = payload['alwayson_scripts']['sd_model_checkpoint']
                        logger.info(f'Try to switching model to: {new_model}.')
                        current_model_name = switch_model(api_base_url, new_model)
                        logger.info(f'Current model is: {current_model_name}.')
                else:
                    payload.update({'alwayson_scripts': {}})

                task_response = invoke_txt2img(api_base_url, payload)

            case 'image-to-image':
                # Compatiability for v1alpha1: Ensure there is an alwayson_scripts
                if 'alwayson_scripts' in payload:
                    # Switch model if necessery
                    if dynamic_sd_model and payload['alwayson_scripts']['sd_model_checkpoint']:
                        new_model = payload['alwayson_scripts']['sd_model_checkpoint']
                        logger.info(f'Try to switching model to: {new_model}.')
                        current_model_name = switch_model(api_base_url, new_model)
                        logger.info(f'Current model is: {current_model_name}.')
                else:
                    payload.update({'alwayson_scripts': {}})

                task_response = invoke_img2img(api_base_url, payload)
            case 'extra-single-image':
                # There is no alwayson_script in API spec
                task_response = invoke_extra_single_image(api_base_url, payload)
            case 'extra-batch-image':
                task_response = invoke_extra_batch_images(api_base_url, payload)
            case _:
                # Catch all
                logger.error(f'Unsupported task type: {task_type}, ignoring')

        imgOutputs = post_invocations(task_response)
        logger.info(f"Received {len(imgOutputs)} images")
        content = json.dumps(succeed(task_id, task_response))
        response["success"] = True
        response["image"] = imgOutputs
        response["content"] = content
        logger.info(f"End process {task_type} task with ID: {task_id}")
    except Exception as e:
        content = json.dumps(failed(task_id, e))
        logger.error(f"{task_type} task with ID: {task_id} finished with error")
        traceback.print_exc()
        response["success"] = False
        response["content"] = content
    return response

@xray_recorder.capture('text-to-image')
def invoke_txt2img(api_base_url: str, body) -> str:
    # Compatiability for v1alpha1: Move override_settings from header to body
    override_settings = {}
    if 'override_settings' in body['alwayson_scripts']:
        override_settings.update(body['alwayson_scripts']['override_settings'])
    if override_settings:
        if 'override_settings' in body:
            body['override_settings'].update(override_settings)
        else:
            body.update({'override_settings': override_settings})

    # Compatiability for v1alpha1: Remove header used for routing in v1alpha1 API request
    body.update({'alwayson_scripts': misc.exclude_keys(body['alwayson_scripts'], ALWAYSON_SCRIPTS_EXCLUDE_KEYS)})

    # Process image link in elsewhere in body
    body = download_image(body)

    response = http_action.do_invocations(api_base_url+"txt2img", body)
    return response

@xray_recorder.capture('image-to-image')
def invoke_img2img(api_base_url: str, body: dict) -> str:
    """Image-to-Image request"""
    # Process image link
    body = download_image(body)

    # Compatiability for v1alpha1: Move override_settings from header to body
    override_settings = {}
    if 'override_settings' in body['alwayson_scripts']:
        override_settings.update(body['alwayson_scripts']['override_settings'])
    if override_settings:
        if 'override_settings' in body:
            body['override_settings'].update(override_settings)
        else:
            body.update({'override_settings': override_settings})

    # Compatiability for v1alpha2: Process image link in "Alwayson_scripts"
    # Plan to remove in next release
    if 'image_link' in body['alwayson_scripts']:
        body.update({"init_images": [body['alwayson_scripts']['image_link']]})

    # Compatiability for v1alpha1: Remove header used for routing in v1alpha1 API request
    body.update({'alwayson_scripts': misc.exclude_keys(body['alwayson_scripts'], ALWAYSON_SCRIPTS_EXCLUDE_KEYS)})

    response = http_action.do_invocations(api_base_url+"img2img", body)
    return response

@xray_recorder.capture('extra-single-image')
def invoke_extra_single_image(api_base_url: str, body) -> str:

    body = download_image(body)

    response = http_action.do_invocations(api_base_url+"extra-single-image", body)
    return response

@xray_recorder.capture('extra-batch-images')
def invoke_extra_batch_images(api_base_url: str, body) -> str:

    body = download_image(body)

    response = http_action.do_invocations(api_base_url+"extra-batch-images", body)
    return response

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
def succeed(task_id, response):
    parameters = {}
    if 'parameters' in response: # text-to-image and image-to-image
        parameters = response['parameters']
        parameters['id_task'] = task_id
        parameters['image_seed'] = ','.join(
            str(x) for x in json.loads(response['info'])['all_seeds'])
        parameters['error_msg'] = ''
    elif 'html_info' in response: # extra-single-image and extra-batch-images
        parameters['html_info'] = response['html_info']
        parameters['id_task'] = task_id
        parameters['error_msg'] = ''
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }


# Customizable for failure responses
def failed(task_id, exception):
    parameters = {}
    parameters['id_task'] = task_id
    parameters['status'] = 0
    parameters['error_msg'] = repr(exception)
    parameters['reason'] = exception.response.json() if hasattr(exception, "response") else None
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }

def download_image(body: dict) -> dict:
    """Search URL in object, and replace all URL with content of URL"""
    jsonpath_expr = parse('$..*')
    for match in jsonpath_expr.find(body):
        value = match.value
        if isinstance(value, str) and (value.startswith('http') or value.startswith('s3://')):
            try:
                # Get the JSONPath of the replaced value
                jsonpath = str(match.full_path)
                logger.info(f"Found URL {value} in {jsonpath}, replacing... ")

                image_byte = http_action.get(value)
                match.full_path.update(body, misc.encode_to_base64(image_byte))
                logger.info(f"{jsonpath} replaced with content. ")
            except Exception as e:
                print(f"Error fetching URL: {value}")
                print(f"Error: {str(e)}")
    return body

def post_invocations(response):
    img_bytes = []

    if "images" in response.keys():
        for i in response["images"]:
            img_bytes.append(base64.b64decode(i))

    elif "image" in response.keys():
        img_bytes.append(base64.b64decode(response["image"]))

    return img_bytes