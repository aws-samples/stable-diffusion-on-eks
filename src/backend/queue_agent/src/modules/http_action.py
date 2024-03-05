
@utils.get_time
def do_invocations(url, body=None):

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

async def async_get(url):
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
            bucket, key = get_bucket_and_key(url)
            async with ab3_session.resource("s3") as s3:
                obj = await s3.Object(bucket, key)
                res = await obj.get()
                return await res['Body'].read()
    except Exception as e:
        raise e