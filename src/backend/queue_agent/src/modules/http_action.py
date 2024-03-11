# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging

import aioboto3
import requests
from aiohttp_client_cache import CacheBackend
from requests.adapters import HTTPAdapter, Retry
from requests_cache import CachedSession

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

REQUESTS_TIMEOUT_SECONDS = 60

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

async def async_get(url: str) -> None:
    try:
        if url.startswith("http://") or url.startswith("https://"):
            async with CachedSession(cache=cache) as session:
                async with session.get(url) as res:
                    res.raise_for_status()
                    # todo: need a counter to delete expired responses
                    # await session.delete_expired_responses()
                    # logger.info(res.from_cache, res.created_at, res.expires, res.is_expired)
                    return await res.read()
        elif url.startswith("s3://"):
            bucket, key = s3_action.get_bucket_and_key(url)
            async with ab3_session.resource("s3") as s3:
                obj = await s3.Object(bucket, key)
                res = await obj.get()
                return await res['Body'].read()
    except Exception as e:
        raise e