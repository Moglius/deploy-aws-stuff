import json

import hcl2


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


if __name__ == "__main__":
    with open("../data/ec2.tfvars", "r") as file:
        dictionary = hcl2.load(file)
        uniq_set = set()

        for item in dictionary["configuration"]:
            ec2_instance = EC2(item)
            uniq_set.add(ec2_instance)

        mylist = []
        for server in sorted(uniq_set):
            mylist.append(server.get_json_data())

        json_object = json.dumps(mylist, indent=2)

        with open("sample.tfvars", "w") as outfile:
            outfile.write(f"configuration = {json_object}")
