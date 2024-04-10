# 镜像构建

您可以从源代码自行构建镜像，并存储在您的镜像仓库中。

!!! danger "运行时选择"
    您需要自行提供Stable Diffusion运行时镜像。您可以从[计划部署](./considerations.md#选择-stable-diffusion-运行时)获取支持的Stable Diffusion运行时。

!!! note "预构建镜像"
    在评估和测试阶段，您可以使用我们预构建的镜像：
    ```
    SD Web UI: public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest
    ComfyUI: public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest
    Queue Agent: public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest
    ```
    请注意，该镜像仅用于技术评估和测试用途，您需要自行负责使用该镜像所带来的许可证风险。

## 构建镜像

运行下方命令以构建`queue-agent`镜像：

```bash
docker build -t queue-agent:latest src/backend/queue_agent/
```
!!! example "示例运行时"

    您可以使用社区提供的[示例 Dockerfile](https://github.com/yubingjiaocn/stable-diffusion-webui-docker) 构建 *Stable Diffusion Web UI* 和 *ComfyUI* 的运行时容器镜像。请注意，该镜像仅用于技术评估和测试用途，请勿将该镜像部署至生产环境。

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

解决方案通过Helm Chart部署。Helm Chart可以存储在任何一个可以通过Internet访问的HTTP服务器上，也可存储在兼容[OCI标准](https://www.opencontainers.org/)的镜像仓库中。您可以将Helm Chart存储在Amazon ECR。

!!! bug "中国区域支持"
    由于CDK框架的[已知问题](https://github.com/aws/aws-cdk/issues/28460)，您无法将Helm Chart存储在中国区域的ECR镜像仓库中。我们正在积极修复此问题。

!!! note "预构建Helm Chart"
    一般情况下，您不需要对Helm Chart内容进行深度自定义。此时您可以直接使用我们预构建的Helm Chart。您可以通过`config.yaml`对运行时进行配置。

===  "使用ECR镜像仓库"
    !!! tip "首次推送"
        Amazon ECR需要在推送前预先创建镜像仓库。
        === "AWS CLI"
            运行下列命令以创建：
            ```bash
            aws ecr create-repository --repository-name sd-on-eks/charts/sd-on-eks
            ```

        === "AWS 管理控制台"
            * 打开位于 https://console.aws.amazon.com/ecr/ 的 Amazon ECR 控制台。
            * 选择**开始使用**。
            * 对于 **Visibility settings**（可见性设置），请选择 **Private**（私密）。
            * 对于 **Repository name**（存储库名称），请输入`sd-on-eks/charts/sd-on-eks`。
            * 选择**创建存储库**。

    运行下列命令以登录到镜像仓库，并推送Helm Chart。请将 `us-east-1` 替换成您的AWS区域，将 `123456789012` 替换为您的 AWS 账户ID:

    ```bash
    helm package src/charts/sd_on_eks
    helm push sd-on-eks-<version>.tgz oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/
    ```

    在上传完成后，您需要修改`config.yaml`，在每个需要使用该Helm Chart的运行时下加入如下内容：

    ```yaml
    modelsRuntime:
    - name: sdruntime
      namespace: default
      type: sdwebui
      chartRepository: "oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/"
      chartVersion: "1.0.0" # 如您自定义Helm Chart的版本，则修改
    ```

===  "使用HTTP服务器"
    !!! tip "访问控制"
        请确保该HTTP服务器向Internet开放，并不设置任何的访问控制（如IP白名单等）。

    运行下列命令以将Helm Chart打包:

    ```bash
    helm package src/charts/sd_on_eks
    ```

    打包完成后，会输出一个名为 `sd-on-eks-<version>.tgz` 的文件。将该文件放入一个空文件夹中，并运行以下命令：

    ```bash
    helm repo index
    ```

    您可以将生成的压缩包和 `index.yaml` 放入HTTP服务器中，假设该HTTP服务器域名为 `example.com` （IP地址也可），您需要修改`config.yaml`，在每个需要使用该Helm Chart的运行时下加入如下内容：

    ```yaml
    modelsRuntime:
    - name: sdruntime
      namespace: default
      type: sdwebui
      chartRepository: "http://example.com/"
      chartVersion: "1.0.0"  # 如您自定义Helm Chart的版本，则修改
    ```