import * as blueprints from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";

export interface dcgmExporterAddOnProps extends blueprints.addons.HelmAddOnUserProps {
}

export const defaultProps: blueprints.addons.HelmAddOnProps & dcgmExporterAddOnProps = {
  chart: 'dcgm-exporter',
  name: 'dcgmExporterAddOn',
  namespace: 'kube-system',
  release: 'dcgm',
  version: '3.4.0',
  repository: 'https://nvidia.github.io/dcgm-exporter/helm-charts',
  values: {
    serviceMonitor: {
      enabled: false
    },
    affinity: {
      nodeAffinity: {
        requiredDuringSchedulingIgnoredDuringExecution: {
          nodeSelectorTerms: [{
              matchExpressions: [{
                  key: "karpenter.k8s.aws/instance-gpu-count",
                  operator: "Exists"
              }]
          }]
        }
      }
    },
    tolerations: [{
      key: "nvidia.com/gpu",
      operator: "Exists",
      effect: "NoSchedule"
    }, {
      key: "runtime",
      operator: "Exists",
      effect: "NoSchedule"
    }]
  }
}

export class dcgmExporterAddOn extends blueprints.addons.HelmAddOn {

  readonly options: dcgmExporterAddOnProps;

  constructor(props: dcgmExporterAddOnProps) {
    super({ ...defaultProps, ...props });
    this.options = this.props as dcgmExporterAddOnProps;
  }

  deploy(clusterInfo: blueprints.ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster;

    const chart = this.addHelmChart(clusterInfo, this.options.values, true, true);
    return Promise.resolve(chart);
  }
}