import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as eks from "aws-cdk-lib/aws-eks";
import * as sns from 'aws-cdk-lib/aws-sns';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import SDRuntimeAddon, { SDRuntimeAddOnProps } from './runtime/sdRuntime';
import { EbsThroughputTunerAddOn, EbsThroughputTunerAddOnProps } from './addons/ebsThroughputTuner'
import { s3CSIDriverAddOn, s3CSIDriverAddOnProps } from './addons/s3CSIDriver'
import { SharedComponentAddOn, SharedComponentAddOnProps } from './addons/sharedComponent';
import { SNSResourceProvider } from './resourceProvider/sns'
import { s3GWEndpointProvider } from './resourceProvider/s3GWEndpoint'
import { dcgmExporterAddOn } from './addons/dcgmExporter';

export interface dataPlaneProps {
  stackName: string,
  modelBucketArn: string;
  APIGW?: {
    stageName?: string,
    throttle?: {
      rateLimit?: number,
      burstLimit?: number
    }
  }
  modelsRuntime: {
    name: string,
    namespace: string,
    type: string,
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
  constructor(scope: Construct, id: string,
    dataplaneProps: dataPlaneProps,
    props: cdk.StackProps) {

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

    const awsForFluentBitParams: blueprints.AwsForFluentBitAddOnProps = {
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
        }]
      },
      createNamespace: true
    }

    const containerInsightsParams: blueprints.ContainerInsightAddonProps = {
      values: {
        adotCollector: {
          daemonSet: {
            tolerations: [{
              "key": "nvidia.com/gpu",
              "operator": "Exists",
              "effect": "NoSchedule"
            }, {
              "key": "runtime",
              "operator": "Exists",
              "effect": "NoSchedule"
            }],
            cwreceivers: {
              preferFullPodName: "true",
              addFullPodNameMetricLabel: "true"
            }
          }
        }
      }
    }

    const SharedComponentAddOnParams: SharedComponentAddOnProps = {
      inputSns: blueprints.getNamedResource("inputSNSTopic"),
      outputSns: blueprints.getNamedResource("outputSNSTopic"),
      outputBucket: blueprints.getNamedResource("outputS3Bucket"),
      apiGWProps: dataplaneProps.APIGW
    };

    const EbsThroughputModifyAddOnParams: EbsThroughputTunerAddOnProps = {
      duration: 300,
      throughput: 125,
      iops: 3000
    };

    const s3CSIDriverAddOnParams: s3CSIDriverAddOnProps = {
      s3BucketArn: dataplaneProps.modelBucketArn
    };

    const addOns: Array<blueprints.ClusterAddOn> = [
      new blueprints.addons.VpcCniAddOn(),
      new blueprints.addons.CoreDnsAddOn(),
      new blueprints.addons.KubeProxyAddOn(),
      new blueprints.addons.AwsLoadBalancerControllerAddOn(),
      new blueprints.addons.EbsCsiDriverAddOn(),
      new blueprints.addons.KarpenterAddOn({ interruptionHandling: true }),
      new blueprints.addons.KedaAddOn(kedaParams),
      new blueprints.addons.ContainerInsightsAddOn(containerInsightsParams),
      new blueprints.addons.AwsForFluentBitAddOn(awsForFluentBitParams),
      new s3CSIDriverAddOn(s3CSIDriverAddOnParams),
      new SharedComponentAddOn(SharedComponentAddOnParams),
      new EbsThroughputTunerAddOn(EbsThroughputModifyAddOnParams),
      new dcgmExporterAddOn({})
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
    dynamicModel: false
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
    allModels: models
  };
  addOns.push(new SDRuntimeAddon(sdRuntimeParams, "dynamicSDRuntime"))
}

// Define initial managed node group for cluster components
const MngProps: blueprints.MngClusterProviderProps = {
  minSize: 2,
  maxSize: 2,
  desiredSize: 2,
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
  .resourceProvider("s3GWEndpoint", new s3GWEndpointProvider("s3GWEndpoint"))
  .clusterProvider(new blueprints.MngClusterProvider(MngProps))
  .build(scope, id + 'Stack', props);

  // Workaround for permission denied when creating cluster
    const handler = blueprint.node.tryFindChild('@aws-cdk--aws-eks.KubectlProvider')!
      .node.tryFindChild('Handler')! as cdk.aws_lambda.Function

    (
      blueprint.node.tryFindChild('@aws-cdk--aws-eks.KubectlProvider')!
        .node.tryFindChild('Provider')!
        .node.tryFindChild('framework-onEvent')!
        .node.tryFindChild('ServiceRole')!
        .node.tryFindChild('DefaultPolicy') as cdk.aws_iam.Policy
    )
      .addStatements(new cdk.aws_iam.PolicyStatement({
        effect: cdk.aws_iam.Effect.ALLOW,
        actions: ["lambda:GetFunctionConfiguration"],
        resources: [handler.functionArn]
      }))

  // Provide static output name for cluster
    const cluster = blueprint.getClusterInfo().cluster
    const clusterNameCfnOutput = cluster.node.findChild('ClusterName') as cdk.CfnOutput;
    clusterNameCfnOutput.overrideLogicalId('ClusterName')

    const configCommandCfnOutput = cluster.node.findChild('ConfigCommand') as cdk.CfnOutput;
    configCommandCfnOutput.overrideLogicalId('ConfigCommand')

    const getTokenCommandCfnOutput = cluster.node.findChild('GetTokenCommand') as cdk.CfnOutput;
    getTokenCommandCfnOutput.overrideLogicalId('GetTokenCommand')
  }
}