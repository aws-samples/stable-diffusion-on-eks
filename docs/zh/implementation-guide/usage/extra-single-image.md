# 文生图 (SD Web UI)

!!! info
    此请求类型仅适用于SD Web UI运行时。

Stable Diffusion的最基本用法，输入Prompt，可以生成对应图像。

## 请求格式

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-t2i", // 必要，任务ID
          "runtime": "sdruntime", // 必要，任务使用的运行时名称
          "tasktype": "text-to-image", // 必要，任务类型
          "prefix": "output", // 必要，输出文件在S3桶中的前缀（即目录名）
          "context": "" // 可选，可放置任何信息，会在回调中包含
        },
        "content": { // 与 SD Web UI text-to-image 接口相同规范
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
            "task": "text-to-image", // 必要，任务类型
            "sd_model_checkpoint": "v1-5-pruned-emaonly.safetensors", // 必要，基础模型名称，关联队列分发或模型切换
            "id_task": "test-t2i", // 必要，任务ID，在上传结果图片和返回响应时会用到
            "save_dir": "outputs" // 必要，输出文件在S3桶中的前缀（即目录名）
        },
        // 以下皆为官方参数，使用默认值或者直接传入即可
        "prompt": "A dog",
        "steps": 16,
        "width": 512,
        "height": 512
    }
    ```

## 响应格式

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


## 图片获取

在图像完成生成后，会存储到 `output_location` 所在的S3存储桶路径中。如设置了`batch_size`或其他生成多张图的参数，则每张图会自动编号后存入。

默认存储格式为无损PNG，但如涉及到特殊格式（如GIF等），系统会自动识别并加扩展名。