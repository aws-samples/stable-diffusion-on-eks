# Quick start

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

If you are deploying in AWS China region:
```yaml
modelBucketArn: arn:aws-cn:s3:::<bucket name>
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
    runtime:
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
SdOnEksDataPlaneStack.FrontApiEndpoint = https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/
...
```

Because of the service differences between AWS China regions, additional operations are required. If you use non-AWS Beijing region and Ningxia region, skip this step:
Open the AWS Console, find the service **Datasync**, select Tasks in the left navigation bar, and select the task you just created, such as "task-092354086086f941c".
Then click Actions - Start in the upper right corner

You can also perform the above steps via the command line:
```
aws datasync start-task-execution --task-arn=$(for taskid in $(aws datasync list-tasks --output yaml | grep TaskArn | awk '{print $2}'); do if [ "$(aws datasync list-tags-for-resource --resource-arn $taskid --output yaml | grep -A1 stack-name | grep Value | awk '{print $2}')" = $(cat config.yaml|grep stackName|awk '{print $2}'|sed 's/\"//g')"Stack" ]; then echo $taskid; fi; done)
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
