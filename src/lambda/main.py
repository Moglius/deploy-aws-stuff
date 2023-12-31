import os
from datetime import date

import boto3

ZONE_ID = os.environ["HOSTED_ZONE_ID"]
ZONE_DOMAIN = os.environ["HOSTED_ZONE_DOMAIN"]
DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]


def perform_dynamodb_update(hostname, ip_address, status):
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(DYNAMODB_TABLE)

    response = table.put_item(
        Item={
            "DNSId": str(hash(hostname)),
            "date": str(date.today()),
            "hostname": hostname,
            "ip_address": ip_address,
            "status": status,
        }
    )
    return response


def get_instance_private_ip(instance_id, instance_state):
    ec2 = boto3.client("ec2")

    instance_data = ec2.describe_instances(
        InstanceIds=[instance_id],
    )

    private_ip = "0.0.0.1"
    if instance_state != "terminated":
        private_ip = instance_data["Reservations"][0]["Instances"][0][
            "PrivateIpAddress"
        ]
    hostname = instance_data["Reservations"][0]["Instances"][0]["Tags"][0]["Value"]

    return hostname, private_ip


def perform_route53_update(route53, action, hostname, private_ip):
    return route53.change_resource_record_sets(
        HostedZoneId=ZONE_ID,
        ChangeBatch={
            "Comment": "Updated by Lambda DDNS",
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"{hostname}.{ZONE_DOMAIN}",
                        "Type": "A",
                        "TTL": 60,
                        "ResourceRecords": [
                            {"Value": private_ip},
                        ],
                    },
                },
            ],
        },
    )


def create_or_update_dns_record(hostname, private_ip):
    route53 = boto3.client("route53")

    response = perform_route53_update(route53, "UPSERT", hostname, private_ip)

    return response


def delete_dns_record(hostname, private_ip):
    route53 = boto3.client("route53")

    response = route53.list_resource_record_sets(
        HostedZoneId=ZONE_ID, StartRecordName=f"{hostname}.{ZONE_DOMAIN}"
    )

    private_ip = response["ResourceRecordSets"][0]["ResourceRecords"][0]["Value"]

    response = perform_route53_update(route53, "DELETE", hostname, private_ip)

    return response


def lambda_handler(event, context):
    instance_id, instance_state = (
        event["detail"]["instance-id"],
        event["detail"]["state"],
    )

    hostname, private_ip = get_instance_private_ip(instance_id, instance_state)

    if instance_state == "terminated":
        print("launch cleanup", hostname, private_ip)
        output = delete_dns_record(hostname, private_ip)
        perform_dynamodb_update(hostname, private_ip, "DELETED")
        print(output)
    else:
        print("launch create/update", hostname, private_ip)
        output = create_or_update_dns_record(hostname, private_ip)
        perform_dynamodb_update(hostname, private_ip, "CREATED")
        print(output)

    return {"statusCode": 200, "body": "Hello World"}
