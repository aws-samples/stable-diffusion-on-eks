# View Logs

You can view the logs for this solution from CloudWatch Logs.

=== "AWS Management Console"
    * Open the [Amazon CloudWatch console](https://console.aws.amazon.com/cloudwatch/).
    * In the left navigation pane, choose **Logs** - **Log groups**.
    * Select the corresponding log group. The log group format is `/aws/eks/fluentbit-cloudwatch/workload/default`, replace `default` with the Kubernetes namespace where the workload is running.
    * You can select the corresponding **Log Stream** to view logs for different components, or select **Search all log streams** to search within the logs.