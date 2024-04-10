# Image Building

You can build images from source code and store them in your image repository.

!!! danger "Runtime Selection"
    You need to provide the Stable Diffusion runtime image yourself. You can get the supported Stable Diffusion runtimes from [Deployment Considerations](./considerations.md#choose-stable-diffusion-runtime).

!!! note "Pre-built Images"
    For evaluation and testing purposes, you can use our pre-built images:
    ```
    SD Web UI: public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest
    ComfyUI: public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest
    Queue Agent: public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest
    ```
    Please note that these images are for technical evaluation and testing purposes only, and you are responsible for any licensing risks associated with using these images.

## Build Images

Run the following command to build the `queue-agent` image:

```bash
docker build -t queue-agent:latest src/backend/queue_agent/
```
!!! example "Example Runtimes"

    You can use the [example Dockerfile](https://github.com/yubingjiaocn/stable-diffusion-webui-docker) provided by the community to build the runtime container images for *Stable Diffusion Web UI* and *ComfyUI*. Please note that these images are for technical evaluation and testing purposes only and should not be deployed to production environments.

### Push Images to Amazon ECR

!!! note "Image Repository Selection"
    We recommend using Amazon ECR as the image repository, but you can also choose other repositories that support the [OCI standard](https://www.opencontainers.org/), such as Harbor.

!!! tip "First-time Push"
    Amazon ECR requires creating the image repository before pushing.
    === "AWS CLI"
        Run the following command to create:
        ```bash
        aws ecr create-repository --repository-name sd-on-eks/queue-agent
        ```

Run the following commands to log in to the image repository and push the image. Replace `us-east-1` with your AWS region, and `123456789012` with your AWS account ID:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker tag queue-agent:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
```

## Build and Push Helm Chart

The solution is deployed via a Helm Chart. The Helm Chart can be stored on any HTTP server accessible over the Internet or in an image repository compatible with the [OCI standard](https://www.opencontainers.org/). You can store the Helm Chart in Amazon ECR.

!!! bug "China Region Support"
    Due to a [known issue](https://github.com/aws/aws-cdk/issues/28460) with the CDK framework, you cannot store the Helm Chart in an ECR image repository in the China regions. We are actively working on fixing this issue.

!!! note "Pre-built Helm Chart"
    In general, you do not need to deeply customize the contents of the Helm Chart. In this case, you can directly use our pre-built Helm Chart. You can configure the runtime via `config.yaml`.

===  "Using ECR Image Repository"
    !!! tip "First-time Push"
        Amazon ECR requires creating the image repository before pushing.
        === "AWS CLI"
            Run the following command to create:
            ```bash
            aws ecr create-repository --repository-name sd-on-eks/charts/sd-on-eks
            ```

        === "AWS Management Console"
            * Open the Amazon ECR console at https://console.aws.amazon.com/ecr/.
            * Choose **Get started**.
            * For **Visibility settings**, choose **Private**.
            * For **Repository name**, enter `sd-on-eks/charts/sd-on-eks`.
            * Choose **Create repository**.

    Run the following commands to log in to the image repository and push the Helm Chart. Replace `us-east-1` with your AWS region, and `123456789012` with your AWS account ID:

    ```bash
    helm package src/charts/sd_on_eks
    helm push sd-on-eks-<version>.tgz oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/
    ```

    After the upload is complete, you need to modify `config.yaml` and add the following content under each runtime that needs to use this Helm Chart:

    ```yaml
    modelsRuntime:
    - name: sdruntime
      namespace: default
      type: sdwebui
      chartRepository: "oci://123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/charts/"
      chartVersion: "1.0.0" # Modify if you customize the Helm Chart version
    ```

===  "Using HTTP Server"
    !!! tip "Access Control"
        Make sure the HTTP server is open to the Internet and does not have any access control (such as IP whitelisting) set up.

    Run the following command to package the Helm Chart:

    ```bash
    helm package src/charts/sd_on_eks
    ```

    After packaging, a file named `sd-on-eks-<version>.tgz` will be output. Place this file in an empty folder and run the following command:

    ```bash
    helm repo index
    ```

    You can place the generated archive and `index.yaml` on the HTTP server. Assuming the domain name of the HTTP server is `example.com` (IP address is also acceptable), you need to modify `config.yaml` and add the following content under each runtime that needs to use this Helm Chart:

    ```yaml
    modelsRuntime:
    - name: sdruntime
      namespace: default
      type: sdwebui
      chartRepository: "http://example.com/"
      chartVersion: "1.0.0" # Modify if you customize the Helm Chart version
    ```