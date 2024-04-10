# 计划部署

请在部署前检查以下所有的考虑因素：

## 可部署区域
此解决方案使用的服务，或 Amazon EC2 实例类型目前可能并非在所有 AWS 区域都可用。请在提供所需服务的 AWS 区域中启动此解决方案。

**已验证可部署的区域**

| 区域名称           | 验证通过 |
|----------------|---------------------------------------|
| 美国东部 (弗吉尼亚北部)  | :material-check-bold:{ .icon_check }  |
| 美国西部 (俄勒冈)     | :material-check-bold:{ .icon_check }  |

如您在未经验证的区域进行部署，可能需要进行以下处理，或面临以下问题：

* 在不支持`g5`实例类型的区域部署时，您需要手工指定 Karpenter 使用的实例类型为 `g4dn` 或其他 GPU 实例类型。

**在亚马逊云科技中国区域部署**

请参见[在亚马逊云科技中国区域部署](./aws-cn.md)

## IAM 权限

部署该解决方案需要管理员或与之相当的权限。由于组件较多，我们暂不提供最小权限列表。

## 服务配额

每个AWS区域的每个AWS账户都有关于可以创建的资源数量的配额，您可以在AWS控制台中使用 [Service Quota](https://console.aws.amazon.com/servicequotas/home/) 工具了解服务配额。如该服务配额可提升，您可以通过该工具并自助式开立工单提升服务配额。

与该解决方案相关的主要服务配额为：

| AWS 服务 | 配额条目 | 预估使用量 | 是否可调整 |
|---------|---------|-----------|-----------|
| Amazon EC2  | [Running On-Demand G and VT instances](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-DB2E81BA) | 按最大并发GPU实例数量 | :material-check-bold:{ .icon_check }  |
| Amazon EC2  | [All G and VT Spot Instance Requests](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-3819A6DF) | 按最大并发GPU实例数量 | :material-check-bold:{ .icon_check }  |
| Amazon SNS  | [Messages Published per Second](https://console.aws.amazon.com/servicequotas/home/services/sns/quotas/L-F8E2BA85) | 按最大并发请求数 | :material-check-bold:{ .icon_check }  |

除此之外，部署时需要考虑以下服务配额：

| AWS 服务 | 配额条目 | 预估使用量 | 是否可调整 |
|---------|---------|-----------|-----------|
| Amazon VPC  | [VPCs per Region](https://console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-F678F1CE) | 1 | :material-check-bold:{ .icon_check }  |
| Amazon VPC  | [NAT gateways per Availability Zone](https://console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-FE5A380F) | 1 | :material-check-bold:{ .icon_check }  |
| Amazon EC2  | [EC2-VPC Elastic IPs](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-0263D0A3) | 1 | :material-check-bold:{ .icon_check }  |
| Amazon S3  | [General purpose buckets](https://console.aws.amazon.com/servicequotas/home/services/s3/quotas/L-DC2B2D3D) | 每个队列1个 | :material-check-bold:{ .icon_check }  |

## 选择 Stable Diffusion 运行时

您需要运行时来部署Stable Diffusion模型并提供API访问。

目前有多个社区Stable Diffusion运行时可用:

| 运行时名称           | 链接 |  验证  |
|----------------|-----------------|----------------------|
| Stable Diffusion Web UI  | [GitHub](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | :material-check-bold:{ .icon_check }  |
| ComfyUI     | [GitHub](https://github.com/comfyanonymous/ComfyUI) | :material-check-bold:{ .icon_check }  |
| InvokeAI     | [GitHub](https://github.com/invoke-ai/InvokeAI) |   |

您也可以选择其他运行时，或构建自己的运行时。您需要将运行时打包为容器镜像，以便在 EKS 上运行。

您需要充分了解并遵守您所使用的 Stable Diffusion 运行时的许可证条款。

!!! example "示例运行时"

    您可以使用社区提供的[示例 Dockerfile](https://github.com/yubingjiaocn/stable-diffusion-webui-docker) 构建 *Stable Diffusion Web UI* 和 *ComfyUI* 的运行时容器镜像。请注意，该镜像仅用于技术评估和测试用途，请勿将该镜像部署至生产环境。

!!! info "模型存储"

    默认情况下，该解决方案会将模型加载至`/opt/ml/code/models`目录，请确保您的运行时被配置成从该目录读取模型。

    您需要将运行时的mmap关闭以获得最高性能。

    * 对于SD Web UI，您需要在`config.json`中设置`disable_mmap_load_safetensors: true`
    * 对于ComfyUI，您需要依照[社区Issue](https://github.com/comfyanonymous/ComfyUI/issues/2288)中的指导，手工修改源代码。

!!! info "SD Web UI运行时注意事项"

    对于SD Web UI运行时，根据运行模型的不同，运行时分为静态运行时（预加载模型）和动态运行时（按需加载模型）。

    * 静态运行时使用的模型需要在`modelFilename`中预先指定。该模型会在启动时加载到显存中。
    * 动态运行时需要指定`dynamicModel: true`。此时无需预先指定模型，运行时会根据请求中使用的模型，从Amazon S3中加载模型并进行模型推理。

## 其他重要提示和限制

- 在当前版本，该解决方案部署时会自动创建一个新的VPC。该VPC包含：
    - CIDR为`10.0.0.0/16`
    - 分布在不同可用区的3个公有子网，子网大小为`/19`
    - 分布在不同可用区的3个私有子网，子网大小为`/19`
    - 3个NAT网关（放置在公有子网）
    - 1个Internet网关
    - 对应的路由表和安全组

    目前该VPC的参数无法自定义。

- 在当前版本，该解决方案只能在新建的EKS集群上部署，且版本固定为`1.28`。我们会随着Amazon EKS版本发布更新集群版本。