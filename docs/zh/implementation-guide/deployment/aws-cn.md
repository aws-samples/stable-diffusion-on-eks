# 在亚马逊云科技中国区域部署

该解决方案支持在亚马逊云科技中国区域部署。

| 区域名称           | 验证通过 |
|----------------|---------------------------------------|
| 中国 (宁夏)  | :material-check-bold:{ .icon_check }  |

但由于中国的网络环境特殊，会受到如下限制：

* 中国区域不支持默认的`g5`实例类型。您需要手工指定 Karpenter 使用的实例类型为 `g4dn` 或其他 GPU 实例类型。
* 需要自行构建容器镜像，或将标准镜像复制到中国区域的ECR上。不建议使用ECR Public的镜像。
* 部分组件的Helm Chart位于Github上，在中国区部署时，有几率无法获取到Helm Chart，需要重试。
* 无法自动从Hugging Face或Github上下载模型，需要手工下载模型并上传至S3存储桶。

## 在中国区部署的步骤

在亚马逊云科技中国区部署的步骤与正常部署流程不同，应按如下方式进行部署：

1. 构建或转移镜像至ECR
2. 下载模型并存储至S3桶
3. 制作EBS磁盘快照
4. 生成并修改配置文件
5. 进行部署

### 构建或转移镜像至ECR

由于默认使用的容器镜像存储在ECR Public，您在拉取镜像或制作镜像缓存时可能面临速度缓慢，或连接中途断开等现象。我们建议您自行构建镜像，或将现有镜像转移到您的ECR镜像仓库中。

如需自行构建镜像，请参考[镜像构建](./image-building.md)文档。

如需将预构建镜像转移到中国区的ECR，您可以在一台已安装Docker，并有ECR权限的实例上，运行如下命令：

```bash
docker pull public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest
docker pull public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest
docker pull public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest

aws ecr create-repository --repository-name sd-on-eks/sdwebui
aws ecr create-repository --repository-name sd-on-eks/comfyui
aws ecr create-repository --repository-name sd-on-eks/queue-agent

docker tag public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/sdwebui:latest
docker tag public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/comfyui:latest
docker tag public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/queue-agent:latest

aws ecr get-login-password --region cn-northwest-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.cn-northwest-1.amazonaws.com.cn

docker push 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/sdwebui:latest
docker push 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/comfyui:latest
docker push 123456789012.dkr.ecr.cn-northwest.amazonaws.com.cn/sd-on-eks/queue-agent:latest
```

我们建议您按照[镜像构建](./image-building.md#构建并推送helm-chart)文档提供的方式，将Helm Chart放置在ECR或HTTP服务器中。

### 下载模型并存储至S3桶

由于在国内无法顺畅访问Hugging Face，请在其他镜像网站下载模型后，按照[模型存储](./models.md)文档提供的方式，上传至S3存储桶中。

### 制作EBS磁盘快照

请按照[镜像缓存构建](./ebs-snapshot.md)文档提供的方式，创建EBS磁盘快照以加速镜像加载。

### 生成并修改配置文件

运行以下命令以安装工具并生成初始配置文件。

```bash
cd deploy
./deploy.sh -b <bucket name> -s <snapshot ID> -d
```

该命令会在上级目录下生成一个 `config.yaml` 的模板，但该模板需要进行编辑以在中国区进行部署，编辑该文件，添加以下内容：

```yaml
stackName: sdoneks
modelBucketArn: arn:aws-cn:s3:::${MODEL_BUCKET}  # 此处ARN中aws改为aws-cn
APIGW:
  stageName: dev
  throttle:
    rateLimit: 30
    burstLimit: 50
modelsRuntime:
- name: sdruntime
  namespace: "default"
  modelFilename: "v1-5-pruned-emaonly.safetensors"
  dynamicModel: false
  # chartRepository: "http://example.com/" # 如您自行托管Helm Chart，请去除此行注释，并将值改为Helm Chart的地址（oci://或http://），否则删除此行。
  type: sdwebui
  extraValues:
    runtime:
      inferenceApi:
        image:
          repository: 123456789012.dkr.ecr.cn-northwest-1.amazonaws.com.cn/sd-on-eks/sdwebui # 此处改为ECR镜像仓库的地址
          tag: latest
      queueAgent:
        image:
          repository: 123456789012.dkr.ecr.cn-northwest-1.amazonaws.com.cn/sd-on-eks/queue-agent # 此处改为ECR镜像仓库的地址
          tag: latest
    karpenter:
      nodeTemplate:
        amiFamily: Bottlerocket
        dataVolume:
          volumeSize: 80Gi
          volumeType: gp3
          deleteOnTermination: true
          iops: 4000
          throughput: 1000
          snapshotID: snap-1234567890 # 此处会自动填入EBS快照的ID
      provisioner:
        instanceType:
        - "g5.xlarge"
        - "g4dn.xlarge"
        - "g5.2xlarge"
        - "g4dn.2xlarge"
        capacityType:
          onDemand: true
          spot: true
      scaling:
        queueLength: 10
        minReplicaCount: 0
        maxReplicaCount: 5
        cooldownPeriod: 300
```

完成后，可运行部署命令进行部署：

```bash
cdk deploy --no-rollback --require-approval never
```