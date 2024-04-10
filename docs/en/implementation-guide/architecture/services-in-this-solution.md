The following AWS services are included in this solution:

| AWS Service | Description |
| ---- | ----|
| [Amazon S3](http://aws.amazon.com/s3/)         | Used for storing models and generated images. |
| [Amazon ECR](http://aws.amazon.com/ecr/)         | Used for storing container images required for runtime. |
| [Amazon API Gateway](http://aws.amazon.com/api-gateway/)         | Used for providing API interface for external access. |
| [AWS Lambda](https://aws.amazon.com/lambda)    | Used for request validation and routing. |
| [Amazon SQS](https://aws.amazon.com/sqs)       | Used for storing pending tasks. |
| [Amazon SNS](https://aws.amazon.com/sns)       | Used for routing tasks to different SQS queues, and providing notification and callback upon completion. |
| [Amazon EKS](https://aws.amazon.com/eks)       | Used for managing and running Stable Diffusion runtime. |
| [Amazon EC2](https://aws.amazon.com/ec2)       | Used for running Stable Diffusion runtime. |
| [Amazon CloudWatch](https://aws.amazon.com/cloudwatch)       | Used for monitoring system health, providing metrics monitoring, logging and tracing. |
| [AWS CDK](https://aws.amazon.com/cdk)       | Used for deploying and updating this solution. |