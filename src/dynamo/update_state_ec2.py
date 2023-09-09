import boto3
import hcl2

FILE_PATH = "src/terraform2/import.tf"
AWS_DB_TABLE_NAME = "ec2_instances"


def set_new_value_in_dynamodb(primary_key, key):
    dynamo_client = boto3.resource("dynamodb").Table(AWS_DB_TABLE_NAME)
    dynamo_client.update_item(
        Key={"id": primary_key},
        UpdateExpression=f"set {key}=:new_{key}",
        ExpressionAttributeValues={f":new_{key}": True},
        ReturnValues="UPDATED_NEW",
    )


def get_server_name(import_server):
    sub1, sub2 = '["', '"]'
    server = import_server["to"]
    idx1 = server.index(sub1)
    idx2 = server.index(sub2)

    return server[idx1 + len(sub1) : idx2]


if __name__ == "__main__":
    with open(FILE_PATH, "r") as file:
        dictionary = hcl2.load(file)

        if "import" in dictionary:
            for import_server in dictionary["import"]:
                server = get_server_name(import_server)
                set_new_value_in_dynamodb(server, "imported")
