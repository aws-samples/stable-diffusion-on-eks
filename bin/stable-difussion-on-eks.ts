#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as Constants from "../lib/constants";
import * as Toolchain from "../lib/toolchain";
import ControlPlane from "../control_plane/component";
import DataPlaneStack from "../data_plane/component";

const app = new cdk.App();

const sanboxEnv = {
    // account: "057313215210",
    region: "us-west-2",
}

const dataPlaneSandboxStack = new DataPlaneStack(app, Constants.APP_NAME + "DataPlaneSandbox", {env: sanboxEnv});

const controlPlaneSandboxStack = new ControlPlane(app, Constants.APP_NAME + "ControlPlaneSandbox", {env: sanboxEnv});