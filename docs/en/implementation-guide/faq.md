# Frequently Asked Questions

## General Questions

* **What is the Stable Diffusion on Amazon EKS solution?**

    The Stable Diffusion on Amazon EKS solution is a reference architecture for deploying Stable Diffusion on Amazon Web Services. This reference architecture is designed based on an event-driven architecture and leverages modern application services such as serverless and containers. With this solution, users can quickly deploy Stable Diffusion for inferencing and generating images on Amazon Web Services, meeting requirements for rapid on-demand scaling, high availability, and cost-effectiveness.

* **What makes this solution unique?**

    The Stable Diffusion on Amazon EKS solution is designed based on an event-driven architecture, utilizing KEDA for automatic scaling based on queue length. It can effectively handle high-concurrency inference requests and, with the help of Karpenter and Bottlerocket, rapidly scale new inference nodes, greatly reducing image generation wait times. Additionally, the solution supports the use of GPU Spot instances, enabling customers to utilize the required computing resources at a lower cost. The solution also supports multiple community Stable Diffusion runtimes and provides unified management through the Kubernetes API for underlying Amazon EKS, offering openness and flexibility. Customers can easily customize this reference architecture to meet their specific business requirements.

* **When is it more suitable for me to use Stable Diffusion on Amazon EKS?**

    Compared to other solutions using Stable Diffusion on Amazon Web Services, this solution is more suitable for business workloads with high concurrent requests or fluctuating demands, where low-latency image generation performance is crucial. Alternatively, for customers already using the Kubernetes technology stack as a resource scheduling and management platform or for customers with more customization requirements, this solution can provide additional benefits.

* **What AWS services does this solution use?**

    Please refer to the [AWS Services](architecture/services-in-this-solution.md) page.

* **How does AWS support this solution?**

    This solution is provided by the AWS Solutions Architecture team under the MIT-0 license. The solution currently only receives community support. If you encounter bugs in the solution code or have feature suggestions, please contact us through GitHub.

    If there are issues with AWS products or services mentioned in the solution, you can contact AWS support based on your support plan.

    The AWS Solutions Architecture team can provide solution discussions, workshops, and deployment support. If you need assistance, please contact your customer team or [contact us](https://aws.amazon.com/cn/contact-us/) through this webpage.

* **How do I deploy this solution?**

    We provide a one-click deployment template based on AWS CDK, allowing you to deploy this solution in your AWS account. You can customize the deployment through various configuration options in the configuration file. After deployment, you can further extend the solution.

* **Which instance types can I use?**

    Currently, you can use accelerated computing instances in the corresponding region. Instances such as g5, g4dn, and p3 have been tested and are supported. g3 instances are not supported due to driver issues. inf series instances are not supported at this time. CPU instance types generate images more slowly and are not recommended for use.