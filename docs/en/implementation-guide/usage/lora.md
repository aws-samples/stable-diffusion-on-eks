# LoRA Fine-Tuning

LoRA can be directly incorporated into the prompt using `<lora:[name]:[version]>`.

## Request Format
```json
{
    "alwayson_scripts": {
        // Required, task type
        "task": "text-to-image",
        // Required, task ID, used for uploading result images and returning responses
        "id_task": "40521",
        // Required, base model name, associated with queue distribution or model switching
        "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
        // Optional, user ID
        "uid": "123",
    },
    // All following are official parameters, use default values or pass them directly
    "prompt": "<lora:LeoArmor:0.9>, Best Quality, 1boy, wear golden LeoArmor, solo, short brown hair, looking at viewer",
    "negative_prompt": "nsfw",
    "sampler_index": "DPM++ SDE Karras",
    "batch_size": 1,
    "steps": 16,
    "cfg_scale": 7,
    "n_iter": 3,
    "width": 512,
    "height": 512,
    "seed": -1
}
```