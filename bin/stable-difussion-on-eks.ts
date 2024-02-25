#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import DataPlaneStack from "../lib/dataPlane";
import { parse } from 'yaml'
import * as fs from 'fs'
import { validateConfig } from '../lib/utils/validateConfig';

const app = new cdk.App();

const env = {
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
const props = parse(file)

if (validateConfig(props)) {
  const dataPlaneStack = new DataPlaneStack(app, props.stackName, props, {
    env: env,
    description: "(SO9306) - Guidance for asynchronous image generation with Stable Diffusion on AWS ["
  });
} else {
  console.log("Deployment failed due to failed validation. Please check and try again.")
}
