#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import * as Constants from "../lib/constants";
import * as Toolchain from "../lib/toolchain";
import ControlPlane from "../lib/control_plane";
import DataPlaneStack from "../lib/data_plane";
import { parse } from 'yaml'
import * as fs from 'fs'

const app = new cdk.App();

const sandboxEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
}

let filename: string

if ("CDK_CONFIG_PATH" in process.env) {
  filename = process.env.CDK_CONFIG_PATH as string
} else {
  filename = 'config.yaml'
}

const file = fs.readFileSync(filename, 'utf8')
const dataPlaneProps = parse(file)

const dataPlaneStack = new DataPlaneStack(app, Constants.APP_NAME + "DataPlane", dataPlaneProps, { env: sandboxEnv });

const controlPlaneStack = new ControlPlane(app, Constants.APP_NAME + "ControlPlane", { env: sandboxEnv });
