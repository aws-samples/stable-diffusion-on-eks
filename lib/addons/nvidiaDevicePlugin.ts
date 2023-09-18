import * as blueprints from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";

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