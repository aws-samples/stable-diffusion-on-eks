import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as eks from "aws-cdk-lib/aws-eks";
import * as sns from 'aws-cdk-lib/aws-sns';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as efs from 'aws-cdk-lib/aws-efs';
import SDRuntimeAddon, { SDRuntimeAddOnProps } from './runtime';
import { SharedComponentAddOn, SharedComponentAddOnProps, EbsThroughputModifyAddOn, EbsThroughputModifyAddOnProps } from './sharedComponent';
import nvidiaDevicePluginAddon, { SNSResourceProvider } from './utils'

export interface dataPlaneProps {
  modelBucketArn: string;
  modelsRuntime: {
    name: string,
    namespace: string,
    modelFilename: string,
    chartRepository?: string,
    chartVersion?: string,
    extraValues?: {}
  }[];
  dynamicModelRuntime: {
    enabled: boolean,
    namespace?: string,
    chartRepository?: string,
    chartVersion?: string,
    extraValues?: {}
  }
}

export default class DataPlaneStack {
  cluster: eks.ICluster;
  outputSns: sns.Topic
  inputSns: sns.Topic
  outputBucket: s3.Bucket

  constructor(scope: Construct, id: string,
    dataplaneProps: dataPlaneProps,
    props: cdk.StackProps) {

    const efsParams: blueprints.CreateEfsFileSystemProps = {
      name: "efs-model-storage",
      efsProps: {
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        throughputMode: efs.ThroughputMode.ELASTIC
      }
    }

    const kedaParams: blueprints.KedaAddOnProps = {
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

    const SharedComponentAddOnParams: SharedComponentAddOnProps = {
      modelstorageEfs: blueprints.getNamedResource("efs-model-storage"),
      inputSns: blueprints.getNamedResource("inputSNSTopic"),
      outputSns: blueprints.getNamedResource("outputSNSTopic"),
      outputBucket: blueprints.getNamedResource("outputS3Bucket")
    };

    const EbsThroughputModifyAddOnParams: EbsThroughputModifyAddOnProps = {
      duration: 300,
      throughput: 125,
      iops: 3000
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
            region: cdk.Aws.REGION,
          },
          tolerations: [{
            "key": "nvidia.com/gpu",
            "operator": "Exists",
            "effect": "NoSchedule"
          }, {
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
      new EbsThroughputModifyAddOn(EbsThroughputModifyAddOnParams)
    ];

    let models: string[] = [];

    // Generate SD Runtime Addon for static runtime
    dataplaneProps.modelsRuntime.forEach((val, idx, array) => {
      const sdRuntimeParams: SDRuntimeAddOnProps = {
        ModelBucketArn: dataplaneProps.modelBucketArn,
        outputSns: blueprints.getNamedResource("outputSNSTopic") as sns.ITopic,
        inputSns: blueprints.getNamedResource("inputSNSTopic") as sns.ITopic,
        outputBucket: blueprints.getNamedResource("outputS3Bucket") as s3.IBucket,
        sdModelCheckpoint: val.modelFilename,
        chartRepository: val.chartRepository,
        chartVersion: val.chartVersion,
        extraValues: val.extraValues,
        targetNamespace: val.namespace,
        dynamicModel: false,
        efsFilesystem: blueprints.getNamedResource("efs-model-storage") as efs.IFileSystem
      };
      addOns.push(new SDRuntimeAddon(sdRuntimeParams, val.name))
      models.push(val.modelFilename)
    });

    // Generate SD Runtime Addon for dynamic runtime
    if (dataplaneProps.dynamicModelRuntime.enabled) {
      const sdRuntimeParams: SDRuntimeAddOnProps = {
        ModelBucketArn: dataplaneProps.modelBucketArn,
        outputSns: blueprints.getNamedResource("outputSNSTopic") as sns.ITopic,
        inputSns: blueprints.getNamedResource("inputSNSTopic") as sns.ITopic,
        outputBucket: blueprints.getNamedResource("outputS3Bucket") as s3.IBucket,
        sdModelCheckpoint: "v1-5-pruned-emaonly.safetensors",
        dynamicModel: true,
        targetNamespace: dataplaneProps.dynamicModelRuntime.namespace,
        chartRepository: dataplaneProps.dynamicModelRuntime.chartRepository,
        chartVersion: dataplaneProps.dynamicModelRuntime.chartVersion,
        extraValues: dataplaneProps.dynamicModelRuntime.extraValues,
        allModels: models,
        efsFilesystem: blueprints.getNamedResource("efs-model-storage") as efs.IFileSystem
      };
      addOns.push(new SDRuntimeAddon(sdRuntimeParams, "dynamicSDRuntime"))
    }

    // Define initial managed node group for cluster components
    const MngProps: blueprints.MngClusterProviderProps = {
      minSize: 3,
      maxSize: 3,
      desiredSize: 3,
      version: eks.KubernetesVersion.V1_27,
      instanceTypes: [new ec2.InstanceType('m5.large')],
      amiType: eks.NodegroupAmiType.AL2_X86_64,
      enableSsmPermissions: true,
      nodeGroupTags: {
        "Name": cdk.Aws.STACK_NAME + "-ClusterComponents",
        "stack": cdk.Aws.STACK_NAME
      }
    }

    // Deploy EKS cluster with all add-ons
    const blueprint = blueprints.EksBlueprint.builder()
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
      .resourceProvider("efs-model-storage", new blueprints.CreateEfsFileSystemProvider(efsParams))
      .clusterProvider(new blueprints.MngClusterProvider(MngProps))
      .build(scope, id + 'Stack');
  }
}
