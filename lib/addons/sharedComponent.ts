import { ClusterAddOn, ClusterInfo } from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as xray from "aws-cdk-lib/aws-xray"
import * as path from 'path';

export interface SharedComponentAddOnProps {
  inputSns: sns.ITopic;
  outputSns: sns.ITopic;
  outputBucket: s3.IBucket;
  apiGWProps?: {
    stageName?: string,
    throttle?: {
      rateLimit?: number,
      burstLimit?: number
    }
  }
}

export const defaultProps: SharedComponentAddOnProps = {
  inputSns: undefined!,
  outputSns: undefined!,
  outputBucket: undefined!,
  apiGWProps: {
    stageName: "prod",
    throttle: {
      rateLimit: 10,
      burstLimit: 2
    }
  }
}

export class SharedComponentAddOn implements ClusterAddOn {
  readonly options: SharedComponentAddOnProps;

  constructor(props: SharedComponentAddOnProps) {
    this.options = { ...defaultProps, ...props };
  }

  deploy(clusterInfo: ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster;

    const v1Alpha1Parser = new lambda.Function(cluster.stack, 'v1Alpha1ParserFunction', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/frontend/input_function/v1alpha1')),
      handler: 'app.lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_11,
      environment: {
        "SNS_TOPIC_ARN": this.options.inputSns.topicArn,
        "S3_OUTPUT_BUCKET": this.options.outputBucket.bucketName
      },
      tracing: lambda.Tracing.ACTIVE
    });

    const v1Alpha2Parser = new lambda.Function(cluster.stack, 'v1Alpha2ParserFunction', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/frontend/input_function/v1alpha2')),
      handler: 'app.lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_11,
      environment: {
        "SNS_TOPIC_ARN": this.options.inputSns.topicArn,
        "S3_OUTPUT_BUCKET": this.options.outputBucket.bucketName
      },
      tracing: lambda.Tracing.ACTIVE
    });

    this.options.inputSns.grantPublish(v1Alpha1Parser);
    this.options.inputSns.grantPublish(v1Alpha2Parser);

    const api = new apigw.RestApi(cluster.stack, 'FrontAPI', {
      restApiName: 'FrontAPI',
      deploy: true,
      cloudWatchRole: true,
      endpointConfiguration: {
        types: [ apigw.EndpointType.REGIONAL ]
      },
      defaultMethodOptions: {
        apiKeyRequired: true
      },
      deployOptions: {
        stageName: this.options.apiGWProps!.stageName,
        tracingEnabled: true,
        metricsEnabled: true,
      }
    });

    const v1alpha1Resource = api.root.addResource('v1alpha1');
    v1alpha1Resource.addMethod('POST', new apigw.LambdaIntegration(v1Alpha1Parser), { apiKeyRequired: true });

    const v1alpha2Resource = api.root.addResource('v1alpha2');
    v1alpha2Resource.addMethod('POST', new apigw.LambdaIntegration(v1Alpha2Parser), { apiKeyRequired: true });

    api.node.addDependency(v1Alpha1Parser);
    api.node.addDependency(v1Alpha2Parser);

    //Force override name of generated output to provide a static name
    const urlCfnOutput = api.node.findChild('Endpoint') as cdk.CfnOutput;
    urlCfnOutput.overrideLogicalId('FrontApiEndpoint')

    const apiKey = new apigw.ApiKey(cluster.stack, `defaultAPIKey`, {
      description: `Default API Key`,
      enabled: true
    })

    const plan = api.addUsagePlan('UsagePlan', {
      name: cluster.stack.stackId + '-Default',
      apiStages: [{
        stage: api.deploymentStage
      }],
      throttle: {
        rateLimit: this.options.apiGWProps!.throttle!.rateLimit,
        burstLimit: this.options.apiGWProps!.throttle!.burstLimit
      }
    });

    plan.addApiKey(apiKey)

    new cdk.CfnOutput(cluster.stack, 'GetAPIKeyCommand', {
      value: "aws apigateway get-api-keys --query 'items[?id==`" + apiKey.keyId + "`].value' --include-values --output text",
      description: 'Command to get API Key'
    });

    //Xray Access Policy
    new xray.CfnResourcePolicy(cluster.stack, cluster.stack.stackName+'XRayAccessPolicyForSNS', {
      policyName: cluster.stack.stackName+'XRayAccessPolicyForSNS',
      policyDocument: '{"Version":"2012-10-17","Statement":[{"Sid":"SNSAccess","Effect":"Allow","Principal":{"Service":"sns.amazonaws.com"},"Action":["xray:PutTraceSegments","xray:GetSamplingRules","xray:GetSamplingTargets"],"Resource":"*","Condition":{"StringEquals":{"aws:SourceAccount":"' + cluster.stack.account + '"},"StringLike":{"aws:SourceArn":"' + cluster.stack.formatArn({ service: "sns", resource: '*' }) + '"}}}]}'
    })

    // Output S3 bucket ARN

    new cdk.CfnOutput(cluster.stack, 'OutputS3Bucket', {
      value: this.options.outputBucket.bucketArn,
      description: 'S3 bucket for generated images'
    });

    return Promise.resolve(plan);
  }
}
