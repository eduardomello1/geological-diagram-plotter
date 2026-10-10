"""Load the immutable Morimoto (1988) field definitions."""

import json
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).with_name("data") / "pyroxene_fields.json"


def load_fields() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)["fields"]
