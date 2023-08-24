import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import * as eks from "aws-cdk-lib/aws-eks";
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';

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

        const CloudWatchLogsWritePolicy = new iam.PolicyStatement({
            actions: [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents"
            ],
            resources: ["*"],
        })

        const addOns: Array<blueprints.ClusterAddOn> = [
            new blueprints.addons.VpcCniAddOn(),
            new blueprints.addons.CoreDnsAddOn(),
            new blueprints.addons.KubeProxyAddOn(),
            new blueprints.addons.EbsCsiDriverAddOn(),
            new blueprints.addons.EfsCsiDriverAddOn(),
            new blueprints.addons.AwsLoadBalancerControllerAddOn(),
            new blueprints.addons.KarpenterAddOn({ interruptionHandling: true }),
            new blueprints.addons.KedaAddOn(kedaParams),
            new blueprints.addons.ContainerInsightsAddOn(),
            new blueprints.addons.AwsForFluentBitAddOn({
                iamPolicies: [CloudWatchLogsWritePolicy],
                namespace: "amazon-cloudwatch",
                values: {
                    cloudWatchLogs: {
                        region: "us-west-2",
                    },
                    tolerations: [{
                        "key": "nvidia.com/gpu",
                        "operator": "Exists",
                        "effect": "NoSchedule"
                    }]
                }
            }),
        ];

        const blueprint = blueprints.EksBlueprint.builder()
            .version(eks.KubernetesVersion.V1_27)
            .addOns(...addOns)
            .build(scope, id + 'Stack');

        const cluster = blueprint.getClusterInfo().cluster

        const xrayDaemonSA = cluster.addServiceAccount('XrayDaemonSA', {
            name: 'xray-daemon',
            namespace: 'amazon-cloudwatch'
        })

        xrayDaemonSA.addToPrincipalPolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            resources: ["*"],
            actions: [
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords",
                "xray:GetSamplingRules",
                "xray:GetSamplingTargets",
                "xray:GetSamplingStatisticSummaries"
            ]
          }))

        const webUISA = cluster.addServiceAccount('WebUISA', {
            name: 'sd-webui-sa'
        })

        const modelBucket = s3.Bucket.fromBucketAttributes(this, 'ModelBucket', {
            bucketArn: 'arn:aws:s3:::sd-on-eks-pdx',
        });
        modelBucket.grantRead(webUISA);

        const inputQueue1 = new sqs.Queue(this, 'InputQueue1');
        inputQueue1.grantConsumeMessages(webUISA);

        this.outputBucket = new s3.Bucket(this, 'sd-output-pdx');
        this.outputBucket.grantWrite(webUISA);
        this.outputBucket.grantPutAcl(webUISA);

        const notificationTopic = new sns.Topic(this, 'sd-notification-pdx');
        notificationTopic.grantPublish(webUISA);

    }
}