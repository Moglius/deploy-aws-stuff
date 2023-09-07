from string import Template

import boto3

AWS_DB_TABLE_NAME = "ec2_instances"
AWS_REGION = "us-east-2"
TEMPLATE_PATH = "../data/import.tpl"
IMPORT_FILE_PATH = "../terraform2/import.tf"


def scan_table(*, TableName, **kwargs):
    dynamo_client = boto3.client("dynamodb")
    paginator = dynamo_client.get_paginator("scan")

    for page in paginator.paginate(TableName=TableName, **kwargs):
        yield from page["Items"]


def instance_needs_import(ec2_item):
    return not ec2_item["imported"]["BOOL"] and ec2_item["discovered"]["BOOL"]


def get_import_struct(ec2_item):
    return {"name": ec2_item["name"]["S"], "instance_id": ec2_item["instance_id"]["S"]}


if __name__ == "__main__":
    ec2_import_list = []
    for ec2_item in scan_table(TableName=AWS_DB_TABLE_NAME):
        if instance_needs_import(ec2_item):
            ec2_import_list.append(get_import_struct(ec2_item))

    with open(TEMPLATE_PATH, "r") as template, open(IMPORT_FILE_PATH, "w") as outfile:
        src = Template(template.read())

        mylist = []
        for imp_instance in ec2_import_list:
            mylist.append(src.substitute(imp_instance))

        for imp in mylist:
            outfile.write(f"{imp}\n")
