# Pipeline (ComfyUI)

!!! info
    This request type is only for ComfyUI runtime.

    This request type only provides the `v1alpha2` API.

ComfyUI provides workflow orchestration. You can design workflows using various nodes on the interface. You can export the workflow to a `json` file.

## Export Workflow

After designing the workflow on the interface, follow these steps to export:
* Select the gear icon on the top right of the menu panel
* Enable `Enable Dev mode Options`
* Select `Save(API Format)` to save the workflow as a file

## Request Format

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-pipeline", // Required, task ID
          "runtime": "sdruntime", // Required, runtime name used
          "tasktype": "pipeline", // Required, task type
          "prefix": "output", // Optional, output file prefix (directory) in S3 bucket
          "context": "" // Optional, can contain any info, included in callback
        },
        "content": {
          ... // Put exported workflow content here
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

## Get Images

After image generation completes, images are stored in the S3 bucket path specified by `output_location`. If `batch_size` or other multi-image parameters are set, each image gets an auto-numbered filename.

Default storage format is lossless PNG, but system auto-detects and adds extensions for special formats like GIF.