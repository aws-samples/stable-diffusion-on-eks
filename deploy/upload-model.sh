#!/bin/bash

set -e

MODEL_BUCKET="$1"

AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')}

MODEL_URL="https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors?download=true"
MODEL_NAME="v1-5-pruned-emaonly.safetensors"

tmp_dir=$(mktemp -d)

printf "Downloading SD 1.5 base model from hugging face...\n"
curl --location --show-error --silent --output "${tmp_dir}/${MODEL_NAME}" "${MODEL_URL}"

printf "Uploading model to S3...\n"
s5cmd cp --destination-region="${AWS_DEFAULT_REGION}" "${tmp_dir}/${MODEL_NAME}" s3://${MODEL_BUCKET}/Stable-diffusion/${MODEL_NAME}

printf "Model uploaded to s3://${MODEL_BUCKET}/Stable-diffusion/${MODEL_NAME}\n"

rm -rf tmp_dir