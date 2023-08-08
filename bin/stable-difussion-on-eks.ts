#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as constants from "../lib/constants";
import * as toolchain from "../lib/toolchain";
import * as control_plane from "../control_plane/component";
import * as data_plane from "../data_plane/component";

const app = new cdk.App();

