# SD on EKS 正式版改动和测试

## 主要改动
* 支持ComfyUI，并提供ComfyUI运行时
* API版本化，改为按运行时名称路由，移除动态运行时（DynamicRuntime）
* Queue Agent重构
* 移除EFS存储，改为S3 Mountpoint以提升读取速度
* 部署脚本重构，支持一键部署
* 压测脚本重构
* EKS 版本更新到 1.28

## 镜像地址
* SD Web UI: `public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest`
* ComfyUI: `public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest`
* Queue Agent: `public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest`
* Helm Chart: `oci://public.ecr.aws/bingjiao/charts/sd-on-eks:1.0.0`

## API 格式和地址

### `v1alpha1`版本（传统SD Web UI版本）

**Endpoint:** `POST <API Endpoint>/v1alpha1`

**API 样例: **
  * 文生图：`test/v1alpha1/t2i.json`
  * 图生图：`test/v1alpha1/i2i.json`

详细定义可参见 `docs/api/v1alpha1.yaml`，或现有文档。

### `v1alpha2`版本（新版本）

**Endpoint:** `POST <API Endpoint>/v1alpha2`

**新版本主要改动：**
* 将任务元数据与任务本体分开
* 支持ComfyUI的Pipeline格式
* 支持透传Context，方便传递业务信息

**格式样例：**

```json
{
  "task": {
    "metadata": {
      "id": "test-t2i", // 任务ID
      "runtime": "sdwebui", // 目标运行时名称，应和config.yaml设置的名称一致（区分大小写）
      "tasktype": "text-to-image", //对SD Web UI，支持text-to-image和image-to-image；对ComfyUI只支持pipeline
      "prefix": "output", // 生成内容存储到S3的路径前缀
      "context": "" // 需要包含在返回中的业务信息
    },
    "content": { // 标准SD Web UI或ComfyUI格式
      "alwayson_scripts": {},
      "prompt": "A dog",
      "steps": 16,
      "width": 512,
      "height": 512
    }
  }
}
```

**API 样例: **
  * 文生图：`test/v1alpha2/t2i.json`
  * 图生图：`test/v1alpha2/i2i.json`
  * Pipeline：`test/v1alpha2/pipeline.json`

详细定义可参见 `docs/api/v1alpha1.yaml`，或现有文档。

## 部署和测试

### 一键部署

在`/deploy`文件夹中提供一键部署脚本，该脚本会完成以下任务：
* 安装所需工具（kubectl, helm, node.js, CDK CLI）
* 创建S3存储桶用于存储模型，获取SD 1.5基础模型并上传至S3存储桶
* 创建EBS镜像缓存以加快启动速度
* 根据配置模板自动生成配置文件，并调用CDK部署

我已经根据目前的镜像地址修改了配置模板，可使用脚本直接部署：
```bash
deploy/deploy.sh
```

### 一键测试

部署完成后，可使用`/test`目录下的脚本进行不同API版本，不同场景的测试：
  * 对SD Web UI，会进行文生图和图生图场景的测试。
  * 对ComfyUI，会进行Pipeline场景的测试。

注意，在切换场景时，需要修改`run.sh`中的`RUNTIME_TYPE`变量，或设置`RUNTIME_TYPE`环境变量为`sdwebui`或`comfyui`。

API Endpoint和API Key会自动从CloudFormation中获取。

如需运行测试，运行该脚本：
```bash
test/run.sh
```
