# Quick start

## Requirement

* Kubernetes cluster 1.22+
* [Helm](https://helm.sh/docs/intro/install/) CLI
* Node.js 16+
* [AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
* An [AWS](https://aws.amazon.com/) Account
* Administrator or equivalent privilege

## Supported Region

The solution is verified on the following regions:

* US East (N. Virginia) `us-east-1`
* US West (Oregon) `us-west-2`

You can deploy the solutions on any region where `g5` instances are available. If you need to deploy the solutions on a region where doesn't have `g5` instances, you need to specify a different instance type on `karpenter.provisioner.instanceType` of each runtime. (See [Configuration](./configuration.md#configuration) for detail. )


## Choose your Stable Diffusion Runtime

You need runtimes to deploy Stable Diffusion model and provide API access. There are several community Stable Diffusion runtimes available, and you can build your own runtime. You need to package runtime as a container image to run the runtime on EKS.

Here are some examples:

* [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
* [InvokeAI](https://github.com/invoke-ai/InvokeAI)
* [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

For you convenience, you can use this [sample Dockerfile](https://github.com/antman2008/stable-diffusion-webui-dockerfile) to build a container image of *AUTOMATIC1111's Stable Diffusion Web UI*.

## Build image

Please refer to [Development Guide](./development.md) to build image from source.

## Provision infrastructure and runtime

Required infrastructure and application is deployed via AWS CDK. We provide default configuration and image for quick start.

Run the following command to clone the code:

```bash
git clone --recursive <repo path>
cd stable-diffusion-on-eks
```

Before deploy, you need to edit `config.yaml` and set parameters of runtimes.

### Define Model Bucket

Set `modelBucketArn` to the S3 bucket created on previous section.

```yaml
modelBucketArn: arn:aws:s3:::<bucket name>
```

### Define Runtime

You need to specify each runtime in `modelsRuntime` section. For each runtime, specify the following value:

```yaml
modelsRuntime:
- name: "sdruntime" # Name of runtime, should be unique
  namespace: "default" # Namespace of runtime, suggest deploy different runtimes on seperate namespaces
  modelFilename: "v1-5-pruned-emaonly.safetensors" # Model for this runtime, request will be routed by model filename.
  type: "SDWebUI" # Specify type of runtime. Different type of runtime represents different API Spec.
  extraValues:
    sdWebuiInferenceApi:
      inferenceApi:
        image:
          repository: sdoneks/inference-api # Image repository of your runtime
          tag: latest # Image tag of your runtime
    queueAgent:
      image:
        repository: sdoneks/queue-agent # Image repository for queue agent
        tag: latest # Image tag of queue agent

```

### Deploy

Run the following command to deploy the stack:

```bash
npm install
cdk synth
cdk deploy --all
```

Deployment requires 20-30 minutes.

## Usage

After deployment completes, you can get endpoint and key of API on CDK output:

```bash
Outputs:
SdOnEksDataPlaneStack.APIKey = 1234567890abcdefghij
SdOnEksDataPlaneStack.EfsFileSystemId = fs-1234567890abcdefg
SdOnEksDataPlaneStack.FrontApiEndpointD7DCAA3A = https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/
...
```

You can try it out by making API call with prompt. Your request should follow API Spec of corresponding runtime. For Stable Diffusion Web UI, save the following content as a JSON file:

```json
{
    "alwayson_scripts": {
        "task": "text-to-image",
        "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
        "id_task": "123",
        "uid": "123",
        "save_dir": "outputs"
    },
    "prompt": "A dog",
    "steps": 16,
    "width": 512,
    "height": 512
}
```

Now you can use `curl` to test the solutions. Copy the following cURL command and paste it into the terminal window, replacing `1234567890abcdefghij` with content of `SdOnEksDataPlaneStack.APIKey`, `https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/` with the content of `SdOnEksDataPlaneStack.FrontApiEndpoint`, and `test.json` of filename you just created.

```bash
curl -X POST https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/ \
    -H 'Content-Type: application/json' \
    -H 'x-api-key: 1234567890abcdefghij' \
    -d @test.json
```

You should get a successful response with a payload similar to the following:

```json
{"id_task": "123", "task": "text-to-image", "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors", "output_location": "s3://sdoneksdataplanestack-outputs3bucket/123"}
```

You may need to wait for several minutes for instance launching and container starting without EBS snapshot. Once container launched and task is proceed, you can find generated image on `output_location`.
