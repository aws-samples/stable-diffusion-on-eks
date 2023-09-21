# Stable diffusion on EKS 部署

## 环境需要:

1. 至少一个VPC 的空余
2. 至少3个EIP 的空余


## 安装:

1. 导入notebook-deploy.yml堆栈
2. 按照deploy.ipynb中的说明进行操作.

## 手动配置:
1. config.yaml:配置参考sample/config.yaml,具体配置参数解释可以参考docs/configuration.md
2. down.csv:tools/S3uploader目录下的 down.csv文件,编辑模型下载地址




