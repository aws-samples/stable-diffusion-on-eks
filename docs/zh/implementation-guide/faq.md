# 常见问题解答

## 一般问题

* **什么是Stable Diffusion on Amazon EKS 解决方案？**

    Stable Diffusion on Amazon EKS解决方案是一套在Amazon Web Services中部署Stable Diffusion的参考架构，该参考架构基于事件驱动架构设计，并使用无服务器和容器等相关现代化应用服务实现。通过该方案，用户可以在Amazon Web Services中快速部署Stable Diffusion用于推理生成图片，并满足快速按需扩展、高可用以及低成本等能力要求。

* **该解决方案都有哪些独特之处？**

    Stable Diffusion on Amazon EKS方案基于事件驱动架构设计，利用 KEDA 实现基于队列长度的自动扩展，可充分应对前端高并发的生图推理请求，并且利用 Karpenter 和 Bottlerocket，可快速扩展新的推理节点，极大降低了出图等待的时间。不仅如此，该方案支持使用 GPU Spot 实例，可帮助客户以较低的成本使用到推理所需要的计算资源。另一方面，该方案支持多种社区Stable Diffusion运行时，并且也支持使用统一的kubernetes API对底层Amazon EKS实现管理，具备良好的开放性和灵活度，客户亦可基于此参考架构方便地针对自身业务诉求进行定制化修改。

* **在什么情况下，我更适合使用Stable Diffusion on Amazon EKS?**

    与其他在Amazon Web Services上使用Stable Diffusion的方案相比，该方案更适合在推理生成图片上并发请求多或者波动较大，出图性能延迟要求高的业务负载。或者，对于已使用Kubernetes技术栈作为资源调度管理平台的客户，或者对于定制化要求较多的客户，也可以更多地从该方案中收益。

* **该解决方案使用哪些AWS服务？**

    请参见 [AWS服务](architecture/services-in-this-solution.md) 页面。

* **AWS 如何支持该解决方案？**

    该方案由 AWS 解决方案架构师团队基于MIT-0协议向您提供。该方案目前仅提供社区支持。如该解决方案代码出现Bug，或对该解决方案有功能建议，请通过Github联系我们。

    如果是方案中涉及到的AWS产品服务出现故障，可基于您所购买的支持计划联系AWS支持团队。

    AWS解决方案架构师团队可以提供方案研讨，Workshop和部署支持。如您需要，请联系您的客户团队，或通过[该网页](https://aws.amazon.com/cn/contact-us/)联系我们。


* **我如何部署该解决方案?**

    我们提供基于AWS CDK的一键部署模板，允许您在您的AWS账户中部署该解决方案。您可以通过配置文件中的各配置项，对部署进行自定义。您也可以在部署完成后对该解决方案进行扩展。


* **我可以使用哪种实例类型?**

    目前您可以使用对应区域下的加速计算实例。目前经过测试，可使用含g5, g4dn, p3等实例类型。g3实例类型由于驱动程序原因不受支持。目前暂不支持inf系列实例类型。CPU机型生成图像较缓慢，不建议使用。
