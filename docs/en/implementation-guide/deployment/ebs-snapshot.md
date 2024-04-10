# Image Cache Build

By pre-caching container images as EBS snapshots, you can optimize the startup speed of compute instances. When launching a new instance, the instance's data volume comes with a container image cache, eliminating the need to pull from the image repository again.

Create the EBS snapshot before deploying the solution. We provide a script for building the EBS snapshot.

===  "Using Custom Image"
    If you build and push the image to Amazon ECR yourself, run the following command. Replace `us-east-1` with the region where the solution is located, and replace `123456789012` with your 12-digit AWS account:

    ```bash
    cd utils/bottlerocket-images-cache
    ./snapshot.sh 123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/sdwebui:latest,123456789012.dkr.ecr.us-east-1.amazonaws.com/sd-on-eks/queue-agent:latest
    ```

=== "Using Pre-built Image"
    If you use the pre-built image provided by the solution, run the following command:

    ```bash
    cd utils/bottlerocket-images-cache
    ./snapshot.sh public.ecr.aws/bingjiao/sd-on-eks/sdwebui:latest,public.ecr.aws/bingjiao/sd-on-eks/comfyui:latest,public.ecr.aws/bingjiao/sd-on-eks/queue-agent:latest
    ```

After the script completes, it will output the EBS snapshot ID (in the format similar to `snap-0123456789`). You can apply this snapshot when deploying.

For more details about this script, please refer to the [GitHub repository](https://github.com/aws-samples/bottlerocket-images-cache)