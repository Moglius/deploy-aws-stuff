import json

import boto3
import hcl2

TEMP_FILE_PATH = "src/data/ec2.tfvars.temp"
FILE_PATH = "src/data/ec2.tfvars"


class EC2:
    def __init__(self, data_item):
        self.name = data_item["name"]
        self.region = data_item["region"]
        self.type = data_item["type"]

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return (self.name) < (other.name)

    def __gt__(self, other):
        return (self.name) > (other.name)

    def __le__(self, other):
        return (self.name) <= (other.name)

    def __ge__(self, other):
        return (self.name) >= (other.name)

    def __hash__(self):
        return hash((self.name, self.region, self.type))

    def get_json_data(self):
        return {
            "name": self.name,
            "type": self.type,
            "region": self.region,
        }


def scan_table(dynamo_client, *, TableName, **kwargs):
    paginator = dynamo_client.get_paginator("scan")

    for page in paginator.paginate(TableName=TableName, **kwargs):
        yield from page["Items"]


if __name__ == "__main__":
    dynamo_client = boto3.client("dynamodb")
    uniq_set = set()

    for item in scan_table(dynamo_client, TableName="ec2_instances"):
        ec2_instance = EC2(
            {
                "name": item["name"]["S"],
                "type": item["type"]["S"],
                "region": item["region"]["S"],
            }
        )
        uniq_set.add(ec2_instance)

    with open(TEMP_FILE_PATH, "r") as file, open(FILE_PATH, "w") as outfile:
        dictionary = hcl2.load(file)

        for item in dictionary["configuration"]:
            ec2_instance = EC2(item)
            uniq_set.add(ec2_instance)

        mylist = []
        for server in sorted(uniq_set):
            mylist.append(server.get_json_data())

        json_object = json.dumps(mylist, indent=2)

        outfile.write(f"configuration = {json_object}\n")
