import json
from pathlib import Path


file_path = Path(__file__)
MAPPING_PATH = file_path.parent / "name_mappings"


with open(MAPPING_PATH / "servant_names.json", "r", encoding="utf-8") as fp:
    SVT_NAME_JPEN = json.load(fp)