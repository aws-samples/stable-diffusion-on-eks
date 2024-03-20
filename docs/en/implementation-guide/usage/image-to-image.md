# Image-to-Image (SD Web UI)

!!! info
    This request type is only applicable to the SD Web UI runtime.

The basic usage of Stable Diffusion is to input a prompt and a reference image, and it can generate an image similar to the reference image.

## Request Format

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-i2i", // Required, task ID
          "runtime": "sdruntime", // Required, runtime name used for the task
          "tasktype": "image-to-image", // Required, task type
          "prefix": "output", // Optional, prefix (directory name) for output files in the S3 bucket
          "context": "" // Optional, can include any information, will be included in the callback
        },
        "content": { // Same specification as the SD Web UI image-to-image interface
          "alwayson_scripts": {
            "image_link": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png" // Place the image link here, the image will be downloaded, base64 encoded, and stored in the image parameter
          },
          "prompt": "cat wizard, gandalf, lord of the rings, detailed, fantasy, cute, adorable, Pixar, Disney, 8k",
          "steps": 16,
          "width": 512,
          "height": 512
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
            "id_task": "test-i2i", // Required, task ID, will be used when uploading the result image and returning the response
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

## Getting the Image

After the image is generated, it will be stored in the S3 bucket path specified by `output_location`. If `batch_size` or other parameters for generating multiple images are set, each image will be automatically numbered and stored.

The default storage format is lossless PNG, but if special formats (such as GIF) are involved, the system will automatically recognize and add the extension.