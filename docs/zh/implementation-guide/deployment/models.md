# 步骤1：模型存储

该解决方案所需要的模型应提前存储在S3存储桶中。

## 创建存储桶

请按以下步骤创建存储桶：

=== "AWS 管理控制台"
    * 打开 [Amazon S3 控制台](https://console.aws.amazon.com/s3/)。
    * 在左侧导航窗格中，选择 **Buckets**（桶）。
    * 选择 **Create Bucket**（创建桶）。
    * 在 **Bucket name**（桶名称）中输入存储桶的名称。名称需符合[存储桶命名规则](https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/bucketnamingrules.html)。
    * 在 **AWS Region** （AWS 区域）中，选择您准备部署解决方案的相同区域。
    !!! warning "注意"
        请确保该存储桶与您的解决方案部署在同一个 AWS 区域。如您希望在多个区域部署解决方案的多个副本，请在每个区域单独创建一个存储桶。
    * 选择 **Create Bucket**（创建桶）

=== "AWS CLI"
    * 运行以下命令以创建存储桶。将`<bucket name>`替换为您希望的存储桶名称，`us-east-1`替换成您准备部署解决方案的 AWS 区域：
    ```bash
    aws s3api create-bucket --bucket <bucket name> --region us-east-1
    ```

## 存储模型

请将所有需要使用的模型存储在S3存储桶中，目录格式如下：

```
└── models/
    ├── stable-diffusions
    ├── controlnet
    └── lora
```

请将模型放入对应的目录中。目前支持 `.safetensors` 和 `.ckpt` 格式。如您从[Civitai](https://civitai.com/)下载的模型不带扩展名，请添加 `.ckpt` 扩展名。

请按以下步骤将模型上传至S3存储桶中：

=== "AWS 管理控制台"
    !!! warning "注意"
        从中国大陆向海外上传模型文件时，可能会遇到模型上传缓慢或连接中途断开的情况。由于浏览器上传不支持断点续传，故不推荐使用管理控制台上传模型。
    * 打开 [Amazon S3 控制台](https://console.aws.amazon.com/s3/)。
    * 在左侧导航窗格中，选择 **Buckets**（桶）。
    * 选择上一步创建的存储桶，并进入所需的文件夹。
    * 如果是首次上传：
      * 选择 **Create Folder**（创建文件夹）
      * 在 **Folder Name**（文件夹名称）中，输入 *models*
      * 选择 **Create folder**（创建文件夹）
      * 重复以上操作，直到文件夹符合以上目录结构。
    * 选择 **Upload**（上传）
    * 选择 **Add files** （添加文件），选择待上传的模型文件。
    * 选择 **Upload**。在上传过程中请不要关闭浏览器。


=== "AWS CLI"
    * 运行以下命令以将模型文件上传至存储桶。将`<model name>`替换成为您的模型文件名，`<bucket name>`替换为您希望的存储桶名称：
    ```bash
    aws s3 cp <model name> s3://<bucket name>/models/stable-diffusion/
    ```
    !!! note "提示"
        采用AWS CLI上传时，无需预先创建目录结构。

    !!! note "提示"
        您可以使用[s5cmd](https://github.com/peak/s5cmd)等第三方工具提升上传速度。
