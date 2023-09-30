"""
json_data = {}
json_data["targets"] = {}
json_data["targets"]["i-040c8a344a26b0148"] = {
    "target_id" : "i-040c8a344a26b0148",
    "port" : 80
}
json_data["targets"]["i-026df02511395f487"] = {
    "target_id" : "i-026df02511395f487",
    "port" : 80
}
"""

import json

import boto3
import hcl2
from boto3.dynamodb.types import TypeDeserializer
from lb_classes import ALB

AWS_DB_TABLE_NAME = "albs"
AWS_REGION = "us-east-2"
TEMP_FILE_PATH = "src/data/albs.tfvars.temp"
FILE_PATH = "src/data/albs.tfvars"


def aws_scan_dynamodb_table(*, table_name, **kwargs):
    dynamo_client = boto3.client("dynamodb")
    paginator = dynamo_client.get_paginator("scan")

    for page in paginator.paginate(TableName=table_name, **kwargs):
        yield from page["Items"]


def convert_from_dynamodb_to_json(item):
    d = TypeDeserializer()
    return {k: d.deserialize(value=v) for k, v in item.items()}


def aws_get_target_instances(discovery_tag):
    ec2_res = boto3.resource("ec2", AWS_REGION)
    filters = [
        {"Name": "instance-state-name", "Values": ["running"]},
        {"Name": "tag:lb-target", "Values": [discovery_tag]},
    ]
    return ec2_res.instances.filter(Filters=filters)


def aws_create_or_update_albs(cur_alb_set, retired_alb_set):
    for dynamodb_alb in aws_scan_dynamodb_table(table_name=AWS_DB_TABLE_NAME):
        json_alb = convert_from_dynamodb_to_json(dynamodb_alb)
        alb_instance = ALB(json_alb)
        target_instances = aws_get_target_instances(
            discovery_tag=json_alb["discovery_tag"]
        )
        for target_instance in target_instances:
            alb_instance.add_subnet_id(target_instance.subnet_id)
            alb_instance.add_target(target_instance.instance_id)
            alb_instance.add_availability_zone(
                target_instance.placement["AvailabilityZone"]
            )
        if alb_instance.is_operational():
            cur_alb_set.add(alb_instance)
        else:
            retired_alb_set.add(alb_instance)


def files_get_albs(cur_alb_set, retired_alb_set):
    with open(TEMP_FILE_PATH, "r") as file:
        dictionary = hcl2.load(file)

        for alb in dictionary["configuration"]:
            alb_instance = ALB(alb)
            cur_alb_set.add(alb_instance)

    return cur_alb_set - retired_alb_set


def files_create_tfvars_file(final_alb_set):
    sorted_albs = []
    for alb in sorted(final_alb_set):
        sorted_albs.append(alb.get_json_data())
    json_albs = json.dumps(sorted_albs, indent=2, default=int)

    with open(FILE_PATH, "w") as outfile:
        outfile.write(f"configuration = {json_albs}\n")


if __name__ == "__main__":
    cur_alb_set, retired_alb_set = set(), set()

    aws_create_or_update_albs(cur_alb_set, retired_alb_set)

    final_alb_set = files_get_albs(cur_alb_set, retired_alb_set)

    files_create_tfvars_file(final_alb_set)
