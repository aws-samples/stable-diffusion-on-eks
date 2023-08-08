import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { KubernetesVersion } from 'aws-cdk-lib/aws-eks';

export class EksClusterConstruct extends Construct {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id);

        const addOns: Array<blueprints.ClusterAddOn> = [
            new blueprints.addons.VpcCniAddOn(),
            new blueprints.addons.CoreDnsAddOn(),
            new blueprints.addons.KubeProxyAddOn(),
            new blueprints.addons.EbsCsiDriverAddOn(),
            new blueprints.addons.EfsCsiDriverAddOn()
        ];

        const blueprint = blueprints.EksBlueprint.builder()
            .version(KubernetesVersion.V1_27)
            .addOns(...addOns)
            .teams()
            .build(scope, id + 'Stack');
    }
}