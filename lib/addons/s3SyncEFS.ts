import * as blueprints from '@aws-quickstart/eks-blueprints';
import { ClusterAddOn, ClusterInfo } from '@aws-quickstart/eks-blueprints';
import { Construct } from "constructs";
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as iam from "aws-cdk-lib/aws-iam"
import * as datasync from 'aws-cdk-lib/aws-datasync';

export interface S3SyncEFSAddOnProps {
  bucketArn: string,
  efsFilesystem: efs.IFileSystem
}

export class S3SyncEFSAddOn implements ClusterAddOn {

  readonly options: S3SyncEFSAddOnProps;

  constructor(props: S3SyncEFSAddOnProps) {
    this.options = props
  }

  @blueprints.utils.dependable("SharedComponentAddOn")

  deploy(clusterInfo: ClusterInfo): Promise<Construct> {
    const cluster = clusterInfo.cluster;

    const srcBucket = s3.Bucket.fromBucketArn(cluster.stack, "SrcBucket", this.options.bucketArn)

    const s3Role = new iam.Role(cluster.stack, "DataSyncS3Role", {
      assumedBy: new iam.ServicePrincipal("datasync.amazonaws.com")
    })

    srcBucket.grantReadWrite(s3Role)

    const srcLocation = new datasync.CfnLocationS3(cluster.stack, "SrcLocationS3", {
      s3Config: {
        bucketAccessRoleArn: s3Role.roleArn
      },
      s3StorageClass: "STANDARD",
      s3BucketArn: this.options.bucketArn
    })

    srcLocation.node.addDependency(s3Role)
    srcLocation.node.addDependency(srcBucket)

    const efsSubnetArn = cdk.Arn.format({
      partition: cdk.Aws.PARTITION,
      service: "ec2",
      region: cdk.Aws.REGION,
      account: cdk.Aws.ACCOUNT_ID,
      resource: "subnet",
      resourceName: cluster.vpc.privateSubnets[0].subnetId
    })

    //TODO: Find EFS Security Group Name
    const efsSgArn = cdk.Arn.format({
      partition: cdk.Aws.PARTITION,
      service: "ec2",
      region: cdk.Aws.REGION,
      account: cdk.Aws.ACCOUNT_ID,
      resource: "security-group",
      resourceName: this.options.efsFilesystem.connections.securityGroups[0].securityGroupId
    })

    const dstLocation = new datasync.CfnLocationEFS(cluster.stack, "DstLocationEFS", {
      ec2Config: {
        securityGroupArns: [efsSgArn],
        subnetArn: efsSubnetArn
      },
      efsFilesystemArn: this.options.efsFilesystem.fileSystemArn
    })

    dstLocation.node.addDependency(this.options.efsFilesystem.mountTargetsAvailable)

    const dataSyncTask = new datasync.CfnTask(cluster.stack, "DataSyncTask", {
      sourceLocationArn: srcLocation.attrLocationArn,
      destinationLocationArn: dstLocation.attrLocationArn,
      options: {
        atime: "BEST_EFFORT",
        bytesPerSecond: -1,
        gid: "INT_VALUE",
        logLevel: "OFF",
        mtime: "PRESERVE",
        overwriteMode: "ALWAYS",
        posixPermissions: "PRESERVE",
        preserveDeletedFiles: "REMOVE",
        preserveDevices: "NONE",
        taskQueueing: "ENABLED",
        transferMode: "CHANGED",
        uid: "INT_VALUE",
        verifyMode: "ONLY_FILES_TRANSFERRED"
      }
    })

    const schedulerRole = new iam.Role(cluster.stack, "SchedulerRole", {
      assumedBy: new iam.ServicePrincipal("scheduler.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("AWSDataSyncFullAccess")
      ]
    })

    const dataSyncScheduler = new cdk.CfnResource(cluster.stack, "dataSyncScheduler", {
      type: "AWS::Scheduler::Schedule",
      properties: {
        Name: "dataSyncScheduler",
        Description: "",
        State: "ENABLED",
        GroupName: "default",
        ScheduleExpression: "rate(1 minutes)",
        FlexibleTimeWindow: {
          Mode: "OFF"
        },
        Target: {
          Arn: "arn:aws:scheduler:::aws-sdk:datasync:startTaskExecution",
          Input: JSON.stringify({
            TaskArn: dataSyncTask.attrTaskArn
          }),
          RoleArn: schedulerRole.roleArn
        }
      }
    })

    return Promise.resolve(dataSyncScheduler);
  }
}