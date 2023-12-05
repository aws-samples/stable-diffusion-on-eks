# View Monitoring

You can view the monitoring metrics for this solution in CloudWatch.

The monitoring metrics are provided by Container Insight. Refer to [Amazon EKS and Kubernetes Container Insights metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-metrics-EKS.html) for metric details.

=== "AWS Management Console"
    * Open the [Amazon CloudWatch console](https://console.aws.amazon.com/cloudwatch/).
    * In the left navigation pane, choose **Metrics** - **All Metrics**.
    * Select **ContainerInsights**.
    * Choose **ClusterName, Namespace, PodName**.
    * You can view metrics for different replicas of the runtime based on **PodName**.