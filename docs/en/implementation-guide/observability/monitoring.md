# View Monitoring

You can view the monitoring metrics for this solution from CloudWatch.

The monitoring metrics are provided by Container Insight, please refer to [Amazon EKS and Kubernetes Container Insights metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-metrics-EKS.html) to learn more about the metrics.

=== "AWS Management Console"
    * Open the [Amazon CloudWatch console](https://console.aws.amazon.com/cloudwatch/).
    * In the left navigation pane, choose **Metrics** - **All Metrics**.
    * Select **ContainerInsights**.
    * Select **ClusterName, Namespace, PodName**
    * You can view the metrics for different replicas based on **PodName**.