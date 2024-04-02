# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import aioboto3
import boto3
import requests
import requests_cache
from aiohttp_client_cache import CacheBackend, CachedSession
from requests.adapters import HTTPAdapter, Retry

from . import s3_action, time_utils

logger = logging.getLogger("queue-agent")


ab3_session = aioboto3.Session()

apiClient = requests.Session()
retries = Retry(
    total=3,
    connect=100,
    backoff_factor=0.1,
    allowed_methods=["GET", "POST"])
apiClient.mount('http://', HTTPAdapter(max_retries=retries))

REQUESTS_TIMEOUT_SECONDS = 300

cache = CacheBackend(
    cache_name='memory-cache',
    expire_after=600
)

@time_utils.get_time
def do_invocations(url: str, body:str=None) -> str:
    if body is None:
        logger.debug(f"Invoking {url}")
        response = apiClient.get(
            url=url, timeout=(1, REQUESTS_TIMEOUT_SECONDS))
    else:
        logger.debug(f"Invoking {url} with body: {body}")
        response = apiClient.post(
            url=url, json=body, timeout=(1, REQUESTS_TIMEOUT_SECONDS))
    response.raise_for_status()
    logger.debug(response.text)
    return response.json()

def get(url: str) -> bytes:
    logger.debug(f"Downloading {url}")
    try:
        if url.lower().startswith("http://") or url.lower().startswith("https://"):
            with requests_cache.CachedSession('demo_cache') as session:
                with session.get(url) as res:
                    res.raise_for_status()
                    return res.content
        elif url.lower().startswith("s3://"):
            bucket_name, key = s3_action.get_bucket_and_key(url)
            with boto3.client('s3') as s3:
                obj = s3.get_object(Bucket=bucket_name, Key=key)
                data = obj['Body'].read()
                return data
    except Exception as e:
        raise e

async def async_get(url: str) -> None:
    try:
        if url.lower().startswith("http://") or url.lower().startswith("https://"):
            async with CachedSession(cache=cache) as session:
                async with session.get(url) as res:
                    res.raise_for_status()
                    return await res.read()
        elif url.lower().startswith("s3://"):
            bucket_name, key = s3_action.get_bucket_and_key(url)
            async with ab3_session.resource("s3") as s3:
                obj = await s3.Object(bucket_name, key)
                res = await obj.get()
                return await res['Body'].read()
    except Exception as e:
        raise e