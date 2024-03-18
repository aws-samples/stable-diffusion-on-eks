# Kubernetes 集群管理

您可以使用`kubectl`命令连接到解决方案创建的集群中，获取当前系统运行状态并进行自定义。

## 安装kubectl

您可以参考 [Installing or updating kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html) 文档安装`kubectl`命令行工具。请安装适用于Kubernetes 1.28的kubectl。

## 登录到 Kubernetes 集群

您可以从CloudFormation的输出中找到连接到EKS集群的命令：

=== "AWS 管理控制台"

    * 进入 [AWS CloudFormation 控制台](https://console.aws.amazon.com/cloudformation/home)
    * 选择 **Stacks** （堆栈）
    * 在列表中，选择 **SdOnEKSStack** （或您自定义的名称）
    * 选择 **Output** （输出）
    * 记录 **ConfigCommand** 项的值
    * 在终端中执行该命令。

=== "AWS CLI"

    运行以下命令以获取该命令：

    ```bash
    aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`ConfigCommand`].OutputValue'
    ```

    在终端中执行该命令。
