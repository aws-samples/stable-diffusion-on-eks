import asyncio
import datetime
import traceback
import utils
import json
import logging
from aws_xray_sdk.core import xray_recorder
from modules import *

logger = logging.getLogger("queue-agent")

ALWAYSON_SCRIPTS_EXCLUDE_KEYS = ['task', 'id_task', 'uid',
                                 'sd_model_checkpoint', 'image_link', 'save_dir', 'sd_vae', 'override_settings']

apiBaseUrl = "http://localhost:8080/sdapi/v1/"

def handler(payload, dynamic_sd_model):
    try:
        taskHeader = payload['alwayson_scripts']
        taskType = taskHeader['task'] if 'task' in taskHeader else None
        taskId = taskHeader['id_task'] if 'id_task' in taskHeader else None
        folder = utils.get_s3_prefix(
            payload['s3_output_path']) if 's3_output_path' in payload else None
        logger.info(f"Start process {taskType} task with ID: {taskId}")

        if dynamic_sd_model and taskHeader['sd_model_checkpoint']:
            logger.info(f'Try to switching model to: {taskHeader["sd_model_checkpoint"]}.')
            current_model_name = switch_model(taskHeader['sd_model_checkpoint'])
            logger.info(f'Current model is: {current_model_name}.')

        if taskType == 'text-to-image':
            r = invoke_txt2img(payload, taskHeader)
        elif taskType == 'image-to-image':
            r = invoke_img2img(payload, taskHeader)
        else:
            logger.error(f'Unsupported task type: {taskType}, ignoring')
        imgOutputs = post_invocations(folder, r, 80)
    except Exception as e:
        content = json.dumps(failed(taskHeader, e))
        traceback.print_exc()
    content = json.dumps(succeed(imgOutputs, r, taskHeader))
    upload_outputs(content, folder, None, 'out')
    return content

@xray_recorder.capture('text-to-image')
def invoke_txt2img(body, header):
    return do_invocations(apiBaseUrl+"txt2img", prepare_payload(body, header))

@xray_recorder.capture('image-to-image')
def invoke_img2img(body, header):
    return do_invocations(apiBaseUrl+"img2img", prepare_payload(body, header))

def invoke_set_options(options):
    return do_invocations(apiBaseUrl+"options", options)

def invoke_get_options():
    return do_invocations(apiBaseUrl+"options")

def invoke_get_model_names():
    return sorted([x["title"] for x in do_invocations(apiBaseUrl+"sd-models")])

def invoke_refresh_checkpoints():
    return utils.do_invocations(apiBaseUrl+"refresh-checkpoints", {})

def switch_model(name, find_closest=False):
    global current_model_name
    # check current model
    if find_closest:
        name = name.lower()
        current = current_model_name.lower()
        if name in current:
            return current_model_name
    else:
        if name == current_model_name:
            return current_model_name

    # refresh then check from model list
    invoke_refresh_checkpoints()
    models = invoke_get_model_names()
    found_model = None

    # exact matching
    if name in models:
        found_model = name
    # find closest
    elif find_closest:
        max_sim = 0.0
        max_model = None
        for model in models:
            sim = utils.str_simularity(name, model.lower())
            if sim > max_sim:
                max_sim = sim
                max_model = model
        found_model = max_model

    if not found_model:
        raise RuntimeError(f'Model not found: {name}')
    elif found_model != current_model_name:
        options = {}
        options["sd_model_checkpoint"] = found_model
        invoke_set_options(options)
        current_model_name = found_model

    return current_model_name

# Customizable for success responses
def succeed(images, response, header):
    n_iter = response['parameters']['n_iter']
    batch_size = response['parameters']['batch_size']
    parameters = response['parameters']
    parameters['id_task'] = header['id_task']
    parameters['status'] = 1
    parameters['image_url'] = ','.join(
        images[: n_iter * batch_size])
    parameters['image_seed'] = ','.join(
        str(x) for x in json.loads(response['info'])['all_seeds'])
    parameters['error_msg'] = ''
    parameters['image_mask_url'] = ','.join(images[n_iter * batch_size:])
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }


# Customizable for failure responses
def failed(header, exception):
    parameters = {}
    parameters['id_task'] = header['id_task']
    parameters['status'] = 0
    parameters['image_url'] = ''
    parameters['image_seed'] = []
    parameters['error_msg'] = repr(exception)
    parameters['reason'] = exception.response.json() if hasattr(exception, "response") else None
    parameters['image_mask_url'] = ''
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
            tasks = [loop.create_task(async_get(u)) for u in urls]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            if offset > 0:
                init_images = [encode_to_base64(x) for x in results[:offset]]
                body.update({"init_images": init_images})

            if 'controlnet' in header:
                for x in header['controlnet']['args']:
                    if 'image_link' in x:
                        x['input_image'] = encode_to_base64(results[offset])
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
        body.update({'alwayson_scripts': exclude_keys(
            header, ALWAYSON_SCRIPTS_EXCLUDE_KEYS)})
    except Exception as e:
        raise e

    return body

def post_invocations(folder, response, quality):
    defaultFolder = datetime.date.today().strftime("%Y-%m-%d")
    if not folder:
        folder = defaultFolder
    images = []
    results = []
    if "images" in response.keys():
        images = [export_pil_to_bytes(decode_to_image(i), quality)
                  for i in response["images"]]
    elif "image" in response.keys():
        images = [export_pil_to_bytes(
            decode_to_image(response["image"]), quality)]

    if len(images) > 0:
        results = [upload_outputs(i, folder, None, 'png') for i in images]

    return results