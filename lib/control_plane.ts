import * as cdk from 'aws-cdk-lib';

export const NAME = "ControlPlane"

export default class ControlPlaneStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

    }
}