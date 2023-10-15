# 图生图

Stable Diffusion的基本用法，输入Prompt和参考图像，可以生成与参考图像类似的图像。

## 请求格式

```json
{
    "alwayson_scripts": {
        // 必要，任务类型
        "task": "image-to-image",
        // 必要，输入图片的url
        "image_link": "https://www.segmind.com/sd-img2img-input.jpeg",
        // 必要，任务ID，在上传结果图片和返回响应时会用到
        "id_task": "31311",
        // 必要，基础模型名称，关联队列分发或模型切换
        "sd_model_checkpoint": "revAnimated_v122.safetensors",
        // 非必要，用户id
        "uid": "456"
    },
    // 以下皆为官方参数，使用默认值或者直接传入即可
    "prompt": "A fantasy landscape, trending on artstation, mystical sky",
    "steps": 16,
    "width": 512,
    "height": 512
}
```

## 响应格式

```json
{
  "id_task": "123",
  "task": "image-to-image",
  "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors",
  "output_location": "s3://sdoneks-pdxstack-outputs3bucket9fe85b9f-s6khzv238u4a/123"
}
```

## 图片获取

在图像完成生成后，会存储到 `output_location` 所在的S3存储桶路径中。