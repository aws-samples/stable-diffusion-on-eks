# 架构概览

## 架构图

![Architecture Diagram](../../images/architecture-diagram.png)

## 组件

该解决方案包含3个主要组件：

* 基于无服务器架构的任务调度和分发
* 基于Amazon EKS和Amazon EC2的Stable Diffusion运行时
* 管理和维护组件

### 任务调度和分发

该组件包含基于Amazon API Gateway的API端点，和基于Amazon SNS，Amazon SQS的任务分发部分。

* 用户将请求（模型，Prompt等）发送至 Amazon API Gateway 提供的API端点
* 请求通过Amazon Lambda进行校验，并投送至 Amazon SNS 主题
* Amazon SNS根据请求中的运行时名称，将请求投送至对应运行时的SQS队列

### Stable Diffusion 运行时

该组件包含基于Amazon EKS的Stable Diffusion运行时，支持根据请求进行弹性伸缩。

对于每个运行时：

* 部署时，每个运行时有独立的 Amazon SQS 队列以接收请求
* Queue Agent会从 Amazon SQS 队列里接收任务，并发送给Stable Diffusion运行时生成图像
* 生成的图片由Queue Agent存储至 Amazon S3存储桶中，并将完成通知投送至 Amazon SNS 主题
* 当 Amazon SQS 队列中积压过多消息时，KEDA会根据队列内消息数量扩充运行时的副本数，同时Karpenter会启动新的GPU实例以承载新的副本。
* 当 Amazon SQS 队列中不再积压消息时，KEDA会缩减副本数，且Karpenter会关闭不需要的GPU实例以节省成本。


### 管理和维护

该解决方案提供完整的可观测性和管理组件：

* 基于CloudWatch的数值监控和日志
* 基于AWS X-Ray的全链路跟踪
* 基于AWS CDK的基础设施即代码部署方式