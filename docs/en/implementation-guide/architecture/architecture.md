# Architecture Overview

## Architecture Diagram

![Architecture Diagram](../../images/architecture-diagram.png)

## Components

This solution consists of three main components:

* Serverless architecture-based task scheduling and distribution
* Stable Diffusion runtime based on Amazon EKS and Amazon EC2
* Management and maintenance components

### Task Scheduling and Distribution

This component includes an API endpoint based on Amazon API Gateway and a task distribution portion based on Amazon SNS and Amazon SQS.

* Users send requests (models, prompts, etc.) to the API endpoint provided by Amazon API Gateway.
* The request is validated by Amazon Lambda and delivered to the Amazon SNS topic.
* Amazon SNS delivers the request to the corresponding runtime's SQS queue based on the model used in the request.

### Stable Diffusion Runtime

This component includes the Stable Diffusion runtime based on Amazon EKS, supporting elastic scaling based on requests.

For each runtime:

* Application backend sends the prompt to Amazon API Gateway, Amazon Lambda validates the requests, and publishes to an Amazon SNS topic
* SNS publishes the message to Amazon SQS queues via matching subscription filters
* In Amazon EKS cluster, open source Kubernetes Event Driven Auto-Scaler (KEDA) scales up new pods based on the queue length
* Karpenter (an open source Kubernetes compute auto-scaler) launches new GPU spot instances to place pending pods. The nodes run Bottlerocket OS with pre-cached Stable Diffusion Runtime images
* SD Runtime loads model files from Amazon S3 bucket
* Queue Agent calls SD Runtime to generate images and save them to Amazon S3
* Queue Agent sends output to a SNS topic and the application backend receives notification from SQS queue
* Amazon CloudWatch, Amazon Distro for OpenTelemetry, and Amazon X-Ray collect metrics, logs, and traces to monitor guidance components
* Amazon IAM for security and resource access control, Amazon CDK for automated deployment of guidance components into AWS

Depending on the model's nature, runtimes are categorized into static runtimes (pre-loaded models) and dynamic runtimes (on-demand loaded models).

#### Static Runtimes

Static runtimes use models that need to be specified in advance and loaded into memory at startup. SNS only delivers requests using the specified model to the corresponding runtime.

#### Dynamic Runtimes

Dynamic runtimes do not require specifying models in advance. SNS delivers all requests without static runtimes to this runtime. The runtime loads the model from Amazon S3 and performs model inference based on the model used in the request.

!!! bug "Note"
    In the current implementation, requests are randomly distributed to one of the replicas of dynamic runtimes. This routing strategy may lead to unnecessary model loading, resulting in longer image generation times.

### Management and Maintenance

This solution provides comprehensive observability and management components:

* Numeric monitoring and logs based on CloudWatch
* End-to-end tracing based on AWS X-Ray
* Infrastructure as code deployment using AWS CDK