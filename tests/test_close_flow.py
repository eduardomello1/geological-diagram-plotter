import threading

from pyroxene_diagram.api import Bridge
from pyroxene_diagram.app import create_closing_handler


class FakeWindow:
    def __init__(self, answer=False):
        self.answer = answer
        self.evaluated = []
        self.called = threading.Event()

    def evaluate_js(self, script):
        self.evaluated.append(script)
        self.called.set()
        return self.answer


def test_closing_blocks_dirty_window_and_prompts_frontend():
    window = FakeWindow()
    bridge = Bridge(window, "")
    bridge.set_unexported_changes(True)
    handler = create_closing_handler(bridge, window)

    assert handler() is False
    assert window.called.wait(1)
    assert window.evaluated == [
        'confirm("Existem alterações na tabela não exportadas. Deseja realmente sair sem exportar?");'
    ]


def test_closing_allows_clean_window():
    window = FakeWindow()
    bridge = Bridge(window, "")
    handler = create_closing_handler(bridge, window)

    assert handler() is True
