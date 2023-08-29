import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { aws_sns_subscriptions } from "aws-cdk-lib";
import * as lodash from "lodash";

export interface SDRuntimeAddOnProps extends blueprints.addons.HelmAddOnUserProps {
  ModelBucketArn?: string,
  outputSns?: sns.ITopic,
  inputSns?: sns.ITopic,
  outputBucket?: s3.IBucket
  sdModelCheckpoint: string,
  dynamicModel: boolean,
  allModels?: string[],
  extraValues?: {}
}

export const defaultProps: blueprints.addons.HelmAddOnProps & SDRuntimeAddOnProps = {
  chart: 'sd-on-eks',
  name: 'sdRuntimeAddOn',
  namespace: 'sdruntime',
  release: 'sdruntime',
  version: '0.1.0',
  repository: 'oci://public.ecr.aws/bingjiao/charts/sd-on-eks',
  values: {
    global: {
      awsRegion: cdk.Aws.REGION,
      repository: "057313215210.dkr.ecr.us-west-2.amazonaws.com/stable-diffusion-webui",
      stackName: cdk.Aws.STACK_NAME,
    },
    sdWebuiInferenceApi: {
      inferenceApi: {
        image: {
          name: "inference-api",
          tag: "0.1.0"
        },

      },
      queueAgent: {
        image: {
          name: "queue-agent",
          tag: "latest"
        },
      }
    }
  },
  sdModelCheckpoint: "v1-5-pruned-emaonly.safetensors",
  dynamicModel: false
}

export default class SDRuntimeAddon extends blueprints.addons.HelmAddOn {

  readonly options: SDRuntimeAddOnProps;
  readonly id: string;

  constructor(props: SDRuntimeAddOnProps, id?: string) {
    super({ ...defaultProps, ...props });
    this.options = this.props as SDRuntimeAddOnProps;
    if (typeof (id) !== 'undefined') {
      this.id = id!.toLowerCase()
    } else {
      this.id = 'sdruntime'
    }
  }

  @blueprints.utils.dependable(blueprints.KarpenterAddOn.name)
  @blueprints.utils.dependable("SharedComponentAddOn")
  @blueprints.utils.dependable("nvidiaDevicePluginAddon")

  deploy(clusterInfo: blueprints.ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster

    this.props.name = this.id + 'Addon'
    this.props.namespace = this.id
    this.props.release = this.id

    const ns = blueprints.utils.createNamespace(this.props.namespace, cluster, true)

    const webUISA = cluster.addServiceAccount('WebUISA' + this.id, { namespace: this.props.namespace });
    webUISA.node.addDependency(ns)

    const modelBucket = s3.Bucket.fromBucketAttributes(cluster.stack, 'ModelBucket' + this.id, {
      bucketArn: this.options.ModelBucketArn!
    });

    modelBucket.grantRead(webUISA);

    const inputQueue = new sqs.Queue(cluster.stack, 'InputQueue' + this.id);
    inputQueue.grantConsumeMessages(webUISA);
    

    this.options.outputBucket!.grantWrite(webUISA);
    this.options.outputBucket!.grantPutAcl(webUISA);
    this.options.outputSns!.grantPublish(webUISA);

    webUISA.role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        'AWSXRayDaemonWriteAccess',
      ))

    var generatedValues = {
      sdWebuiInferenceApi: {
        serviceAccountName: webUISA.serviceAccountName,
        inferenceApi: {
          SD_MODEL_CHECKPOINT: this.options.sdModelCheckpoint
        },
        queueAgent: {
          s3Bucket: this.options.outputBucket!.bucketName,
          snsTopicArn: this.options.outputSns!.topicArn,
          sqsQueueUrl: inputQueue.queueUrl,
          dynamicModel: false
        }
      }
    }

    if (!this.options.dynamicModel) {
      this.options.inputSns!.addSubscription(new aws_sns_subscriptions.SqsSubscription(inputQueue, {
        filterPolicy: {
          sd_model_checkpoint:
            sns.SubscriptionFilter.stringFilter({
              allowlist: [this.options.sdModelCheckpoint]
            })
        }
      }))
      generatedValues.sdWebuiInferenceApi.queueAgent.dynamicModel = false
    } else {
      this.options.inputSns!.addSubscription(new aws_sns_subscriptions.SqsSubscription(inputQueue, {
        filterPolicy: {
          sd_model_checkpoint:
            sns.SubscriptionFilter.stringFilter({
              denylist: this.options.allModels
            })
        }
      }))
      generatedValues.sdWebuiInferenceApi.queueAgent.dynamicModel = true
    }

    const values = lodash.merge(this.props.values, this.options.extraValues, generatedValues)

    const chart = this.addHelmChart(clusterInfo, values, true);

    return Promise.resolve(chart);
  }
}