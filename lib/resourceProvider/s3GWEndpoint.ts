import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export class s3GWEndpointProvider implements blueprints.ResourceProvider<ec2.IGatewayVpcEndpoint> {
  constructor(readonly name: string) { }

  provide(context: blueprints.ResourceContext): ec2.IGatewayVpcEndpoint {
    const vpc = context.get('vpc') as ec2.IVpc
    const vpce = new ec2.GatewayVpcEndpoint(context.scope, this.name, {
      service: ec2.GatewayVpcEndpointAwsService.S3,
      vpc: vpc
    });

    return vpce
  }
}