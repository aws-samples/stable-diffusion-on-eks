import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as eks from "aws-cdk-lib/aws-eks";
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';

export class EksClusterConstruct extends Construct {
    outputBucket: s3.IBucket;


    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id);

        const kedaParams = {
            podSecurityContextFsGroup: 1001,
            securityContextRunAsGroup: 1001,
            securityContextRunAsUser: 1001,
            irsaRoles: ["CloudWatchFullAccess", "AmazonSQSFullAccess"]
        }

        const addOns: Array<blueprints.ClusterAddOn> = [
            new blueprints.addons.VpcCniAddOn(),
            new blueprints.addons.CoreDnsAddOn(),
            new blueprints.addons.KubeProxyAddOn(),
            new blueprints.addons.EbsCsiDriverAddOn(),
            new blueprints.addons.EfsCsiDriverAddOn(),
            new blueprints.addons.KarpenterAddOn({ interruptionHandling: true }),
            new blueprints.addons.KedaAddOn(kedaParams),
        ];

        const blueprint = blueprints.EksBlueprint.builder()
            .version(eks.KubernetesVersion.V1_27)
            .addOns(...addOns)
            .build(scope, id + 'Stack');

        const cluster = blueprint.getClusterInfo().cluster

        const WebUISA = cluster.addServiceAccount('WebUISA', {
            name: 'sd-webui-sa',
        })

        const modelBucket = s3.Bucket.fromBucketAttributes(this, 'ModelBucket', {
            bucketArn: 'arn:aws:s3:::sd-on-eks-pdx',
        });
        modelBucket.grantRead(WebUISA);

        const karpenterNodeRole = iam.Role.fromRoleName(this, 'KarpenterNodeRole', cdk.Fn.importValue('SdOnEksDataPlaneSandboxeksClusterStackC763FDF9KarpenterNodeRoleName'));
        modelBucket.grantRead(karpenterNodeRole);

        const inputQueue1 = new sqs.Queue(this, 'InputQueue1');
        inputQueue1.grantConsumeMessages(WebUISA);

        this.outputBucket = new s3.Bucket(this, 'sd-output-pdx');
        this.outputBucket.grantWrite(WebUISA);
        this.outputBucket.grantPutAcl(WebUISA);

        const notificationTopic = new sns.Topic(this, 'sd-notification-pdx');
        notificationTopic.grantPublish(WebUISA);

    }
}