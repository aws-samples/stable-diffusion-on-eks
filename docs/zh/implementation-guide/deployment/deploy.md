# 手动部署

根据以下步骤部署本解决方案：

## 安装必要组件

请在部署前安装以下运行时：

* [Node.js](https://nodejs.org/en) 18及以上版本
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [AWS CDK 工具包](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
* [git](https://git-scm.com/downloads)

## 编辑配置文件

本解决方案的配置存储在`config.yaml`文件中，我们提供了配置文件模板，您可以根据您的实际需求对解决方案进行自定义。

### 设置模型存储桶（必需）

将 `modelBucketArn` 中的 `<bucket name>` 修改为放置模型的S3存储桶名称。

```yaml
modelBucketArn: arn:aws:s3:::<bucket name>
```

!!! warning "中国区域"

    如您使用亚马逊云科技中国区域, 请确保ARN中的partition为`aws-cn`.

    ```yaml
    modelBucketArn: arn:aws-cn:s3:::<bucket name>
    ```

### 设置Stable Diffusion运行时（必需）

您需要指定运行时的参数。运行时定义在 `modelsRuntime` 中，配置如下：

```yaml
modelsRuntime:
- name: "sdruntime" # 必要参数，运行时的名称，不能和其他运行时重名
  namespace: "default" # 必要参数，运行时所在的Kubernetes命名空间，不建议和其他运行时放置在相同的命名空间。
  type: "sdwebui" # 必要参数，该运行时的类型，目前仅支持"sdwebui"和"comfyui"
  modelFilename: "v1-5-pruned-emaonly.safetensors" # （SD Web UI）该运行时使用的模型名称，不能和其他运行时重复。
  dynamicModel: false # （SD Web UI）该运行时是否允许动态加载模型。
```

您可以在 `modelsRuntime` 段配置多个运行时。

### 设置自定义镜像（可选）

如您[自行构建了镜像和/或Helm Chart](./image-building.md)，则需要在对应的运行时中指定镜像，配置如下：

```yaml
modelsRuntime:
- name: "sdruntime"
  namespace: "default"
  type: "sdwebui"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  dynamicModel: false
  chartRepository: "" # 可选参数，如您构建了Helm Chart，则需要填入Chart所在的地址。需要包含协议前缀 (oci:// 或 https:// )
  chartVersion: "" # 可选参数，如您构建了Helm Chart，则需要填入Chart的版本
  extraValues: # 添加以下内容
    runtime:
      inferenceApi:
        image:
          repository: <account_id>.dkr.ecr.<region>.amazonaws.com/sd-on-eks/sdwebui # Stable Diffusion 运行时镜像的地址.
          tag: latest # 镜像的Tag
      queueAgent:
        image:
          repository: <account_id>.dkr.ecr.<region>.amazonaws.com/sd-on-eks/queue-agent # Queue agent镜像的地址.
          tag: latest # 镜像的Tag
```

### 设置基于 EBS 快照的镜像缓存（可选）

如您构建了[基于EBS快照的镜像缓存](./ebs-snapshot.md)，则需要在对应的运行时中指定快照ID，配置如下：

```yaml
modelsRuntime:
- name: "sdruntime"
  namespace: "default"
  type: "sdwebui"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  extraValues:
    karpenter: # 添加以下内容
      nodeTemplate:
        amiFamily: Bottlerocket
        dataVolume:
          volumeSize: 80Gi # 请勿修改至小于80Gi的值
          volumeType: gp3 # 请勿修改
          deleteOnTermination: true # 请勿修改
          iops: 4000 # 请勿修改
          throughput: 1000 # 请勿修改
          snapshotID: snap-0123456789 # 修改为EBS快照ID
```

### 其他详细设置（可选）

如您需要对运行时进行详细配置，请参考[配置项](./configuration.md)。


## 开始部署

完成配置后，运行以下命令进行部署：

```bash
npm install
cdk deploy  --no-rollback --require-approval never
```

部署一般需要 15-20 分钟。由于部署通过CloudFormation在AWS侧进行，当CDK CLI被意外关闭时，您无需重新进行部署。

## 下一步

在部署完成后，您会看到如下输出：

```bash
Outputs:
sdoneksStack.GetAPIKeyCommand = aws apigateway get-api-keys --query 'items[?id==`abcdefghij`].value' --include-values --output text
sdoneksStack.FrontApiEndpoint = https://abcdefghij.execute-api.us-east-1.amazonaws.com/prod/
sdoneksStack.ConfigCommand = aws eks update-kubeconfig --name sdoneksStack --region us-east-1 --role-arn arn:aws:iam::123456789012:role/sdoneksStack-sdoneksStackAccessRole
...
```

现在, 您可以：

* [发送API请求](../usage/index.md)以使用Stable Diffusion生成图像
* [登录到Kubernetes集群](../operation/kubernetes-cluster.md)中以进行运维操作
