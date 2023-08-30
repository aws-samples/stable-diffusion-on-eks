import { ClusterAddOn, ClusterInfo } from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as xray from "aws-cdk-lib/aws-xray"
import * as iam from "aws-cdk-lib/aws-iam"
import * as path from 'path';

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

    //Create IAM role for API GW logging

    const roleforAPIGWLogging = new iam.Role(cluster.stack, 'APIGatewayLoggingRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonAPIGatewayPushToCloudWatchLogs")
      ]
    })

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


    const plan = api.addUsagePlan('UsagePlan', {
      name: 'Easy',
      throttle: {
        rateLimit: 10,
        burstLimit: 2
      }
    });
    const key = api.addApiKey('myId');
    plan.addApiKey(key);

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

    new xray.CfnResourcePolicy(cluster.stack, 'XRayAccessPolicyForSNS', {
      policyName: 'XRayAccessPolicyForSNS',
      policyDocument: '{"Version":"2012-10-17","Statement":[{"Sid":"SNSAccess","Effect":"Allow","Principal":{"Service":"sns.amazonaws.com"},"Action":["xray:PutTraceSegments","xray:GetSamplingRules","xray:GetSamplingTargets"],"Resource":"*","Condition":{"StringEquals":{"aws:SourceAccount":"'+cluster.stack.account+'"},"StringLike":{"aws:SourceArn":"' + cluster.stack.formatArn({service: "sns", resource: '*'}) + '"}}}]}'
    })

    return Promise.resolve(plan);
  }
}