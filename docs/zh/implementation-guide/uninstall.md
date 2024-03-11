# 删除解决方案

部署的解决方案可以使用CloudFormation删除。

!!! danger "永久删除"
    所有删除的资源将被永久删除，无法以任何手段被恢复。

## 删除范围

* 以下内容**会**被永久删除：
    * Amazon EKS 集群及所有工作节点
    * SNS 主题及所有订阅
    * SQS 队列
    * VPC
    * 解决方案使用的IAM角色

* 以下内容**不会**被删除：
    * 存储输出图像的S3存储桶
    * 存储模型的S3存储桶

## 删除前准备

在删除解决方案前，请确保解决方案满足以下条件：

* 所有SQS队列已被清空
* 所有的IAM角色没有附加额外策略
* VPC内无额外的资源（如EC2，ENI，Cloud9等）

## 删除解决方案

您可以通过CDK CLI或AWS 管理控制台删除该解决方案。

=== "AWS 管理控制台"

    * 进入 [AWS CloudFormation 控制台](https://console.aws.amazon.com/cloudformation/home)
    * 选择 **Stacks** （堆栈）
    * 在列表中，选择 **SdOnEKSStack** （或您自定义的名称）
    * 选择 **Delete** （删除），在弹出的对话框中选择 **Delete** （删除）

=== "AWS CDK"

    在解决方案源代码目录，运行以下命令以删除解决方案：

    ```bash
    npx cdk destroy
    ```

删除解决方案大约需要 20-30 分钟。
