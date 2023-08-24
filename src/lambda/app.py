import os
import boto3
import json
import traceback
import uuid

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            payload = json.loads(event['body'])

            if('alwayson_scripts' not in payload or 'task' not in payload['alwayson_scripts'] or 'sd_model_checkpoint' not in payload['alwayson_scripts'] or 'id_task' not in payload['alwayson_scripts']):
                return {
                    'statusCode': 400,
                    'body': 'Incorrect payload structure'
                }

            # payload['s3_output_path'] = f"{os.environ['S3_OUTPUT_BUCKET']}/{payload['alwayson_scripts']['id_task']/{str(uuid.uuid4())}}"
            payload['s3_output_path'] = f"{os.environ['S3_OUTPUT_BUCKET']}/{payload['alwayson_scripts']['id_task']}"

            print(event['headers'])
            print(event['queryStringParameters'])

            sns_client.publish(
                TargetArn=os.environ['SNS_TOPIC_ARN'],
                Message=json.dumps({"default": json.dumps(payload)}),
                MessageStructure='json'
            )
            
            return {
                'statusCode': 200,
                'body': payload['s3_output_path']
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
