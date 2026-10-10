from pyroxene_diagram.fields import load_fields
from pyroxene_diagram.plot_builder import field_traces
import pytest


def test_fields_are_outlines_with_internal_labels():
    traces = field_traces(load_fields())
    outlines = traces[::2]
    labels = traces[1::2]

    assert len(outlines) == len(labels) == 6
    assert all(trace["mode"] == "lines" for trace in outlines)
    assert all("fill" not in trace and trace["showlegend"] is False for trace in outlines)
    assert all(trace["mode"] == "text" for trace in labels)
    assert {trace["text"][0] for trace in labels} == {
        "Clinoenstatita",
        "Clinoferrossilita",
        "Pigeonita",
        "Augita",
        "Diopsídio",
        "Hedenbergita",
    }


def test_field_labels_use_polygon_centroids():
    field = {"name": "X", "polygon": [
        {"wo": 0, "en": 100, "fs": 0}, {"wo": 10, "en": 90, "fs": 0},
        {"wo": 10, "en": 0, "fs": 90}, {"wo": 0, "en": 0, "fs": 100},
    ]}
    label = field_traces([field])[1]
    assert label["a"][0] == pytest.approx(4.9122807)
    assert label["b"][0] == pytest.approx(47.5438596)
    assert label["c"][0] == pytest.approx(47.5438596)
