import os
import io
import asyncio
import base64
import json
import time
import datetime
import requests
import boto3
import logging
import traceback
import uuid
import aioboto3
import difflib
from aiohttp_client_cache import CachedSession, CacheBackend
from botocore.exceptions import ClientError
from PIL import PngImagePlugin, Image
from requests.adapters import HTTPAdapter, Retry
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.models.trace_header import TraceHeader

patch_all()

logging.getLogger("aws_xray_sdk").setLevel(logging.ERROR)

aws_default_region = os.getenv("AWS_DEFAULT_REGION")
sqs_queue_url = os.getenv("SQS_QUEUE_URL")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
s3_bucket = os.getenv("S3_BUCKET")
dynamic_sd_model = os.getenv("DYNAMIC_SD_MODEL")

current_model_name = ''
sqsRes = boto3.resource('sqs')
ab3_session = aioboto3.Session()

apiBaseUrl = "http://localhost:8080/sdapi/v1/"
apiClient = requests.Session()
retries = Retry(
    total=3,
    connect=100,
    backoff_factor=0.1,
    allowed_methods=["GET", "POST"])
apiClient.mount('http://', HTTPAdapter(max_retries=retries))
REQUESTS_TIMEOUT_SECONDS = 30

cache = CacheBackend(
    cache_name='memory-cache',
    expire_after=600
)


def main():
    # Initialization:
    # 1. Environment parameters;
    # 2. AWS services resources(sqs/sns/s3);
    # 3. SD API readiness check, current checkpoint cached;
    print_env()

    queue = sqsRes.Queue(sqs_queue_url)
    SQS_WAIT_TIME_SECONDS = 20

    check_readiness()

    # main loop
    # todo: Implement scale-in hook signal
    # 1. Pull msg from sqs;
    # 2. Translate parameteres;
    # 3. (opt)Switch model;
    # 4. (opt)Prepare inputs for image downloading and encoding;
    # 5. Call SD API;
    # 6. Prepare outputs for decoding, uploading and notifying;
    # 7. Delete msg;
    while True:
        received_messages = receive_messages(queue, 1, SQS_WAIT_TIME_SECONDS)

        for message in received_messages:
            with xray_recorder.in_segment('Queue-Agent') as segment:
                # Retrieve x-ray trace header from SQS message
                traceHeaderStr = message.attributes['AWSTraceHeader']
                sqsTraceHeader = TraceHeader.from_header_str(traceHeaderStr)
                # Update current segment to link with SQS
                segment.trace_id = sqsTraceHeader.root
                segment.parent_id = sqsTraceHeader.parent
                segment.sampled = sqsTraceHeader.sampled

                try:
                    snsPayload = json.loads(message.body)
                    payload = json.loads(snsPayload['Message'])
                    taskHeader = payload.pop('alwayson_scripts', None)
                    taskType = taskHeader['task']
                    folder = get_prefix(payload['s3_output_path'])
                    print(
                        f"Start process {taskType} task with ID: {taskHeader['id_task']}")

                    if dynamic_sd_model == 'true' and taskHeader['sd_model_checkpoint']:
                        switch_model(taskHeader['sd_model_checkpoint'])
                        print(f'Current model is: {current_model_name}.')

                    if taskType == 'text-to-image':
                        r = invoke_txt2img(payload, taskHeader)
                    elif taskType == 'image-to-image':
                        r = invoke_img2img(payload, taskHeader)
                    else:
                        raise RuntimeError(
                            f'Unsupported task type: {taskType}')

                    imgOutputs = post_invocations(folder, r, 80)

                except Exception as e:
                    content = json.dumps(failed(taskHeader, repr(e)))
                    traceback.print_exc()
                else:
                    content = json.dumps(succeed(imgOutputs, r, taskHeader))
                finally:
                    handle_outputs(content, folder)
                    delete_message(message)
                    print(
                        f"End process {taskType} task with ID: {taskHeader['id_task']}")


def print_env():
    print(f'AWS_DEFAULT_REGION={aws_default_region}')
    print(f'SQS_QUEUE_URL={sqs_queue_url}')
    print(f'SNS_TOPIC_ARN={sns_topic_arn}')
    print(f'S3_BUCKET={s3_bucket}')
    print(f'DYNAMIC_SD_MODEL={dynamic_sd_model}')


def check_readiness():
    while True:
        try:
            print('Checking service readiness...')
            # checking with options "sd_model_checkpoint" also for caching current model
            opts = invoke_get_options()
            print('Service is ready.')
            if "sd_model_checkpoint" in opts:
                global current_model_name
                current_model_name = opts['sd_model_checkpoint']
                print(f'Init model is: {current_model_name}.')
            break
        except Exception as e:
            print(repr(e))
            time.sleep(1)


def get_time(f):

    def inner(*arg, **kwarg):
        s_time = time.time()
        res = f(*arg, **kwarg)
        e_time = time.time()
        print('Used: {:.4f} seconds on api: {}.'.format(
            e_time - s_time, arg[0]))
        return res
    return inner


def receive_messages(queue, max_number, wait_time):
    """
    Receive a batch of messages in a single request from an SQS queue.

    :param queue: The queue from which to receive messages.
    :param max_number: The maximum number of messages to receive. The actual number
                       of messages received might be less.
    :param wait_time: The maximum time to wait (in seconds) before returning. When
                      this number is greater than zero, long polling is used. This
                      can result in reduced costs and fewer false empty responses.
    :return: The list of Message objects received. These each contain the body
             of the message and metadata and custom attributes.
    """
    try:
        messages = queue.receive_messages(
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time,
            AttributeNames=['All'],
            MessageAttributeNames=['All']
        )
    except ClientError as error:
        traceback.print_exc()
        raise error
    else:
        return messages


