import boto3
import json


def get_instance_private_ip(instance_id, instance_state):

    ec2 = boto3.client('ec2')

    instance_data = ec2.describe_instances(
        InstanceIds=[instance_id],
    )

    private_ip = '0.0.0.0'
    if instance_state != 'terminated':
        private_ip = instance_data['Reservations'][0]['Instances'][0]['PrivateIpAddress']
    hostname = instance_data['Reservations'][0]['Instances'][0]['Tags'][0]['Value']

    return hostname, private_ip


def create_or_update_dns_record(hostname, private_ip):

    route53 = boto3.client('route53')

    response = route53.change_resource_record_sets(
            HostedZoneId='Z03897701QHUM8QRP9QGT',
            ChangeBatch={
                "Comment": "Updated by Lambda DDNS",
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": hostname + '.customzone.local',
                            "Type": 'A',
                            "TTL": 60,
                            "ResourceRecords": [
                                {
                                    "Value": private_ip
                                },
                            ]
                        }
                    },
                ]
            }
        )
    
    return response


def delete_dns_record(hostname, private_ip):

    route53 = boto3.client('route53')

    response = route53.list_resource_record_sets(
        HostedZoneId='Z03897701QHUM8QRP9QGT',
        StartRecordName=hostname + '.customzone.local'
    )

    dns_private_ip = response['ResourceRecordSets'][0]['ResourceRecords'][0]['Value']

    response = route53.change_resource_record_sets(
            HostedZoneId='Z03897701QHUM8QRP9QGT',
            ChangeBatch={
                "Comment": "Updated by Lambda DDNS",
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": hostname + '.customzone.local',
                            "Type": 'A',
                            "TTL": 60,
                            "ResourceRecords": [
                                {
                                    "Value": dns_private_ip
                                },
                            ]
                        }
                    },
                ]
            }
        )
    
    return response


def lambda_handler(event, context):

    instance_id, instance_state = event['detail']['instance-id'], event['detail']['state']

    hostname, private_ip = get_instance_private_ip(instance_id, instance_state)

    if instance_state == 'terminated':
        print("launch cleanup", hostname, private_ip)
        output = delete_dns_record(hostname, private_ip)
        print(output)
    else:
        print("launch create/update", hostname, private_ip)
        output = create_or_update_dns_record(hostname, private_ip)
        print(output)

    return {
        'statusCode' : 200,
        'body': "Hello World"
    }
