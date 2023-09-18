import { KubernetesManifest } from "aws-cdk-lib/aws-eks";
import * as eks from "aws-cdk-lib/aws-eks";

export type Values = {
  [key: string]: any;
};

export function createNamespace(id: string, name: string, cluster: eks.ICluster, overwrite?: boolean, prune?: boolean, annotations?: Values, labels?: Values) {
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