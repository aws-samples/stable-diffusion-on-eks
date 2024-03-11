# Considerations

## Deployable Regions
The services used by this solution or the EC2 instance types may not be available in all AWS regions. Please launch this solution in an AWS region that provides the required services.

**Verified Deployable Regions**

| Region Name     | Verified |
|-----------------|--------------------------|
| us-east-1        | :material-check-bold:{ .icon_check }  |
| us-west-2        | :material-check-bold:{ .icon_check }  |

If you deploy in an unverified region, you may need to take the following actions or face potential issues:

* When deploying in a region that does not support the g5 instance type, you may need to manually specify the instance type used by Karpenter as `g4dn` or another GPU instance type.

## IAM Permissions

Deploying this solution requires administrator or equivalent permissions.

## Choose your Stable Diffusion Runtime

You need runtimes to deploy the Stable Diffusion model and provide API access. Several community Stable Diffusion runtimes are available, and you can build your own runtime. Package the runtime as a container image to run it on EKS.

Here are some examples:

* [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
* [InvokeAI](https://github.com/invoke-ai/InvokeAI)
* [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

For your convenience, you can use this [sample Dockerfile](https://github.com/antman2008/stable-diffusion-webui-dockerfile) to build a container image of *AUTOMATIC1111's Stable Diffusion Web UI*.

## Important Note

- Only one active Stable Diffusion on Amazon EKS solution stack is allowed in a region. If your deployment fails, ensure that the failed stack is deleted before attempting to redeploy.