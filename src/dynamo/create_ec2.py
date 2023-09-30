import json

import boto3
import hcl2
from ec2_classes import EC2, EC2IMAGE

TEMP_FILE_PATH = "src/data/ec2.tfvars.temp"
FILE_PATH = "src/data/ec2.tfvars"
AWS_OWNER = "456639116688"
AWS_REGION = "us-east-2"
AWS_DB_TABLE_NAME = "ec2_instances"
AWS_VPC_ID = "vpc-022211da1d6546ff3"


def set_new_id_in_dynamodb(primary_key, new_id, replace_key):
    dynamo_client = boto3.resource("dynamodb").Table(AWS_DB_TABLE_NAME)
    dynamo_client.update_item(
        Key={"id": primary_key},
        UpdateExpression=f"set {replace_key}=:new_{replace_key}",
        ExpressionAttributeValues={f":new_{replace_key}": new_id},
        ReturnValues="UPDATED_NEW",
    )


def scan_table(*, TableName, **kwargs):
    dynamo_client = boto3.client("dynamodb")
    paginator = dynamo_client.get_paginator("scan")

    for page in paginator.paginate(TableName=TableName, **kwargs):
        yield from page["Items"]


def get_latest_image(ami_filter):
    ec2_client = boto3.client("ec2", region_name=AWS_REGION)

    images = ec2_client.describe_images(
        Owners=[AWS_OWNER],
        Filters=[
            {
                "Name": "name",
                "Values": [
                    f"{ami_filter}*",
                ],
            },
        ],
    )

    image_list = []
    for image in images["Images"]:
        ec2_image = EC2IMAGE(image)
        image_list.append(ec2_image)

    return sorted(image_list).pop()


def get_least_used_subnet_id():
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_subnets(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [
                    AWS_VPC_ID,
                ],
            },
        ],
    )

    subnet_id, max_value = "", 0
    for subnet in response["Subnets"]:
        if subnet["AvailableIpAddressCount"] > max_value:
            subnet_id, max_value = subnet["SubnetId"], subnet["AvailableIpAddressCount"]

    return subnet_id


def ec2_should_be_added(item):
    return (item["discovered"]["BOOL"] is False) or (
        item["discovered"]["BOOL"] and item["imported"]["BOOL"]
    )


if __name__ == "__main__":
    operation_set = set()
    retired_set = set()

    for item in scan_table(TableName=AWS_DB_TABLE_NAME):
        if ec2_should_be_added(item):
            ec2_instance = EC2(
                {
                    "id": item["id"]["S"],
                    "name": item["name"]["S"],
                    "type": item["type"]["S"],
                    "region": item["region"]["S"],
                    "subnet_id": item["subnet_id"]["S"],
                    "ami_id": item["ami_id"]["S"],
                    "ami_filter": item["ami_filter"]["S"],
                    "root_block_device": item["root_block_device"]["M"],
                    "ebs_block_devices": item["ebs_block_devices"]["L"],
                    "tags": item["tags"]["M"],
                }
            )

            if not ec2_instance.get_ami_id():
                image = get_latest_image(ec2_instance.get_ami_filter())
                ec2_instance.set_ami_id(image.get_ami_id())
                set_new_id_in_dynamodb(
                    ec2_instance.get_primary_key(), image.get_ami_id(), "ami_id"
                )

            if not ec2_instance.get_subnet_id():
                subnet_id = get_least_used_subnet_id()
                ec2_instance.set_subnet_id(subnet_id)
                set_new_id_in_dynamodb(
                    ec2_instance.get_primary_key(), subnet_id, "subnet_id"
                )

            if item["operational"]["BOOL"]:
                operation_set.add(ec2_instance)
            else:
                retired_set.add(ec2_instance)

    with open(TEMP_FILE_PATH, "r") as file, open(FILE_PATH, "w") as outfile:
        dictionary = hcl2.load(file)

        for item in dictionary["configuration"]:
            ec2_instance = EC2(item)
            operation_set.add(ec2_instance)

        final_set = operation_set - retired_set

        mylist = []
        for server in sorted(final_set):
            mylist.append(server.get_json_data())

        json_object = json.dumps(mylist, indent=2)

        outfile.write(f"configuration = {json_object}\n")
