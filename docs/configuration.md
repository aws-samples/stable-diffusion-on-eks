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
| `sdWebuiInferenceApi.scaling.cooldownPeriod` | The period (in seconds) to wait after the last trigger reported active before scaling the resource back to `minReplicaCount`.  | `60` |
| `sdWebuiInferenceApi.scaling.maxReplicaCount` | This setting is passed to the HPA definition that KEDA will create for a given resource and holds the maximum number of replicas of the target resource. | `20` |
| `sdWebuiInferenceApi.scaling.minReplicaCount` | Minimum number of replicas KEDA will scale the resource down to.  | `0` |
| `sdWebuiInferenceApi.scaling.pollingInterval` | Interval (in seconds) to check each trigger on.  | `1` |
| `sdWebuiInferenceApi.scaling.scaleOnInFlight` | When set to `true`, not visible (in-flight) messages will be counted in `ApproximateNumberOfMessage` | `false` |
| `sdWebuiInferenceApi.scaling.extraHPAConfig` | KEDA would feed values from this section directly to the HPA’s `behavior` field. Follow [Kubernetes documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#configurable-scaling-behavior) for details. | `{}` |
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