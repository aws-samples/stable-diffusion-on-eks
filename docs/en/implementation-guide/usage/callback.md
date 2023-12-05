# Callbacks and Notifications

The Stable Diffusion on Amazon EKS solution operates in an asynchronous inference mode. When an image is generated or an error occurs, the user is notified through Amazon SNS. User applications can subscribe to the SNS Topic to receive notifications when image generation is complete.

Refer to the SNS documentation to understand the types of backends supported by SNS.

You can find the generated SNS Topic in the CloudFormation output.