def publish_message(topic, message):
    try:
        response = topic.publish(Message=message)
        message_id = response['MessageId']
    except ClientError as error:
        traceback.print_exc()
        raise error
    else:
        return message_id


def delete_message(message):
    """
    Delete a message from a queue. Clients must delete messages after they
    are received and processed to remove them from the queue.

    :param message: The message to delete. The message's queue URL is contained in
                    the message's metadata.
    :return: None
    """
    try:
        message.delete()
    except ClientError as error:
        traceback.print_exc()
        raise error


def get_bucket_and_key(s3uri):
    pos = s3uri.find('/', 5)
    bucket = s3uri[5: pos]
    key = s3uri[pos + 1:]
    return bucket, key


def get_prefix(path):
    pos = path.find('/')
    return path[pos + 1:]


def str_simularity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def encode_to_base64(buffer):
    return str(base64.b64encode(buffer))[2:-1]


def decode_to_image(encoding):
    image = None
    try:
        image = Image.open(io.BytesIO(base64.b64decode(encoding)))
    except Exception as e:
        raise e
    return image


def export_pil_to_bytes(image, quality):
    with io.BytesIO() as output_bytes:

        use_metadata = False
        metadata = PngImagePlugin.PngInfo()
        for key, value in image.info.items():
            if isinstance(key, str) and isinstance(value, str):
                metadata.add_text(key, value)
                use_metadata = True
        image.save(output_bytes, format="PNG", pnginfo=(
            metadata if use_metadata else None), quality=quality if quality else 80)

        bytes_data = output_bytes.getvalue()

    return bytes_data


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
    return do_invocations(apiBaseUrl+"refresh-checkpoints", {})


def switch_model(name, find_closest=True):
    global current_model_name
    # check current model
    if find_closest:
        name = name.lower()
        current = current_model_name.lower()

    if name in current:
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
            sim = str_simularity(name, model.lower())
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


def succeed(images, response, header):
    n_iter = response['parameters']['n_iter']
    batch_size = response['parameters']['batch_size']
    parameters = {}
    parameters['id_task'] = header['id_task']
    parameters['status'] = 1
    parameters['image_url'] = ','.join(
        images[: n_iter * batch_size])
    parameters['seed'] = ','.join(
        str(x) for x in json.loads(response['info'])['all_seeds'])
    parameters['error_msg'] = ''
    parameters['image_mask_url'] = ','.join(
        images[n_iter * batch_size:])
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }


def failed(header, message):
    parameters = {}
    parameters['id_task'] = header['id_task']
    parameters['status'] = 0
    parameters['image_url'] = ''
    parameters['seed'] = []
    parameters['error_msg'] = message
    parameters['image_mask_url'] = ''
    return {
        'images': [''],
        'parameters': parameters,
        'info': ''
    }


@get_time
def do_invocations(url, body=None):
    if body is None:
        response = apiClient.get(url=url, timeout=(1.0, 3.0))
    else:
        response = apiClient.post(
            url=url, json=body, timeout=(1, REQUESTS_TIMEOUT_SECONDS))
    response.raise_for_status()
    return response.json()


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
        loop = asyncio.get_event_loop()
        tasks = [async_upload(i, folder) for i in images]
        results = loop.run_until_complete(asyncio.gather(*tasks))

    return results


def handle_outputs(content, folder):
    loop = asyncio.get_event_loop()
    tasks = [async_upload(content, folder, None, suffix='out'),
             async_publish_message(content)]
    loop.run_until_complete(asyncio.wait(tasks))


async def async_get(url):
    try:
        if url.startswith("http://") or url.startswith("https://"):
            async with CachedSession(cache=cache) as session:
                async with session.get(url) as res:
                    res.raise_for_status()
                    # todo: need a counter to delete expired responses
                    # await session.delete_expired_responses()
                    # print(res.from_cache, res.created_at, res.expires, res.is_expired)
                    return await res.read()
        elif url.startswith("s3://"):
            bucket, key = get_bucket_and_key(url)
            async with ab3_session.resource("s3") as s3:
                obj = await s3.Object(bucket, key)
                res = await obj.get()
                return await res['Body'].read()
    except Exception as e:
        raise e


async def async_upload(object_bytes, folder, file_name=None, suffix=None):
    try:
        async with ab3_session.resource("s3") as s3:
            if suffix == 'out':
                content_type = f'application/json'
                if file_name is None:
                    file_name = f"response-{uuid.uuid4()}"
            else:
                suffix = 'png'
                content_type = f'image/{suffix}'
                if file_name is None:
                    file_name = datetime.datetime.now().strftime(
                        f"%Y%m%d%H%M%S-{uuid.uuid4()}")

            bucket = await s3.Bucket(s3_bucket)
            await bucket.put_object(
                Body=object_bytes, Key=f'{folder}/{file_name}.{suffix}', ContentType=content_type)

            return f's3://{s3_bucket}/{folder}/{file_name}.{suffix}'
    except Exception as e:
        raise e


async def async_publish_message(content):
    try:
        async with ab3_session.resource("sns") as sns:
            topic = await sns.Topic(sns_topic_arn)
            response = await topic.publish(Message=content)
            return response['MessageId']
    except Exception as e:
        raise e


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
            tasks = [async_get(u) for u in urls]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            if offset > 0:
                init_images = [encode_to_base64(x) for x in results[:offset]]
                body.update({"init_images": init_images})

            if 'controlnet' in header:
                for x in header['controlnet']['args']:
                    if 'image_link' in x:
                        x['input_image'] = encode_to_base64(results[offset])
                        offset += 1
                body.update(
                    {'alwayson_scripts': {'controlnet': header['controlnet']}})
    except Exception as e:
        raise e

    return body


if __name__ == '__main__':
    main()
