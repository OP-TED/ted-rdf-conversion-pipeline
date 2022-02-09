import json
import pathlib


def get_api_response():
    path = pathlib.Path(__file__).parent.parent.parent / "test_data" / "notices" / "2021-OJS237-623049.json"
    return json.loads(path.read_text())

