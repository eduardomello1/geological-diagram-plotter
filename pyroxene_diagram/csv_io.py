"""CSV and spreadsheet import helpers."""

import csv
from pathlib import Path

from .conversion import Composition


def _compositions(rows, headers, source_name: str) -> list[Composition]:
    normalized = {str(field).strip().casefold(): field for field in headers if field is not None}
    name_key = next((normalized[key] for key in ("name", "nome", "sample", "amostra", "id") if key in normalized), None)
    value_keys = []
    for aliases in (("wo", "a"), ("en", "b"), ("fs", "c")):
        value_keys.append(next((normalized[key] for key in aliases if key in normalized), None))
    if name_key is None or any(key is None for key in value_keys):
        available = list(headers)[:4]
        if len(available) < 4:
            raise ValueError(f"{source_name} must contain a name and three numeric columns.")
        name_key, *value_keys = available
    result = []
    for line_number, row in enumerate(rows, start=2):
        try:
            result.append(Composition(
                str(row[name_key]).strip(),
                float(row[value_keys[0]]), float(row[value_keys[1]]), float(row[value_keys[2]]),
            ))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid composition at {source_name} line {line_number}.") from exc
    return result


def read_csv(path: str | Path) -> list[Composition]:
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("The CSV has no header.")
        return _compositions(reader, reader.fieldnames, "CSV")


def read_compositions(path: str | Path) -> list[Composition]:
    source = Path(path)
    if source.suffix.casefold() == ".csv":
        return read_csv(source)
    if source.suffix.casefold() not in {".xls", ".xlsx"}:
        raise ValueError("Supported files are CSV, XLS, and XLSX.")
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("Spreadsheet import requires pandas and its Excel engines.") from exc
    frame = pd.read_excel(source)
    if frame.empty:
        return []
    return _compositions(frame.to_dict("records"), list(frame.columns), source.name)
