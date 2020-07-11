import json

class Config:
    def __init__(self, json_path="config.json"):
        config = json.load(open(json_path, "r"))
        self.api_key = config["api_key"]
