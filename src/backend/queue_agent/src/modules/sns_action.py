import logging

import aioboto3
from botocore.exceptions import ClientError

logger = logging.getLogger("queue-agent")

ab3_session = aioboto3.Session()

def publish_message(topic, message: str) -> str:
    try:
        response = topic.publish(Message=message)
        message_id = response['MessageId']
    except ClientError as error:
        logger.error('Failed to send message to SNS', exc_info=True)
        raise error
    else:
        return message_id

async def async_publish_message(topic, content: str):
    try:
        async with ab3_session.resource("sns") as sns:
            topic = await sns.Topic(topic)
            response = await topic.publish(Message=content)
            return response['MessageId']
    except Exception as e:
        raise e