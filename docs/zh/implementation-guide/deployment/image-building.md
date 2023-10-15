# 镜像构建

您可以从源代码自行构建镜像，并存储在您的镜像仓库中。

!!! danger "运行时选择"
    您需要自行提供Stable Diffusion运行时镜像。您可以从[计划部署](./considerations.md#选择-stable-diffusion-运行时)获取支持的Stable Diffusion运行时。

!!! note "预构建镜像"
    在评估和测试阶段，您可以使用我们预构建的镜像：
    ```
    docker.io/sdoneks/queue-agent:latest
    docker.io/sdoneks/inference-api:latest
    ```
    但由于[DockerHub的限流政策](https://docs.docker.com/docker-hub/download-rate-limit/)，我们建议您将镜像转移至您的ECR镜像仓库中。

## 构建镜像

运行下方命令以构建`queue-agent`镜像：

```bash
docker build -t queue-agent:latest src/backend/queue_agent/
```

### 将镜像推送至Amazon ECR

!!! note "镜像仓库选择"
    我们推荐使用Amazon ECR作为镜像仓库，但您也可以选择其他支持[OCI标准](https://www.opencontainers.org/)的镜像仓库（如Harbor）。

!!! tip "首次推送"
    Amazon ECR需要在推送前预先创建镜像仓库。
    === "AWS CLI"
        运行下列命令以创建：
        ```bash
        aws ecr create-repository --repository-name sd-on-eks/queue-agent
        ```

运行下列命令以登录到镜像仓库，并推送镜像。请将 `us-east-1` 替换成您的AWS区域，将 `123456789012` 替换为您的 AWS 账户ID:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker tag queue-agent:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
```

## 构建并推送Helm Chart

解决方案通过Helm Chart部署。Helm Chart可以存储在兼容[OCI标准](https://www.opencontainers.org/)的镜像仓库中。您可以将Helm Chart存储在Amazon ECR。

!!! note "预构建Helm Chart"
    一般情况下，您不需要对Helm Chart内容进行深度自定义。此时您可以直接使用我们预构建的Helm Chart。您可以通过`config.yaml`对运行时进行配置。

!!! tip "首次推送"
    Amazon ECR需要在推送前预先创建镜像仓库。
    === "AWS CLI"
        运行下列命令以创建：
        ```bash
        aws ecr create-repository --repository-name sd-on-eks/charts/sd-on-eks
        ```

运行下列命令以登录到镜像仓库，并推送Helm Chart。请将 `us-east-1` 替换成您的AWS区域，将 `123456789012` 替换为您的 AWS 账户ID:

```bash
helm package src/charts/sd_on_eks
helm push sd-on-eks-<version>.tgz oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/
```