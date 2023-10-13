# 查看监控

您可以从CloudWatch中查看该解决方案的监控指标。

监控指标由Container Insight提供，请参考 [Amazon EKS and Kubernetes Container Insights metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-metrics-EKS.html) 以了解指标详情。

=== "AWS 管理控制台"
    * 打开 [Amazon CloudWatch 控制台](https://console.aws.amazon.com/cloudwatch/)。
    * 在左侧导航窗格中，选择 **Metrics** - **All Metrics**。
    * 选择 **ContainerInsights**。
    * 选择 **ClusterName, Namespace, PodName**
    * 可以根据 **PodName** 查看运行时不同副本的指标。
