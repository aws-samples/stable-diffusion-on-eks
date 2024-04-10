# Kubernetes Cluster Management

You can use the `kubectl` command to connect to the cluster created by the solution, get the current system running status, and perform customizations.

## Install kubectl

You can refer to the [Installing or updating kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html) documentation to install the `kubectl` command-line tool. Please install kubectl compatible with Kubernetes 1.28.

## Log in to the Kubernetes Cluster

You can find the command to connect to the EKS cluster from the CloudFormation output:

=== "AWS Management Console"

    * Go to the [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation/home)
    * Select **Stacks**
    * In the list, select **SdOnEKSStack** (or your custom name)
    * Select **Output**
    * Record the value of the **ConfigCommand** item
    * Execute the command in the terminal.

=== "AWS CLI"

    Run the following command to get the command:

    ```bash
    aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`ConfigCommand`].OutputValue'
    ```

    Execute the command in the terminal.