import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as sns from 'aws-cdk-lib/aws-sns';

export class SNSResourceProvider implements blueprints.ResourceProvider<sns.ITopic> {
  constructor(readonly topicName: string, readonly displayName?: string) { }

  provide(context: blueprints.ResourceContext): sns.ITopic {

    const cfnTopic = new cdk.aws_sns.CfnTopic(context.scope, this.topicName + 'Cfn', {
      displayName: this.displayName,
      tracingConfig: 'Active'
    });

    new cdk.CfnOutput(context.scope, this.topicName + 'ARN', {
      value: cfnTopic.attrTopicArn
    })

    return sns.Topic.fromTopicArn(context.scope, this.topicName, cfnTopic.attrTopicArn)
  }
}