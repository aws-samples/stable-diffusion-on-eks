# Kubernetes Cluster Management

You can use the `kubectl` command to connect to the cluster created by the solution, retrieve the current system status, and make customizations.

## Install kubectl

Refer to the [Installing or updating kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html) documentation to install the `kubectl` command-line tool. Install a version of kubectl that is compatible with Kubernetes 1.27.

## Log in to the Kubernetes Cluster

You can find the command to connect to the EKS cluster from the CloudFormation output:

=== "AWS Management Console"

    * Go to the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation/home)
    * Choose **Stacks**
    * In the list, select **SdOnEKSStack** (or your custom name)
    * Choose **Output**
    * Record the value of the **ConfigCommand** item
    * Execute that command in your terminal.

=== "AWS CLI"

    Run the following command to retrieve the command:

    ```bash
    aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`sdNotificationOutputArn`].OutputValue'
    ```

    Execute that command in your terminal.