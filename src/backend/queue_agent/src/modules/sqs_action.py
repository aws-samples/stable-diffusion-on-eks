import logging
from botocore.exceptions import ClientError

logger = logging.getLogger("queue-agent")

def receive_messages(queue, max_number, wait_time):
    try:
        messages = queue.receive_messages(
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time,
            AttributeNames=['All'],
            MessageAttributeNames=['All']
        )
    except ClientError as error:
        logger.error('Failed to get message from SQS', exc_info=True)
        raise error
    else:
        return messages

def delete_message(message):
    try:
        message.delete()
    except ClientError as error:
        logger.error('Failed to delete message from SQS', exc_info=True)
        raise error