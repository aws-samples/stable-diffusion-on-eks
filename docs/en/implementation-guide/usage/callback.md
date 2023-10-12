# 回调和通知

Stable Diffusion on Amazon EKS方案采用异步推理模式，当图片生成或报错后，会通过Amazon SNS通知用户。用户应用可以通过订阅SNS Topic以获取图片生成完成的通知。

请参考SNS文档以了解SNS支持的后端种类。

您可以在CloudFormation的输出中找到生成的SNS Topic
