"""Build Plotly figure data for the frontend."""

from typing import Any


def _polygon_centroid(polygon: list[dict[str, float]]) -> dict[str, float]:
    """Return the centroid in the En/Fs plane and recover Wo from the sum."""
    area_twice = 0.0
    en_moment = 0.0
    fs_moment = 0.0
    for first, second in zip(polygon, polygon[1:] + polygon[:1]):
        cross = first["en"] * second["fs"] - second["en"] * first["fs"]
        area_twice += cross
        en_moment += (first["en"] + second["en"]) * cross
        fs_moment += (first["fs"] + second["fs"]) * cross
    if area_twice == 0:
        return {
            axis: sum(point[axis] for point in polygon) / len(polygon)
            for axis in ("wo", "en", "fs")
        }
    en = en_moment / (3 * area_twice)
    fs = fs_moment / (3 * area_twice)
    return {"wo": 100 - en - fs, "en": en, "fs": fs}


def field_traces(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    traces = []
    for field in fields:
        polygon = field["polygon"]
        traces.append({
            "type": "scatterternary",
            "mode": "lines",
            "a": [point["wo"] for point in polygon] + [polygon[0]["wo"]],
            "b": [point["en"] for point in polygon] + [polygon[0]["en"]],
            "c": [point["fs"] for point in polygon] + [polygon[0]["fs"]],
            "line": {"color": "#4b5563", "width": 1.5},
            "hoverinfo": "skip",
            "showlegend": False,
        })
        polygon = field["polygon"]
        centroid = _polygon_centroid(polygon)
        traces.append({
            "type": "scatterternary",
            "mode": "text",
            "a": [centroid["wo"]],
            "b": [centroid["en"]],
            "c": [centroid["fs"]],
            "text": [field["name"]],
            "textfont": {"color": "#263238", "size": 12},
            "hoverinfo": "skip",
            "showlegend": False,
        })
    return traces
