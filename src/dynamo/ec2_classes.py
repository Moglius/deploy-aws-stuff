from datetime import datetime


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

    def get_ami_id(self):
        return self.ami_id


class EC2:
    def __init__(self, data_item):
        self.id = data_item["id"]
        self.name = data_item["name"]
        self.region = data_item["region"]
        self.subnet_id = data_item["subnet_id"]
        self.type = data_item["type"]
        self.ami_id = data_item["ami_id"]
        self.ami_filter = data_item["ami_filter"]
        self.root_block_device = data_item["root_block_device"]
        self.ebs_block_devices = data_item["ebs_block_devices"]

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
        return hash((self.name, self.id))

    def get_ami_id(self):
        return self.ami_id

    def get_subnet_id(self):
        return self.subnet_id

    def get_ami_filter(self):
        return self.ami_filter

    def get_primary_key(self):
        return self.id

    def get_block_device(self, block):
        return {
            "device_name": block["device_name"]["S"],
            "volume_size": block["volume_size"]["N"],
            "volume_type": block["volume_type"]["S"],
        }

    def get_ebs_block_devices(self, extra_blocks):
        block_list = []
        for block in extra_blocks:
            block_list.append(self.get_block_device(block["M"]))

        return block_list

    def get_json_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "region": self.region,
            "subnet_id": self.subnet_id,
            "ami_id": self.ami_id,
            "ami_filter": self.ami_filter,
            "root_block_device": self.get_block_device(self.root_block_device),
            "ebs_block_devices": self.get_ebs_block_devices(self.ebs_block_devices),
        }

    def set_ami_id(self, ami_id):
        self.ami_id = ami_id

    def set_subnet_id(self, subnet_id):
        self.subnet_id = subnet_id
