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
* 在部分区域部署时， EFS 的性能可能会受到影响，请参见 [Amazon EFS文档](https://docs.aws.amazon.com/efs/latest/ug/limits.html#:~:text=Total%20default%20Elastic%20Throughput) 以了解在不同区域的EFS读取性能。

**在亚马逊云科技中国区域部署**

!!! danger "中国区域网络限制"

    近期，我们发现在中国区部署该解决方案时，出现EBS和EFS无法部署，报错信息显示 `Waiter has timed out` 或 `Unexpected EOF`. 详情请参考对应[Issue](https://github.com/aws-samples/stable-diffusion-on-eks/issues/53).

    该问题的根因是部分组件的Helm Chart位于Github上，在中国区部署时，负责部署自定义资源的Lambda无法获取Helm Chart，导致报错。目前我们正在积极处理该问题，后续会将需要的Helm Chart和容器镜像复制到中国区域。该过程预计在2024年Q1完成。

    如您在部署过程中遇到该问题，请暂时切换到海外区域进行测试，或自行搭建Helm Repo以临时解决此问题。


该解决方案可以在亚马逊云科技中国区域部署。

| 区域名称           | 验证通过 |
|----------------|---------------------------------------|
| 中国 (宁夏)  | :material-check-bold:{ .icon_check }  |

在中国区域部署时，由于环境限制，需要进行以下处理，或可能面临以下问题：

* 中国区域不支持默认的`g5`实例类型。您需要手工指定 Karpenter 使用的实例类型为 `g4dn` 或其他 GPU 实例类型。
* 中国区域不支持EventBridge Scheduler，故在首次运行或模型有更新时，您需要**手工触发**DataSync将模型从S3同步至EFS上，或直接将模型存储在EFS中。

## IAM 权限

部署该解决方案需要管理员或与之相当的权限。

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
| InvokeAI     | [GitHub](https://github.com/invoke-ai/InvokeAI) |   |
| ComfyUI     | [GitHub](https://github.com/comfyanonymous/ComfyUI) |   |

您也可以选择其他运行时，或构建自己的运行时。您需要将运行时打包为容器镜像，以便在 EKS 上运行。

您需要充分了解并遵守您所使用的 Stable Diffusion 运行时的许可证条款。

## 其他重要提示和限制

- 一个区域中只能有一个活动的Stable Diffusion on Amazon EKS解决方案堆栈。如果您的部署失败，请确保在重试部署之前已删除失败的堆栈。
- 在当前版本，该解决方案部署时会自动创建一个新的VPC。该VPC包含：
    - CIDR为`10.0.0.0/16`
    - 分布在不同可用区的3个公有子网，子网大小为`/19`
    - 分布在不同可用区的3个私有子网，子网大小为`/19`
    - 3个NAT网关（放置在公有子网）
    - 1个Internet网关
    - 对应的路由表和安全组

    目前该VPC的参数无法自定义。后续版本会允许您在现有VPC内部署。

- 在当前版本，该解决方案只能在新建的EKS集群上部署，且版本固定为`1.27`。我们会随着Amazon EKS版本发布更新集群版本。解决方案的后续版本会允许您在现有EKS集群内部署。