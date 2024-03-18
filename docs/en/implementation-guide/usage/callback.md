# Callbacks and Notifications

The Stable Diffusion on Amazon EKS solution uses an asynchronous inference mode. When an image is generated or an error occurs, users will be notified through Amazon SNS. User applications can subscribe to the SNS topic to receive notifications when image generation is complete.

## Adding Subscriptions

Please refer to the [Amazon SNS documentation](https://docs.aws.amazon.com/sns/latest/dg/sns-event-destinations.html) to understand the types of message destinations supported by SNS.

You can find the ARN of the generated SNS topic in the outputs of CloudFormation:

=== "AWS Management Console"

    * Go to the [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation/home)
    * Select **Stacks**
    * In the list, select **SdOnEKSStack** (or your custom name)
    * Select **Output**
    * Record the value of the **sdNotificationOutputArn** item (in the format `arn:aws:sns:us-east-1:123456789012:SdOnEKSStack-sdNotificationOutputCfn-abcdefgh`)

=== "AWS CLI"

    Run the following command to get the SNS topic ARN:

    ```bash
    aws cloudformation describe-stacks --stack-name SdOnEKSStack --output text --query 'Stacks[0].Outputs[?OutputKey==`sdNotificationOutputArn`].OutputValue'
    ```

To receive messages, you need to add your message receiver (such as an Amazon SQS queue, HTTP endpoint, etc.) as a **subscription** to this SNS topic.

=== "AWS Management Console"

    * In the left navigation pane, select **Subscriptions**.
    * On the **Subscriptions** page, select **Create subscription**.
    * In the Details section of the **Create subscription** page, do the following:
        * For **Topic ARN**, select the ARN you recorded in the previous step.
        * For **Protocol**, select the type of your receiver.
        * For **Endpoint**, enter the address of your receiver, such as an email address or the ARN of an Amazon SQS queue.
    * Select **Create subscription**

=== "AWS CLI"

    Please refer to [Use Amazon SNS with the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-services-sns.html#cli-subscribe-sns-topic) to add a subscription to this topic.

## Callback Message Format

The solution will send task completion notifications to SNS in the following format, regardless of the API version used in the request:

```json
{
    "id": "task_id", // Task ID
    "result": true, // true for successful completion, false for unsuccessful completion
    "image_url": [ // S3 URLs of generated images, in the format task_id+4_random_digits+image_number. If there are multiple images, all image links will be included.
        "s3://outputbucket/output/test-t2i/test-t2i-abcd-1.png"
    ],
    "output_url": "s3://outputbucket/output/test-t2i/test-t2i-abcd.out", // S3 URL of the task output, containing the complete runtime output
    "context": { // Context content included in the request
        "abc": 123
    }
}
```