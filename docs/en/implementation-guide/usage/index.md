# Rules for API Calls

After deploying the solution, you can send requests to the Stable Diffusion runtime through the API endpoint of Amazon API Gateway.

When sending requests, please follow these rules:

## API Request Example

You can use the test script to verify if the solution is deployed successfully. Run the following command to test:

```bash
cd test
STACK_NAME=sdoneksStack RUNTIME_TYPE=sdwebui ./run.sh
```

If you have modified the solution stack name or runtime type, please replace `sdoneksStack` and `sdwebui` with the corresponding content.

The script will automatically find the API Gateway endpoint, obtain the API Key, and send a test request.

* For the SD Web UI runtime, it will send a text-to-image and an image-to-image request.
* For the ComfyUI runtime, it will send a Pipeline request.

After a few seconds to a few minutes (depending on whether image caching is enabled and the minimum number of instance replicas), you can find the generated images at the `output_location`.

## Request Endpoint and Format

The API endpoint of the solution can be obtained from the CloudFormation outputs:

=== "AWS Management Console"

    * Go to the [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation/home)
    * Select **Stacks**
    * In the list, select **SdOnEKSStack** (or your custom name)
    * Select **Output**
    * Record the value of the **FrontApiEndpoint** item (in the format of `https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/`)

=== "AWS CLI"

    Run the following command to get the API endpoint:

    ```bash
    aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`FrontApiEndpoint`].OutputValue'
    ```

You need to append the API version to the endpoint. Currently, we support `v1alpha1` and `v1alpha2` versions. When using the `v1alpha2` version API, the request should be sent to:

```
https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/v1alpha2
```

This endpoint only accepts JSON-formatted POST requests, and the `Content-Type: application/json` request header is required.

## Request Types

Depending on the runtime type, each runtime only accepts specific types of requests:

* For the SD Web UI runtime, it only accepts [text-to-image](./text-to-image.md) and [image-to-image](./image-to-image.md) requests.
* For the ComfyUI runtime, it only accepts [Pipeline](./pipeline.md) requests.

Please refer to the detailed documentation of each request type for the specific request format.

## API Key

For security reasons, all requests need to include an API Key. Follow these steps to obtain the API Key:

=== "AWS Management Console"

    * Go to the [Amazon API Gateway Console](https://console.aws.amazon.com/apigateway)
    * Select **API Keys**
    * In the list, select the API Key with a name similar to `SdOnEK-defau-abcdefghij` (or your custom name)
    * Record the value of the **API key** item

=== "AWS CLI"

    Run the following command to get the API Key:

    ```bash
    echo $(aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`GetAPIKeyCommand`].OutputValue')
    ```

When sending requests, you need to include the `x-api-key` request header, with its value being the API Key obtained above.

!!! danger "Unauthenticated Requests"
    Requests without an API Key will directly return a `401` error.

## Throttling Rules

To protect the backend API, API Gateway will throttle excessive requests sent using the same API Key.

The default settings are:

* 30 requests per second
* Burst of 50 requests

For detailed information about throttling principles, please refer to [Throttle API requests for better throughput](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html)

If you need to modify these settings, please change the relevant content in the `APIGW` section of the `config.yaml` file. You can also modify the corresponding Usage Plan in API Gateway.

## Next Steps

According to the different usage methods in the right-hand directory, send requests to Stable Diffusion.