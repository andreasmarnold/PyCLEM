import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/pyclem-cache")
os.environ.setdefault("XDG_CONFIG_HOME", "/tmp/pyclem-config")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/pyclem-mpl")

import numpy as np
import tifffile
from napari.layers import Image, Shapes


def test_napari_widget_modules_import():
    import pyclem.cellmask
    import pyclem.checkseg

    assert pyclem.cellmask.cellmask_widget is not None
    assert pyclem.checkseg.checkseg_widget is not None


def test_napari_reader_plugins_open_tiff_with_viewer_model(tmp_path):
    from napari.components import ViewerModel
    from napari.plugins import _initialize_plugins

    path = tmp_path / "smoke.tif"
    tifffile.imwrite(path, np.arange(100, dtype=np.uint16).reshape(10, 10))

    _initialize_plugins()
    viewer = ViewerModel()
    layers = viewer.open(path, name="EM image", interpolation2d="linear")

    assert len(layers) == 1
    assert layers[0].name == "EM image"
    assert layers[0].data.shape == (10, 10)


def test_shapes_to_mask_rasterizes_polygon():
    from pyclem.utils import shapes_to_mask

    polygon = np.array(
        [
            [1, 1],
            [1, 4],
            [4, 4],
            [4, 1],
        ]
    )
    shapes = Shapes(
        [polygon],
        shape_type="polygon",
        name="Cell Mask",
    )

    mask = shapes_to_mask(mask_shape=(6, 6), shapes_layer=shapes)

    assert mask.dtype == bool
    assert mask.shape == (6, 6)
    assert mask[2, 2]
    assert not mask[0, 0]


def test_checkseg_grid_and_mark_tile_smoke():
    from pyclem.checkseg import mark_tile, prepare_grid, reset_view

    progress = Image(
        np.zeros((20, 20), dtype=np.uint8),
        name="Progress map",
    )
    grid, centers, tile_size_px = prepare_grid(
        im_shape=(20, 20),
        tile_size=5,
        px_size=1,
    )

    assert grid.shape[1:] == (2, 2)
    assert centers.shape[1] == 2
    assert tile_size_px == 5

    mark_tile(layer=progress, center=centers[0], size=tile_size_px)
    assert np.count_nonzero(progress.data) > 0

    viewer = SimpleNamespace(
        dims=SimpleNamespace(ndisplay=2),
        camera=SimpleNamespace(center=None, zoom=None),
        _canvas_size=(100, 100),
    )
    reset_view(viewer=viewer, center=centers[0], size=tile_size_px)
    assert viewer.camera.zoom > 0


def test_analysis_template_has_no_outputs():
    import json

    notebook = json.loads(Path("examples/analysis_template.ipynb").read_text())

    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None
            assert cell["outputs"] == []
