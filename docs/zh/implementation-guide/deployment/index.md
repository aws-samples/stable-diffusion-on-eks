# 概览

在部署解决方案之前，建议您先查看本指南中有关架构图和区域支持等信息，然后按照下面的说明配置解决方案并将其部署到您的账户中。

## 前提条件
根据[计划部署](./considerations.md)文档检查所有的考虑因素是否满足。

## 部署步骤

我们提供了一键部署脚本以快速开始。总部署时间约为 30 分钟。

### 获取源代码

运行以下命令以获取源代码和部署脚本：

```bash
git clone --recursive https://github.com/aws-samples/stable-diffusion-on-eks
cd stable-diffusion-on-eks
```

### 一键部署

运行以下命令以使用最简设置快速部署：

```bash
cd deploy
./deploy.sh --deploy
```

该脚本将：

* 安装必要的运行时和工具
* 创建S3存储桶，从[HuggingFace](https://huggingface.co/runwayml/stable-diffusion-v1-5)中下载Stable Diffusion 1.5的基础模型，放置在存储桶中
* 使用我们提供的示例镜像，创建包含SD Web UI镜像的EBS快照
* 创建一个含SD Web UI运行时的Stable Diffusion解决方案

### 部署参数

该脚本提供一些参数，以便您自定义部署的解决方案：

* `-h, --help`: 显示帮助信息
* `-n, --stack-name`: 自定义部署的解决方案名称，影响生成的资源命名。默认为`sdoneks`.
* `-R, --region`: 解决方案部署到的区域。默认为当前AWS配置文件所在区域。
* `-d, --dry-run`: 仅生成配置文件，不执行部署。
* `-b, --bucket`: 指定保存模型的现有S3桶名称，该S3桶必须已存在，且与解决方案在相同区域。您可以根据[此文档](./models.md)手动创建S3存储桶。
* `-s, --snapshot`: 指定现有的EBS快照ID。您可以根据[此文档](./ebs-snapshot.md)自行构建EBS快照。
* `-r, --runtime-name`: 指定部署的运行时名称，影响API调用时使用的名称。默认为`sdruntime`。
* `-t, --runtime-type`: 指定部署的运行时类型，只接受`sdwebui`和`comfyui`。默认为`sdwebui`。

如您需要部署多个运行时，或有其他参数需求（如自定义镜像），您可先使用`--dry-run`参数，使用脚本生成基础配置文件后再行修改。

## 手动部署

您也可以不适用脚本，使用以下步骤手动在 AWS 上部署此解决方案。

1. [创建 Amazon S3 模型存储桶](./models.md)，并将所需要的模型存储到桶中
2. *（可选）* [构建容器镜像](./image-building.md)
3. *（可选）* [将容器镜像存储到EBS缓存中以加速启动](./ebs-snapshot.md)
4. [部署并启动解决方案堆栈](./deploy.md)
