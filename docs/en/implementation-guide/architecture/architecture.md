# Architecture Overview

## Architecture Diagram

![Architecture Diagram](../../images/architecture-diagram.png)

## Components

This solution has 3 main components:

- Serverless task scheduling and dispatching
- Stable Diffusion runtime based on Amazon EKS and Amazon EC2
- Management and maintenance components

### Task Scheduling and Dispatching

This component has an API endpoint based on Amazon API Gateway. It also has a task dispatching part based on Amazon SNS and Amazon SQS.

- The user sends requests (model, prompt, etc.) to the API endpoint provided by Amazon API Gateway.
- Requests are validated by Amazon Lambda and sent to an Amazon SNS topic.
- Amazon SNS sends the requests to the corresponding runtime's SQS queue based on the runtime name in the request.

### Stable Diffusion Runtime

This component is a Stable Diffusion runtime based on Amazon EKS. It can scale elastically based on requests.

For each runtime:

- During deployment, each runtime has its own Amazon SQS queue to receive requests.
- The Queue Agent receives tasks from the SQS queue and sends them to the Stable Diffusion runtime to generate images.
- The generated images are stored in an Amazon S3 bucket by the Queue Agent. A completion notification is sent to an Amazon SNS topic.
- When there are too many messages in the SQS queue, KEDA increases the number of runtime replicas based on the queue length. Karpenter starts new GPU instances to host the new replicas.
- When there are no more messages queued, KEDA reduces the number of replicas. Karpenter shuts down unnecessary GPU instances to save costs.

### Management and Maintenance

This solution provides complete observability and management components:

- Metrics monitoring and logging based on CloudWatch
- End-to-end tracing based on AWS X-Ray
- Infrastructure as code deployment using AWS CDK