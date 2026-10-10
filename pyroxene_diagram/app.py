"""Desktop application entry point."""

from pathlib import Path
import json
import os
import subprocess
import threading

import webview

from .api import Bridge
from .csv_io import read_csv
from .fields import load_fields
from .plot_builder import field_traces


ROOT = Path(__file__).parent


def create_closing_handler(api_instance, window):
    prompt_active = False
    prompt_lock = threading.Lock()

    def on_closing(*args) -> bool:
        nonlocal prompt_active
        if not api_instance.has_unexported_changes:
            return True
        with prompt_lock:
            if prompt_active:
                return False
            prompt_active = True

        def ask_user():
            nonlocal prompt_active
            user_agrees = window.evaluate_js(
                'confirm("Existem alterações na tabela não exportadas. Deseja realmente sair sem exportar?");'
            )
            if user_agrees:
                subprocess.Popen(
                    ["taskkill", "/F", "/T", "/PID", str(os.getpid())],
                    creationflags=0x08000000,
                )
            with prompt_lock:
                prompt_active = False

        threading.Thread(target=ask_user, daemon=True).start()
        return False

    return on_closing


def main() -> None:
    bridge = Bridge(None, str(ROOT / "data" / "example.csv"))
    window = webview.create_window(
        "Plotador Ternário — v0.3.5-alpha",
        (ROOT / "ui" / "index.html").as_uri(),
        js_api=bridge,
        width=1400,
        height=900,
        min_size=(1000, 650),
    )
    bridge.window = window
    window.events.closing += create_closing_handler(bridge, window)
    webview.start(debug=False, private_mode=True)


def initial_payload() -> str:
    compositions = read_csv(ROOT / "data" / "example.csv")
    points = [{"name": item.name, "wo": item.wo, "en": item.en, "fs": item.fs} for item in compositions]
    return json.dumps({"fields": field_traces(load_fields()), "points": points})
