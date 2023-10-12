# 回调和通知

Stable Diffusion on Amazon EKS方案采用异步推理模式，当图片生成或报错后，会通过Amazon SNS通知用户。用户应用可以通过订阅 SNS 主题以获取图片生成完成的通知。

请参考 [Amazon SNS文档](https://docs.aws.amazon.com/sns/latest/dg/sns-event-destinations.html) 以了解 SNS 支持的消息目标类型。

您可以从CloudFormation的输出中找到生成的 SNS 主题 ARN：

=== "AWS 管理控制台"

    * 进入 [AWS CloudFormation 控制台](https://console.aws.amazon.com/cloudformation/home)
    * 选择 **Stacks** （堆栈）
    * 在列表中，选择 **SdOnEKSStack** （或您自定义的名称）
    * 选择 **Output** （输出）
    * 记录 **sdNotificationOutputArn** 项的值（格式为  `arn:aws:sns:us-east-1:123456789012:SdOnEKSStack-sdNotificationOutputCfn-abcdefgh`）

=== "AWS CLI"

    运行以下命令以获取 SNS 主题 ARN：

    ```bash
    getkey="$(aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`sdNotificationOutputArn`].OutputValue')"
    ```

如需接收消息，您需要将您的消息接收端（如Amazon SQS队列，HTTP 终端节点等）作为**订阅**添加到该SNS主题中。

=== "AWS 管理控制台"

    * 在左侧导航窗格中，选择**Subscriptions** （订阅）。
    * 在 **Subscriptions**（订阅）页面上，选择 **Create subscription**（创建订阅）。
    * 在 **Create subscription**（创建订阅）页上的 Details（详细信息）部分中，执行以下操作：
        * 对于 **Topic ARN**（主题 ARN），选择您在上一步中记录的ARN。
        * 对于 **Protocol**（协议），选择您的接收端类型。
        * 对于 **Endpoint**（终端节点），输入您的接收端地址，例如电子邮件地址或 Amazon SQS 队列的 ARN。
    * 选择 **Create subscription**（创建订阅）

=== "AWS CLI"

    请参考[Use Amazon SNS with the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-services-sns.html#cli-subscribe-sns-topic)