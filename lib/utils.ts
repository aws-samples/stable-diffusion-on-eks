import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as sns from 'aws-cdk-lib/aws-sns';
import { Construct } from "constructs";
import { KubernetesManifest } from "aws-cdk-lib/aws-eks";
import * as eks from "aws-cdk-lib/aws-eks";

export type Values = {
  [key: string]: any;
};

export function createNamespace(id: string, name: string, cluster: eks.ICluster, overwrite?: boolean, prune?: boolean, annotations?: Values, labels? : Values) {
  return new KubernetesManifest(cluster.stack, id, {
      cluster: cluster,
      manifest: [{
          apiVersion: 'v1',
          kind: 'Namespace',
          metadata: {
              name: name,
              annotations,
              labels
          }
      }],
      overwrite: overwrite ?? true,
      prune: prune ?? true
  });
}

export class SNSResourceProvider implements blueprints.ResourceProvider<sns.ITopic> {
  constructor(readonly topicName: string, readonly displayName?: string) { }

  provide(context: blueprints.ResourceContext): sns.ITopic {

    const cfnTopic = new cdk.aws_sns.CfnTopic(context.scope, this.topicName + 'Cfn', {
      displayName: this.displayName,
      tracingConfig: 'Active'
    });

    return sns.Topic.fromTopicArn(context.scope, this.topicName, cfnTopic.attrTopicArn)
  }
}

export interface nvidiaDevicePluginAddOnProps extends blueprints.addons.HelmAddOnUserProps {

}

export const defaultProps: blueprints.addons.HelmAddOnProps & nvidiaDevicePluginAddOnProps = {
  chart: 'nvidia-device-plugin',
  name: 'nvidiaDevicePluginAddOn',
  namespace: 'nvidia-device-plugin',
  release: 'nvdp',
  version: '0.14.1',
  repository: 'https://nvidia.github.io/k8s-device-plugin'
}

export default class nvidiaDevicePluginAddon extends blueprints.addons.HelmAddOn {

  readonly options: nvidiaDevicePluginAddOnProps;

  constructor(props: nvidiaDevicePluginAddOnProps) {
    super({ ...defaultProps, ...props });
    this.options = this.props as nvidiaDevicePluginAddOnProps;
  }

  deploy(clusterInfo: blueprints.ClusterInfo): Promise<Construct> {
    const chart = this.addHelmChart(clusterInfo, {
        nodeSelector: {
          "karpenter.k8s.aws/instance-gpu-manufacturer": "nvidia"
        },
        tolerations: [
          {
            effect: "NoSchedule",
            key: "runtime",
            operator: "Exists"
          },
          {
            effect: "NoSchedule",
            key: "nvidia.com/gpu",
            operator: "Exists"
          },
        ]
      },
      true, true
    );

    return Promise.resolve(chart);
  }
}