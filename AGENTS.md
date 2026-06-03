# Non-negotiables
- Preserve scientific correctness over implementation speed.
- Preserve package architecture and public APIs unless explicitly instructed otherwise.
- Prefer simple, explicit code over clever abstractions.
- Validate inputs and fail with clear, actionable errors.
- Update and run tests for behavior changes.
- Stochastic operations must accept a random seed parameter with a fixed documented default. Non-reproducible steps must be flagged in the docstring.
- Provide a brief final report including:
	- files changed
	- architectural rationale
	- assumptions
	- uncertainties
	- tests performed
	- remaining risks

# Scientific Correctness
Never assume existing code is scientifically correct.

If scientific intent is unclear, report uncertainty and ask for clarification before making assumption-heavy changes.

# Architecture
- AI-generated code tends to split responsibilities across files without meaningful boundaries, duplicate logic slightly differently in multiple places, and merge unrelated concerns into single classes or functions. Before finishing, check your own output for these patterns specifically.
- Search for existing functionality before adding new modules or abstractions.
- Prefer extending existing patterns over creating parallel implementations.
- Keep modules focused on one responsibility.
- Preserve public APIs unless a breaking change is explicitly requested.
- Flag duplicated concepts or architectural drift when encountered.
- If extending an existing pattern requires inheriting a suspected scientific error, stop, document the concern in the final report, and ask for clarification. Do not silently adopt a wrong convention to preserve architectural consistency.
- After writing each new module, name in one sentence what it is responsible for. If the sentence contains "and," reconsider the boundary. Check that all code serving that responsibility lives in the module, not spread across others.
- If a function exceeds roughly 30 lines, consider whether its sub-steps should be extracted as named helpers.
- After adding each new module, check whether any existing module's responsibility has been implicitly narrowed or expanded by what you just added. Boundaries that were clean at two modules may not be clean at five. 
- When a public function needs to be flexible and forgiving, separate it into a thin friendly layer over a strict internal function that accepts only exactly what it needs. The internal function should be independently testable.

# Naming
- Use descriptive names based on domain concepts.
- Use the same word for the same concept everywhere.
- Use full words unless an abbreviation is standard in the field.
- Name functions as actions: `load_particles`, `compute_curvature`, `validate_star_file`.
- Name classes as domain concepts: `ParticleSet`, `TomogramMetadata`, `CurvatureResult`.
- Name variables after the data they contain: `particle_positions`, `tomogram_path`, `condition_labels`.
- Name booleans as yes/no statements: `is_valid`, `has_particles`.
- Name modules after responsibilities: `star_io.py`, `curvature.py`, `conditions.py`, `validation.py`.
- Avoid vague names such as `data`, `temp`, `helper`, `misc`, `manager`, or `utils` unless the scope is narrow and obvious.

# Units and Coordinate Systems

- Canonical internal units are defined in `src/package_name/constants.py`. Do not redefine unit conventions elsewhere; import from `constants.py` instead.
- State the canonical internal unit for each physical quantity in the package
  (e.g. all distances in Ångström, all angles in degrees).
- Perform unit conversion explicitly at I/O boundaries, never silently inside
  processing functions.
- When file formats use different conventions, document the conversion and flag
  it in the relevant I/O function's docstring.
- Coordinate system handedness and origin conventions must be documented at the
  module level for any geometry or transformation code.

# Dependencies and Package Choices
- Prefer dependencies already listed in `pyproject.toml`.
- Use `dependency-groups` in pyproject.toml for development dependencies (pytest, ruff, etc.), not requirements files.
- Do not introduce new dependencies unless clearly justified.
- If a new dependency is needed, verify it exists and explain why before adding it.
- Use `pandas` for tabular data such as CSV, TSV, Excel, and similar structured tables.
- When reading tabular data, check for NaN/NA in all scientifically critical columns before processing. Do not rely on downstream errors to surface missing values.
- Use `starfile` for RELION `.star` files.
- Use `pathlib.Path` for filesystem paths.
- Use `matplotlib` for static visualizations.
- Use `plotly` for interactive visualizations.
- Use standard-library tools when they are sufficient and clearer.

# Documentation
- Use NumPy-style docstrings for public APIs.
- Preserve existing docstrings unless behavior changes or they are inaccurate.
- Preserve existing type annotations and add them to new public API functions and methods.
- Keep docstrings concise: document purpose, parameters, returns, raised errors, and non-obvious scientific assumptions.
- Document units, valid ranges, and scientific assumptions for parameters when they affect correctness.
- Do not add comments or docstrings that merely restate obvious code.

# Validation and Testing
- Fail loudly for missing columns, invalid paths, unsupported file formats, or ambiguous scientific assumptions.
- Write tests from the outside in: start with public interface behaviour, then add unit tests for critical or fragile internals.
- Include tests for edge cases and malformed inputs when relevant.
- Check physical plausibility of numerical inputs: reject or warn on values that are structurally valid but scientifically implausible (e.g. negative pixel sizes, out-of-bounds coordinates, degenerate matrices).
- Run relevant tests before finishing.
- Report which tests were run and any tests that could not be run.
- Run tests for changed modules and direct dependents when practical.
- For numerical changes, include at least one test comparing output against a known-good reference value, not just against the previous implementation.
