# Stable Diffusion on EKS

!!! failure "Working in progress"
    Documentation in English is a working in progress.

Implementing a fast scaling and low cost Stable Diffusion inference solution with serverless and containers on AWS

Stable Diffusion is a popular open source project for generating images using Gen AI. Building a scalable and cost efficient inference solution is a common challenge AWS customers facing. This project shows how to use serverless and container services to build an end-to-end low cost and fast scaling asyncronous image generation architecture. This repo contains the sample code and CDK deployment scripts, helping you to deploy this solution in a few steps.

## Features

- Asyncronous API and Serverless Event-Driven Architecture
- Image Generation with Stable Diffusion Web UI on Amazon EKS
- Automatic queue length based scaling with KEDA
- Automatic provisioning ec2 instances with Karpenter
- Scaling up new inference nodes within 2 minutes
- Saving up to 70% with GPU spot instances
