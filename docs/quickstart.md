## Quick start

### Requirement

* Kubernetes cluster 1.22+
* Helm v3
* Node.js 16+
* [AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
* An [AWS](https://aws.amazon.com/) Account
* Administrator or equivalent privilege


### Create S3 bucket and store model

Models should be stored in S3 bucket. Stable diffusion runtime will fetch model from S3 bucket at launch.

Create S3 bucket by running the following command:

```bash
aws s3api create-bucket --bucket model-store --region us-east-1
```

You can upload model to newly created S3 bucket by running the following command:

```bash
aws s3 cp <model name> s3://<bucket name>/models/
```

### Provision infrastructure and runtime

Required infrastructure and application is deployed via AWS CDK. We provide default configuration and image for quick start.

Run the following command to clone the code:

```bash
git clone --recursive <repo path>
cd stable-diffusion-on-eks
```

Before deploy, edit `config.yaml` and set `modelBucketArn` to the S3 bucket created on previous section.

```yaml
modelBucketArn: arn:aws:s3:::<bucket name>
```

Run the following command to deploy the stack:

```bash
npm install
cdk synth
cdk deploy --all
```

Deployment requires 20-30 minutes.

### Usage

TODO: Add usage guide

### Building EBS Snapshot

You can optimize launch speed by pre-caching your image as an EBS snapshot. When a new instance is launched, the data volume of the instance is pre-populated with image. When using image caching, you don't need to pull image from registry. You need to use `BottleRocket` as OS of worker node to use image caching.

EBS snapshot should be built before deploy infrastructure. Image should be pushed to a registry (Amazon ECR) before being cached. We provided a script for building EBS snapshot. Run the following command to build. Replace `us-east-1` to your region and `123456789012` to your AWS account 12-digit ID:

```bash
git submodule update --init --recursive
cd utils/bottlerocket-images-cache
./snapshot.sh 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/inference-api:latest,123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
```

This script will launch an instance, pull image from registry, and capture a snapshot with pulled image. After snapshot is built, put snapshot ID into `config.yaml`:

```yaml
modelsRuntime:
- name: "sdruntime"
  namespace: "default"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  extraValues:
    karpenter:
      nodeTemplate:
        amiFamily: Bottlerocket
        dataVolume:
          volumeSize: 80Gi
          volumeType: gp3
          deleteOnTermination: true
          iops: 4000
          throughput: 1000
          snapshotID: snap-0123456789 # Change to actual snapshot ID
```

See `ebs-snapshot.yaml` for more reference.
