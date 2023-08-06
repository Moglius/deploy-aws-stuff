import boto3
import json


def lambda_handler(event, context):

    instance_id = json.loads(event['detail']['instance-id'])
    instance_state = json.loads(event['detail']['state'])
    print(f"instance ID: {instance_id}")

    ec2 = boto3.resource('ec2')

    response = ec2.describe_instances(
        InstanceIds=[instance_id],
    )

    print("RESPONSE", response)

    result = "Hello World"
    return {
        'statusCode' : 200,
        'body': result
    }