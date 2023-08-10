import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as path from 'path';
import { IBucket } from 'aws-cdk-lib/aws-s3';


export class FrontendApiConstruct extends Construct {
    constructor(scope: Construct, id: string, outputBucket: IBucket, props?: cdk.StackProps) {
        super(scope, id);

        const sns_topic = new sns.Topic(this, 'Topic', {
            displayName: "Notification-" + cdk.Aws.STACK_NAME,
        });

        const lambdaFunction = new lambda.Function(this, 'MyLambda', {
            code: lambda.Code.fromAsset(path.join(__dirname, 'src/lambda')),
            handler: 'app.lambda_handler',
            runtime: lambda.Runtime.PYTHON_3_9,
            environment: {
                "SNS_TOPIC_ARN": sns_topic.topicArn,
                "S3_OUTPUT_BUCKET": outputBucket.bucketName
            }
        });

        sns_topic.grantPublish(lambdaFunction);

        const api = new apigw.LambdaRestApi(this, 'myapi', {
            handler: lambdaFunction,
            proxy: true
        });

    }
}
