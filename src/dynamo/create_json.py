import json

import hcl2

TEMP_FILE_PATH = "src/data/albs.tfvars"
FILE_PATH = "src/data/albs_json.tfvars"


with open(TEMP_FILE_PATH, "r") as file, open(FILE_PATH, "w") as outfile:
    dictionary = hcl2.load(file)

    json_object = json.dumps(dictionary["configuration"], indent=2)

    outfile.write(f"configuration = {json_object}\n")
