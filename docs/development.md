## Build from source

### Build Image

You can build images on your environment from source. This solutions requires 2 images, `inference-api` for Stable Diffusion Web UI runtime, and `queue-agent` for fetching message from queue and calling SD-Web UI.

To build `inference-api` image, run the following command:

```bash
docker build -t inference-api:latest src/sd_webui_api/
```

To build `queue-agent` image, run the following command:

```bash
docker build -t queue-agent:latest src/queue_agent/
```

### Push image to Amazon ECR

Before pushing image, create reposirory in Amazon ECR by running the following command:

```bash
aws ecr create-repository --repository-name sd-on-eks/inference-api
aws ecr create-repository --repository-name sd-on-eks/queue-agent
```

You can push image to Amazon ECR by running the following command. Replace `us-east-1` to your region and `123456789012` to your AWS account 12-digit ID:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker tag inference-api:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/inference-api:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/inference-api:latest

docker tag queue-agent:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
```

### Build and push helm chart

Helm chart is packaged and stored in [OCI](https://www.opencontainers.org/)-based registry. You can store helm chart in Amazon ECR.

Before pushing charts, create reposirory in Amazon ECR by running the following command:

```bash
aws ecr create-repository --repository-name sd-on-eks/charts/sd-on-eks
```

Package and push helm chart to Amazon ECR by running the following command. Replace `us-east-1` to your region and `123456789012` to your AWS account 12-digit ID:

```bash
helm package src/eks_cluster/charts/sd-on-eks
helm push sd-on-eks-<version>.tgz oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/
```

Now your chart is stored in Amazon ECR with `oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/sd-on-eks:<version>`.

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
