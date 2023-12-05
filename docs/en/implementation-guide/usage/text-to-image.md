# Text-to-Image

The most basic usage of Stable Diffusion involves providing a prompt to generate a corresponding image.

## Request Format

```json
{
    "alwayson_scripts": {
        // Required, task type
        "task": "text-to-image",
        // Required, base model name, associated with queue distribution or model switching
        "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
        // Required, task ID, used for uploading result images and returning responses
        "id_task": "21123",
        "uid": "456",
        "save_dir": "outputs"
    },
    // All following are official parameters, use default values or pass them directly
    "prompt": "A dog",
    "steps": 16,
    "width": 512,
    "height": 512
}
```

## Response Format

```json
{
  "id_task": "123",
  "task": "text-to-image",
  "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
  "output_location": "s3://sdoneks-pdxstack-outputs3bucket9fe85b9f-s6khzv238u4a/123"
}
```

## Image Retrieval

After the image is generated, it will be stored in the S3 bucket path specified by `output_location`.