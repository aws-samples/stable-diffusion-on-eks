import { ClusterAddOn, ClusterInfo } from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as xray from "aws-cdk-lib/aws-xray"
import * as iam from "aws-cdk-lib/aws-iam"
import * as path from 'path';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as crypto from "crypto";

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
      },
      tracing: lambda.Tracing.ACTIVE
    });

    this.options.inputSns.grantPublish(lambdaFunction);

    const api = new apigw.LambdaRestApi(cluster.stack, 'FrontApi', {
      handler: lambdaFunction,
      proxy: true,
      deploy: true,
      cloudWatchRole: true,
      deployOptions: {
        stageName: "prod",
        tracingEnabled: true,
        metricsEnabled: true,
      }
    });
    api.node.addDependency(lambdaFunction);

    const key = crypto.randomBytes(10).toString('hex')

    const apiKey = new apigw.ApiKey(cluster.stack, `defaultAPIKey`, {
      description: `Default API Key`,
      enabled: true,
      value: key
    })

    const plan = api.addUsagePlan('UsagePlan', {
      name: 'Default',
      apiStages: [{
        stage: api.deploymentStage
      }],
      throttle: {
        rateLimit: 10,
        burstLimit: 2
      }
    });

    plan.addApiKey(apiKey)

    new cdk.CfnOutput(cluster.stack, 'APIKey', {
      value: key,
      description: 'API Key for request'
    });

/*     const sc = cluster.addManifest("efs-model-storage-sc", {
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
        "subPathPattern": ".",
        "ensureUniqueDirectory": "false"
      }
    }) */

    // Static provisioning EFS filesystem
    const sc = cluster.addManifest("efs-model-storage-sc", {
      "apiVersion": "storage.k8s.io/v1",
      "kind": "StorageClass",
      "metadata": {
        "name": "efs-sc"
      },
      "provisioner": "efs.csi.aws.com"
    })

    //Xray Access Policy
    new xray.CfnResourcePolicy(cluster.stack, 'XRayAccessPolicyForSNS', {
      policyName: 'XRayAccessPolicyForSNS',
      policyDocument: '{"Version":"2012-10-17","Statement":[{"Sid":"SNSAccess","Effect":"Allow","Principal":{"Service":"sns.amazonaws.com"},"Action":["xray:PutTraceSegments","xray:GetSamplingRules","xray:GetSamplingTargets"],"Resource":"*","Condition":{"StringEquals":{"aws:SourceAccount":"'+cluster.stack.account+'"},"StringLike":{"aws:SourceArn":"' + cluster.stack.formatArn({service: "sns", resource: '*'}) + '"}}}]}'
    })

    return Promise.resolve(plan);
  }
}

export interface EbsThroughputModifyAddOnProps {
  duration: number;
  throughput: number;
  iops: number;
}

export class EbsThroughputModifyAddOn implements ClusterAddOn {

  readonly options: EbsThroughputModifyAddOnProps;

  constructor(props: EbsThroughputModifyAddOnProps) {
    this.options = props
  }

  deploy(clusterInfo: ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster;

    const lambdaTimeout: number = 300

    //EBS Throughput Modify lambda function
    const lambdaFunction = new lambda.Function(cluster.stack, 'EbsThroughputModifyLambda', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../src/ebs_throughput_modify')),
      handler: 'app.lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_9,
      timeout: cdk.Duration.seconds(lambdaTimeout),
      environment: {
        "TARGET_EC2_TAG_KEY": "stack",
        "TARGET_EC2_TAG_VALUE": cdk.Aws.STACK_NAME,
        "THROUGHPUT_VALUE": this.options.throughput.toString(),
        "IOPS_VALUE": this.options.iops.toString()
      },
    });

    const functionRole = lambdaFunction.role!.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        'AmazonEC2FullAccess',
    ))

    // Step Functions definition
    const waitTask = new sfn.Wait(cluster.stack, 'Wait time', {
      time: sfn.WaitTime.duration(cdk.Duration.seconds(this.options.duration)),
    });

    const triggerTask =  new tasks.LambdaInvoke(cluster.stack, 'Change throughput', {
      lambdaFunction: lambdaFunction
    }).addRetry({
      backoffRate: 2,
      maxAttempts: 3,
      interval: cdk.Duration.seconds(5)
    })

    const stateDefinition = waitTask
      .next(triggerTask)

    const stateMachine = new sfn.StateMachine(cluster.stack, 'EbsThroughputModifyStateMachine', {
      definitionBody: sfn.DefinitionBody.fromChainable(stateDefinition),
      timeout: cdk.Duration.seconds(this.options.duration + lambdaTimeout + 30),
    });

    lambdaFunction.grantInvoke(stateMachine)

    const rule = new events.Rule(cluster.stack, 'EbsThroughputModifyRule', {
      eventPattern: {
        detail: {
          'state': events.Match.equalsIgnoreCase("running")
        },
        detailType: events.Match.equalsIgnoreCase('EC2 Instance State-change Notification'),
        source: ['aws.ec2'],
      }
    });

    rule.addTarget(new targets.SfnStateMachine(stateMachine))

    return Promise.resolve(rule);
  }
}