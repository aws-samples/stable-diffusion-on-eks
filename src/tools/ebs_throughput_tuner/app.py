# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3, os

def get_ebs_volume_id(instance_id):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        volume_id = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][-1]['Ebs']['VolumeId']
        return volume_id
    except Exception as e:
        print("Error:", e)
        return None

def get_instance_tag(instance, key):
    for tag in instance.get('Tags', []):
        if tag['Key'] == key:
            return tag['Value']
    return None

def modify_ebs_throughput_and_iops(volume_id, throughput, iops):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.modify_volume(VolumeId=volume_id, Throughput=throughput, Iops=iops)
        print("Successfully modified EBS throughput of " + volume_id)
    except Exception as e:
        print("Error:", e)

# Entrypoint
def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    instance_id = event['detail']['instance-id']
    print (f"Process with instance " + instance_id)
    target_ec2_tag_key = os.environ['TARGET_EC2_TAG_KEY']
    target_ec2_tag_value = os.environ['TARGET_EC2_TAG_VALUE']
    # Get the instance tag
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    instance_tag_value = get_instance_tag(instance, target_ec2_tag_key)
    volume_id = get_ebs_volume_id(instance_id)
    if instance_tag_value:
        # Determine if EBS throughput needs to be modified based on instance name
        if target_ec2_tag_value in instance_tag_value:
            print (f"Got matching tag from " + instance_id + " ,processing...")
            throughput_value = int(os.environ['THROUGHPUT_VALUE'])  # Modify throughput
            IOPS_value = int(os.environ['IOPS_VALUE']) # Modify IOPS
            modify_ebs_throughput_and_iops(volume_id, throughput_value, IOPS_value)
        else:
            print (f"Skipped " + instance_id)
