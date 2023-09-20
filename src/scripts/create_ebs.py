import json

import boto3
import hcl2
from ec2_classes import EBS

VOL_TEMP_FILE_PATH = "src/data/ebs_volumes.tfvars.temp"
VOL_FILE_PATH = "src/data/ebs_volumes.tfvars"

ATT_TEMP_FILE_PATH = "src/data/ebs_attachments.tfvars.temp"
ATT_FILE_PATH = "src/data/ebs_attachments.tfvars"

AWS_DB_TABLE_NAME = "ec2_instances"


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


def ebs_should_be_created(item):
    return (
        item["instance_id"]["S"] != ""
        and item["instance_az"]["S"] != ""
        and item["ebs_block_devices"]["L"]
    )


def get_ebs_devices(item):
    instance_name = item["id"]["S"]
    instance_id = item["instance_id"]["S"]
    instance_az = item["instance_az"]["S"]

    return_list = set()
    for ebs_volume in item["ebs_block_devices"]["L"]:
        return_list.add(
            EBS(
                instance_name=instance_name,
                instance_id=instance_id,
                instance_az=instance_az,
                volume_id=ebs_volume["M"]["volume_id"]["S"],
                volume_type=ebs_volume["M"]["volume_type"]["S"],
                volume_size=ebs_volume["M"]["volume_size"]["N"],
                device_name=ebs_volume["M"]["device_name"]["S"],
            )
        )

    return return_list


def create_ebs_volumes_file(operational_set, retired_set):
    with open(VOL_TEMP_FILE_PATH, "r") as file, open(VOL_FILE_PATH, "w") as outfile:
        dictionary = hcl2.load(file)

        for item in dictionary["ebs_volumes"]:
            operational_set.add(
                EBS(
                    instance_name=item["instance_name"],
                    instance_id=item["instance_id"],
                    instance_az=item["instance_az"],
                    volume_type=item["volume_type"],
                    volume_size=item["volume_size"],
                    device_name=item["device_name"],
                )
            )

        final_set = operational_set - retired_set

        mylist = []
        for ebs_vol in sorted(final_set):
            mylist.append(ebs_vol.get_ebs_vol_json_data())

        json_object = json.dumps(mylist, indent=2)

        outfile.write(f"ebs_volumes = {json_object}\n")


def create_ebs_attachment_file(operational_set, retired_set):
    with open(ATT_TEMP_FILE_PATH, "r") as file, open(ATT_FILE_PATH, "w") as outfile:
        dictionary = hcl2.load(file)

        for item in dictionary["ebs_attachments"]:
            operational_set.add(
                EBS(
                    instance_name=item["instance_name"],
                    instance_id=item["instance_id"],
                    volume_id=item["volume_id"],
                    device_name=item["device_name"],
                    volume_type="",
                    volume_size="",
                )
            )

        final_set = operational_set - retired_set

        mylist = []
        for ebs_vol in sorted(final_set):
            if ebs_vol.volume_id:
                mylist.append(ebs_vol.get_ebs_att_json_data())

        json_object = json.dumps(mylist, indent=2)

        outfile.write(f"ebs_attachments = {json_object}\n")


if __name__ == "__main__":
    operational_set = set()
    retired_set = set()

    for item in scan_table(TableName=AWS_DB_TABLE_NAME):
        if ebs_should_be_created(item):
            ebs_set = get_ebs_devices(item)
            if item["operational"]["BOOL"]:
                operational_set.update(ebs_set)
            else:
                retired_set.update(ebs_set)

    create_ebs_volumes_file(operational_set, retired_set)
    create_ebs_attachment_file(operational_set, retired_set)
