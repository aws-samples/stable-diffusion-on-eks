# Pipeline (ComfyUI)

!!! info
    This request type is only applicable to the ComfyUI runtime.

    This request type only provides the `v1alpha2` API.

ComfyUI provides workflow orchestration capabilities, allowing you to orchestrate workflows using various nodes in the interface and export them to a `json` file.

## Export Workflow

After designing the workflow in the interface, follow these steps to export it:

* Select the gear icon in the top right corner of the menu panel
* Select `Enable Dev mode Options`
* Select `Save(API Format)` to save the workflow as a file.

## Request Format

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-pipeline", // Required, task ID
          "runtime": "sdruntime", // Required, runtime name used by the task
          "tasktype": "pipeline", // Required, task type
          "prefix": "output", // Required, prefix (directory name) for output files in the S3 bucket
          "context": "" // Optional, can contain any information, will be included in the callback
        },
        "content": {
          ... // Insert the exported workflow content here
        }
    }
    }
    ```

## Response Format

=== "v1alpha2"
    ```json
    {
      "id_task": "test-pipeline",
      "runtime": "sdruntime",
      "output_location": "s3://outputbucket/output/test-pipeline"
    }
    ```

## Image Retrieval

After the image generation is complete, the images will be stored in the S3 bucket path specified by `output_location`. If `batch_size` or other parameters for generating multiple images are set, each image will be automatically numbered and stored.

The default storage format is lossless PNG, but if special formats (such as GIF) are involved, the system will automatically recognize and add the appropriate extension.