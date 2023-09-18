import { ClusterAddOn, ClusterInfo } from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from "aws-cdk-lib/aws-iam"
import * as path from 'path';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';

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
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/functions/ebsThroughputModify')),
      handler: 'app.lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_11,
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

    const triggerTask = new tasks.LambdaInvoke(cluster.stack, 'Change throughput', {
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