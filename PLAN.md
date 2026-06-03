# napari 0.7.1 Upgrade Audit and Plan

## Summary
- Upgrade target is a large jump from `napari==0.5.5` to `0.7.1`; the main compatibility break is the 0.7.0 transition to npe2-only plugin behavior.
- Recommended default: keep PyQt5 for this branch to minimize workflow churn, update `napari-aicsimageio` to `0.7.2`, and add direct `AICSImage` loading fallbacks where package code owns the workflow.
- Local environment is not yet representative: installed napari is `0.6.0a1.dev2`, `napari-aicsimageio` is `0.2.0`, and headless imports currently abort without offscreen Qt setup.

## Risk Report
- **High: dependency metadata mismatch**  
  `pyproject.toml` declares `requires-python >=3.9`, but napari 0.7.1 requires Python 3.10-3.14. Update project metadata to `>=3.10`.
- **High: stale reader plugin**  
  `napari-aicsimageio` can be updated from local `0.2.0` to published `0.7.2`, but that release is from August 22, 2022. Its main branch has an npe2 `napari.manifest`, so it is worth testing, but package-owned code should not depend solely on `viewer.open(..., plugin='napari-aicsimageio')`.
- **Medium: Qt backend choice**  
  PyQt5 is lowest risk because the package already depends on it and napari 0.7.1 still supports it. PyQt6 better matches napari’s current recommendation but risks broader environment churn. “Backend extra only” is cleaner for a reusable plugin/package, but less practical here because these scripts launch napari directly.
- **Medium: private/fragile napari API usage**  
  `checkseg.py` uses `viewer._canvas_size`, `layer.source.path`, `selected_data`, `remove_selected`, magicgui `_call_button`, shape CSV `layer.save`, and `interpolation2d`. Each should be smoke-tested on 0.7.1.
- **Medium: headless/testability gap**  
  Importing GUI modules can initialize Qt and fail in non-GUI environments. Add offscreen test setup or lazy GUI imports so non-GUI tests stay usable.
- **Low: notebooks/docs drift**  
  `examples/analysis_template.ipynb` should be checked for napari 0.7.1 install/opening instructions, especially reader selection and Qt backend guidance.

## Order of Operations
- Update napari first, then migrate the reader. The napari 0.7.1 jump changes the GUI/plugin environment, Python floor, Qt behavior, and npe2 expectations; reader failures before that upgrade would be ambiguous.
- Start with a clean Python 3.10 or 3.11 environment using `napari==0.7.1`, keep PyQt5 initially, and keep current direct `AICSImage` imports while stabilizing the napari widgets.
- Make `cellmask` and `checkseg` work on napari 0.7.1 before changing image reader libraries. Fix widget/API breakage, shape save/load behavior, `Shapes.to_labels`, and headless/offscreen test setup first.
- Swap Qt backend from PyQt5 to PyQt6 after napari 0.7.1 is stable if desired.
- Remove package-owned reliance on `viewer.open(..., plugin='napari-aicsimageio')` after the napari upgrade is stable. Prefer direct image loading inside pyclem workflows so plugin behavior is not part of core processing.
- Spike `bioio` / `napari-bioio-reader` after napari 0.7.1 is stable by comparing `AICSImage` and `BioImage` outputs on representative files: dimensions, physical pixel sizes, scene handling, memory use, metadata, and saved mask/shape compatibility.

## Implementation Changes
- Update `pyproject.toml`:
  - Set `requires-python = ">=3.10"`.
  - Change `napari==0.5.5` to `napari==0.7.1`.
  - Prefer `PyQt5` for this branch unless explicit PyQt6 migration is later requested.
  - Pin or bound `napari-aicsimageio>=0.7.2` if retained.
- In `checkseg.py` and `cellmask.py`:
  - Replace package-owned `viewer.open(..., plugin='napari-aicsimageio')` paths with direct `AICSImage` reads where practical, preserving layer names, scale, colormap, and interpolation behavior.
  - Keep plugin-based opening only where interactive reader behavior is intentionally desired, with clear fallback to direct loading.
  - Replace `viewer._canvas_size` with a public or guarded equivalent; if none is stable, isolate it behind a small helper with fallback behavior.
- In `utils.py` / shapes workflow:
  - Verify `Shapes.to_labels(mask_shape)` behavior under 0.7.1, especially scale handling and empty shapes.
  - Preserve existing public function names and workflow outputs.

## Test Plan
- Create a clean Python 3.10 or 3.11 environment with `napari==0.7.1`, selected Qt backend, and updated package dependencies.
- Run dependency checks: `python -m pip check`, import checks, and existing tests.
- Add focused smoke tests for:
  - constructing `cellmask_widget` and `checkseg_widget` under offscreen Qt,
  - adding EM image, cell mask, grid, progress map, and shape layers,
  - `shapes_to_mask` round trip with empty and polygon shapes,
  - saving/reloading shape CSVs,
  - direct `AICSImage` fallback path.
- Manually validate both widgets in a real napari session with representative EM image, cell mask, segmentation mask, and existing shape/protocol files.

## Sources
- napari 0.7.1 release notes: https://napari.org/dev/release/release_0_7_1.html
- napari 0.7.0 breaking changes: https://napari.org/stable/release/release_0_7_0.html
- napari install/backend guidance: https://napari.org/dev/getting_started/installation.html
- napari-aicsimageio PyPI: https://pypi.org/project/napari-aicsimageio/
- napari-aicsimageio npe2 manifest metadata: https://github.com/AllenCellModeling/napari-aicsimageio/blob/main/pyproject.toml

## Assumptions
- This branch should prioritize a working napari 0.7.1 migration over a Qt6 migration.
- Existing command/module entry points should remain stable.
- Scientific behavior and saved mask/shape outputs must remain unchanged unless a napari API change makes that impossible.
