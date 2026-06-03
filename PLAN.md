# napari 0.7.1 Upgrade Plan

## Current State
- `pyproject.toml` targets Python `>=3.10`, `napari==0.7.1rc2`, `numpy==1.26.4`, and `napari-bioio-reader>=0.3.0`.
- `napari-aicsimageio` has been removed from project dependencies and from the local `pyclem-n0.7.1` environment.
- Package code no longer hard-codes `plugin='napari-aicsimageio'`; current source uses napari reader auto-discovery for display.
- Keep `AICSImage` for pyclem internal data and metadata reads for now.
- Current verification passes: `pytest -q` reports 10 tests passing, and `python -m pip check` reports no broken requirements.
- Real desktop napari smoke checks on `DISPLAY=:0` pass for the smaller fixture. Full Viewer rendering opens the EM TIFF. `checkseg_widget` Start loads EM image, cellmask, grid, progress map, shape layers, and existing progress state; Save Mask and Finish writes a scratch-copy checked mask and resets the viewer. `cellmask_widget` Start loads/rescales the EM image plus prior cellmask; Finish and Save writes a scratch-copy cellmask and resets the viewer.
- Larger fixture stress checks pass on `DISPLAY=:0` using scratch copies for write paths. `checkseg_widget` loaded the 27170x27170 EM image, cellmask, grid, progress map, 89 flats, 11 domes, and 26 spheres in about 21 seconds, then Save Mask and Finish recreated the checked mask and reset the viewer in about 167 seconds. `cellmask_widget` loaded and rescaled the larger EM image and prior cellmask to 3222x3222 display layers in about 54 seconds, then Finish and Save wrote the full-resolution cellmask and reset the viewer in about 13 seconds.

## Reader Outcome
- `napari-bioio-reader` works for napari model-level reader discovery in tests.
- Do not migrate internal `AICSImage` usage to `BioImage` yet.
- Generated TIFF/OME-TIFF parity matched only after adding `bioio-tifffile` and `bioio-ome-tiff`, but those packages require a newer `tifffile` than `aicsimageio==4.14.0` allows.
- Real fixture parity also matched after temporarily adding `bioio-tifffile==1.3.0` and `bioio-ome-tiff==1.4.0`: the smaller fixture matched by full array equality for EM image, cellmask, segmask, and checked segmask; the larger fixture matched by shape, dtype, dimensions, scenes, physical pixel sizes, and sampled data blocks.
- Real EM/CLEM checks now cover the local smaller fixture with `AICSImage`, napari auto-open via `ViewerModel`, previous shape CSVs, segprotocol, grid/progress helpers, and metadata for the larger fixture.
- Explicit `plugin='napari-bioio-reader'` still fails on the real TIFF fixtures in the clean environment because `BioImage` routes through Bio-Formats and Java is not available/cached. Keep napari reader auto-discovery for display and keep `AICSImage` for pyclem-owned reads.
- `BioImage` is technically compatible with the current real TIFF fixtures only when the optional bioio TIFF readers are installed. Those readers currently force a `tifffile` version that conflicts with `aicsimageio==4.14.0`, so removing `aicsimageio` would need to be a separate dependency migration.
- Java/Bio-Formats is optional for this branch. It is not required for the current pyclem TIFF workflows. It is only needed when explicitly forcing `napari-bioio-reader` / `bioio-bioformats` or reading formats that require Bio-Formats; that path also needs scyjava configured to use system Java and a writable/pre-populated Maven cache.

## Local Data
- `tests/data/` is ignored locally and contains real package inputs/outputs for manual validation.
- `tests/data/smaller_file_size/` is the first reader/workflow fixture set. It includes the EM image, cell mask, segmentation masks, shape CSVs for domes/flats/spheres, feature stats, and segprotocol. Use this first for `AICSImage` vs `BioImage` parity and end-to-end `checkseg` smoke testing.
- `tests/data/bigger_file_size/` is the stress/performance fixture set. It includes the original EM image, previous outputs, and a very large segmentation mask. Current tests inspect TIFF metadata only, while manual scratch-copy checks cover large-file loading, rescaling, and save/finish behavior.

## Remaining Risks
- Full `napari.Viewer` rendering works in the current desktop session using `DISPLAY=:0`; it still cannot be validated from a purely headless shell without a real display or Xvfb.
- `checkseg.py` and `cellmask.py` now clear layers without depending on selection state, and `checkseg.py` isolates canvas-size lookup behind a compatibility helper.
- Remaining fragile/private napari-facing APIs include magicgui `_call_button`, shape CSV `layer.save`, and `interpolation2d`.
- PyQt5 is intentionally retained for this branch; PyQt6 should be a later, separate migration if needed.

## Next Steps
- Treat any removal of `aicsimageio` as a separate migration: add the optional bioio TIFF readers, resolve the `tifffile` dependency conflict, and rerun real-data/widget checks.
- Add Xvfb or another virtual display only if automated full-viewer tests are needed.
- Continue replacing or isolating fragile napari API usage after real workflow testing identifies actual breakage.
