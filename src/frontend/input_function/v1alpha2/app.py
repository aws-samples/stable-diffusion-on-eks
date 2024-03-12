# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import traceback

import boto3

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            payload = json.loads(event['body'])
            val = validate(payload)
            if val != "success":
                return {
                    'statusCode': 400,
                    'body': 'Incorrect payload structure, ' + val
                }

            id = payload["metadata"]["id"]
            runtime = payload["metadata"]["runtime"]
            prefix = payload["metadata"]["prefix"]
            s3_output_path = f"{os.environ['S3_OUTPUT_BUCKET']}/{prefix}/{id}"

            print(event['headers'])
            print(event['queryStringParameters'])

            sns_client.publish(
                TargetArn=os.environ['SNS_TOPIC_ARN'],
                Message=json.dumps(payload),
                MessageStructure='json',
                MessageAttributes={
                    'runtime': {
                        'DataType': 'String',
                        'StringValue': runtime
                    }
                }
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    "id": id,
                    "runtime": runtime,
                    "output_location": f"s3://{s3_output_path}"
                })
            }

        except Exception as e:
            traceback.print_exc()
            return {
                'statusCode': 400,
                'body': str(e)
            }
    else:
        return {
            'statusCode': 400,
            'body': "Unsupported HTTP method"
        }


def validate(body: dict) -> str:
    result = "success"
    if "metadata" not in body.keys():
        result = "metadata is missing"
    else:
        if "id" not in body["metadata"].keys():
            result = "id is missing"
        if "runtime" not in body["metadata"].keys():
            result = "runtime is missing"
        if "tasktype" not in body["metadata"].keys():
            result = "tasktype is missing"
    if "content" not in body.keys():
        result = "content is missing"
    return result