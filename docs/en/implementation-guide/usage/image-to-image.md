# Image-to-Image

The basic usage of Stable Diffusion involves providing a prompt and a reference image to generate an image similar to the reference.

## Request Format

```json
{
    "alwayson_scripts": {
        // Required, task type
        "task": "image-to-image",
        // Required, URL of the input image
        "image_link": "https://www.segmind.com/sd-img2img-input.jpeg",
        // Required, task ID, used for uploading result images and returning responses
        "id_task": "31311",
        // Required, base model name, associated with queue distribution or model switching
        "sd_model_checkpoint": "revAnimated_v122.safetensors",
        // Optional, user ID
        "uid": "456"
    },
    // All following are official parameters, use default values or pass them directly
    "prompt": "A fantasy landscape, trending on artstation, mystical sky",
    "steps": 16,
    "width": 512,
    "height": 512
}
```

## Response Format

```json
{
  "id_task": "123",
  "task": "image-to-image",
  "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
  "output_location": "s3://sdoneks-pdxstack-outputs3bucket9fe85b9f-s6khzv238u4a/123"
}
```

## Image Retrieval

After the image is generated, it will be stored in the S3 bucket path specified by `output_location`.