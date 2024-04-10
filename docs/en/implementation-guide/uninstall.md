# Delete Solution

The deployed solution can be deleted using CloudFormation.

!!! danger "Permanent Deletion"
    All deleted resources will be permanently deleted and cannot be recovered by any means.

## Deletion Scope

* The following **will** be permanently deleted:
    * Amazon EKS cluster and all worker nodes
    * SNS topics and all subscriptions
    * SQS queues
    * VPC
    * IAM roles used by the solution

* The following **will not** be deleted:
    * S3 bucket storing output images
    * S3 bucket storing models

## Preparation Before Deletion

Before deleting the solution, please ensure that the solution meets the following conditions:

* All SQS queues have been emptied
* No additional policies are attached to any IAM roles
* No additional resources (such as EC2, ENI, Cloud9, etc.) exist in the VPC

## Delete Solution

You can delete this solution via the CDK CLI or the AWS Management Console.

=== "AWS Management Console"

    * Go to the [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation/home)
    * Select **Stacks**
    * In the list, select **sdoneksStack** (or your custom name)
    * Select **Delete**, and in the pop-up dialog, select **Delete**

=== "AWS CDK"

    In the solution source code directory, run the following command to delete the solution:

    ```bash
    npx cdk destroy
    ```

Deleting the solution will take approximately 20-30 minutes.