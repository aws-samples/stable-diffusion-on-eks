#!/bin/bash

set -e

SCRIPTPATH=$(dirname "${BASH_SOURCE[0]}")
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')}
STACK_NAME=${STACK_NAME:-"SDonEKS"}
declare -l RUNTIME_TYPE=${STACK_NAME:-"sdwebui"}

# Step 1: Install tools

printf "Step 1: Install tools... \n"
${SCRIPTPATH}/install-tools.sh

# Step 2: Create S3 bucket and upload model

printf "Step 2: Create S3 bucket and upload SD 1.5 model... \n"
if [ -z ${MODEL_BUCKET} ] ; then
  MODEL_BUCKET="${STACK_NAME}"-model-bucket-$(echo ${RANDOM} | md5sum | head -c 4)
  aws s3api create-bucket --bucket ${MODEL_BUCKET} --region ${AWS_DEFAULT_REGION}
  ${SCRIPTPATH}/upload-model.sh ${MODEL_BUCKET}
else
  printf "Existing bucket detected, skipping... \n"
fi

# Step 3: Create EBS Snapshot

printf "Step 3: Creating EBS snapshot for faster launching... \n"
if [ -z $SNAPSHOT_ID ] ; then
  cd ${SCRIPTPATH}/..
  git submodule update --init --recursive
  if [[ $RUNTIME_TYPE = "sdwebui" ]] ; then
    SNAPSHOT_ID=$(utils/bottlerocket-images-cache/snapshot.sh -q docker.io/sdoneks/inference-api:sdwebui-v1.7.0,docker.io/sdoneks/queue-agent:latest)
  else
    SNAPSHOT_ID=$(utils/bottlerocket-images-cache/snapshot.sh -q docker.io/sdoneks/inference-api:comfyui,docker.io/sdoneks/queue-agent:latest)
else
  printf "Existing snapshot ID detected, skipping... \n"
fi

# Step 4: Deploy

printf "Step 4: Start deploy... \n"
cd ${SCRIPTPATH}/..
npm install
envsubst < deploy/config.yaml.template > config.yaml
cdk install --no-rollback --require-approval never

printf "Deploy complete. \n"
