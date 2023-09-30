class ALB:
    def __init__(self, data_item):
        self.name = data_item["name"]
        self.operational = data_item["operational"]
        self.with_targets = False
        self.availability_zones = set()
        self.json_data = data_item
        self.json_data["subnets"] = []

        for target_group in self.json_data["target_groups"]:
            target_group["targets"] = {}

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
        return hash(self.name)

    def is_operational(self):
        return (
            self.operational and self.with_targets and len(self.availability_zones) > 1
        )

    def add_subnet_id(self, subnet_id):
        if subnet_id not in self.json_data["subnets"]:
            self.json_data["subnets"].append(subnet_id)

    def add_availability_zone(self, availability_zone):
        self.availability_zones.add(availability_zone)

    def _create_target(self, instance_id, target_group):
        return {
            instance_id: {
                "target_id": instance_id,
                "port": target_group["backend_port"],
            }
        }

    def add_target(self, instance_id):
        self.with_targets = True
        for target_group in self.json_data["target_groups"]:
            target = self._create_target(instance_id, target_group)
            target_group["targets"].update(target)

    def get_json_data(self):
        return self.json_data
