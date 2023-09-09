import hashlib

import boto3

AWS_DB_TABLE_NAME = "ec2_instances"
AWS_REGION = "us-east-2"


def get_hash(name: str):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


def ec2_get_running_instances():
    ec2 = boto3.resource("ec2")

    return ec2.instances.filter(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "availability-zone", "Values": [f"{AWS_REGION}*"]},
        ]
    )


def ec2_get_instance_name(ec2_instance):
    for tag in ec2_instance.tags:
        if tag["Key"] == "Name":
            return tag["Value"]


def instance_in_dynamo(instance):
    dynamodb_resource = boto3.resource("dynamodb")
    ec2_table = dynamodb_resource.Table(AWS_DB_TABLE_NAME)

    return "Item" in ec2_table.get_item(Key={"id": ec2_get_instance_name(instance)})


def get_root_device_id(instance):
    root_device = instance.root_device_name
    root_vol_id = ""
    vol_to_name = {}

    for volume in instance.block_device_mappings:
        vol_to_name[volume["Ebs"]["VolumeId"]] = volume["DeviceName"]

        if root_device == volume["DeviceName"]:
            root_vol_id = volume["Ebs"]["VolumeId"]

    return root_vol_id, vol_to_name


def get_extra_volumes(instance, root_vol_id, vol_to_name):
    extra_volumes = []
    for volume in instance.volumes.all():
        if volume.id != root_vol_id:
            ebs_volume = {
                "device_name": vol_to_name[volume.id],
                "volume_size": volume.size,
                "volume_type": volume.volume_type,
            }
            extra_volumes.append(ebs_volume)

    return extra_volumes


def get_root_volume(instance, root_vol_id, vol_to_name):
    for volume in instance.volumes.all():
        if volume.id == root_vol_id:
            return {
                "device_name": vol_to_name[volume.id],
                "volume_size": volume.size,
                "volume_type": volume.volume_type,
            }


def dynamo_build_item(instance):
    root_vol_id, vol_to_name = get_root_device_id(instance)

    return {
        "id": ec2_get_instance_name(instance),
        "name": ec2_get_instance_name(instance),
        "instance_id": instance.instance_id,
        "subnet_id": instance.subnet_id,
        "ami_filter": "N/A",
        "ami_id": instance.image_id,
        "discovered": True,
        "imported": False,
        "operational": True,
        "region": AWS_REGION,
        "type": instance.instance_type,
        "root_block_device": get_root_volume(instance, root_vol_id, vol_to_name),
        "ebs_block_devices": get_extra_volumes(instance, root_vol_id, vol_to_name),
    }


def dynamo_put_item(instance):
    dynamodb_resource = boto3.resource("dynamodb")
    ec2_table = dynamodb_resource.Table(AWS_DB_TABLE_NAME)

    ec2_data = dynamo_build_item(instance)

    ec2_table.put_item(Item=ec2_data)


if __name__ == "__main__":
    ec2_instances = ec2_get_running_instances()

    import_list = []
    for instance in ec2_instances:
        if not instance_in_dynamo(instance):
            dynamo_put_item(instance)
