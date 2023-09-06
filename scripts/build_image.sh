#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"

IMAGE_TAG=$(git rev-parse --short HEAD)
REPO=public.ecr.aws/bingjiao/sd-on-eks
AGENT_IMAGE_NAME=queue-agent
SDWEBUI_IMAGE_NAME=inference-api

# Login: This line for ECR public
aws ecr-public get-login-password --region us-east-1 | helm registry login public.ecr.aws -u AWS --password-stdin
# Uncomment this line for ECR private
# aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

# Build images
docker build -t $AGENT_IMAGE_NAME:$IMAGE_TAG ../src/queue_agent/
docker tag $AGENT_IMAGE_NAME:$IMAGE_TAG $REPO/$AGENT_IMAGE_NAME:$IMAGE_TAG
docker push $REPO/$AGENT_IMAGE_NAME:$IMAGE_TAG

docker build -t $SDWEBUI_IMAGE_NAME:$IMAGE_TAG ../src/sd_webui_api/
docker tag $SDWEBUI_IMAGE_NAME:$IMAGE_TAG $REPO/$SDWEBUI_IMAGE_NAME:$IMAGE_TAG
docker push $REPO/$SDWEBUI_IMAGE_NAME:$IMAGE_TAG

echo "Images built: "
echo "$REPO/$AGENT_IMAGE_NAME:$IMAGE_TAG"
echo "$REPO/$SDWEBUI_IMAGE_NAME:$IMAGE_TAG"

# Build EBS snapshot
echo "Building EBS snapshot: "
cd ../utils/bottlerocket-images-cache/
./snapshot.sh $REPO/$AGENT_IMAGE_NAME:$IMAGE_TAG, $REPO/$SDWEBUI_IMAGE_NAME:$IMAGE_TAG
