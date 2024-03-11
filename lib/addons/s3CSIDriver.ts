import * as blueprints from '@aws-quickstart/eks-blueprints';
import { ManagedPolicy } from 'aws-cdk-lib/aws-iam';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from "constructs";

export interface s3CSIDriverAddOnProps extends blueprints.addons.HelmAddOnUserProps {
  s3BucketArn: string;
}

export const defaultProps: blueprints.addons.HelmAddOnProps & s3CSIDriverAddOnProps = {
  chart: 'aws-mountpoint-s3-csi-driver',
  name: 's3CSIDriverAddOn',
  namespace: 'kube-system',
  release: 's3-csi-driver-release',
  version: 'v1.4.0',
  repository: 'https://awslabs.github.io/mountpoint-s3-csi-driver',
  s3BucketArn: ''
}

export class s3CSIDriverAddOn extends blueprints.addons.HelmAddOn {

  readonly options: s3CSIDriverAddOnProps;

  constructor(props: s3CSIDriverAddOnProps) {
    super({ ...defaultProps, ...props });
    this.options = this.props as s3CSIDriverAddOnProps;
  }

  deploy(clusterInfo: blueprints.ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster;
    const serviceAccount = cluster.addServiceAccount('s3-csi-driver-sa', {
      name: 's3-csi-driver-sa',
      namespace: this.options.namespace,
    });

    // new IAM policy to grand access to S3 bucket
    // https://github.com/awslabs/mountpoint-s3/blob/main/doc/CONFIGURATION.md#iam-permissions
    const s3BucketPolicy = new iam.Policy(cluster, 's3-csi-driver-policy', {
      statements: [
        new iam.PolicyStatement({
          sid: 'MountpointFullBucketAccess',
          actions: [
            "s3:ListBucket"
          ],
          resources: [this.options.s3BucketArn]
        }),
        new iam.PolicyStatement({
          sid: 'MountpointFullObjectAccess',
          actions: [
            "s3:GetObject",
            "s3:PutObject",
            "s3:AbortMultipartUpload",
            "s3:DeleteObject"
          ],
          resources: [`${this.options.s3BucketArn}/*`]
      })]
    });
    serviceAccount.role.attachInlinePolicy(s3BucketPolicy);
 
    const chart = this.addHelmChart(clusterInfo, {
      node: {
        serviceAccount: {
          create: false
        },
        tolerateAllTaints: true
      }
    }, true, true);
    return Promise.resolve(chart);
  }
}