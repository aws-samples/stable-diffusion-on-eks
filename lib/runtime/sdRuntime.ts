import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { aws_sns_subscriptions } from "aws-cdk-lib";
import * as lodash from "lodash";
import { createNamespace }  from "../utils/namespace"

export interface SDRuntimeAddOnProps extends blueprints.addons.HelmAddOnUserProps {
  type: string,
  targetNamespace?: string,
  ModelBucketArn?: string,
  outputSns?: sns.ITopic,
  inputSns?: sns.ITopic,
  outputBucket?: s3.IBucket
  sdModelCheckpoint?: string,
  dynamicModel?: boolean,
  chartRepository?: string,
  chartVersion?: string,
  extraValues?: object
}

export const defaultProps: blueprints.addons.HelmAddOnProps & SDRuntimeAddOnProps = {
  chart: 'sd-on-eks',
  name: 'sdRuntimeAddOn',
  namespace: 'sdruntime',
  release: 'sdruntime',
  version: '1.1.0',
  repository: 'oci://public.ecr.aws/bingjiao/sd-on-eks/charts/sd-on-eks',
  values: {
    global: {
      awsRegion: cdk.Aws.REGION,
      stackName: cdk.Aws.STACK_NAME,
    }
  },
  type: "sdwebui"
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
  @blueprints.utils.dependable("s3CSIDriverAddOn")

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

    const runtimeSA = cluster.addServiceAccount('runtimeSA' + this.id, { namespace: this.props.namespace });
    runtimeSA.node.addDependency(ns)

    if (this.options.chartRepository) {
      this.props.repository = this.options.chartRepository
    }

    if (this.options.chartVersion) {
      this.props.version = this.options.chartVersion
    }

    const modelBucket = s3.Bucket.fromBucketAttributes(cluster.stack, 'ModelBucket' + this.id, {
      bucketArn: this.options.ModelBucketArn!
    });

    modelBucket.grantRead(runtimeSA);

    const inputQueue = new sqs.Queue(cluster.stack, 'InputQueue' + this.id);
    inputQueue.grantConsumeMessages(runtimeSA);


    this.options.outputBucket!.grantWrite(runtimeSA);
    this.options.outputBucket!.grantPutAcl(runtimeSA);
    this.options.outputSns!.grantPublish(runtimeSA);

    runtimeSA.role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        'AWSXRayDaemonWriteAccess',
      ))

    // Static provisioning resource
    const pv = cluster.addManifest(this.id+"S3ModelStoragePv", {
      "apiVersion": "v1",
      "kind": "PersistentVolume",
      "metadata": {
        "name": this.id+"-s3-model-storage-pv"
      },
      "spec": {
        "capacity": {
          "storage": "2Ti"
        },
        "accessModes": [
          "ReadWriteMany"
        ],
        "mountOptions": [
          "allow-delete",
          "allow-other",
          "file-mode=777",
          "dir-mode=777"
        ],
        "csi": {
          "driver": "s3.csi.aws.com",
          "volumeHandle": "s3-csi-driver-volume",
          "volumeAttributes": {
            "bucketName": modelBucket.bucketName
          }
        }
      }
    })
    pv.node.addDependency(ns)

    const pvc = cluster.addManifest(this.id+"S3ModelStoragePvc", {
      "apiVersion": "v1",
      "kind": "PersistentVolumeClaim",
      "metadata": {
        "name": this.id+"-s3-model-storage-pvc",
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
        "storageClassName": "",
        "volumeName": this.id+"-s3-model-storage-pv"
      }
    })
    pvc.node.addDependency(ns)

    const nodeRole = blueprints.getNamedResource("karpenter-node-role") as iam.IRole

    var generatedValues = {
      runtime: {
        type: this.options.type,
        serviceAccountName: runtimeSA.serviceAccountName,
        queueAgent: {
          s3Bucket: this.options.outputBucket!.bucketName,
          snsTopicArn: this.options.outputSns!.topicArn,
          sqsQueueUrl: inputQueue.queueUrl,
        },
        persistence: {
          enabled: true,
          existingClaim: this.id+"-s3-model-storage-pvc"
        }
      },
      karpenter: {
        nodeTemplate: {
          iamRole: nodeRole.roleName
        }
      }
    }
    // Temp change: set image repo to ECR Public
    if (this.options.type == "sdwebui") {
      var imagerepo: string
      if (!(lodash.get(this.options, "extraValues.runtime.inferenceApi.image.repository"))) {
        imagerepo = "public.ecr.aws/bingjiao/sd-on-eks/sdwebui"
      } else {
        imagerepo = lodash.get(this.options, "extraValues.runtime.inferenceApi.image.repository")!
      }
      var sdWebUIgeneratedValues =  {
        runtime: {
          inferenceApi: {
            image: {
              repository: imagerepo
            },
            modelFilename: this.options.sdModelCheckpoint
          },
          queueAgent: {
            dynamicModel: this.options.dynamicModel
          }
        }
      }

      generatedValues = lodash.merge(generatedValues, sdWebUIgeneratedValues)
    }

    if (this.options.type == "comfyui") {
      var imagerepo: string
      if (!(lodash.get(this.options, "extraValues.runtime.inferenceApi.image.repository"))) {
        imagerepo = "public.ecr.aws/bingjiao/sd-on-eks/comfyui"
      } else {
        imagerepo = lodash.get(this.options, "extraValues.runtime.inferenceApi.image.repository")!
      }

      var comfyUIgeneratedValues =  {
        runtime: {
          inferenceApi: {
            image: {
              repository: imagerepo
            },
          }
        }
      }

      generatedValues = lodash.merge(generatedValues, comfyUIgeneratedValues)
    }

    if (this.options.type == "sdwebui" && this.options.sdModelCheckpoint) {
      // Legacy and new routing, use CFN as a workaround since L2 construct doesn't support OR
      const cfnSubscription = new sns.CfnSubscription(cluster.stack, this.id+'CfnSubscription', {
        protocol: 'sqs',
        endpoint: inputQueue.queueArn,
        topicArn: this.options.inputSns!.topicArn,
        filterPolicy: {
          "$or": [
            {
              "sd_model_checkpoint": [
                this.options.sdModelCheckpoint!
              ]
            }, {
              "runtime": [
                this.id
              ]
            }]
        },
        filterPolicyScope: "MessageAttributes"
      })

      inputQueue.addToResourcePolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        principals: [new iam.ServicePrincipal('sns.amazonaws.com')],
        actions: ['sqs:SendMessage'],
        resources: [inputQueue.queueArn],
        conditions: {
          'ArnEquals': {
            'aws:SourceArn': this.options.inputSns!.topicArn
          }
        }
      }))


/* It should like this...
       this.options.inputSns!.addSubscription(new aws_sns_subscriptions.SqsSubscription(inputQueue, {
        filterPolicy: {
          : sns.SubscriptionFilter.stringFilter({
            allowlist: [this.options.sdModelCheckpoint!]
          }),
          runtime: sns.SubscriptionFilter.stringFilter({
            allowlist: [this.id]
          })
        }
      })) */
    } else {
      // New version routing only
      this.options.inputSns!.addSubscription(new aws_sns_subscriptions.SqsSubscription(inputQueue, {
        filterPolicy: {
          runtime:
            sns.SubscriptionFilter.stringFilter({
              allowlist: [this.id]
            })
        }
      }))
    }

    const values = lodash.merge(this.props.values, this.options.extraValues, generatedValues)

    const chart = this.addHelmChart(clusterInfo, values, true);

    chart.node.addDependency(pv)
    chart.node.addDependency(pvc)

    return Promise.resolve(chart);
  }
}