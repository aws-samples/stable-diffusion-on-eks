# Deploying in AWS China Regions

This solution supports deployment in AWS China Regions.

| Region Name           | Validated |
|----------------|---------------------------------------|
| China (Ningxia)  | :material-check-bold:{ .icon_check }  |

However, due to the special network environment in China, the following limitations will apply:

* The default `g5` instance type is not supported in China regions. You need to manually specify the instance type used by Karpenter to be `g4dn` or other GPU instance types.
* You need to build container images yourself, or copy the standard images to ECR in the China region. It is not recommended to use images from ECR Public.
* Some component Helm Charts are hosted on Github, and there may be a chance that they cannot be retrieved when deploying in China regions, and you need to retry.
* Models cannot be automatically downloaded from Hugging Face or Github, and you need to manually download the models and upload them to an S3 bucket.

## Steps for Deploying in China Regions

The steps for deploying in AWS China Regions are different from the normal deployment process, and you should follow these steps:

1. Build or transfer images to ECR
2. Download models and store them in an S3 bucket
3. Create an EBS disk snapshot
4. Generate and modify configuration files
5. Proceed with deployment

### Build or Transfer Images to ECR

Since the default container images are stored in ECR Public, you may experience slow speeds or connection interruptions when pulling images or creating image caches. We recommend that you build the images yourself or transfer the existing images to your ECR image repository.

If you need to build the images yourself, please refer to the [Image Building](./image-building.md) documentation.

If you need to transfer pre-built images to ECR in the China region, you can run the following commands on an instance with Docker installed and ECR permissions:

```bash
docker pull public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest
docker pull public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest
docker pull public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest

aws ecr create-repository --repository-name sd-on-eks/sdwebui
aws ecr create-repository --repository-name sd-on-eks/comfyui
aws ecr create-repository --repository-name sd-on-eks/queue-agent

docker tag public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/sdwebui:latest
docker tag public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/comfyui:latest
docker tag public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/queue-agent:latest

aws ecr get-login-password --region cn-northwest-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.cn-northwest-1.amazonaws.com.cn

docker push 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/sdwebui:latest
docker push 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/comfyui:latest
docker push 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/queue-agent:latest
```

We recommend that you follow the instructions in the [Image Building](./image-building.md#build-and-push-helm-chart) documentation to place the Helm Chart in ECR or an HTTP server.

### Download Models and Store Them in an S3 Bucket

Since Hugging Face cannot be accessed smoothly in China, please download the models from other image sites and upload them to an S3 bucket following the instructions in the [Model Storage](./models.md) documentation.

### Create an EBS Disk Snapshot

Please follow the instructions in the [Image Cache Building](./ebs-snapshot.md) documentation to create an EBS disk snapshot to accelerate image loading.

### Generate and Modify Configuration Files

Run the following command to install the tools and generate the initial configuration files:

```bash
cd deploy
./deploy.sh -b <bucket name> -s <snapshot ID> -d
```

This command will generate a `config.yaml` template in the parent directory, but this template needs to be edited for deployment in the China region. Edit this file and add the following content:

```yaml
stackName: sdoneks
modelBucketArn: arn:aws-cn:s3:::${MODEL_BUCKET}  # Change aws to aws-cn in this ARN
APIGW:
  stageName: dev
  throttle:
    rateLimit: 30
    burstLimit: 50
modelsRuntime:
- name: sdruntime
  namespace: "default"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  dynamicModel: false
  # chartRepository: "http://example.com/" # If you host the Helm Chart yourself, uncomment this line and change the value to the address of the Helm Chart (oci:// or http://), otherwise delete this line.
  type: sdwebui
  extraValues:
    runtime:
      inferenceApi:
        image:
          repository: 123456789012.dkr.ecr.cn-northwest-1.amazonaws.com.cn/sd-on-eks/sdwebui # Change this to the address of your ECR image repository
          tag: latest
      queueAgent:
        image:
          repository: 123456789012.dkr.ecr.cn-northwest-1.amazonaws.com.cn/sd-on-eks/queue-agent # Change this to the address of your ECR image repository
          tag: latest
    karpenter:
      nodeTemplate:
        amiFamily: Bottlerocket
        dataVolume:
          volumeSize: 80Gi
          volumeType: gp3
          deleteOnTermination: true
          iops: 4000
          throughput: 1000
          snapshotID: snap-1234567890 # The EBS snapshot ID will be automatically filled in here
      provisioner:
        instanceType:
        - "g5.xlarge"
        - "g4dn.xlarge"
        - "g5.2xlarge"
        - "g4dn.2xlarge"
        capacityType:
          onDemand: true
          spot: true
      scaling:
        queueLength: 10
        minReplicaCount: 0
        maxReplicaCount: 5
        cooldownPeriod: 300
```

After completing the above steps, you can run the deployment command:

```bash
cdk deploy --no-rollback --require-approval never
```