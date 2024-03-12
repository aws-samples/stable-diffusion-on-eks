# One-key deployment script

This script will work as a quick start for this solution. This script will:

* Install required tools
* Download Stable Diffusions 1.5 model from HuggingFace and upload to S3 bucket
* Generate EBS snapshot with prefetched container images
* Generate a sample config file
* Deploy SD on EKS solutions

## Usage

```bash
cd deploy
./deploy.sh
```

## Test after deploy

This script will generate text-to-image and image-to-image request to SD on EKS endpoints.

```bash
cd ../test
./run.sh
```