import json
from string import Template

import boto3
import hcl2
from ec2_classes import EC2

AWS_DB_TABLE_NAME = "ec2_instances"
AWS_REGION = "us-east-2"
TEMPLATE_PATH = "src/data/import.tpl"
IMPORT_FILE_PATH = "src/terraform2/import.tf"
TEMP_FILE_PATH = "src/data/ec2.tfvars.temp"
FILE_PATH = "src/data/ec2.tfvars"


def scan_table(*, TableName, **kwargs):
    dynamo_client = boto3.client("dynamodb")
    paginator = dynamo_client.get_paginator("scan")

    for page in paginator.paginate(TableName=TableName, **kwargs):
        yield from page["Items"]


def instance_needs_import(ec2_item):
    return not ec2_item["imported"]["BOOL"] and ec2_item["discovered"]["BOOL"]


def get_import_struct(ec2_item):
    return {"name": ec2_item["name"]["S"], "instance_id": ec2_item["instance_id"]["S"]}


def get_json(ec2_instance):
    return {
        "id": ec2_instance["id"]["S"],
        "name": ec2_instance["name"]["S"],
        "type": ec2_instance["type"]["S"],
        "region": ec2_instance["region"]["S"],
        "subnet_id": ec2_instance["subnet_id"]["S"],
        "ami_id": ec2_instance["ami_id"]["S"],
        "ami_filter": ec2_instance["ami_filter"]["S"],
        "root_block_device": ec2_instance["root_block_device"]["M"],
        "ebs_block_devices": ec2_instance["ebs_block_devices"]["L"],
    }


if __name__ == "__main__":
    ec2_import_list = []
    ec2_tfvar_list = []
    for ec2_item in scan_table(TableName=AWS_DB_TABLE_NAME):
        if instance_needs_import(ec2_item):
            ec2_import_list.append(get_import_struct(ec2_item))
            ec2_tfvar_list.append(ec2_item)

    with open(TEMPLATE_PATH, "r") as template, open(IMPORT_FILE_PATH, "w") as outfile:
        src = Template(template.read())

        mylist = []
        for imp_instance in ec2_import_list:
            mylist.append(src.substitute(imp_instance))

        for imp in mylist:
            outfile.write(f"{imp}\n")

    operation_set = set()
    with open(TEMP_FILE_PATH, "r") as file, open(FILE_PATH, "w") as outfile:
        dictionary = hcl2.load(file)

        for ec2_json in dictionary["configuration"]:
            operation_set.add(EC2(ec2_json))

        for ec2_instance in ec2_tfvar_list:
            operation_set.add(EC2(get_json(ec2_instance)))

        mylist = []
        for server in sorted(operation_set):
            mylist.append(server.get_json_data())

        json_object = json.dumps(mylist, indent=2)

        outfile.write(f"configuration = {json_object}\n")
