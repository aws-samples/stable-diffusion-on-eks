# Model Storage

The models required for this solution should be pre-stored in an S3 bucket.

## Create a Bucket

Please follow these steps to create a bucket:

=== "AWS Management Console"
    * Open the [Amazon S3 console](https://console.aws.amazon.com/s3/).
    * In the left navigation pane, choose **Buckets**.
    * Choose **Create Bucket**.
    * In **Bucket name**, enter a name for your bucket. The name must follow the [bucket naming rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html).
    * In **AWS Region**, choose the same region where you plan to deploy the solution.
    !!! warning "Note"
        Make sure the bucket is in the same AWS Region as your solution deployment. If you plan to deploy multiple copies of the solution across multiple regions, create a separate bucket in each region.
    * Choose **Create Bucket**.

=== "AWS CLI"
    Run the following command to create a bucket. Replace `<bucket name>` with the name you want to use for your bucket, and `us-east-1` with the AWS Region where you plan to deploy the solution:
    ```bash
    aws s3api create-bucket --bucket <bucket name> --region us-east-1
    ```

## Store Models

Please store all the models you need to use in the S3 bucket, with the following directory structure:

```
└── /
    ├── CLIP
    ├── Codeformer
    ├── ControlNet
    ├── ESRGAN
    ├── GFPGAN
    ├── LDSR
    ├── Lora
    ├── RealESRGAN
    ├── ScuNET
    ├── Stable-diffusion
    ├── SwinIR
    ├── VAE
    ├── VAE-approx
    ├── embeddings
    └── hypernetworks
```

Please place the models in their corresponding directories. The `Stable-diffusion` directory must exist and contain the Stable Diffusion model. Other directories can be omitted if there are no models for them.

Currently, models in `.safetensors` and `.ckpt` formats are supported. If the models you downloaded from [Civitai](https://civitai.com/) do not have an extension, please add the `.ckpt` extension.

Please follow these steps to upload the models to the S3 bucket:

=== "AWS Management Console"
    !!! warning "Note"
        When uploading model files from mainland China to overseas, you may encounter slow upload speeds or connection interruptions. Since browser uploads do not support resuming from interruptions, it is not recommended to use the management console to upload models.
    * Open the [Amazon S3 console](https://console.aws.amazon.com/s3/).
    * In the left navigation pane, choose **Buckets**.
    * Select the bucket you created in the previous step, and navigate to the desired folder.
    * If the corresponding folder does not exist:
        * Choose **Create Folder**.
        * In **Folder Name**, enter the folder name.
        * Choose **Create folder**.
        * Repeat the above steps until the folder structure matches the one above.
    * Choose **Upload**.
    * Choose **Add files**, and select the model files you want to upload.
    * Choose **Upload**. Do not close the browser during the upload process.

=== "AWS CLI"
    Run the following command to upload the model files to the bucket. Replace `<model name>` with the name of your model file, `<folder>` with the model type, and `<bucket name>` with the name of your bucket:
    ```bash
    aws s3 cp <model name> s3://<bucket name>/<folder>/
    ```
    !!! note "Tip"
        When using the AWS CLI for uploading, you do not need to create the directory structure beforehand.

    !!! note "Tip"
        You can use third-party tools like [s5cmd](https://github.com/peak/s5cmd) to improve upload speed.