import json

with open("stb-mc3ds.unistore", "r") as f:
    json_data = json.loads(f.read())

if not ("storeInfo" in json_data):
    print("storeInfo is missing in file")
if not ("storeContent" in json_data):
    print("storeContent is missing in file")

for key in json_data["storeInfo"]:
    print(key)

element = json_data["storeContent"]
element_1 = element[0]
