"""Methods exposed to JavaScript by pywebview."""

import io
import csv
import json
from pathlib import Path

from PIL import Image
import plotly.io as pio
import webview

from .csv_io import read_compositions
from .plot_builder import field_traces
from .templates import template_payload, TEMPLATES


class Bridge:
    def __init__(self, window, sample_path: str):
        self.window = window
        self.sample_path = sample_path
        self.has_unexported_changes = False

    def set_unexported_changes(self, value: bool):
        self.has_unexported_changes = bool(value)

    def choose_csv(self):
        paths = self.window.create_file_dialog(
            webview.FileDialog.OPEN,
            file_types=("Data files (*.csv;*.xls;*.xlsx)", "CSV files (*.csv)", "Excel files (*.xls;*.xlsx)"),
        )
        return str(paths[0]) if paths else None

    def read_data(self, path: str):
        return [
            {"name": item.name, "wo": item.wo, "en": item.en, "fs": item.fs}
            for item in read_compositions(path)
        ]

    def initial_data(self):
        return {
            "templates": template_payload(),
            "template": "morimoto_pyroxenes",
            "points": self.read_data(self.sample_path),
        }

    def template_data(self, template_key: str):
        template = TEMPLATES[template_key]
        return {"axes": template["axes"], "fields": field_traces(template["fields"])}

    def export_file(self, figure_json: str, file_format: str):
        extension = file_format.lower()
        paths = self.window.create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=f"pyroxene_diagram.{extension}",
            file_types=(f"{extension.upper()} files (*.{extension})",),
        )
        if not paths:
            return None
        if extension not in {"png", "svg", "tiff"}:
            raise ValueError(f"Unsupported export format: {extension}")
        figure = pio.from_json(figure_json)
        figure.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            margin={"t": 30, "l": 55, "r": 55, "b": 75},
        )
        if figure.layout.ternary:
            figure.update_layout(
                ternary={
                    "bgcolor": "white",
                    "aaxis": {"linecolor": "#222", "gridcolor": "#d5d9dc"},
                    "baxis": {"linecolor": "#222", "gridcolor": "#d5d9dc"},
                    "caxis": {"linecolor": "#222", "gridcolor": "#d5d9dc"},
                }
            )
        destination = Path(paths[0])
        if extension == "tiff":
            buffer = io.BytesIO()
            pio.write_image(
                figure,
                buffer,
                format="png",
                width=1800,
                height=1400,
                scale=2,
            )
            buffer.seek(0)
            with Image.open(buffer) as image:
                image.convert("RGB").save(destination, format="TIFF", compression="tiff_lzw")
        else:
            pio.write_image(
                figure,
                destination,
                format=extension,
                width=1800,
                height=1400,
                scale=2,
            )
        return str(destination)

    def export_table(self, points_json: str, axes_json: str, file_format: str, template_key: str):
        extension = file_format.lower()
        if extension not in {"csv", "xlsx"}:
            raise ValueError(f"Unsupported table format: {extension}")
        points = json.loads(points_json)
        axes = json.loads(axes_json)
        safe_template = "pyroxenios_morimoto_1988" if template_key == "morimoto_pyroxenes" else "ternario_geral"
        destination_paths = self.window.create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=f"dados_{safe_template}.{extension}",
            file_types=(f"{extension.upper()} files (*.{extension})",),
        )
        if not destination_paths:
            return None
        destination = Path(destination_paths[0])
        headers = ["Nome/código", *axes]
        rows = [[point["name"], point["wo"], point["en"], point["fs"]] for point in points]
        if extension == "csv":
            with destination.open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream)
                writer.writerow(headers)
                writer.writerows(rows)
        else:
            try:
                import pandas as pd
            except ImportError as exc:
                raise RuntimeError("Excel export requires pandas and openpyxl.") from exc
            pd.DataFrame(rows, columns=headers).to_excel(destination, index=False)
        return str(destination)
