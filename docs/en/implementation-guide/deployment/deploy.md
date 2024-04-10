# Manual Deployment

Follow these steps to deploy this solution:

## Install Prerequisites

Please install the following runtimes before deployment:

* [Node.js](https://nodejs.org/en) version 18 or later
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [AWS CDK Toolkit](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
* [git](https://git-scm.com/downloads)

## Edit Configuration File

The configuration for this solution is stored in the `config.yaml` file. We provide a configuration file template that you can customize according to your actual needs.

### Set Model Bucket (Required)

Replace `<bucket name>` in `modelBucketArn` with the name of the S3 bucket where you store the models.

```yaml
modelBucketArn: arn:aws:s3:::<bucket name>
```

!!! warning "China Regions"

    If you are using an AWS China Region, ensure that the partition in the ARN is `aws-cn`.

    ```yaml
    modelBucketArn: arn:aws-cn:s3:::<bucket name>
    ```

### Set Stable Diffusion Runtime (Required)

You need to specify the parameters for the runtime. The runtime is defined in `modelsRuntime` as follows:

```yaml
modelsRuntime:
- name: "sdruntime" # Required parameter, the name of the runtime, cannot be the same as other runtimes
  namespace: "default" # Required parameter, the Kubernetes namespace where the runtime is located, it is not recommended to place it in the same namespace as other runtimes.
  type: "sdwebui" # Required parameter, the type of this runtime, currently only "sdwebui" and "comfyui" are supported
  modelFilename: "v1-5-pruned-emaonly.safetensors" # (SD Web UI) The name of the model used by this runtime, cannot be the same as other runtimes.
  dynamicModel: false # (SD Web UI) Whether this runtime allows dynamic model loading.
```

You can configure multiple runtimes in the `modelsRuntime` section.

### Set Custom Image (Optional)

If you have [built your own image and/or Helm Chart](./image-building.md), you need to specify the image in the corresponding runtime as follows:

```yaml
modelsRuntime:
- name: "sdruntime"
  namespace: "default"
  type: "sdwebui"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  dynamicModel: false
  chartRepository: "" # Optional parameter, if you have built a Helm Chart, you need to fill in the address where the Chart is located. It should include the protocol prefix (oci:// or https://)
  chartVersion: "" # Optional parameter, if you have built a Helm Chart, you need to fill in the version of the Chart
  extraValues: # Add the following
    runtime:
      inferenceApi:
        image:
          repository: <account_id>.dkr.ecr.<region>.amazonaws.com/sd-on-eks/sdwebui # The address of the Stable Diffusion runtime image.
          tag: latest # The tag of the image
      queueAgent:
        image:
          repository: <account_id>.dkr.ecr.<region>.amazonaws.com/sd-on-eks/queue-agent # The address of the Queue agent image.
          tag: latest # The tag of the image
```

### Set EBS Snapshot-based Image Cache (Optional)

If you have built an [EBS snapshot-based image cache](./ebs-snapshot.md), you need to specify the snapshot ID in the corresponding runtime as follows:

```yaml
modelsRuntime:
- name: "sdruntime"
  namespace: "default"
  type: "sdwebui"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  extraValues:
    karpenter: # Add the following
      nodeTemplate:
        amiFamily: Bottlerocket
        dataVolume:
          volumeSize: 80Gi # Do not modify to a value less than 80Gi
          volumeType: gp3 # Do not modify
          deleteOnTermination: true # Do not modify
          iops: 4000 # Do not modify
          throughput: 1000 # Do not modify
          snapshotID: snap-0123456789 # Replace with the EBS snapshot ID
```

### Other Detailed Settings (Optional)

If you need to configure the runtime in detail, please refer to the [configuration options](./configuration.md).

## Start Deployment

After completing the configuration, run the following commands to deploy:

```bash
npm install
cdk deploy  --no-rollback --require-approval never
```

The deployment generally takes 15-20 minutes. Since the deployment is performed on the AWS side through CloudFormation, you do not need to redeploy if the CDK CLI is accidentally closed.

## Next Steps

After the deployment is complete, you will see the following output:

```bash
Outputs:
sdoneksStack.GetAPIKeyCommand = aws apigateway get-api-keys --query 'items[?id==`abcdefghij`].value' --include-values --output text
sdoneksStack.FrontApiEndpoint = https://abcdefghij.execute-api.us-east-1.amazonaws.com/prod/
sdoneksStack.ConfigCommand = aws eks update-kubeconfig --name sdoneksStack --region us-east-1 --role-arn arn:aws:iam::123456789012:role/sdoneksStack-sdoneksStackAccessRole
...
```

Now, you can:

* [Send API requests](../usage/index.md) to use Stable Diffusion to generate images
* [Log in to the Kubernetes cluster](../operation/kubernetes-cluster.md) for maintenance operations