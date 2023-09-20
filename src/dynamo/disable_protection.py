import sys
from io import StringIO as sio

import boto3

"""
$ terraform plan -var-file=../data/ec2.tfvars -out tfplan.out |grep destroyed | \
    awk '{print $3}' | python ../dynamo/disable_protection.py
"""

EC2_RES = boto3.resource("ec2")
EC2_FILTER_STATES = ["running", "stopped"]


def disable_termination_protection(instances):
    for instance in instances:
        EC2_RES.Instance(instance.id).modify_attribute(
            DisableApiTermination={"Value": False}
        )


def get_aws_instances_from_ec2_names(ec2_list):
    Filters = [
        {"Name": "instance-state-name", "Values": EC2_FILTER_STATES},
        {"Name": "tag:Name", "Values": ec2_list},
    ]
    return EC2_RES.instances.filter(Filters=Filters)


def get_ec2_name(raw_server):
    sub1, sub2 = '["', '"]'
    idx1 = raw_server.index(sub1)
    idx2 = raw_server.index(sub2)
    return raw_server[idx1 + len(sub1) : idx2]


def get_ec2_names_to_disable_protection():
    raw_ec2_names = sys.stdin.read()
    return [get_ec2_name(raw_ec2_name) for raw_ec2_name in sio(raw_ec2_names)]


if __name__ == "__main__":
    ec2_list = get_ec2_names_to_disable_protection()
    instances = get_aws_instances_from_ec2_names(ec2_list)
    disable_termination_protection(instances)
