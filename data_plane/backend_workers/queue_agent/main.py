import os
import json
import base64
import requests
import boto3
import uuid
from botocore.exceptions import NoCredentialsError
from requests.adapters import HTTPAdapter, Retry

def main():
    session = boto3.Session(
        region_name=os.getenv("AWS_REGION")
    )

    sqs = session.client('sqs')
    s3 = session.client('s3')
    sns = session.client('sns')

    http_client = requests.Session()
    retries = Retry(connect=100,
                    backoff_factor=0.1,
                    allowed_methods=["GET", "POST"])
    http_client.mount('http://', HTTPAdapter(max_retries=retries))

    while True:
        response = sqs.receive_message(
            QueueUrl=os.getenv("SQS_QUEUE_URL"),
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
        )

        if 'Messages' not in response:
            print("No messages received")
            continue

        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        print("Received 1 request")

        sqs_payload = json.loads(message['Body'])

        http_response = http_client.post('http://localhost:8080/sdapi/v1/txt2img', json=sqs_payload)

        http_payload = http_response.json()

        image_filenames = []
        for img in http_payload['images']:
            image_bytes = base64.b64decode(img.split(",",1)[0])

            try:
                unique_filename = str(uuid.uuid4()) + ".png"
                s3.put_object(
                    Bucket=os.getenv("S3_BUCKET"),
                    Key=unique_filename,
                    Body=image_bytes
                )
                image_filenames.append(unique_filename)
            except NoCredentialsError:
                print("S3 access denied")
                return

        sns.publish(
            TopicArn=os.getenv("SNS_TOPIC_ARN"),
            Message=json.dumps({
                "message": "Images uploaded to S3 successfully!",
                "filenames": image_filenames
            })
        )

        sqs.delete_message(
            QueueUrl=os.getenv("SQS_QUEUE_URL"),
            ReceiptHandle=receipt_handle
        )
        print("Processed 1 request")

if __name__ == '__main__':
    main()