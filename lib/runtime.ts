import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { aws_sns_subscriptions } from "aws-cdk-lib";

export interface SDRuntimeAddOnProps extends blueprints.addons.HelmAddOnUserProps {
  ModelBucketArn?: string,
  outputSns?: sns.ITopic,
  inputSns?: sns.ITopic,
  outputBucket?: s3.IBucket
}

export const defaultProps: blueprints.addons.HelmAddOnProps & SDRuntimeAddOnProps = {
  chart: 'sd-on-eks',
  name: 'sdRuntimeAddOn',
  namespace: 'sdruntime',
  release: 'sdruntime',
  version: '0.1.0',
  repository: 'oci://public.ecr.aws/bingjiao/charts/sd-on-eks',
  values: {}
}

export default class SDRuntimeAddon extends blueprints.addons.HelmAddOn  {

  readonly options: SDRuntimeAddOnProps;

  constructor(props: SDRuntimeAddOnProps) {
    super({...defaultProps, ...props});
    this.options = this.props as SDRuntimeAddOnProps;
  }
  @blueprints.utils.dependable(blueprints.KarpenterAddOn.name)
  @blueprints.utils.dependable("SharedComponentAddOn")
  @blueprints.utils.dependable("nvidiaDevicePluginAddon")

  deploy(clusterInfo: blueprints.ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster

    const ns = blueprints.utils.createNamespace(this.props.namespace!, cluster, true)

    const webUISA = cluster.addServiceAccount('WebUISA', { namespace: this.props.namespace! });
    webUISA.node.addDependency(ns)

    const modelBucket = s3.Bucket.fromBucketAttributes(cluster.stack, 'ModelBucket', {
        bucketArn: this.options.ModelBucketArn!
    });

    modelBucket.grantRead(webUISA);

    const inputQueue = new sqs.Queue(cluster.stack, 'InputQueue1');
    inputQueue.grantConsumeMessages(webUISA);

    this.options.outputBucket!.grantWrite(webUISA);
    this.options.outputBucket!.grantPutAcl(webUISA);
    this.options.outputSns!.grantPublish(webUISA);
    this.options.inputSns!.addSubscription(new aws_sns_subscriptions.SqsSubscription(inputQueue));

    webUISA.role.addManagedPolicy(
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'AWSXRayDaemonWriteAccess',
      ))

    const chart = this.addHelmChart(clusterInfo, {
            global: {
              awsRegion: cdk.Stack.of(cluster.stack).region,
              repository: "057313215210.dkr.ecr.us-west-2.amazonaws.com/stable-diffusion-webui",
              stackName: cdk.Aws.STACK_NAME,
            },
            sdWebuiInferenceApi: {
              serviceAccountName: webUISA.serviceAccountName,
              inferenceApi: {
                image: {
                  name: "inference-api",
                  tag: "0.1.0"
                }
              },
              queueAgent: {
                image: {
                  name: "queue-agent",
                  tag: "latest"
                },
                s3Bucket: this.options.outputBucket!.bucketName,
                snsTopicArn: this.options.outputSns!.topicArn,
                sqsQueueUrl: inputQueue.queueUrl
              }
            }
          }
    , true);

    return Promise.resolve(chart);
  }
}