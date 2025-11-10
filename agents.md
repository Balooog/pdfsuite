# agents.md

Central notes for any Codex/AI agent working inside the `pdfsuite` repo. Keep this document updated as workflows evolve.

## Project snapshot
- Goal: ship an all-FOSS, Acrobat-grade CLI that shells out to best-in-class tools (qpdf, pdfcpu, Ghostscript, OCRmyPDF, pdftk-java, jSignPdf, MAT2, diff-pdf, etc.).
- Primary entry point: `pdfsuite/__main__.py` (Typer CLI) which only wires modules; each feature lives under `pdfsuite/commands/`.
- Docs: `README.md` (quick start + smoke tests), `docs/PROJECT_LAUNCH.md` (roadmap + tool map), `docs/OPERATOR_GUIDE.md` (task recipes).

## Development conventions
- Python 3.9+, Typer + Rich. Formatting via Black (100 cols) + isort (black profile). Ruff lint optional.
- CLI wiring only happens in `__main__`; add/modify behavior inside `pdfsuite/commands/<feature>.py` and reuse helpers from `pdfsuite/utils/common.py` (e.g., `run_or_exit`, `require_tools`, range parsing).
- Avoid reimplementing PDF logic—call external tools through helpers and provide descriptive errors when deps are missing.
- Never remove user code or unrelated changes; watch for dirty worktree constraints in instructions.

## External tooling expectations
- Core binaries required: `qpdf`, `pdfcpu`, `gs`, `ocrmypdf`, `tesseract`, `pdftk`, `java`, `pdfsig`, `mat2`, plus `diff-pdf` or `diffpdf`.
- `scripts/doctor.py` reports missing deps; `scripts/install_linux.sh` / `scripts/install_windows.ps1` provide baseline install recipes.
- When adding commands, call `require_tools(...)` before shelling out and document OS-specific quirks.

## Testing & validation
- `scripts/smoke_test.sh` exercises the CLI end-to-end using the PDFs in `tests/fixtures/`; invoke via `bash scripts/smoke_test.sh`, `make smoke`, or `just smoke`.
- Prefer end-to-end CLI invocations (`pdfsuite …`) in future automated tests so external tools stay covered.
- CI plan: add GitHub Actions job that runs formatter/lint (optional) plus the smoke script on Linux (and eventually Windows).

## Active roadmap (high level)
1. Continue expanding CLI surface (rotate, crop, background/overlay, etc.) using the modular pattern.
2. Harden utilities (better error messaging, Windows path quirks, optional JSON logging).
3. Grow smoke coverage into pytest-based regression suite + GitHub Actions workflow.
4. Package/distribute (pipx, PyInstaller, potential AppImage/Windows EXE) and document release steps.

When in doubt, keep wrappers thin, make logs deterministic, and defer advanced behavior to the upstream tool that does it best.
