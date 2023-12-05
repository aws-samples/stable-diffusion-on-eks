# Overview

Before deploying the solution, it is recommended to review information in this guide, such as the architecture diagram and region support. Then, follow the instructions below to configure and deploy the solution to your account.

## Prerequisites
Check if all considerations are met according to the [Deployment Considerations](./considerations.md) document.

## Deployment Steps

Deploy this solution on AWS using the following steps.

1. [Create the Amazon S3 Model Bucket](./models.md) and store the required models in the bucket.
2. *(Optional)* [Build Container Images](./image-building.md).
3. *(Optional)* [Store Container Images in EBS Snapshots for Faster Startups](./ebs-snapshot.md).
4. [Deploy and Launch the Solution Stack](./deploy.md).

The total deployment time is approximately 30 minutes.

## Get the Source Code

Run the following commands to get the source code and deployment scripts:

```bash
git clone --recursive https://github.com/aws-samples/stable-diffusion-on-eks
cd stable-diffusion-on-eks
```