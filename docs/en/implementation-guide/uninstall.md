# Delete Solution

The deployed solution can be deleted using CloudFormation.

!!! danger "Permanent Deletion"
    All deleted resources will be permanently removed and cannot be recovered by any means.

## Deletion Scope

* The following will be **permanently deleted**:
    * Amazon EKS cluster and all worker nodes
    * SNS topics and all subscriptions
    * SQS queues
    * VPC
    * IAM roles used by the solution

* The following will **not be deleted**:
    * S3 bucket storing output images
    * S3 bucket storing models

## Pre-Deletion Preparation

Before deleting the solution, ensure the following conditions are met:

* All SQS queues have been emptied.
* No additional policies are attached to IAM roles.
* No additional resources (such as EC2 instances, ENIs, Cloud9 environments, etc.) exist within the VPC.

## Deleting the Solution

You can delete the solution using either the CDK CLI or the AWS Management Console.

=== "AWS Management Console"

    * Navigate to the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation/home)
    * Select **Stacks**
    * In the list, select **SdOnEKSStack** (or the name you customized)
    * Select **Delete**, and in the pop-up dialog, choose **Delete**

=== "AWS CDK"

    In the solution's source code directory, run the following command to delete the solution:

    ```bash
    npx cdk destroy
    ```

Deleting the solution takes approximately 20-30 minutes.