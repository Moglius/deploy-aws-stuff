import json

import boto3
from django.contrib import admin
from django.core import serializers

from .models import BlockDevice, EC2Server

AWS_DB_TABLE_NAME = "ec2_instances"
AWS_REGION = "us-east-2"


def dynamo_build_item(instance_list):
    instance = instance_list[0]
    serialized_data = serializers.serialize(
        "json", instance_list, use_natural_foreign_keys=True
    )
    json_object = json.loads(serialized_data)
    dynamo_obj = json_object[0]["fields"]
    dynamo_obj["id"] = dynamo_obj["name"]
    dynamo_obj["root_block_device"] = instance.root_block_device.get_json_repr()
    dynamo_obj["ebs_block_devices"] = [
        block.get_json_repr() for block in instance.ebs_block_devices.all()
    ]

    return dynamo_obj


def dynamo_put_item(instance_list):
    dynamodb_resource = boto3.resource("dynamodb")
    ec2_table = dynamodb_resource.Table(AWS_DB_TABLE_NAME)

    ec2_data = dynamo_build_item(instance_list)

    ec2_table.put_item(Item=ec2_data)


class BlockDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_name", "volume_size", "volume_type")


class EC2ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "operational", "region", "type")

    def save_related(self, request, form, formsets, change):
        super(EC2ServerAdmin, self).save_related(request, form, formsets, change)
        dynamo_put_item([form.instance])


admin.site.register(BlockDevice, BlockDeviceAdmin)
admin.site.register(EC2Server, EC2ServerAdmin)
