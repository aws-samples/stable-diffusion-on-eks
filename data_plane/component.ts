import * as cdk from 'aws-cdk-lib';
import * as BackendWorkers from "./backend_workers/infrastructure";
import * as EventRouter from "./event_router/infrastructure";
import * as FrontendApi from "./frontend_api/infrastructure";
import * as Monitoring from "./monitoring/infrastructure";

export default class DataPlaneStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // const eksCluster = new BackendWorkers.EksClusterConstruct(this, "eksCluster");
    const frontApi = new FrontendApi.frontApiStack(this, "frontApi");
  }
}