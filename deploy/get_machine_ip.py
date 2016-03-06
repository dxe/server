#!/usr/bin/env python
import json
from boto3.session import Session

def auto_scaling_group_name():
    with open('terraform.tfstate') as f:
        tfstate = json.load(f)
        return tfstate['modules'][0]['resources']['aws_autoscaling_group.server']['primary']['id']

def get_machine_ip():
    session = Session(region_name='us-east-1')
    asg_client = session.client('autoscaling')

    name = auto_scaling_group_name()
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[name])
    instance_id = asg_response['AutoScalingGroups'][0]['Instances'][0]['InstanceId']

    ec2_client = session.client('ec2')
    instances = ec2_client.describe_instances(InstanceIds=[instance_id])
    return instances['Reservations'][0]['Instances'][0]['PublicIpAddress']

if __name__ == '__main__':
    print get_machine_ip()
