from typing import Any

import numpy as np


def clear_layers(viewer: Any) -> None:
    """
    Remove all viewer layers without depending on selection state.
    """
    layers = viewer.layers
    clear = getattr(layers, "clear", None)
    if callable(clear):
        clear()
        return

    for layer in list(layers):
        layers.remove(layer)


def viewer_canvas_size(viewer: Any) -> np.ndarray:
    """
    Return the viewer canvas size while isolating napari private API access.
    """
    canvas_size = getattr(viewer, "_canvas_size", None)
    if canvas_size is not None:
        return np.asarray(canvas_size)

    window = getattr(viewer, "window", None)
    qt_viewer = getattr(window, "qt_viewer", None) or getattr(window, "_qt_viewer", None)
    canvas = getattr(qt_viewer, "canvas", None)
    canvas_size = getattr(canvas, "size", None)
    if canvas_size is not None:
        return np.asarray(canvas_size)

    return np.asarray((1000, 1000))


def call_button_text(widget: Any) -> str:
    """
    Return a magicgui widget call-button label.
    """
    return _call_button(widget).text


def set_call_button_text(widget: Any, text: str) -> None:
    """
    Set a magicgui widget call-button label.
    """
    _call_button(widget).text = text


def _call_button(widget: Any) -> Any:
    call_button = getattr(widget, "call_button", None)
    if call_button is not None:
        return call_button

    return widget._call_button
