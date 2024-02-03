import json

with open("stb-mc3ds.unistore", "r") as f:
    json_data = json.loads(f.read())

element = json_data["storeContent"]
element_1 = element[0]
print(element_1["info"])