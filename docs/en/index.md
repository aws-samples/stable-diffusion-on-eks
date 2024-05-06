# Stable Diffusion on EKS

Implement a scalable and cost-effective Stable Diffusion image generation solution using serverless and container solutions on AWS

Stable Diffusion is a popular open-source project that generates images using generative AI technology. Building a scalable and cost-effective inference solution is a common challenge faced by AWS customers. This project demonstrates how to build an end-to-end, cost-effective, and rapidly scalable asynchronous image generation architecture using serverless and container services.

## Key Features

- Event-driven architecture
- Autoscaling based on queue length using KEDA
- Automatic EC2 instance provisioning using Karpenter
- Scale new inference nodes within 2 minutes
- Save up to 70% cost using GPU Spot instances
- Support for various community Stable Diffusion runtimes

!!! warning "Migration Notice"
    This project has been migrated to [aws-solutions-library-samples/guidance-for-asynchronous-inference-with-stable-diffusion-webui-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-asynchronous-inference-with-stable-diffusion-webui-on-aws) This repository and docs is for archive only and no longer receives update.

    You can migrate your configuration by moving `config.yaml` to the new repository.

!!! abstract "Disclaimer"
    This solution is for reference architecture and sample code provided to you under the [MIT-0 License](https://github.com/aws-samples/stable-diffusion-on-eks/blob/main/LICENSE).

    This solution is for demonstration, proof of concept, or learning purposes only. You should not use this solution directly in your production account or for production or other critical data.

    Deploying this solution may incur AWS charges for creating or using AWS chargeable resources, such as running Amazon EC2 instances or using Amazon S3 storage.