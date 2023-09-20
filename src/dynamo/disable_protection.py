import sys
from io import StringIO as sio

import boto3

"""
$ terraform plan -var-file=../data/ec2.tfvars -out tfplan.out |grep destroyed | \
    awk '{print $3}' | python ../dynamo/disable_protection.py
"""


def disable_termination_protection(ec2_list):
    ec2_res = boto3.resource("ec2")
    Filters = [
        {"Name": "instance-state-name", "Values": ["running", "stopped"]},
        {"Name": "tag:Name", "Values": ec2_list},
    ]
    instances = ec2_res.instances.filter(Filters=Filters)
    for instance in instances:
        ec2_res.Instance(instance.id).modify_attribute(
            DisableApiTermination={"Value": False}
        )


def get_ec2_name(raw_server):
    sub1, sub2 = '["', '"]'
    idx1 = raw_server.index(sub1)
    idx2 = raw_server.index(sub2)

    return raw_server[idx1 + len(sub1) : idx2]


if __name__ == "__main__":
    raw_ec2_names = sys.stdin.read()

    ec2_list = [get_ec2_name(raw_ec2_name) for raw_ec2_name in sio(raw_ec2_names)]

    disable_termination_protection(ec2_list)
