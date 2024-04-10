# Single Image Super-Resolution Upscaling (SD Web UI)

!!! info
    This request type is only applicable to SD Web UI runtime.

    This request type only provides the `v1alpha2` API.

For a single image, use the super-resolution model to upscale the image.

## Request Format

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


## Response Format

=== "v1alpha2"
    ```json
    {
      "id_task": "test-extra",
      "runtime": "sdruntime",
      "output_location": "s3://outputbucket/output/test-t2i"
    }
    ```


## Available Super-Resolution Models

The available super-resolution models are the same as the default models in SD Web UI:

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

If you need more super-resolution models, you can place them in the `LDSR`, `SwinIR`, `ESRGAN`, `RealESRGAN`, `ScuNET` directories in the S3 bucket according to the model type.

After that, you need to restart the Pod for the new models to take effect.

## Image Retrieval

After the image is generated, it will be stored in the S3 bucket path specified by `output_location`. The default storage format is lossless PNG, but if special formats (such as GIF) are involved, the system will automatically recognize and add the extension.