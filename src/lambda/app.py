import os
import boto3
import json
import traceback

sns_client = boto3.client('sns')


def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            payload = json.loads(event['body'])

            if ('alwayson_scripts' not in payload or 'task' not in payload['alwayson_scripts'] or 'sd_model_checkpoint' not in payload['alwayson_scripts'] or 'id_task' not in payload['alwayson_scripts']):
                return {
                    'statusCode': 400,
                    'body': 'Incorrect payload structure'
                }

            task = payload['alwayson_scripts']['task']
            id_task = payload['alwayson_scripts']['id_task']
            sd_model_checkpoint = payload['alwayson_scripts']['sd_model_checkpoint']
            s3_output_path = f"{os.environ['S3_OUTPUT_BUCKET']}/{payload['alwayson_scripts']['id_task']}"

            payload['s3_output_path'] = s3_output_path

            print(event['headers'])
            print(event['queryStringParameters'])

            sns_client.publish(
                TargetArn=os.environ['SNS_TOPIC_ARN'],
                Message=json.dumps({"default": json.dumps(payload)}),
                MessageStructure='json',
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
                    "task": task,
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
