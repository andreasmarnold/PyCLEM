import configparser
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/pyclem-cache")
os.environ.setdefault("XDG_CONFIG_HOME", "/tmp/pyclem-config")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/pyclem-mpl")

import numpy as np
import pytest
import tifffile
from aicsimageio import AICSImage


DATA_ROOT = Path("tests/data")
SMALL = DATA_ROOT / "smaller_file_size"
BIG = DATA_ROOT / "bigger_file_size"
SMALL_STEM = "20260403_jr20ack_gb2_C5_cell002_inv"
BIG_STEM = "20260320_jr20wt_gb2_A3_cell001_inv"

pytestmark = pytest.mark.skipif(
    not SMALL.exists(),
    reason="local ignored test data is not available",
)


def test_local_smaller_aicsimage_reads_core_images():
    em = AICSImage(SMALL / f"{SMALL_STEM}.tif")
    cellmask = AICSImage(SMALL / f"{SMALL_STEM}_cellmask.tif")
    em_px_size = em.physical_pixel_sizes[-1]
    cellmask_px_size = cellmask.physical_pixel_sizes[-1]

    assert em.data.shape == (1, 1, 1, 7920, 13264)
    assert em.data.dtype == np.uint16
    assert cellmask.data.shape == em.data.shape
    assert cellmask.data.dtype == np.uint8
    assert em_px_size == pytest.approx(0.0011860000287012007)
    assert cellmask_px_size is not None


def test_local_smaller_napari_auto_open_and_shapes_workflow():
    from napari.components import ViewerModel
    from napari.plugins import _initialize_plugins

    from pyclem.checkseg import display_feature_shapes, mark_tile, prepare_grid, reset_view

    em_path = SMALL / f"{SMALL_STEM}.tif"
    protocol_path = SMALL / f"{SMALL_STEM}_segprotocol.txt"
    em = AICSImage(em_path)
    px_size = em.physical_pixel_sizes[-1]

    _initialize_plugins()
    viewer = ViewerModel()
    viewer.open(em_path, name="EM image", interpolation2d="linear")
    display_feature_shapes(viewer=viewer, file=em_path)

    assert viewer.layers["EM image"].data.shape == (7920, 13264)
    assert len(viewer.layers["Domes"].data) == 5
    assert len(viewer.layers["Flats"].data) == 20
    assert len(viewer.layers["Spheres"].data) == 3

    protocol = configparser.ConfigParser()
    protocol.read(protocol_path)
    current_ind = protocol.getint("CHECKSEG", "current_ind")
    tile_size = protocol.getint("CHECKSEG", "tile_size")

    grid, centers, tile_size_px = prepare_grid(
        im_shape=em.data.shape[-2:],
        tile_size=tile_size,
        px_size=px_size,
    )

    assert current_ind == 24
    assert tile_size == 3
    assert grid.shape == (12, 2, 2)
    assert centers.shape == (24, 2)
    assert tile_size_px == 2530

    progress = viewer.add_image(
        np.zeros(em.data.shape[-2:], dtype=np.uint8),
        name="Progress map",
    )
    helper_ind = min(current_ind, len(centers) - 1)
    mark_tile(progress, centers[helper_ind], tile_size_px)
    assert np.count_nonzero(progress.data) > 0

    reset_view(viewer, centers[helper_ind], tile_size_px)
    assert viewer.camera.zoom > 0


@pytest.mark.skipif(
    not BIG.exists(),
    reason="larger local ignored test data is not available",
)
def test_local_tiff_output_metadata_for_smaller_and_bigger_sets():
    expected = {
        SMALL / f"{SMALL_STEM}.tif": ((7920, 13264), "uint16"),
        SMALL / f"{SMALL_STEM}_cellmask.tif": ((7920, 13264), "uint8"),
        SMALL / f"{SMALL_STEM}_segmask.tif": ((7920, 13264, 3), "uint8"),
        SMALL / f"{SMALL_STEM}_segmask_check.tif": ((7920, 13264, 3), "uint8"),
        BIG / f"{BIG_STEM}.tif": ((27170, 27170), "int16"),
        BIG / f"{BIG_STEM}_cellmask.tif": ((27170, 27170), "uint8"),
        BIG / f"{BIG_STEM}_segmask.tif": ((27170, 27170, 3), "uint8"),
        BIG / f"{BIG_STEM}_segmask_check.tif": ((27170, 27170, 3), "uint8"),
    }

    for path, (shape, dtype) in expected.items():
        with tifffile.TiffFile(path) as tif:
            page = tif.pages[0]
            assert page.shape == shape
            assert str(page.dtype) == dtype
            assert len(tif.pages) == 1
