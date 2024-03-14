# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import boto3
import json
import traceback

sns_client = boto3.client('sns')


def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            payload = json.loads(event['body'])["task"]
            val = validate(payload)
            if (val != "success"):
                return {
                    'statusCode': 400,
                    'body': "Incorrect payload structure, {val}"
                }

            task = payload['alwayson_scripts']['task']
            id_task = payload['alwayson_scripts']['id_task']
            sd_model_checkpoint = payload['alwayson_scripts']['sd_model_checkpoint']
            prefix = payload['alwayson_scripts']['save_dir']
            s3_output_path = f"{os.environ['S3_OUTPUT_BUCKET']}/{prefix}/{id_task}"

            payload['s3_output_path'] = s3_output_path

            print(event['headers'])
            print(event['queryStringParameters'])

            msg = {"metadata": {
                "id": id_task,
                "runtime": "legacy",
                "tasktype": task,
                "prefix": prefix,
                "context": {}
                },"content": payload}

            sns_client.publish(
                TargetArn=os.environ['SNS_TOPIC_ARN'],
                Message=json.dumps({"default": json.dumps(msg)}),
                MessageAttributes={
                    'sd_model_checkpoint': {
                        'DataType': 'String',
                        'StringValue': sd_model_checkpoint
                    }
                }
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    "id_task": id_task,
                    "sd_model_checkpoint": sd_model_checkpoint,
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
    if 'alwayson_scripts' not in body.keys():
        result = "alwayson_scripts is missing"
    else:
        if "task" not in body["alwayson_scripts"].keys():
            result = "task is missing"
        if "sd_model_checkpoint" not in body["alwayson_scripts"].keys():
            result = "sd_model_checkpoint is missing"
        if "id_task" not in body["alwayson_scripts"].keys():
            result = "id_task is missing"
    return result