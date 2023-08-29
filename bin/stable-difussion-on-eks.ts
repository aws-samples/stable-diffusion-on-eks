#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as Constants from "../lib/constants";
import * as Toolchain from "../lib/toolchain";
import ControlPlane from "../lib/control_plane";
import DataPlaneStack from "../lib/data_plane";

const app = new cdk.App();

const sandboxEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
}

const dataPlaneStack = new DataPlaneStack(app, Constants.APP_NAME + "DataPlane", {
  modelBucketArn: 'arn:aws:s3:::sd-on-eks-pdx',
  modelsRuntime: [
    {
      name: "sdruntime1",
      modelFilename: "v1-5-pruned-emaonly.ckpt"
    }, {
      name: "sdruntime2",
      modelFilename: "1234567",
      extraValues: {
        sdWebuiInferenceApi: {
          labels: {
            runtime: "second"
          },
          replicas: 1
        }
      }
    }
  ],
  generateDynamic: true
  },
  { env: sandboxEnv });

const controlPlaneStack = new ControlPlane(app, Constants.APP_NAME + "ControlPlane", { env: sandboxEnv });
