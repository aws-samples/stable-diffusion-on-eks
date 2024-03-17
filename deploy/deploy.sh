#!/bin/bash

set -e

SHORTOPTS="h,n:,R:,d,b:,s:,r:,t:"
LONGOPTS="help,stack-name:,region:,deploy,bucket:,snapshot:,runtime-name:,runtime-type:"
ARGS=$(getopt --options $SHORTOPTS --longoptions $LONGOPTS -- "$@" )

eval set -- "$ARGS"
while true;
do
    case $1 in
        -h|--help)
          printf "Usage: deploy.sh [options] \n"
          printf "Options: \n"
          printf "  -h, --help                   Print this help message \n"
          printf "  -n, --stack-name             Name of the stack to be created (Default: sdoneks) \n"
          printf "  -R, --region                 AWS region to be used \n"
          printf "  -d, --deploy                 Deploy the stack. If not specified, you can manually deploy the stack.\n"
          printf "  -b, --bucket                 S3 bucket name to store the model. If not specified, S3 bucket will be created and SD 1.5 model will be placed. \n"
          printf "  -s, --snapshot               EBS snapshot ID with container image. If not specified, EBS snapshot will be automatically generated. \n"
          printf "  -r, --runtime-name           Runtime name. (Default: sdruntime) \n"
          printf "  -t, --runtime-type           Runtime type. Only 'sdwebui' and 'comfyui' is accepted. (Default: sdwebui) \n"
          shift
          ;;
        -n|--stack-name)
          STACK_NAME=$2
          shift 2
          ;;
        -R|--region)
          AWS_DEFAULT_REGION=$2
          shift 2
          ;;
        -d|--deploy)
          DEPLOY=true
          shift
          ;;
        -b|--bucket)
          MODEL_BUCKET=$2
          shift 2
          ;;
        -s|--snapshot)
          SNAPSHOT_ID=$2
          shift 2
          ;;
        -r|--runtime-name)
          RUNTIME_NAME=$2
          shift 2
          ;;
        -t|--runtime-type)
          RUNTIME_TYPE=$2
          shift 2
          ;;
        --)
          shift
          break
          ;;
    esac
done


SCRIPTPATH=$(realpath $(dirname "$0"))
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')}
declare -l STACK_NAME=${STACK_NAME:-"sdoneks"}
RUNTIME_NAME=${RUNTIME_NAME:-"sdruntime"}
declare -l RUNTIME_TYPE=${RUNTIME_TYPE:-"sdwebui"}
DEPLOY=${DEPLOY:-false}
SDWEBUI_IMAGE=public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest
COMFYUI_IMAGE=public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest
QUEUE_AGENT_IMAGE=public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest

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
    SNAPSHOT_ID=$(utils/bottlerocket-images-cache/snapshot.sh -q ${SDWEBUI_IMAGE},${QUEUE_AGENT_IMAGE})
  fi
  if [[ ${RUNTIME_TYPE} == "comfyui" ]]; then
    SNAPSHOT_ID=$(utils/bottlerocket-images-cache/snapshot.sh -q ${COMFYUI_IMAGE},${QUEUE_AGENT_IMAGE})
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
cdk bootstrap
if [ ${DEPLOY} = true ] ; then
  cdk deploy --no-rollback --require-approval never
  printf "Deploy complete. \n"
else
  printf "Please revise config.yaml and run 'cdk deploy --no-rollback --require-approval never' to deploy. \n"
fi
