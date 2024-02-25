# Configuration

## Infrastructure

We use config file to customize infrastructure and runtime. By default, the config file name is `config.yaml`. You can use alternative config file by changing environment variable `CDK_CONFIG_PATH`.

The following table lists the configurable parameters of CDK template and the default values.

| Parameter | Description | Required | Default |
| --- | --- | --- | --- |
| `stackName` | Name of the stack. The name will be added as a prefix of all resource name.  | Yes | `SdOnEKS` |
| `modelBucketArn` | S3 bucket for model storage. Models file should be manual populated into the bucket. This parameter applies to all runtimes. | Yes | `""` |
| `modelsRuntime` | Define Stable diffusion runtime. At least one runtime should be defined. | Yes | `- name: "sdruntime"  modelFilename: "v1-5-pruned-emaonly.ckpt"`
| `modelsRuntime.name` | Name of individual Stable diffusion runtime. | Yes | `sdruntime` |
| `modelsRuntime.namespace` | Namespace of individual Stable diffusion runtime. | Yes | `default` |
| `modelsRuntime.chartRepository` | Override default helm chart repository. Protocol (`oci://` or `https://`)should be added as a prefix of repository. (Default: `https://aws-samples.github.io/stable-diffusion-on-eks`) | No | N/A |
| `modelsRuntime.chartVersion` | Override version of helm chart. (Default: 0.1.0) | No | N/A |
| `modelsRuntime.modelFilename` | File of model using in the runtime. Filename should be in `.ckpt` or `.safetensors` format. Filename should be quoted if contains number only. | Yes | `v1-5-pruned-emaonly.safetensors` |
| `modelsRuntime.extraValues` | Extra parameter passed to the runtime. See [values definition](#application-helm-chart) for detail. | No | N/A |
| `dynamicModelRuntime.enabled` | Generate a runtime which allows models be switched by request. See multi model support for detail. | Yes | `false` |
| `dynamicModelRuntime.namespace` | Namespace of dynamic model runtime. Required if `dynamicModelRuntime.enabled` is `true`. | No | `default` |
| `dynamicModelRuntime.chartRepository` | Override default helm chart repository. (Default: `https://aws-samples.github.io/stable-diffusion-on-eks`) | No | N/A |
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
| **runtime** | | |
| `runtime.labels` | Labels applied to all resources. Should be in key-values format. | `""` |
| `runtime.annotations` | Annotations applied to stable diffusion runtime. Should be in key-values format. | `""` |
| `runtime.serviceAccountName` | Name of service account used by runtime. Not changable. | Populated by CDK |
| `runtime.replicas` | Replica count of runtime. | `1` |
| `runtime.scaling.enabled` | Enable auto scaling by SQS length.  | `true` |
| `runtime.scaling.queueLength` | Target value for queue length. KEDA will scale pod to `ApproximateNumberOfMessage / queueLength` replicas.  | `10` |
| `runtime.scaling.cooldownPeriod` | The period (in seconds) to wait after the last trigger reported active before scaling the resource back to `minReplicaCount`.  | `60` |
| `runtime.scaling.maxReplicaCount` | This setting is passed to the HPA definition that KEDA will create for a given resource and holds the maximum number of replicas of the target resource. | `20` |
| `runtime.scaling.minReplicaCount` | Minimum number of replicas KEDA will scale the resource down to.  | `0` |
| `runtime.scaling.pollingInterval` | Interval (in seconds) to check each trigger on.  | `1` |
| `runtime.scaling.scaleOnInFlight` | When set to `true`, not visible (in-flight) messages will be counted in `ApproximateNumberOfMessage` | `false` |
| `runtime.scaling.extraHPAConfig` | KEDA would feed values from this section directly to the HPA’s `behavior` field. Follow [Kubernetes documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#configurable-scaling-behavior) for details. | `{}` |
| **Stable Diffusion Runtime** | | |
| `runtime.inferenceApi.image.repository` | Image Repository of Runtime.  | `sdoneks/inference-api` |
| `runtime.inferenceApi.image.tag` | Image tag of Runtime.  | `latest` |
| `runtime.inferenceApi.modelFilename` | Model filename of Runtime. Not changable. | Populated by CDK |
| `runtime.inferenceApi.extraEnv` | Extra environment variable for Runtime. Should be in [Kubernetes format](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#define-an-environment-variable-for-a-container). | `{}` |
| `runtime.inferenceApi.resources` | Resource request and limit for Runtime. |  |
| **Queue Agent** | | |
| `runtime.queueAgent.image.repository` | Image Repository of queue agent.  | `sdoneks/queue-agent` |
| `runtime.queueAgent.image.tag` | Image tag of queue agent.  | `latest` |
| `runtime.queueAgent.extraEnv` | Extra environment variable for queue agent. Should be in [Kubernetes format](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#define-an-environment-variable-for-a-container). | `{}` |
| `runtime.queueAgent.dynamicModel` | Enable model switch by request. Not changable. | Populated by CDK |
| `runtime.queueAgent.s3Bucket` | S3 bucket for generated image. Not changable. | Populated by CDK |
| `runtime.queueAgent.snsTopicArn` | SNS topic for image generate complete notification. Not changable. | Populated by CDK |
| `runtime.queueAgent.sqsQueueUrl` | SQS queue URL of job queue. Not changable. | Populated by CDK |
| `runtime.queueAgent.resources` | Resource request and limit for queue agent. | |
| `runtime.queueAgent.XRay.enabled` | Enable X-ray tracing agent for queue agent. | `true` |
| **Persistence** | | |
| `runtime.persistence.enabled` | Enable presistence of model stroage. | `true` |
| `runtime.persistence.labels` | Labels applied to presistence volume. Should be in key-values format. | `{}` |
| `runtime.persistence.annotations` | Annotations applied to presistence volume. Should be in key-values format. | `{}` |
| `runtime.persistence.storageClass` | Storage class for model storage | `efs-model-storage-sc` |
| `runtime.persistence.size` | Size of persistence volume. | `2Ti` |
| `runtime.persistence.accessModes` | Access mode of persistence volume. | `ReadWriteMany` |

## Deployment Examples

We provided example config file for your reference. These config files are located in `/examples`.

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