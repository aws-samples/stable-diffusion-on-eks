#!/bin/bash
set -v
set -e

# This script shows how to build the Docker image and push it to ECR to be ready for use
# by SageMaker.

# The argument to this script is the region name. 

if [ "$#" -ne 1 ] ; then
    echo "usage: $0 [region-name] [option]"
    exit 1
fi

region=$1

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)

if [ $? -ne 0 ]
then
    exit 255
fi

inference_image=inference-api
inference_fullname=${account}.dkr.ecr.${region}.amazonaws.com/${inference_image}:latest

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${inference_image}" --region ${region} || aws ecr create-repository --repository-name "${inference_image}" --region ${region}

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${inference_image}" --region ${region}
fi

# Get the login command from ECR and execute it directly
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $account.dkr.ecr.$region.amazonaws.com

aws ecr set-repository-policy \
    --repository-name "${inference_image}" \
    --policy-text "file://ecr-policy.json" \
    --region ${region}

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

docker build -t ${inference_image}:latest ../stable-diffusion-on-eks/src/backend/sd_webui_api/

docker tag ${inference_image} ${inference_fullname}

docker push ${inference_fullname}

queue_image=queue-agent
queue_fullname=${account}.dkr.ecr.${region}.amazonaws.com/${queue_image}:latest

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${queue_image}" --region ${region} || aws ecr create-repository --repository-name "${queue_image}" --region ${region}

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${queue_image}" --region ${region}
fi

# Get the login command from ECR and execute it directly
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $account.dkr.ecr.$region.amazonaws.com

aws ecr set-repository-policy \
    --repository-name "${queue_image}" \
    --policy-text "file://ecr-policy.json" \
    --region ${region}

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

docker build -t ${queue_image}:latest ../stable-diffusion-on-eks/src/backend/queue_agent/

docker tag ${queue_image} ${queue_fullname}

docker push ${queue_fullname}


helm_packge=sd-on-eks/charts/sd-on-eks
helm_packge_fullname=${account}.dkr.ecr.${region}.amazonaws.com/${helm_packge}

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${helm_packge}" --region ${region} || aws ecr create-repository --repository-name "${helm_packge}" --region ${region}

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${helm_packge}" --region ${region}
fi

# Get the login command from ECR and execute it directly
aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $account.dkr.ecr.$region.amazonaws.com

aws ecr set-repository-policy \
    --repository-name "${helm_packge}" \
    --policy-text "file://ecr-policy.json" \
    --region ${region}

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

helm package ../stable-diffusion-on-eks/src/charts/sd_on_eks
helm push sd-on-eks-0.1.0.tgz oci://$account.dkr.ecr.$region.amazonaws.com/sd-on-eks/charts/