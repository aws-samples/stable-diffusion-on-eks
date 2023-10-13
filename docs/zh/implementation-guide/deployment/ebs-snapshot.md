# 镜像缓存构建

通过将容器镜像预缓存为 EBS 快照，可以优化计算实例的启动速度。启动新实例时，实例的数据卷自带容器镜像缓存，从而无需从镜像仓库中再行拉取。

应在部署解决方案前创建 EBS 快照。我们提供了用于构建 EBS 快照的脚本。

===  "使用自定义镜像"
    如您在[步骤2](./image-building.md)自行构建镜像并推送到Amazon ECR，则运行下列命令。将 `us-east-1`替换成解决方案所在区域，将 `123456789012` 替换为您的12位AWS账号:

    ```bash
    cd utils/bottlerocket-images-cache
    ./snapshot.sh 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/inference-api:latest,123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
    ```

=== "使用预构建镜像"
    如您使用解决方案自带的镜像，则运行下列命令：

    ```bash
    cd utils/bottlerocket-images-cache
    ./snapshot.sh docker.io/sdoneks/inference-api:latest,docker.io/sdoneks/queue-agent:latest
    ```

脚本运行完成后，会输出EBS快照ID（格式类似于`snap-0123456789`）。您可以在[配置运行时](./deploy.md#设置基于-ebs-快照的镜像缓存可选)中应用该快照。

有关该脚本的详细信息，请参考[GitHub仓库](https://github.com/aws-samples/bottlerocket-images-cache)