# Architecture Overview

## Architecture Diagram

![Architecture Diagram](../../images/architecture-diagram.png)

## Components

The solution consists of 3 main components:

* Serverless task scheduling and dispatching
* Stable Diffusion runtime based on Amazon EKS and Amazon EC2
* Management and maintenance components

### Task Scheduling and Dispatching

This component includes an API endpoint based on Amazon API Gateway, and a task dispatching part based on Amazon SNS and Amazon SQS.

* Users send requests (model, prompt, etc.) to the API endpoint provided by Amazon API Gateway
* Requests are validated by Amazon Lambda and published to an Amazon SNS topic
* Amazon SNS publishes the requests to the corresponding SQS queue based on the runtime name specified in the request

### Stable Diffusion Runtime

This component includes a Stable Diffusion runtime based on Amazon EKS, which supports elastic scaling based on requests.

For each runtime:

* Upon deployment, each runtime has a dedicated Amazon SQS queue to receive requests
* The Queue Agent receives tasks from the Amazon SQS queue and sends them to the Stable Diffusion runtime to generate images
* The generated images are stored by the Queue Agent in an Amazon S3 bucket, and a completion notification is published to an Amazon SNS topic
* When there are too many messages queued in the Amazon SQS queue, KEDA will scale out the runtime replicas based on the number of messages in the queue, and Karpenter will launch new GPU instances to host the new replicas.
* When there are no more messages queued in the Amazon SQS queue, KEDA will scale in the replicas, and Karpenter will terminate unnecessary GPU instances to save costs.

### Management and Maintenance

This solution provides comprehensive observability and management components:

* Metrics monitoring and logging based on CloudWatch
* End-to-end tracing based on AWS X-Ray
* Infrastructure as Code deployment using AWS CDK