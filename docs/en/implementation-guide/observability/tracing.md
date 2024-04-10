# View Traces

You can view the time spent on each stage of individual requests from X-Ray to achieve tracing.

## Service Overview

=== "AWS Management Console"
    * Open the [Amazon CloudWatch console](https://console.aws.amazon.com/cloudwatch/).
    * In the left navigation pane, choose **X-Ray traces** - **Service map**.
    * The service map will list the relevant components of this solution, and you can click on a component to display its metrics (including latency, request count, and error count).

## View Request Details

    * In the left navigation pane, choose **X-Ray traces** - **Traces**.
    * In the **Traces** section below, the details of each request will be listed, and you can select an individual request to display the detailed time spent on each step.