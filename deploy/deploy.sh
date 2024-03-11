#!/bin/bash

set -e

SCRIPTPATH=$(realpath $(dirname "$0"))
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')}
declare -l STACK_NAME=${STACK_NAME:-"sdoneks"}
declare -l RUNTIME_TYPE=${RUNTIME_TYPE:-"sdwebui"}

# Step 1: Install tools

printf "Step 1: Install tools... \n"
"${SCRIPTPATH}"/install-tools.sh

# Step 2: Create S3 bucket and upload model

printf "Step 2: Create S3 bucket and upload SD 1.5 model... \n"
if [ -z "${MODEL_BUCKET}" ] ; then
  MODEL_BUCKET="${STACK_NAME}"-model-bucket-$(echo ${RANDOM} | md5sum | head -c 4)
  aws s3 mb "s3://${MODEL_BUCKET}" --region "${AWS_DEFAULT_REGION}"
  "${SCRIPTPATH}"/upload-model.sh "${MODEL_BUCKET}"
else
  printf "Existing bucket detected, skipping... \n"
fi

# Step 3: Create EBS Snapshot

printf "Step 3: Creating EBS snapshot for faster launching... \n"
if [ -z "$SNAPSHOT_ID" ]; then
  cd "${SCRIPTPATH}"/..
  git submodule update --init --recursive
  if [[ "$RUNTIME_TYPE" == "sdwebui" ]] ; then
    SNAPSHOT_ID=$(utils/bottlerocket-images-cache/snapshot.sh -q docker.io/sdoneks/inference-api:sdwebui-v1.7.0-20240229,docker.io/sdoneks/queue-agent:latest)
  fi
  if [[ ${RUNTIME_TYPE} == "comfyui" ]]; then
    SNAPSHOT_ID=$(utils/bottlerocket-images-cache/snapshot.sh -q docker.io/sdoneks/inference-api:comfyui,docker.io/sdoneks/queue-agent:latest)
  fi
else
  printf "Existing snapshot ID detected, skipping... \n"
fi

# Step 4: Deploy

printf "Step 4: Start deploy... \n"
aws iam create-service-linked-role --aws-service-name spot.amazonaws.com >/dev/null 2>&1 || true
cd "${SCRIPTPATH}"/..
sudo npm install

template="$(cat deploy/config.yaml.template)"
eval "echo \"${template}\"" > config.yaml

cdk deploy --no-execute --require-approval never

printf "Deploy complete. \n"
