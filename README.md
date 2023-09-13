# Guidance for Asynchronous Inference with Stable Diffusion Web UI on AWS

Implementing a fast scaling and low cost Stable Diffusion inference solution with serverless and containers on AWS

[AUTOMATIC1111 Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) is a popular open source project for generating images using Gen AI. Building a scalable and cost efficient inference solution is a common challenge AWS customers facing. This guidance shows how to use serverless and container services, such as Amazon API Gateway, AWS Lambda, Amazon SNS, Amazon SQS, and Amazon EKS to build an end-to-end low cost and fast scaling asyncronous image generation architecture. This repo contains the sample code and CDK deployment scripts, helping customers to deploy this solution in hours.

![SD-on-EKS-Arch](docs/images/sd-on-eks.png)

## Requirement

* Kubernetes cluster 1.22+
* Helm v3
* Node.js 16+
* [AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
* An [AWS](https://aws.amazon.com/) Account
* Administrator or equivalent privilege

## Quick start

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

See [the example](#ebs-snapshot-for-image-caching) below.

## Configuration

### Infrastructure

We use config file to customize infrastructure and runtime. By default, the config file name is `config.yaml`. You can use alternative config file by changing environment variable `CDK_CONFIG_PATH`.

The following table lists the configurable parameters of CDK template and the default values.

| Parameter | Description | Required | Default |
| --- | --- | --- | --- |
| `modelBucketArn` | S3 bucket for model storage. Models file should be manual populated into the bucket. This parameter applies to all runtimes. | Yes | `""` |
| `modelsRuntime` | Define Stable diffusion runtime. At least one runtime should be defined. | Yes | `- name: "sdruntime"  modelFilename: "v1-5-pruned-emaonly.ckpt"`
| `modelsRuntime.name` | Name of individual Stable diffusion runtime. | Yes | `sdruntime` |
| `modelsRuntime.namespace` | Namespace of individual Stable diffusion runtime. | Yes | `default` |
| `modelsRuntime.chartRepository` | Override default helm chart repository. Protocol (`oci://` or `https://`)should be added as a prefix of repository. (Default: `oci://public.ecr.aws/bingjiao/charts/sd-on-eks`) | No | N/A |
| `modelsRuntime.chartVersion` | Override version of helm chart. (Default: 0.1.0) | No | N/A |
| `modelsRuntime.modelFilename` | File of model using in the runtime. Filename should be in `.ckpt` or `.safetensors` format. Filename should be quoted if contains number only. | Yes | `v1-5-pruned-emaonly.safetensors` |
| `modelsRuntime.extraValues` | Extra parameter passed to the runtime. See [values definition](#application-helm-chart) for detail. | No | N/A |
| `dynamicModelRuntime.enabled` | Generate a runtime which allows models be switched by request. See multi model support for detail. | Yes | `false` |
| `dynamicModelRuntime.namespace` | Namespace of dynamic model runtime. Required if `dynamicModelRuntime.enabled` is `true`. | No | `default` |
| `dynamicModelRuntime.chartRepository` | Override default helm chart repository. (Default: `oci://public.ecr.aws/bingjiao/charts/sd-on-eks`) | No | N/A |
| `dynamicModelRuntime.chartVersion` | Override version of helm chart. (Default: 0.1.0) | No | N/A |
| `dynamicModelRuntime.extraValues` | Extra parameter passed to the runtime. See [values definition](#application-helm-chart) for detail. | No | N/A |

### Application (Helm Chart)

Stable diffusion runtime are deployed via helm chart. You can customize individual stable diffusion runtime by passing values via `modelsRuntime.extraValues`.

The following table lists the configurable parameters of helm chart and the default values. All values are not mandatory. Please some value will be populated by CDK, and not changeable by user.

| Parameter | Description | Default |
| --- | --- | --- |
| **Global** |  |  |
| `global.awsRegion` | AWS region where the stack resides. Not changable.  | Populated by CDK |
| `global.stackName` | Name of CDK stack. Not changable.  | Populated by CDK |
| **Karpenter Provisioner** | | |
| `karpenter.provisioner.labels` | Labels applied to all nodes. Should be in key-values format. | `{}` |
| `karpenter.provisioner.capacityType.onDemand` | Allow Karpenter to launch on-demand node.  | `true` |
| `karpenter.provisioner.capacityType.spot` | Allow Karpenter to create spot node. When `provisioner.capacityType.onDemand` is true, Karpenter will priortize launching Spot instance. | `true` |
| `karpenter.provisioner.instanceType` | An array of instance types Karpenter can launch. Should only include instance type available in current region. | `- "g5.xlarge"` |
| `karpenter.provisioner.extraRequirements` | Additional [requirement](https://karpenter.sh/preview/concepts/provisioners/#specrequirements) for Karpenter to choose instance type. | `[]` |
| `karpenter.provisioner.extraTaints` | Provisioned nodes will have `nvidia.com/gpu:NoSchedule` and `runtime:NoSchedule` taints by default. Use this paremeter for additional taints. | `[]` |
| `karpenter.provisioner.resourceLimits` | Resource limits prevent Karpenter from creating new instances once the limit is exceeded. `cpu`, `memory` and `nvidia.com/gpu` are supported. | `nvidia.com/gpu: 100` |
| `karpenter.provisioner.consolidation` | Enables [consolidation](https://karpenter.sh/preview/concepts/deprovisioning/#consolidation) which attempts to removing un-needed nodes and down-sizing those that can't be removed. | `true` |
| **Karpenter Node Template** | | |
| `karpenter.nodeTemplate.securityGroupSelector` | Tagged security groups will be attached to instances. Not changable. | Populated by CDK |
| `karpenter.nodeTemplate.subnetSelector` | Instances will be launched in tagged subnets. Not changable. | Populated by CDK |
| `karpenter.nodeTemplate.tags` | Tags applied to all nodes. Should be in key-values format. | `{}` |
| `karpenter.nodeTemplate.amiFamily` | OS option for worker nodes. Karpenter will automatically query for the appropriate EKS optimized AMI via AWS Systems Manager (SSM). `AL2` and `Bottlerocket` are supported. | `Bottlerocket` |
| `karpenter.nodeTemplate.osVolume` | Control the Elastic Block Storage (EBS) volumes that Karpenter attaches to provisioned nodes. See [this](https://karpenter.sh/docs/concepts/node-templates/#specblockdevicemappings) for schema. This volume will be attached to `/dev/xvda`. |  |
| `karpenter.nodeTemplate.dataVolume` | Control the Elastic Block Storage (EBS) volumes that Karpenter attaches to provisioned nodes. See [this](https://karpenter.sh/docs/concepts/node-templates/#specblockdevicemappings) for schema. This volume will be attached to `/dev/xvdb`. Required when using `Bottlerocket`. |  |
| `karpenter.nodeTemplate.userData` | UserData that is applied to your worker nodes. See [the examples here](https://github.com/aws/karpenter/tree/main/examples/provisioner/launchtemplates) for format. | `""` |
| **sdWebuiInferenceApi** | | |
| `sdWebuiInferenceApi.labels` | Labels applied to all resources. Should be in key-values format. | `""` |
| `sdWebuiInferenceApi.annotations` | Annotations applied to stable diffusion runtime. Should be in key-values format. | `""` |
| `sdWebuiInferenceApi.serviceAccountName` | Name of service account used by runtime. Not changable. | Populated by CDK |
| `sdWebuiInferenceApi.replicas` | Replica count of runtime. | `1` |
| `sdWebuiInferenceApi.scaling.enabled` | Enable auto scaling by SQS length.  | `true` |
| `sdWebuiInferenceApi.scaling.queueLength` | Target value for queue length. KEDA will scale pod to `ApproximateNumberOfMessage / queueLength` replicas.  | `10` |
| **Stable Diffusion Web UI** | | |
| `sdWebuiInferenceApi.inferenceApi.image.repository` | Image Repository of SD Web UI.  | `public.ecr.aws/bingjiao/sd-on-eks/inference-api` |
| `sdWebuiInferenceApi.inferenceApi.image.tag` | Image tag of SD Web UI.  | `latest` |
| `sdWebuiInferenceApi.inferenceApi.modelFilename` | Model filename of SD Web UI. Not changable. | Populated by CDK |
| `sdWebuiInferenceApi.inferenceApi.extraEnv` | Extra environment variable for SD Web UI. Should be in [Kubernetes format](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#define-an-environment-variable-for-a-container). | `{}` |
| `sdWebuiInferenceApi.inferenceApi.resources` | Resource request and limit for SD Web UI. |  |
| **Queue Agent** | | |
| `sdWebuiInferenceApi.queueAgent.image.repository` | Image Repository of queue agent.  | `public.ecr.aws/bingjiao/sd-on-eks/queue-agent` |
| `sdWebuiInferenceApi.queueAgent.image.tag` | Image tag of queue agent.  | `latest` |
| `sdWebuiInferenceApi.queueAgent.extraEnv` | Extra environment variable for queue agent. Should be in [Kubernetes format](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#define-an-environment-variable-for-a-container). | `{}` |
| `sdWebuiInferenceApi.queueAgent.dynamicModel` | Enable model switch by request. Not changable. | Populated by CDK |
| `sdWebuiInferenceApi.queueAgent.s3Bucket` | S3 bucket for generated image. Not changable. | Populated by CDK |
| `sdWebuiInferenceApi.queueAgent.snsTopicArn` | SNS topic for image generate complete notification. Not changable. | Populated by CDK |
| `sdWebuiInferenceApi.queueAgent.sqsQueueUrl` | SQS queue URL of job queue. Not changable. | Populated by CDK |
| `sdWebuiInferenceApi.queueAgent.resources` | Resource request and limit for queue agent. | |
| `sdWebuiInferenceApi.queueAgent.XRay.enabled` | Enable X-ray tracing agent for queue agent. | `true` |
| **Persistence** | | |
| `sdWebuiInferenceApi.persistence.enabled` | Enable presistence of model stroage. | `true` |
| `sdWebuiInferenceApi.persistence.labels` | Labels applied to presistence volume. Should be in key-values format. | `{}` |
| `sdWebuiInferenceApi.persistence.annotations` | Annotations applied to presistence volume. Should be in key-values format. | `{}` |
| `sdWebuiInferenceApi.persistence.storageClass` | Storage class for model storage | `efs-model-storage-sc` |
| `sdWebuiInferenceApi.persistence.size` | Size of persistence volume. | `2Ti` |
| `sdWebuiInferenceApi.persistence.accessModes` | Access mode of persistence volume. | `ReadWriteMany` |

## Deployment Examples

We provided example config file for your reference. These config files are located in `/examples`.

### Single Runtime with custom image

You can override default image repository or tag by passing values in `extraValues`. See the following example:

```yaml
modelsRuntime:
- name: "sdruntime"
  namespace: "default"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  extraValues:
    sdWebuiInferenceApi:
      inferenceApi:
        image:
          repository: public.ecr.aws/bingjiao/sd-on-eks/inference-api # Change image repository here
          tag: latest # Change image tag here
    queueAgent:
      image:
        repository: public.ecr.aws/bingjiao/sd-on-eks/queue-agent # Change image repository here
        tag: latest # Change image tag here
```

See `custom-image.yaml` for more reference.

### Multiple Runtimes

You can add multiple runtimes with different models by adding entries in `modelsRuntime` array. Each runtime should have different `modelFilename`. We recommand deploying runtimes in their own namespace.

```yaml
modelsRuntime:
- name: "sdruntime1" # First runtime
  namespace: "sdruntime1"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
- name: "sdruntime2" # Second runtime
  namespace: "sdruntime2"
  modelFilename: "v2-1_768-ema-pruned.safetensors"
```

See `multiple-runtimes.yaml` for more reference.

### Dynamic Model Runtime

By default, models are pre-loaded to runtime. Each runtime only accept request with its model filename. You can create dynamic model runtime as a catch-all option. By enabling dynamic model runtime, a new runtime with default model `v1-5-pruned-emaonly.safetensors` is created. This runtime will accept all requests without a matching runtime. Then, the runtime will load model by request. Models should be stored in S3 bucket before sending a request with this model.

```yaml
dynamicModelRuntime:
  enabled: true # Enable dynamic model runtime by change the value to "true"
  namespace: "default"
```

See `dynamic-runtime.yaml` for more reference.

### EBS Snapshot for Image Caching

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


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the Apache 2.0 License. See the LICENSE file.
