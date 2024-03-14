#!/bin/bash

docker run -it -e AWS_DEFAULT_REGION=us-west-2 \
-e RUNTIME_TYPE="comfyui" \
-e S3_BUCKET="sdoneks-devstack-outputs3bucket9fe85b9f-erbvhhpcyjnr" \
-e SNS_TOPIC_ARN="arn:aws:sns:us-west-2:600413481647:sdoneks-devStack-sdNotificationOutputCfn-5s8JofkPogUJ" \
-e SQS_QUEUE_URL="https://sqs.us-west-2.amazonaws.com/600413481647/sdoneks-devStack-InputQueuecomfyui55CAAB14-vuHib4Ztmt5g" \
-e API_BASE_URL="172.31.33.229:8000" \
-e LOGLEVEL="DEBUG" \
600413481647.dkr.ecr.us-west-2.amazonaws.com/queue-agent:20240314