The following AWS services are included in this solution:

| AWS Service | Description |
| ---- | ----|
| [Amazon S3](http://aws.amazon.com/s3/)         | Used for storing models and generated images.|
| [Amazon ECR](http://aws.amazon.com/ecr/)         | Used for storing container images required by the runtime.|
| [Amazon API Gateway](http://aws.amazon.com/api-gateway/)         | Used to provide an API interface for external access.|
| [AWS Lambda](https://aws.amazon.com/lambda)    | Used for request validation and routing.|
| [Amazon SQS](https://aws.amazon.com/sqs)       | Used to store pending tasks for processing.|
| [Amazon SNS](https://aws.amazon.com/sns)       | Used to route tasks to different SQS queues and provide notifications and callbacks after processing is complete.|
| [Amazon EKS](https://aws.amazon.com/eks)       | Used for managing and running the Stable Diffusion runtime.|
| [Amazon EC2](https://aws.amazon.com/ec2)       | Used for running the Stable Diffusion runtime.|
| [Amazon CloudWatch](https://aws.amazon.com/cloudwatch)       | Used for monitoring the system's operation, providing numerical monitoring, logs, and tracing.|
| [AWS CDK](https://aws.amazon.com/cdk)       | Used for deploying and updating this solution.|