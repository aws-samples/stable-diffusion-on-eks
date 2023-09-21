# Build from source

## Build Image

You can build queue agent container image on your environment from source. `queue-agent` is for fetching message from queue and convert message to API request to Stable Diffusion Runtime.

To build `queue-agent` image, run the following command:

```bash
docker build -t queue-agent:latest src/backend/queue_agent/
```

## Push image to Amazon ECR

Before pushing image, create reposirory in Amazon ECR by running the following command:

```bash
aws ecr create-repository --repository-name sd-on-eks/queue-agent
```

You can push image to Amazon ECR by running the following command. Replace `us-east-1` to your region and `123456789012` to your AWS account 12-digit ID:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker tag queue-agent:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
```

## Build and push helm chart

Helm chart is packaged and stored in [OCI](https://www.opencontainers.org/)-based registry. You can store helm chart in Amazon ECR.

Before pushing charts, create reposirory in Amazon ECR by running the following command:

```bash
aws ecr create-repository --repository-name sd-on-eks/charts/sd-on-eks
```

Package and push helm chart to Amazon ECR by running the following command. Replace `us-east-1` to your region and `123456789012` to your AWS account 12-digit ID:

```bash
helm package src/charts/sd_on_eks
helm push sd-on-eks-<version>.tgz oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/
```

Now your chart is stored in Amazon ECR with `oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/sd-on-eks:<version>`.
