# Deployment Planning

Please check the following considerations before deployment:

## Deployable Regions
The services used in this solution, or the Amazon EC2 instance types, may not be available in all AWS Regions at this time. Please launch this solution in an AWS Region that provides the required services.

**Verified Deployable Regions**

| Region Name           | Verified |
|----------------|---------------------------------------|
| US East (N. Virginia)  | :material-check-bold:{ .icon_check }  |
| US West (Oregon)     | :material-check-bold:{ .icon_check }  |

If you deploy in an unverified region, you may need to handle the following or face the following issues:

* When deploying in regions that do not support `g5` instance types, you need to manually specify the instance type used by Karpenter as `g4dn` or other GPU instance types.

**Deploying in AWS China Regions**

Please refer to [Deploying in AWS China Regions](./aws-cn.md)

## IAM Permissions

Deploying this solution requires administrator or equivalent permissions. Due to the number of components involved, we do not provide a minimal permissions list.

## Service Quotas

Each AWS account in each AWS Region has quotas on the number of resources you can create. You can view your service quotas using the [Service Quota](https://console.aws.amazon.com/servicequotas/home/) tool in the AWS console. If a service quota can be increased, you can request an increase through the tool by opening a case.

The main service quotas related to this solution are:

| AWS Service | Quota Entry | Estimated Usage | Adjustable |
|---------|---------|-----------|-----------|
| Amazon EC2  | [Running On-Demand G and VT instances](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-DB2E81BA) | Based on max concurrent GPU instances | :material-check-bold:{ .icon_check }  |
| Amazon EC2  | [All G and VT Spot Instance Requests](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-3819A6DF) | Based on max concurrent GPU instances | :material-check-bold:{ .icon_check }  |
| Amazon SNS  | [Messages Published per Second](https://console.aws.amazon.com/servicequotas/home/services/sns/quotas/L-F8E2BA85) | Based on max concurrent requests | :material-check-bold:{ .icon_check }  |

In addition, you need to consider the following service quotas during deployment:

| AWS Service | Quota Entry | Estimated Usage | Adjustable |
|---------|---------|-----------|-----------|
| Amazon VPC  | [VPCs per Region](https://console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-F678F1CE) | 1 | :material-check-bold:{ .icon_check }  |
| Amazon VPC  | [NAT gateways per Availability Zone](https://console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-FE5A380F) | 1 | :material-check-bold:{ .icon_check }  |
| Amazon EC2  | [EC2-VPC Elastic IPs](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-0263D0A3) | 1 | :material-check-bold:{ .icon_check }  |
| Amazon S3  | [General purpose buckets](https://console.aws.amazon.com/servicequotas/home/services/s3/quotas/L-DC2B2D3D) | 1 per queue | :material-check-bold:{ .icon_check }  |

## Choosing a Stable Diffusion Runtime

You need a runtime to deploy the Stable Diffusion model and provide API access.

Currently, there are multiple community Stable Diffusion runtimes available:

| Runtime Name           | Link |  Verified  |
|----------------|-----------------|----------------------|
| Stable Diffusion Web UI  | [GitHub](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | :material-check-bold:{ .icon_check }  |
| ComfyUI     | [GitHub](https://github.com/comfyanonymous/ComfyUI) | :material-check-bold:{ .icon_check }  |
| InvokeAI     | [GitHub](https://github.com/invoke-ai/InvokeAI) |   |

You can also choose other runtimes or build your own runtime. You need to package the runtime as a container image to run it on EKS.

You need to fully understand and comply with the license terms of the Stable Diffusion runtime you are using.

!!! example "Example Runtime"

    You can use the community-provided [example Dockerfile](https://github.com/yubingjiaocn/stable-diffusion-webui-docker) to build the runtime container images for *Stable Diffusion Web UI* and *ComfyUI*. Please note that this image is only for technical evaluation and testing purposes, and should not be deployed to production environments.

!!! info "Model Storage"

    By default, this solution will load the model to the `/opt/ml/code/models` directory, please ensure your runtime is configured to read the model from this directory.

    You need to disable mmap to achieve the highest performance for your runtime.

    * For SD Web UI, you need to set `disable_mmap_load_safetensors: true` in `config.json`
    * For ComfyUI, you need to manually modify the source code as guided in the [community issue](https://github.com/comfyanonymous/ComfyUI/issues/2288).

!!! info "Notes on SD Web UI Runtime"

    For the SD Web UI runtime, depending on the model being run, the runtime can be either a static runtime (pre-loading the model) or a dynamic runtime (loading the model on-demand).

    * Static runtime requires specifying the model to be used in `modelFilename`. This model will be loaded into GPU memory at startup.
    * Dynamic runtime requires specifying `dynamicModel: true`. In this case, there is no need to specify the model in advance. The runtime will load the model from Amazon S3 and perform model inference based on the model used in the request.

## Other Important Notes and Limitations

- In the current version, this solution will automatically create a new VPC when deployed. This VPC includes:
    - CIDR `10.0.0.0/16`
    - 3 public subnets distributed across different Availability Zones, with subnet size `/19`
    - 3 private subnets distributed across different Availability Zones, with subnet size `/19`
    - 3 NAT gateways (placed in public subnets)
    - 1 Internet gateway
    - Corresponding route tables and security groups

    Currently, the parameters of this VPC cannot be customized.

- In the current version, this solution can only be deployed on a newly created EKS cluster, and the version is fixed at `1.28`. We will update the cluster version as Amazon EKS releases new versions.