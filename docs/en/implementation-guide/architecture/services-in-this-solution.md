以下 AWS 服务包括在此解决方案中：

| AWS 服务 | 描述                                                                                                                                               |
| ---- | ----|
| [Amazon S3](http://aws.amazon.com/s3/)         | 用于存储模型和生成的图像。|
| [Amazon EFS](http://aws.amazon.com/efs/)         | 用于存储模型。|
| [Amazon ECR](http://aws.amazon.com/ecr/)         | 用于存储运行时所需的容器镜像。|
| [Amazon API Gateway](http://aws.amazon.com/api-gateway/)         | 用于提供对外访问的API接口。|
| [AWS Lambda](https://aws.amazon.com/lambda)    | 用于进行请求验证和路由。|
| [Amazon SQS](https://aws.amazon.com/sqs)       | 用于存放待处理的任务。|
| [Amazon SNS](https://aws.amazon.com/sns)       | 用于将任务路由到不同的SQS队列，以及提供处理完成后通知和回调。|
| [Amazon EKS](https://aws.amazon.com/eks)       | 用于管理和运行 Stable Diffusion 运行时。|
| [Amazon EC2](https://aws.amazon.com/ec2)       | 用于运行 Stable Diffusion 运行时。|
| [Amazon CloudWatch](https://aws.amazon.com/cloudwatch)       | 用于监控系统的运行状况，提供数值监控，日志和跟踪。|
| [AWS CDK](https://aws.amazon.com/cdk)       | 用于部署和更新该解决方案。|