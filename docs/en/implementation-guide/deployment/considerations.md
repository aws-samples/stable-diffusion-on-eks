# Deployment Consideration

Please check the following considerations before deployment:

## Deployable Regions
The services or Amazon EC2 instance types used in this solution may not be available in all AWS regions. Launch this solution in an AWS region that provides the required services.

**Verified Deployable Regions**

| Region Name | Verified |
|-------------|----------|
| US East (N. Virginia) | :material-check-bold:{ .icon_check } |
| US West (Oregon) | :material-check-bold:{ .icon_check } |

If deploying in an unverified region, you may need to:

* Manually specify the instance type used by Karpenter as `g4dn` or other GPU instance types when deploying in regions that do not support `g5` instances.

**Deploying in AWS China Regions**

!!! danger "Network Restrictions in China Regions"

    Recently, we found issues when deploying this solution in China regions. The EBS failed to deploy, with error messages like `Waiter has timed out` or `Unexpected EOF`. See [this issue](https://github.com/aws-samples/stable-diffusion-on-eks/issues/53) for details.

    The root cause is that some Helm Charts are hosted on Github. When deploying in China regions, the Lambda function responsible for deploying custom resources cannot retrieve the Helm Charts, causing failures. We are actively working on this issue and will copy the required Helm Charts and container images to China regions.

    If you encounter this issue during deployment, please switch to a non-China region for testing, or set up your own Helm repo as a temporary solution.

This solution can be deployed in AWS China regions.

| Region Name | Verified |
|-------------|----------|
| China (Ningxia), operated by NWCD | :material-check-bold:{ .icon_check } |

When deploying in China regions, due to environment limitations, you may need to:

* China regions do not support the default `g5` instance type. You need to manually specify the instance type used by Karpenter as `g4dn` or other GPU instance types.

## IAM Permissions

Deploying this solution requires administrator or equivalent permissions. Due to the number of components, we do not provide a minimal permissions list.

## Service Quotas

Each AWS account has quotas on the number of resources that can be created in each AWS region. You can view service quotas in the AWS console using the [Service Quotas](https://console.aws.amazon.com/servicequotas/home/) tool. If a service quota can be increased, you can open a case through this tool to request an increase.

The main service quotas related to this solution are:

| AWS Service | Quota Entry | Estimated Usage | Adjustable |
|-------------|--------------|------------------|------------|
| Amazon EC2 | [Running On-Demand G and VT instances](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-DB2E81BA) | Based on max concurrent GPU instances | :material-check-bold:{ .icon_check } |
| Amazon EC2 | [All G and VT Spot Instance Requests](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-3819A6DF) | Based on max concurrent GPU instances | :material-check-bold:{ .icon_check } |
| Amazon SNS | [Messages Published per Second](https://console.aws.amazon.com/servicequotas/home/services/sns/quotas/L-F8E2BA85) | Based on max concurrent requests | :material-check-bold:{ .icon_check } |

Additionally, consider the following service quotas during deployment:

| AWS Service | Quota Entry | Estimated Usage | Adjustable |
|-------------|--------------|------------------|------------|
| Amazon VPC | [VPCs per Region](https://console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-F678F1CE) | 1 | :material-check-bold:{ .icon_check } |
| Amazon VPC | [NAT gateways per Availability Zone](https://console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-FE5A380F) | 1 | :material-check-bold:{ .icon_check } |
| Amazon EC2 | [EC2-VPC Elastic IPs](https://console.aws.amazon.com/servicequotas/home/services/ec2/quotas/L-0263D0A3) | 1 | :material-check-bold:{ .icon_check } |
| Amazon S3 | [General purpose buckets](https://console.aws.amazon.com/servicequotas/home/services/s3/quotas/L-DC2B2D3D) | 1 per queue | :material-check-bold:{ .icon_check } |

## Choose Stable Diffusion Runtime

You need a runtime to deploy the Stable Diffusion model and provide API access.

Currently, there are multiple community Stable Diffusion runtimes available:

| Runtime Name | Link | Verified |
|---------------|------|----------|
| Stable Diffusion Web UI | [GitHub](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | :material-check-bold:{ .icon_check } |
| ComfyUI | [GitHub](https://github.com/comfyanonymous/ComfyUI) | :material-check-bold:{ .icon_check } |
| InvokeAI | [GitHub](https://github.com/invoke-ai/InvokeAI) | |

You can also choose other runtimes or build your own. You need to package the runtime as a container image to run on EKS.

You need to fully understand and comply with the license terms of the Stable Diffusion runtime you use.

!!! example "Example Runtime"

    You can use the community-provided [example Dockerfile](https://github.com/yubingjiaocn/stable-diffusion-webui-docker) to build runtime container images for *Stable Diffusion Web UI* and *ComfyUI*. Note that these images are for technical evaluation and testing purposes only, and should not be deployed to production environments.

!!! info "Model Storage"

    By default, this solution will load models to the `/opt/ml/code/models` directory. Ensure your runtime is configured to read models from this directory.

    You need to disable mmap to achieve the highest performance.

    * For SD Web UI, set `disable_mmap_load_safetensors: true` in `config.json`
    * For ComfyUI, manually modify the source code as guided in [this community issue](https://github.com/comfyanonymous/ComfyUI/issues/2288).

!!! info "Notes on SD Web UI Runtime"

    For the SD Web UI runtime, there are static runtimes (pre-load models) and dynamic runtimes (load models on-demand) depending on the model being run.

    * Static runtimes use models specified in `modelFilename`. The model is loaded into GPU memory at startup.
    * Dynamic runtimes need to set `dynamicModel: true`. No model needs to be specified. The runtime will load the model from Amazon S3 and perform inference based on the model used in the request.

## Other Important Notes and Limitations

- In the current version, this solution will automatically create a new VPC when deployed. The VPC includes:
    - CIDR `10.0.0.0/16`
    - 3 public subnets in different availability zones, with size `/19`
    - 3 private subnets in different availability zones, with size `/19`
    - 3 NAT gateways (placed in public subnets)
    - 1 Internet gateway
    - Corresponding route tables and security groups

    Currently, the parameters of this VPC cannot be customized.

- In the current version, this solution can only be deployed on a new EKS cluster with a fixed version of `1.28`. We will update the cluster version as new Amazon EKS versions are released.