# ControlNet Plugin

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
        // Optional, ControlNet parameters
        "controlnet": {
            "args": [
                {
                    "image_link": "https://tse3-mm.cn.bing.net/th/id/OIP-C.2Z9l9li7mrfDThPW3_LE5wHaLG?pid=ImgDet&rs=1",
                    "module": "openpose",
                    "model": "control_v11p_sd15_openpose",
                    "enabled": true,
                    "weight": 1,
                    "resize_mode": "Crop and Resize"
                },
                {
                    "image_link": "https://tse3-mm.cn.bing.net/th/id/OIP-C.2Z9l9li7mrfDThPW3_LE5wHaLG?pid=ImgDet&rs=1",
                    "module": "depth_leres",
                    "model": "control_v11f1p_sd15_depth",
                    "enabled": true,
                    "weight": 0.8,
                    "resize_mode": "Crop and Resize"
                }
            ]
        }
    },
    // All following are official parameters, use default values or pass them directly
    "prompt": "Best Quality, 1boy, wear golden LeoArmor, solo, short brown hair, looking at viewer",
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