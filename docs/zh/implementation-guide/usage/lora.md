# LoRA 精细化调优

LoRA可以直接在Prompt中通过`<lora:[名称]:[版本]>`传入。

## 请求格式
```json
{
    "alwayson_scripts": {
        // 必要，任务类型
        "task": "text-to-image",
        // 必要，任务ID，在上传结果图片和返回响应时会用到
        "id_task": "40521",
        // 必要，基础模型名称，关联队列分发或模型切换
        "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
        // 非必要，用户id
        "uid": "123",
    },
    // 以下皆为官方参数，使用默认值或者直接传入即可
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
