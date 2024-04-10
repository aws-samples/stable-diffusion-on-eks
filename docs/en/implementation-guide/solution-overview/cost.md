# Cost Estimation

!!! Important "Important"

    The cost estimates described in this section are examples and may vary depending on your environment.


You will incur costs for using various Amazon Web Services when running the solution. The main factors affecting the cost of the solution include:

- The instance type and purchasing option you choose
- The number of images generated
- The Elastic Scaling configuration

Taking the text-to-image task with 512x512, steps=16 as an example, using the g5.xlarge instance in the AWS US East (N. Virginia) region, the average generation speed per image is about 1.5s/image. According to the [Amazon Web Services official page](https://aws.amazon.com/ec2/instance-types/g5/), the on-demand pricing is $1.006/hour, and the average inference computing cost per thousand images is $0.42. If you choose a 1-year ISP ($0.604/hour), the average inference computing cost per thousand images is $0.25. If you choose a 3-year ISP ($0.402/hour), the average inference computing cost per thousand images can be as low as $0.17.

In addition, other running costs of the solution include storage costs, on-demand costs for serverless services, and network data transfer costs. For detailed pricing formulas, please refer to the [Pricing Calculator](https://docs.aws.amazon.com/pricing-calculator/latest/userguide/getting-started.html).