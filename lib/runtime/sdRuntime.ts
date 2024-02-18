import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { aws_sns_subscriptions } from "aws-cdk-lib";
import * as lodash from "lodash";
import { createNamespace }  from "../utils/namespace"

export interface SDRuntimeAddOnProps extends blueprints.addons.HelmAddOnUserProps {
  targetNamespace?: string,
  ModelBucketArn?: string,
  outputSns?: sns.ITopic,
  inputSns?: sns.ITopic,
  outputBucket?: s3.IBucket
  sdModelCheckpoint: string,
  dynamicModel: boolean,
  allModels?: string[],
  chartRepository?: string,
  chartVersion?: string,
  extraValues?: {},
  efsFilesystem?: efs.IFileSystem
}

export const defaultProps: blueprints.addons.HelmAddOnProps & SDRuntimeAddOnProps = {
  chart: 'sd-on-eks',
  name: 'sdRuntimeAddOn',
  namespace: 'sdruntime',
  release: 'sdruntime',
  version: '0.1.0',
  repository: 'https://aws-samples.github.io/stable-diffusion-on-eks/charts',
  values: {
    global: {
      awsRegion: cdk.Aws.REGION,
      stackName: cdk.Aws.STACK_NAME,
    }
  },
  sdModelCheckpoint: "",
  dynamicModel: false
}

export default class SDRuntimeAddon extends blueprints.addons.HelmAddOn {

  readonly options: SDRuntimeAddOnProps;
  readonly id: string;

  constructor(props: SDRuntimeAddOnProps, id?: string) {
    super({ ...defaultProps, ...props });
    this.options = this.props as SDRuntimeAddOnProps;
    if (id) {
      this.id = id!.toLowerCase()
    } else {
      this.id = 'sdruntime'
    }
  }

  @blueprints.utils.dependable(blueprints.KarpenterAddOn.name)
  @blueprints.utils.dependable("SharedComponentAddOn")
//  @blueprints.utils.dependable("nvidiaDevicePluginAddon")

  deploy(clusterInfo: blueprints.ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster

    this.props.name = this.id + 'Addon'
    this.props.release = this.id

    if (this.options.targetNamespace) {
      this.props.namespace = this.options.targetNamespace.toLowerCase()
    } else {
      this.props.namespace = "default"
    }

    const ns = createNamespace(this.id+"-"+this.props.namespace+"-namespace-struct", this.props.namespace, cluster, true)

    const webUISA = cluster.addServiceAccount('WebUISA' + this.id, { namespace: this.props.namespace });
    webUISA.node.addDependency(ns)

    if (this.options.chartRepository) {
      this.props.repository = this.options.chartRepository
    }

    if (this.options.chartVersion) {
      this.props.version = this.options.chartVersion
    }

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

    // Static provisioning resource
    const pv = cluster.addManifest(this.id+"EfsModelStoragePv", {
      "apiVersion": "v1",
      "kind": "PersistentVolume",
      "metadata": {
        "name": this.id+"-efs-model-storage-pv"
      },
      "spec": {
        "capacity": {
          "storage": "2Ti"
        },
        "volumeMode": "Filesystem",
        "accessModes": [
          "ReadWriteMany"
        ],
        "storageClassName": "efs-sc",
        "persistentVolumeReclaimPolicy": "Retain",
        "csi": {
          "driver": "efs.csi.aws.com",
          "volumeHandle": this.options.efsFilesystem!.fileSystemId
        }
      }
    })
    pv.node.addDependency(ns)

    const pvc = cluster.addManifest(this.id+"EfsModelStoragePvc", {
      "apiVersion": "v1",
      "kind": "PersistentVolumeClaim",
      "metadata": {
        "name": this.id+"-efs-model-storage-pvc",
        "namespace": this.props.namespace
      },
      "spec": {
        "resources": {
          "requests": {
            "storage": "2Ti"
          }
        },
        "accessModes": [
          "ReadWriteMany"
        ],
        "storageClassName": "efs-sc"
      }
    })
    pvc.node.addDependency(ns)

    var generatedValues = {
      sdWebuiInferenceApi: {
        serviceAccountName: webUISA.serviceAccountName,
        inferenceApi: {
          modelFilename: this.options.sdModelCheckpoint
        },
        queueAgent: {
          s3Bucket: this.options.outputBucket!.bucketName,
          snsTopicArn: this.options.outputSns!.topicArn,
          sqsQueueUrl: inputQueue.queueUrl,
          dynamicModel: this.options.dynamicModel
        },
        // Temp add static provisioning values here
        persistence: {
          existingClaim: this.id+"-efs-model-storage-pvc"
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