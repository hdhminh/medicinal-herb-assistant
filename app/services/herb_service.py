import json
import os

HERB_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "herbs_sample.json")

with open(HERB_JSON_PATH, "r", encoding="utf-8") as f:
    herb_data = json.load(f)

def get_herb_info(code: str) -> dict | None:
    for herb in herb_data:
        if herb["code"] == code:
            return herb
    return None
