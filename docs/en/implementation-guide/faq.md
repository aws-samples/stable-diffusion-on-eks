# Frequently Asked Questions

## General Questions

* **What is the Stable Diffusion on Amazon EKS solution?**

    The Stable Diffusion on Amazon EKS solution is a reference architecture for deploying Stable Diffusion on Amazon Web Services. This reference architecture is designed based on an event-driven architecture and leverages modern application services such as serverless and containers. With this solution, users can quickly deploy Stable Diffusion on Amazon Web Services for image generation inference, meeting requirements for rapid on-demand scaling, high availability, and low cost.

* **What are the unique features of this solution?**

    The Stable Diffusion on Amazon EKS solution is designed based on an event-driven architecture, utilizing KEDA for queue-length-based auto-scaling to handle high-concurrency image generation inference requests from the frontend. It also leverages Karpenter and Bottlerocket to quickly scale out new inference nodes, significantly reducing the waiting time for image generation. Additionally, this solution supports using GPU Spot instances, helping customers leverage the required compute resources for inference at a lower cost. Furthermore, the solution supports various community Stable Diffusion runtimes and provides a unified Kubernetes API for managing the underlying Amazon EKS, offering excellent openness and flexibility. Customers can also easily customize this reference architecture to meet their specific business requirements.

* **In what scenarios is the Stable Diffusion on Amazon EKS solution more suitable?**

    Compared to other solutions for using Stable Diffusion on Amazon Web Services, this solution is more suitable for workloads with high or fluctuating concurrent requests for image generation inference, or with stringent performance requirements for image generation latency. Additionally, customers who have already adopted the Kubernetes technology stack as their resource scheduling and management platform, or those with extensive customization requirements, can also benefit more from this solution.

* **What AWS services are used in this solution?**

    Please refer to the [AWS Services](architecture/services-in-this-solution.md) page.

* **How does AWS support this solution?**

    This solution is provided to you by the AWS Solutions Architect team under the MIT-0 license. Currently, it only offers community support. If you encounter any bugs in the solution code or have feature suggestions, please contact us through GitHub.

    If there are any issues with the AWS product services involved in the solution, you can contact the AWS Support team based on your purchased support plan.

    The AWS Solutions Architect team can provide solution discussions, workshops, and deployment support. If you need assistance, please contact your customer team or reach out to us through [this webpage](https://aws.amazon.com/contact-us/).

* **How do I deploy this solution?**

    We provide a one-click deployment template based on AWS CDK, allowing you to deploy this solution in your AWS account. You can customize the deployment through various configuration options in the configuration file. You can also extend the solution after deployment.

* **What instance types can I use?**

    Currently, you can use accelerated computing instances available in the corresponding region. Based on testing, you can use instance types such as g5, g4dn, and p3. The g3 instance type is not supported due to driver issues. The inf series instance types are currently not supported. CPU instances are not recommended for image generation as they are relatively slow.