# Stable Diffusion on EKS

在 AWS 上使用无服务器和容器解决方案，实施快速扩展和低成本的Stable Diffusion图像生成解决方案

Stable Diffusion 是一个使用生成式AI技术生成图像的流行开源项目。构建可扩展、低成本的推理解决方案是 AWS 客户面临的共同挑战。本项目展示了如何使用无服务器和容器服务构建端到端低成本、快速扩展的异步图像生成架构。

## 功能特性

- 基于事件驱动架构
- 利用 KEDA 实现基于队列长度的自动扩展
- 利用 Karpenter 自动配置 EC2 实例
- 在 2 分钟内扩展新的推理节点
- 使用 GPU Spot 实例可节省高达 70% 的成本
- 支持多种社区Stable Diffusion运行时

!!! warning "迁移公告"
    该项目已迁移至 [aws-solutions-library-samples/guidance-for-asynchronous-inference-with-stable-diffusion-webui-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-asynchronous-inference-with-stable-diffusion-webui-on-aws) 存储库。原存储库和本文档已不再更新。

    在您拉取新的存储库后，您可以将 `config.yaml` 迁移到新的存储库以实现配置迁移。

!!! abstract "免责声明"
    该解决方案仅为参考架构和示例代码，按照[MIT-0协议](https://github.com/aws-samples/stable-diffusion-on-eks/blob/main/LICENSE)向您提供。

    该解决方案仅作为演示，概念验证（Proof of Concept）或学习用途，您不应将该解决方案直接用在您的生产账户中，或用于生产或其他关键数据。

    部署该解决方案会因创建或使用 AWS 可收费资源（例如，运行 Amazon EC2 实例或使用 Amazon S3 存储）而产生 AWS 费用。