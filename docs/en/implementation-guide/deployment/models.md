# Create S3 bucket and store model

Models should be stored in S3 bucket. Stable diffusion runtime will fetch model from S3 bucket at launch.

Create S3 bucket by running the following command. Replace `<bucket name>` to your desired bucket name.

```bash
aws s3api create-bucket --bucket <bucket name> --region us-east-1
```

You can upload model to newly created S3 bucket by running the following command:

```bash
aws s3 cp <model name> s3://<bucket name>/models/stable-diffusion/
```
