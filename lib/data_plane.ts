import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { ClusterAddOn, ClusterInfo }  from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as eks from "aws-cdk-lib/aws-eks";
import * as sns from 'aws-cdk-lib/aws-sns';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as path from 'path';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as iam from 'aws-cdk-lib/aws-iam';
import SDRuntimeAddon, { SDRuntimeAddOnProps } from './runtime';
import nvidiaDevicePluginAddon, { SNSResourceProvider } from './utils'

export interface SharedComponentAddOnProps {
  modelstorageEfs: efs.IFileSystem;
  inputSns: sns.ITopic;
  outputSns: sns.ITopic;
  outputBucket: s3.IBucket;
}

export class SharedComponentAddOn implements ClusterAddOn {
  readonly options: SharedComponentAddOnProps;

  constructor(props: SharedComponentAddOnProps) {
    this.options = props
  }

  deploy(clusterInfo: ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster;

    const lambdaFunction = new lambda.Function(cluster.stack, 'InputLambda', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../src/lambda')),
      handler: 'app.lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_9,
      environment: {
        "SNS_TOPIC_ARN": this.options.inputSns.topicArn,
        "S3_OUTPUT_BUCKET": this.options.outputBucket.bucketName
      }
    });

    this.options.inputSns.grantPublish(lambdaFunction);

    const api = new apigw.LambdaRestApi(cluster.stack, 'FrontApi', {
      handler: lambdaFunction,
      proxy: true
    });

    api.node.addDependency(lambdaFunction);

    const sc = cluster.addManifest("efs-model-storage-sc", {
      "kind": "StorageClass",
      "apiVersion": "storage.k8s.io/v1",
      "metadata": {
        "name": "efs-model-storage-sc"
      },
      "provisioner": "efs.csi.aws.com",
      "parameters": {
        "provisioningMode": "efs-ap",
        "fileSystemId": this.options.modelstorageEfs.fileSystemId,
        "directoryPerms": "777",
        "subPathPattern": "",
        "ensureUniqueDirectory": "false"
      }
    })
    return Promise.resolve(api);
  }
}

export default class DataPlaneStack {
  cluster: eks.ICluster;
  outputSns: sns.Topic
  inputSns: sns.Topic
  outputBucket: s3.Bucket

  constructor(scope: Construct, id: string, props: cdk.StackProps) {

    const kedaParams = {
      podSecurityContextFsGroup: 1001,
      securityContextRunAsGroup: 1001,
      securityContextRunAsUser: 1001,
      irsaRoles: ["CloudWatchFullAccess", "AmazonSQSFullAccess"]
    };

    const CloudWatchLogsWritePolicy = new iam.PolicyStatement({
      actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:GetLogEvents"
      ],
      resources: ["*"],
  })


    const sdRuntimeParams: SDRuntimeAddOnProps = {
      ModelBucketArn: 'arn:aws:s3:::sd-on-eks-pdx',
      outputSns: blueprints.getNamedResource("outputSNSTopic") as sns.ITopic,
      inputSns: blueprints.getNamedResource("inputSNSTopic") as sns.ITopic,
      outputBucket: blueprints.getNamedResource("outputS3Bucket") as s3.IBucket
    };

    const SharedComponentAddOnParams: SharedComponentAddOnProps = {
      modelstorageEfs: blueprints.getNamedResource("efs-model-storage"),
      inputSns: blueprints.getNamedResource("inputSNSTopic"),
      outputSns: blueprints.getNamedResource("outputSNSTopic"),
      outputBucket: blueprints.getNamedResource("outputS3Bucket")
    };

    const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.KubeProxyAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.EbsCsiDriverAddOn(),
      new blueprints.addons.EfsCsiDriverAddOn(),
      new blueprints.addons.KarpenterAddOn({ interruptionHandling: true }),
      new blueprints.addons.KedaAddOn(kedaParams),
      new blueprints.addons.ContainerInsightsAddOn(),
      new blueprints.addons.AwsForFluentBitAddOn({
          iamPolicies: [CloudWatchLogsWritePolicy],
          namespace: "amazon-cloudwatch",
          values: {
              cloudWatchLogs: {
                  region: "us-west-2",
              },
              tolerations: [{
                  "key": "nvidia.com/gpu",
                  "operator": "Exists",
                  "effect": "NoSchedule"
              },{
                "key": "runtime",
                "operator": "Exists",
                "effect": "NoSchedule"
            }
            ]
          },
          createNamespace: true
      }),
      new nvidiaDevicePluginAddon({}),
      new SharedComponentAddOn(SharedComponentAddOnParams),
      new SDRuntimeAddon(sdRuntimeParams)
    ];

    const MngProps: blueprints.MngClusterProviderProps = {
      minSize: 3,
      maxSize: 3,
      desiredSize: 3,
      version: eks.KubernetesVersion.V1_27,
      instanceTypes: [new ec2.InstanceType('m5.large')],
      amiType: eks.NodegroupAmiType.AL2_X86_64
    }

    const blueprint = blueprints.EksBlueprint.builder() // Deploy cluster
      .version(eks.KubernetesVersion.V1_27)
      .addOns(...addOns)
      .resourceProvider(
        blueprints.GlobalResources.Vpc,
        new blueprints.VpcProvider())
      .resourceProvider("inputSNSTopic", new SNSResourceProvider("sdNotificationLambda"))
      .resourceProvider("outputSNSTopic", new SNSResourceProvider("sdNotificationOutput"))
      .resourceProvider("outputS3Bucket", new blueprints.CreateS3BucketProvider({
        id: 'outputS3Bucket'
      }))
      .resourceProvider("efs-model-storage", new blueprints.CreateEfsFileSystemProvider({ name: "efs-model-storage" }))
      .clusterProvider(new blueprints.MngClusterProvider(MngProps))
      .build(scope, id + 'Stack');
  }
}
