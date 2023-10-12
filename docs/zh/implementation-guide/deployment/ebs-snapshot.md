# Building EBS Snapshot

You can optimize launch speed by pre-caching your image as an EBS snapshot. When a new instance is launched, the data volume of the instance is pre-populated with image. When using image caching, you don't need to pull image from registry. You need to use `BottleRocket` as OS of worker node to use image caching.

EBS snapshot should be built before deploy infrastructure. Image should be pushed to a registry (Amazon ECR) before being cached. We provided a script for building EBS snapshot.

Run the following command to build if you have built your own image. Replace `us-east-1` to your region and `123456789012` to your AWS account 12-digit ID:

```bash
git submodule update --init --recursive
cd utils/bottlerocket-images-cache
./snapshot.sh 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/inference-api:latest,123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
```

Run the following command to build if you want to use pre-built image from Dockerhub:

```bash
git submodule update --init --recursive
cd utils/bottlerocket-images-cache
./snapshot.sh sdoneks/inference-api:latest,sdoneks/queue-agent:latest
```

This script will launch an instance, pull image from registry, and capture a snapshot with pulled image.

After snapshot is built, put snapshot ID into `config.yaml`:

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

See [`example/ebs-snapshot.yaml`](../examples/ebs-snapshot.yaml) for more reference.