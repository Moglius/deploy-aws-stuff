from datetime import datetime

import boto3


class EC2IMAGE:
    def __init__(self, data_item):
        self.ami_id = data_item["ImageId"]
        self.date = datetime.strptime(
            data_item["CreationDate"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )

    def __str__(self):
        return self.ami_id

    def __eq__(self, other):
        return self.ami_id == other.ami_id

    def __lt__(self, other):
        return (self.date) < (other.date)

    def __gt__(self, other):
        return (self.date) > (other.date)

    def __le__(self, other):
        return (self.date) <= (other.date)

    def __ge__(self, other):
        return (self.date) >= (other.date)

    def __hash__(self):
        return hash((self.ami_id))


ec2_client = boto3.client("ec2", region_name="us-east-2")

images = ec2_client.describe_images(
    Owners=["456639116688"],
    Filters=[
        {
            "Name": "name",
            "Values": [
                "MDM Linux image*",
            ],
        },
    ],
)

image_list = set()
for image in images["Images"]:
    ec2_image = EC2IMAGE(image)
    image_list.add(ec2_image)


print(sorted(image_list).pop())
