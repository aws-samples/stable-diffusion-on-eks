# 单图像超分辨率放大 (SD Web UI)

!!! info
    此请求类型仅适用于SD Web UI运行时。

    此请求类型仅提供`v1alpha2` API。

对于单个图片，使用超分辨率模型将图片放大。

## 请求格式

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-extra",
          "runtime": "sdruntime",
          "tasktype": "extra-single-image",
          "prefix": "output",
          "context": ""
        },
        "content": {
          "resize_mode":0,
          "show_extras_results":false,
          "gfpgan_visibility":0,
          "codeformer_visibility":0,
          "codeformer_weight":0,
          "upscaling_resize":4,
          "upscaling_resize_w":512,
          "upscaling_resize_h":512,
          "upscaling_crop":false,
          "upscaler_1":"R-ESRGAN 4x+",
          "upscaler_2":"None",
          "extras_upscaler_2_visibility":0,
          "upscale_first":false,
          "image":"https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png"
        }
      }
    }
    ```


## 响应格式

=== "v1alpha2"
    ```json
    {
      "id_task": "test-extra",
      "runtime": "sdruntime",
      "output_location": "s3://outputbucket/output/test-t2i"
    }
    ```


## 可使用的超分辨率模型

可使用的超分辨率模型与SD Web UI默认的模型一致：

* Lanczos
* Nearest
* 4x-UltraSharp
* ESRGAN_4X
* LDSR
* R-ESRGAN 4x+
* R-ESRGAN 4x+ Anime6B
* ScuNET GAN
* ScuNET PSNR
* SwinIR 4x

如您需要更多超分辨率模型，您可以根据模型类型，将其放入S3存储桶的`LDSR`, `SwinIR`, `ESRGAN`, `RealESRGAN`, `ScuNET`等目录。

完成后，您需要重启Pod才能使新模型生效。

## 图片获取

在图像完成生成后，会存储到 `output_location` 所在的S3存储桶路径中。默认存储格式为无损PNG，但如涉及到特殊格式（如GIF等），系统会自动识别并加扩展名。