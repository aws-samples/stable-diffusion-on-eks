# 考虑因素

## 可部署区域
此解决方案使用的服务，或EC2实例类型目前可能并非在所有 AWS 区域都可用。请在提供所需服务的 AWS 区域中启动此解决方案。

**已验证可部署的区域**

| 区域名称           | 验证通过 |
|----------------|---------------------------------------|
| 美国东部 (弗吉尼亚北部)  | :material-check-bold:{ .icon_check }  |
| 美国西部 (俄勒冈)     | :material-check-bold:{ .icon_check }  |

如您在未经验证的区域进行部署，可能需要进行以下处理，或面临以下问题：

* 在不支持g5实例类型的区域部署时，您需要手工指定 Karpenter 使用的实例类型为 `g4dn` 或其他 GPU 实例类型。
* 在部分区域部署时， EFS 的性能可能会受到影响，请参见 [Amazon EFS文档](https://docs.aws.amazon.com/efs/latest/ug/limits.html#:~:text=Total%20default%20Elastic%20Throughput) 以了解在不同区域的EFS读取性能。

## IAM 权限

部署该解决方案需要管理员或与之相当的权限。

## Choose your Stable Diffusion Runtime

You need runtimes to deploy Stable Diffusion model and provide API access. There are several community Stable Diffusion runtimes available, and you can build your own runtime. You need to package runtime as a container image to run the runtime on EKS.

Here are some examples:

* [AUTOMATIC1111's Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
* [InvokeAI](https://github.com/invoke-ai/InvokeAI)
* [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

For you convenience, you can use this [sample Dockerfile](https://github.com/antman2008/stable-diffusion-webui-dockerfile) to build a container image of *AUTOMATIC1111's Stable Diffusion Web UI*.


## 重要提示

- 一个区域中只能有一个活动的Stable Diffusion on Amazon EKS解决方案堆栈。如果您的部署失败，请确保在重试部署之前已删除失败的堆栈。