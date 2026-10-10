import json

from PIL import Image

from pyroxene_diagram.api import Bridge


class SaveWindow:
    def __init__(self, destination):
        self.destination = str(destination)

    def create_file_dialog(self, *_args, **_kwargs):
        return [self.destination]


def test_export_file_generates_all_image_formats(tmp_path):
    figure = {
        "data": [
            {
                "type": "scatterternary",
                "mode": "text",
                "a": [50],
                "b": [25],
                "c": [25],
                "text": ["Campo"],
                "textfont": {"color": "#263238", "size": 12},
                "selected": {"textfont": {"color": "#263238"}},
                "unselected": {"textfont": {"color": "#263238"}},
            },
            {
                "type": "scatterternary",
                "mode": "markers",
                "a": [30, 60],
                "b": [40, 20],
                "c": [30, 20],
                "uid": "sample-points",
                "meta": {"role": "samples"},
                "selectedpoints": [0],
                "selected": {"marker": {"opacity": 1}},
                "unselected": {"marker": {"opacity": 0.25}},
                "marker": {"size": 11, "color": "#202a33"},
            },
        ],
        "layout": {
            "template": "plotly_white",
            "ternary": {"sum": 100},
            "xaxis": {"range": [0, 1]},
        },
    }

    for extension in ("png", "svg", "tiff"):
        destination = tmp_path / f"diagram.{extension}"
        bridge = Bridge(SaveWindow(destination), "")
        result = bridge.export_file(json.dumps(figure), extension)
        assert result == str(destination)
        assert destination.exists()
        assert destination.stat().st_size > 0
        if extension in {"png", "tiff"}:
            with Image.open(destination) as image:
                assert image.width > 0
                assert image.height > 0
