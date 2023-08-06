import boto3


def lambda_handler(event, context):
    print("EVENT", event)
    print("CONTEXT", context)
    result = "Hello World"
    return {
        'statusCode' : 200,
        'body': result
    }