# Text-to-Image (SD Web UI)

!!! info
    This request type is only applicable to SD Web UI runtime.

The most basic usage of Stable Diffusion is to input a prompt and generate a corresponding image.

The content in the request will be passed directly to SD Web UI, but if there are links (HTTP or S3 URL), the content of the links will be converted to base64 encoded content and filled in the corresponding fields.

## Request Format

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-t2i", // Required, task ID
          "runtime": "sdruntime", // Required, runtime name used for the task
          "tasktype": "text-to-image", // Required, task type
          "prefix": "output", // Required, prefix (directory name) of output files in S3 bucket
          "context": "" // Optional, can contain any information, will be included in the callback
        },
        "content": { // Same specification as SD Web UI text-to-image interface
          "alwayson_scripts": {},
          "prompt": "A dog",
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
            "task": "text-to-image", // Required, task type
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors", // Required, base model name, associated with queue distribution or model switching
            "id_task": "test-t2i", // Required, task ID, will be used when uploading result images and returning responses
            "save_dir": "outputs" // Required, prefix (directory name) of output files in S3 bucket
        },
        // The following are official parameters, use default values or pass them directly
        "prompt": "A dog",
        "steps": 16,
        "width": 512,
        "height": 512
    }
    ```

## Response Format

=== "v1alpha2"
    ```json
    {
      "id_task": "test-t2i",
      "runtime": "sdruntime",
      "output_location": "s3://outputbucket/output/test-t2i"
    }
    ```

=== "v1alpha1"
    ```json
    {
      "id_task": "test-t2i",
      "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
      "output_location": "s3://outputbucket/output/test-t2i"
    }
    ```

## Model Switching

If the corresponding runtime has `dynamicModel: true` set, you need to add the following content in the `alwayson_scripts` of the request:

```json
        "content": {
          "alwayson_scripts": {
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors" //Put the model name here
          },
        }
```

After receiving the request, SD Web UI will unload the current model and load the corresponding model from memory/S3 bucket. If the specified model does not exist, the request will directly return an error.

## Image Retrieval

After the image generation is completed, it will be stored in the S3 bucket path specified by `output_location`. If `batch_size` or other parameters for generating multiple images are set, each image will be automatically numbered and stored.

The default storage format is lossless PNG, but if special formats (such as GIF) are involved, the system will automatically recognize and add the extension.