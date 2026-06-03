# napari 0.7.1 Upgrade Plan

## Current State
- `pyproject.toml` targets Python `>=3.10`, `napari==0.7.1rc2`, `numpy==1.26.4`, and `napari-bioio-reader>=0.3.0`.
- `napari-aicsimageio` has been removed from project dependencies and from the local `pyclem-n0.7.1` environment.
- Package code no longer hard-codes `plugin='napari-aicsimageio'`; current source uses napari reader auto-discovery for display.
- Keep `AICSImage` for pyclem internal data and metadata reads for now.
- Current verification passes: `pytest -q` reports 8 tests passing, and `python -m pip check` reports no broken requirements.
- Real desktop napari smoke checks on `DISPLAY=:0` pass for the smaller fixture. Full Viewer rendering opens the EM TIFF. `checkseg_widget` Start loads EM image, cellmask, grid, progress map, shape layers, and existing progress state; Save Mask and Finish writes a scratch-copy checked mask and resets the viewer. `cellmask_widget` Start loads/rescales the EM image plus prior cellmask; Finish and Save writes a scratch-copy cellmask and resets the viewer.

## Reader Outcome
- `napari-bioio-reader` works for napari model-level reader discovery in tests.
- Do not migrate internal `AICSImage` usage to `BioImage` yet.
- Generated TIFF/OME-TIFF parity matched only after adding `bioio-tifffile` and `bioio-ome-tiff`, but those packages require a newer `tifffile` than `aicsimageio==4.14.0` allows.
- Real EM/CLEM checks now cover the local smaller fixture with `AICSImage`, napari auto-open via `ViewerModel`, previous shape CSVs, segprotocol, grid/progress helpers, and metadata for the larger fixture.
- Explicit `plugin='napari-bioio-reader'` still fails on the real TIFF fixtures in the clean environment because `BioImage` routes through Bio-Formats and Java is not available/cached. Keep napari reader auto-discovery for display and keep `AICSImage` for pyclem-owned reads.
- Java/Bio-Formats is optional for this branch. It is not required for the current pyclem TIFF workflows. It is only needed when explicitly forcing `napari-bioio-reader` / `bioio-bioformats` or reading formats that require Bio-Formats; that path also needs scyjava configured to use system Java and a writable/pre-populated Maven cache.

## Local Data
- `tests/data/` is ignored locally and contains real package inputs/outputs for manual validation.
- `tests/data/smaller_file_size/` is the first reader/workflow fixture set. It includes the EM image, cell mask, segmentation masks, shape CSVs for domes/flats/spheres, feature stats, and segprotocol. Use this first for `AICSImage` vs `BioImage` parity and end-to-end `checkseg` smoke testing.
- `tests/data/bigger_file_size/` is the stress/performance fixture set. It includes the original EM image, previous outputs, and a very large segmentation mask. Current tests inspect TIFF metadata only; use this after the smaller set passes to check memory behavior, loading time, and large-output compatibility.

## Remaining Risks
- Full `napari.Viewer` rendering works in the current desktop session using `DISPLAY=:0`; it still cannot be validated from a purely headless shell without a real display or Xvfb.
- `checkseg.py` still uses fragile/private napari-facing APIs such as `viewer._canvas_size`, `layer.source.path`, `selected_data`, `remove_selected`, magicgui `_call_button`, shape CSV `layer.save`, and `interpolation2d`.
- PyQt5 is intentionally retained for this branch; PyQt6 should be a later, separate migration if needed.

## Next Steps
- Use the larger fixture for manual stress testing only after the smaller fixture remains stable.
- Run `AICSImage` vs `BioImage` parity on real files before deciding whether to remove `aicsimageio`.
- Add Xvfb or another virtual display only if automated full-viewer tests are needed.
- Continue replacing or isolating fragile napari API usage after real workflow testing identifies actual breakage.
