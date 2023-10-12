# 架构概览

[![arch]][arch]

* Users send prompts to the application running on Amazon Fargate via Amazon CloudFront
* Application backend sends the prompt to Amazon API Gateway, Amazon Lambda validates the requests, and publishes to an Amazon SNS topic
* SNS publishes the message to Amazon SQS queues via matching subscription filters
* In Amazon EKS cluster, open source Kubernetes Event Driven Auto-Scaler (KEDA) scales up new pods based on the queue length
* Karpenter (an open source Kubernetes compute auto-scaler) launches new GPU spot instances to place pending pods. The nodes run Bottlerocket OS with pre-cached Stable Diffusion Runtime images
* SD Runtime loads model files from Amazon EFS file system
* Queue Agent calls SD Runtime to generate images and save them to Amazon S3
* Queue Agent sends output to a SNS topic and the application backend receives notification from SQS queue
* Amazon CloudWatch, Amazon Distro for OpenTelemetry, and Amazon X-Ray collect metrics, logs, and traces to monitor guidance components
* Amazon IAM for security and resource access control, Amazon CDK for automated deployment of guidance components into AWS*