# 概览

在部署解决方案之前，建议您先查看本指南中有关架构图和区域支持等信息，然后按照下面的说明配置解决方案并将其部署到您的账户中。

## 前提条件
根据[计划部署](./considerations.md)文档检查所有的考虑因素是否满足。

## 部署步骤

使用以下步骤在 AWS 上部署此解决方案。

1. [创建 Amazon S3 模型存储桶](./models.md)，并将所需要的模型存储到桶中
2. *（可选）* [构建容器镜像](./image-building.md)
3. *（可选）* [将容器镜像存储到EBS缓存中以加速启动](./ebs-snapshot.md)
4. [部署并启动解决方案堆栈](./deploy.md)

总部署时间约为 30 分钟。

## 获取源代码

运行以下命令以获取源代码和部署脚本：

```bash
git clone --recursive https://github.com/aws-samples/stable-diffusion-on-eks
cd stable-diffusion-on-eks
```