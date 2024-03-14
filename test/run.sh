#!/bin/bash

set -e

SCRIPTPATH=$(realpath $(dirname "$0"))
STACK_NAME=${STACK_NAME:-"sdoneks-devStack"}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')}
declare -l RUNTIME_TYPE=${RUNTIME_TYPE:-"comfyui"}
API_VERSION=${API_VERSION:-"v1alpha2"}

API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --output text --query 'Stacks[0].Outputs[?OutputKey==`FrontApiEndpoint`].OutputValue')

printf "API Endpoint is ${API_ENDPOINT}\n"

API_KEY_COMMAND=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --output text --query 'Stacks[0].Outputs[?OutputKey==`GetAPIKeyCommand`].OutputValue')

API_KEY=$(echo $API_KEY_COMMAND | bash)

printf "API Key is ${API_KEY}\n"

if [[ ${RUNTIME_TYPE} == "sdwebui" ]]
  then
    printf "Generating test text-to-image request... \n"

    curl -X POST ${API_ENDPOINT}/${API_VERSION}/ \
        -H "Content-Type: application/json" \
        -H "x-api-key: ${API_KEY}" \
        -d @${SCRIPTPATH}/${API_VERSION}/t2i.json

    printf "\nGenerating test image-to-image request... \n"

    curl -X POST ${API_ENDPOINT}/${API_VERSION}/ \
        -H "Content-Type: application/json" \
        -H "x-api-key: ${API_KEY}" \
        -d @${SCRIPTPATH}/${API_VERSION}/i2i.json
fi

if [[ ${RUNTIME_TYPE} == "comfyui" ]]
  then
    printf "Generating test pipeline request... \n"

    curl -X POST ${API_ENDPOINT}/${API_VERSION} \
        -H "Content-Type: application/json" \
        -H "x-api-key: ${API_KEY}" \
        -d @${SCRIPTPATH}/${API_VERSION}/pipeline.json
fi