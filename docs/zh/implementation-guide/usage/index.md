# API 调用规则

在部署解决方案后，您可以通过Amazon API Gateway的API端点，向Stable Diffusion运行时发送请求。

发送请求时，请遵循以下规则：

## API 请求示例

您可以使用测试脚本验证解决方案是否部署成功。运行以下命令以进行测试：

```bash
cd test
STACK_NAME=sdoneksStack RUNTIME_TYPE=sdwebui ./run.sh
```

如您修改了解决方案堆栈名称，或运行时类型，请将`sdoneksStack`和`sdwebui`替换成对应内容。

该脚本会自动查找API Gateway端点，获取API Key，并发送测试请求。

* 对SD Web UI运行时，会发送一个文生图和图生图请求。
* 对ComfyUI运行时，会发送一个Pipeline请求。

在数秒至数分钟（取决于是否启用了镜像缓存，和最小实例副本数量）后，您可以在`output_location`的位置找到生成的图像。

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
    aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`FrontApiEndpoint`].OutputValue'
    ```

您需要在端点后附加API版本。目前我们支持`v1alpha1`和`v1alpha2`版本。当您使用`v1alpha2`版本API时，请求应发送至：

```
https://abcdefghij.execute-api.ap-southeast-1.amazonaws.com/prod/v1alpha2
```

该端点仅接收JSON格式的POST请求，需要包含`Content-Type: application/json`请求头。


## 请求类型

根据运行时类型不同，每种运行时只接受特定类型的请求：

* 对于SD Web UI运行时，只接受[文生图](./text-to-image.md)和[图生图](./image-to-image.md)请求。
* 对于ComfyUI运行时，只接受[Pipeline](./pipeline.md)请求。

具体请求格式请参见各类型请求的详细文档。

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
    echo $(aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`GetAPIKeyCommand`].OutputValue')
    ```

在发送请求时，需包含`x-api-key`请求头，其值为上方获取的API Key。

!!! danger "未验证的请求"
    未包含API Key的请求将会直接返回`401`错误。

## 限流规则

为保护后端API，对使用同一个API Key发送的过多请求，API Gateway会进行限流。

默认设置为:

* 每秒30个请求
* 可突增50个请求

关于限流的原理详细信息，请参考[Throttle API requests for better throughput](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html)

如您需要修改该设置，请在`config.yaml`中修改`APIGW`段的相关内容。您也可以在API Gateway中修改对应Usage Plan。

## 下一步

根据右方目录的不同使用方式，向Stable Diffusion发送请求。