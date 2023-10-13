# 查看日志

您可以从CloudWatch Logs中查看该解决方案的日志。

=== "AWS 管理控制台"
    * 打开 [Amazon CloudWatch 控制台](https://console.aws.amazon.com/cloudwatch/)。
    * 在左侧导航窗格中，选择 **Logs** - **Log groups**。
    * 选择对应的日志组。日志组格式为 `/aws/eks/fluentbit-cloudwatch/workload/default`，将`default`替换为运行时所在的Kubernetes命名空间。
    * 您可以选择对应的 **Log Stream** 查看不同组件的日志，也可选择 **Search all log streams** 在日志中搜索。
