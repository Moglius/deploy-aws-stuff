import json

import boto3
import hcl2
from ec2_classes import EC2, EC2IMAGE

TEMP_FILE_PATH = "src/data/ec2.tfvars.temp"
FILE_PATH = "src/data/ec2.tfvars"
AWS_OWNER = "456639116688"
AWS_REGION = "us-east-2"
AWS_DB_TABLE_NAME = "ec2_instances"


def set_ami_id_in_dynamodb(tablename, primary_key, ami_id):
    dynamo_client = boto3.resource("dynamodb").Table(AWS_DB_TABLE_NAME)
    dynamo_client.update_item(
        Key={"id": primary_key},
        UpdateExpression="set ami_id=:new_ami_id",
        ExpressionAttributeValues={":new_ami_id": ami_id},
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


if __name__ == "__main__":
    operation_set = set()
    retired_set = set()

    for item in scan_table(TableName=AWS_DB_TABLE_NAME):
        ec2_instance = EC2(
            {
                "id": item["id"]["S"],
                "name": item["name"]["S"],
                "type": item["type"]["S"],
                "region": item["region"]["S"],
                "ami_id": item["ami_id"]["S"],
                "ami_filter": item["ami_filter"]["S"],
            }
        )

        if not ec2_instance.get_ami_id():
            image = get_latest_image(ec2_instance.get_ami_filter())
            ec2_instance.set_ami_id(image.get_ami_id())
            set_ami_id_in_dynamodb(
                AWS_DB_TABLE_NAME, ec2_instance.get_primary_key(), image.get_ami_id()
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
