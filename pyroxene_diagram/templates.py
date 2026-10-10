"""Diagram templates available to the generic ternary plotter."""

from .fields import load_fields
from .plot_builder import field_traces


TEMPLATES = {
    "general": {
        "label": "Ternário Geral (Sem campos)",
        "axes": ["A", "B", "C"],
        "fields": [],
    },
    "morimoto_pyroxenes": {
        "label": "Piroxênios — Morimoto (1988)",
        "axes": ["Wo", "En", "Fs"],
        "fields": load_fields(),
    },
}


def template_payload() -> dict:
    return {
        key: {
            "label": value["label"],
            "axes": value["axes"],
            "fields": field_traces(value["fields"]),
        }
        for key, value in TEMPLATES.items()
    }
