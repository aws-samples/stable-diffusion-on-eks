# Image-to-Image (SD Web UI)

!!! info
    This request type is only applicable to the SD Web UI runtime.

The basic usage of Stable Diffusion is to input a prompt and a reference image, and it can generate an image similar to the reference image.

The content in the request will be passed directly to the SD Web UI, but if there are links (HTTP or S3 URL), the content of the links will be converted to base64 encoded content and filled in the corresponding items.

## Request Format

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-i2i", // Required, task ID
          "runtime": "sdruntime", // Required, runtime name used by the task
          "tasktype": "image-to-image", // Required, task type
          "prefix": "output", // Required, prefix (directory name) of output files in the S3 bucket
          "context": "" // Optional, can contain any information, will be included in the callback
        },
        "content": { // Same specification as the SD Web UI image-to-image interface
          "alwayson_scripts": {},
          "prompt": "cat wizard, gandalf, lord of the rings, detailed, fantasy, cute, adorable, Pixar, Disney, 8k",
          "steps": 16,
          "width": 512,
          "height": 512,
          "init_images": ["https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png"] // Place image links here, images will be downloaded, base64 encoded and put into the request
        }
      }
    }
    ```

=== "v1alpha1"
    ```json
    {
        "alwayson_scripts": {
            "task": "image-to-image", // Required, task type
            "image_link": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png", // Required, URL of the input image
            "id_task": "test-i2i", // Required, task ID, will be used when uploading result images and returning responses
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors", // Required, base model name, associated with queue distribution or model switching
        },
        // The following are official parameters, use the default values or pass them in directly
        "prompt": "cat wizard, gandalf, lord of the rings, detailed, fantasy, cute, adorable, Pixar, Disney, 8k",
        "steps": 16,
        "width": 512,
        "height": 512
    }
    ```

## Response Format

=== "v1alpha2"
    ```json
    {
      "id_task": "test-i2i",
      "runtime": "sdruntime",
      "output_location": "s3://outputbucket/output/test-t2i"
    }
    ```

=== "v1alpha1"
    ```json
    {
      "id_task": "test-i2i",
      "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
      "output_location": "s3://outputbucket/output/test-t2i"
    }
    ```

## Model Switching

If the corresponding runtime has `dynamicModel: true` set, you need to add the following content to the `alwayson_scripts` in the request:

```json
        "content": {
          "alwayson_scripts": {
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors" //Place the model name here
          },
        }
```

After receiving the request, the SD Web UI will unload the current model and load the corresponding model from memory/S3 bucket. If the specified model does not exist, the request will return an error directly.

## Image Retrieval

After the image generation is completed, it will be stored in the S3 bucket path specified by `output_location`. If `batch_size` or other parameters for generating multiple images are set, each image will be automatically numbered and stored.

The default storage format is lossless PNG, but if special formats (such as GIF) are involved, the system will automatically recognize and add the extension.