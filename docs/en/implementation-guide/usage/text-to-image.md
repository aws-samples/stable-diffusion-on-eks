# Text-to-Image (SD Web UI)

!!! info
    This request type is only applicable to the SD Web UI runtime.

The most basic usage of Stable Diffusion is to input a prompt and generate a corresponding image.

## Request Format

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-t2i", // Required, task ID
          "runtime": "sdruntime", // Required, runtime name used for the task
          "tasktype": "text-to-image", // Required, task type
          "prefix": "output", // Optional, prefix (directory name) for output files in the S3 bucket
          "context": "" // Optional, can include any information, will be included in the callback
        },
        "content": { // Same specification as the SD Web UI text-to-image interface
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
            "save_dir": "outputs" // Required, prefix (directory name) for output files in the S3 bucket
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

## Image Retrieval

After the image generation is complete, it will be stored in the S3 bucket path specified by `output_location`. If `batch_size` or other parameters for generating multiple images are set, each image will be automatically numbered and stored.

The default storage format is lossless PNG, but if special formats (such as GIF) are involved, the system will automatically recognize and add the extension.