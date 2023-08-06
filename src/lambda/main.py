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


def lambda_handler(event, context):

    instance_id, instance_state = event['detail']['instance-id'], event['detail']['state']

    hostname, private_ip = get_instance_private_ip(instance_id, instance_state)

    if instance_state == 'terminated':
        print("launch cleanup", hostname, private_ip)
    else:
        print("launch create/update", hostname, private_ip)

    return {
        'statusCode' : 200,
        'body': "Hello World"
    }
