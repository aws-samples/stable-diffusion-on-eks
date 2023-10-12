# API 调用规则

在部署解决方案后，您可以通过Amazon API Gateway的API端点，向Stable Diffusion运行时发送请求。发送请求时，请遵循以下规则：

## 请求端点和格式

解决方案的API端点可以从CloudFormation的输出中获取：

=== "AWS 管理控制台"

    * 进入 [AWS CloudFormation 控制台](https://console.aws.amazon.com/cloudformation/home)
    * 选择 **Stacks** （堆栈）
    * 在列表中，选择 **SdOnEKSStack** （或您自定义的名称）
    * 选择 **Output** （输出）
    * 记录 **FrontApiEndpoint** 项的值（格式为  `https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/`）

=== "AWS CLI"

    运行以下命令以获取 API端点：

    ```bash
    getkey="$(aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`FrontApiEndpoint`].OutputValue')"
    ```

该端点仅接收JSON格式的POST请求，需要包含`Content-Type: application/json`请求头。

## API Key

出于安全考虑，所有请求需要附加API Key。通过以下步骤获取API Key：

=== "AWS 管理控制台"

    * 进入 [Amazon API Gateway 控制台](https://console.aws.amazon.com/apigateway)
    * 选择 **API Keys**
    * 在列表中，选择名称类似于 `SdOnEK-defau-abcdefghij`（或您自定义的名称）的API Key
    * 记录 **API key** 项的值

=== "AWS CLI"

    运行以下命令以获取API Key：

    ```bash
    getkey="$(aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`GetAPIKeyCommand`].OutputValue')"
    ```

在发送请求时，需包含`x-api-key`请求头，其值为上方获取的API Key。

!!! failure
    未包含API Key的请求将会直接返回`401`错误。

## 限流规则

为保护后端API，对使用同一个API Key发送的过多请求，API Gateway会进行限流。

默认设置为:

* 每秒10个请求
* 可突增2个请求

关于限流的原理详细信息，请参考[Throttle API requests for better throughput](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html)

如您需要修改该设置，请在API Gateway中修改对应Usage Plan。

## API 请求示例

您可以使用下方的测试请求验证解决方案是否部署成功。将下方内容存储为`test.json`:

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

运行以下命令，将`1234567890abcdefghij` 替换为 API Key，将 `https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/` 替换为API端点。

```bash
curl -X POST https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/ \
    -H 'Content-Type: application/json' \
    -H 'x-api-key: 1234567890abcdefghij' \
    -d @test.json
```

如果部署正确，您会立即获得以下返回:

```json
{"id_task": "123", "task": "text-to-image", "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors", "output_location": "s3://sdoneksdataplanestack-outputs3bucket/123"}
```

在数秒至数分钟（取决于是否启用了镜像缓存，和最小实例副本数量）后，您可以在`output_location`的位置找到生成的图像。

## 下一步

根据右方目录的不同使用方式，向Stable Diffusion发送请求。