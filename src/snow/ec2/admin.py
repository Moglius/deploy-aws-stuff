import json

import boto3
from django.contrib import admin
from django.core import serializers

from .models import (
    ALB,
    BlockDevice,
    EC2Server,
    HealthCheck,
    Listener,
    SecurityGroup,
    Tag,
    TargetGroup,
)

AWS_DB_TABLE_NAME = "ec2_instances"
AWS_ALB_DB_TABLE_NAME = "albs"
AWS_REGION = "us-east-2"


def set_ec2_extra_dynamo_data(dynamo_obj, instance):
    dynamo_obj["root_block_device"] = instance.root_block_device.get_json_repr()
    dynamo_obj["ebs_block_devices"] = [
        block.get_json_repr() for block in instance.ebs_block_devices.all()
    ]
    dynamo_obj["tags"] = instance.get_json_tags()


def set_alb_extra_dynamo_data(dynamo_obj, instance):
    dynamo_obj["security_groups"] = [sg.sg_id for sg in instance.security_groups.all()]
    dynamo_obj["http_tcp_listeners"] = [instance.get_http_tcp_listener()]
    dynamo_obj["target_groups"] = [instance.get_target_group()]


def dynamo_build_item(instance_list, item_type):
    instance = instance_list[0]
    serialized_data = serializers.serialize(
        "json", instance_list, use_natural_foreign_keys=True
    )
    json_object = json.loads(serialized_data)
    dynamo_obj = json_object[0]["fields"]
    dynamo_obj["id"] = dynamo_obj["name"]

    if item_type == "ec2":
        set_ec2_extra_dynamo_data(dynamo_obj, instance)
    else:
        set_alb_extra_dynamo_data(dynamo_obj, instance)

    print(dynamo_obj)

    return dynamo_obj


def dynamo_put_item(instance_list, table, item_type):
    dynamodb_resource = boto3.resource("dynamodb")
    ec2_table = dynamodb_resource.Table(table)

    ec2_data = dynamo_build_item(instance_list, item_type)

    ec2_table.put_item(Item=ec2_data)


class TagAdmin(admin.ModelAdmin):
    list_display = ("key", "value")


class BlockDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_name", "volume_size", "volume_type")


class EC2ServerAdmin(admin.ModelAdmin):
    readonly_fields = ("get_tags",)
    list_display = ("name", "operational", "region", "type", "get_tags")

    def get_tags(self, obj):
        return ", ".join(sorted([f"{tag.key}:{tag.value}" for tag in obj.tags.all()]))

    def save_related(self, request, form, formsets, change):
        super(EC2ServerAdmin, self).save_related(request, form, formsets, change)
        dynamo_put_item([form.instance], table=AWS_DB_TABLE_NAME, item_type="ec2")


class ALBAdmin(admin.ModelAdmin):
    list_display = ("name", "vpc_id", "discovery_tag")

    def save_related(self, request, form, formsets, change):
        super(ALBAdmin, self).save_related(request, form, formsets, change)
        dynamo_put_item([form.instance], table=AWS_ALB_DB_TABLE_NAME, item_type="alb")


admin.site.register(BlockDevice, BlockDeviceAdmin)
admin.site.register(EC2Server, EC2ServerAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(SecurityGroup)
admin.site.register(Listener)
admin.site.register(HealthCheck)
admin.site.register(TargetGroup)
admin.site.register(ALB, ALBAdmin)
