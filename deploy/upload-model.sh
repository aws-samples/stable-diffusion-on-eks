#!/bin/bash

set -e

MODEL_BUCKET="$1"

AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws ec2 describe-availability-zones --output text --query 'AvailabilityZones[0].[RegionName]')}

MODEL_URL="https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors?download=true"
MODEL_NAME="v1-5-pruned-emaonly.safetensors"

printf "Transport SD 1.5 base model from hugging face to S3 bucket...\n"
curl -L "$MODEL_URL" | aws s3 cp - s3://${MODEL_BUCKET}/Stable-diffusion/${MODEL_NAME}

printf "Model uploaded to s3://${MODEL_BUCKET}/Stable-diffusion/${MODEL_NAME}\n"
