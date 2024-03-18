# Overview

Before deploying the solution, it is recommended to review information about the architecture diagram and regional support in this guide. Then follow the instructions below to configure and deploy the solution to your account.

## Prerequisites
Check if all considerations are met according to the [deployment planning](./considerations.md) document.

## Deployment Steps

We provide a one-click deployment script for quick start. Total deployment time is around 30 minutes.

### Get Source Code

Run the following command to get the source code and deployment scripts:

```bash
git clone --recursive https://github.com/aws-samples/stable-diffusion-on-eks
cd stable-diffusion-on-eks
```

### One-Click Deploy

Run the following command to quickly deploy with minimal settings:

```bash
cd deploy
./deploy.sh --deploy
```

The script will:

* Install required runtimes and tools
* Create an S3 bucket, download Stable Diffusion 1.5 base model from [HuggingFace](https://huggingface.co/runwayml/stable-diffusion-v1-5) and place it in the bucket
* Create an EBS snapshot containing the SD Web UI image using our sample image
* Create a Stable Diffusion solution with SD Web UI runtime

### Deployment Parameters

The script provides some parameters for you to customize the deployed solution:

* `-h, --help`: Show help information
* `-n, --stack-name`: Customize solution name, affecting generated resource names. Default is `sdoneks`.
* `-R, --region`: Region to deploy the solution. Defaults to current AWS profile region.
* `-d, --dry-run`: Only generate config files, do not deploy.
* `-b, --bucket`: Specify existing S3 bucket name to store models. The bucket must exist and be in same region as solution. You can manually create the S3 bucket following [this doc](./models.md).
* `-s, --snapshot`: Specify existing EBS snapshot ID. You can build the EBS snapshot yourself following [this doc](./ebs-snapshot.md).
* `-r, --runtime-name`: Specify deployed runtime name, affecting name used in API calls. Default is `sdruntime`.
* `-t, --runtime-type`: Specify deployed runtime type, only accepts `sdwebui` and `comfyui`. Default is `sdwebui`.

If you need to deploy multiple runtimes, or have other parameter requirements (like custom image), you can first use `--dry-run` to generate base config files by the script, then modify them.

## Manual Deployment

You can also manually deploy this solution on AWS without using the script by following these steps:

1. [Create Amazon S3 model bucket](./models.md) and store required models in the bucket
2. *(Optional)* [Build container image](./image-building.md)
3. *(Optional)* [Store container image in EBS cache to accelerate startup](./ebs-snapshot.md)
4. [Deploy and launch the solution stack](./deploy.md)