# Pipeline (ComfyUI)

!!! info
    此请求类型仅适用于ComfyUI运行时。

    此请求类型仅提供`v1alpha2` API。

ComfyUI提供工作流编排功能，可以在界面上使用多种节点编排工作流，并导出至`json`文件。

## 导出工作流

在界面上设计完成工作流后，进行以下操作以导出工作流：
* 选择菜单面板右上角的齿轮图标
* 选择开启 `Enable Dev mode Options`
* 选择 `Save(API Format)`，将工作流保存为文件。

## 请求格式

=== "v1alpha2"
    ```json
    {
      "task": {
        "metadata": {
          "id": "test-pipeline", // 必要，任务ID
          "runtime": "sdruntime", // 必要，任务使用的运行时名称
          "tasktype": "pipeline", // 必要，任务类型
          "prefix": "output", // 可选，输出文件在S3桶中的前缀（即目录名）
          "context": "" // 可选，可放置任何信息，会在回调中包含
        },
        "content": {
          ... // 此处放入之前导出的工作流内容
        }
      }
    }
    ```

## 响应格式

=== "v1alpha2"
    ```json
    {
      "id_task": "test-pipeline",
      "runtime": "sdruntime",
      "output_location": "s3://outputbucket/output/test-pipeline"
    }
    ```

## 图片获取

在图像完成生成后，会存储到 `output_location` 所在的S3存储桶路径中。如设置了`batch_size`或其他生成多张图的参数，则每张图会自动编号后存入。

默认存储格式为无损PNG，但如涉及到特殊格式（如GIF等），系统会自动识别并加扩展名。