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
        self.type = data_item["type"]
        self.ami_id = data_item["ami_id"]
        self.ami_filter = data_item["ami_filter"]

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

    def get_ami_filter(self):
        return self.ami_filter

    def get_primary_key(self):
        return self.id

    def get_json_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "region": self.region,
            "ami_id": self.ami_id,
            "ami_filter": self.ami_filter,
        }

    def set_ami_id(self, ami_id):
        self.ami_id = ami_id
