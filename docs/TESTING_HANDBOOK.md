# Testing Handbook

Reference for running and interpreting tests across pdfsuite.

## Test layers

- **Smoke**: `bash scripts/smoke_test.sh` (CLI end-to-end using fixtures). Required before PR.
- **Unit/pytest**: `pytest --cov=pdfsuite --cov-report=term-missing` covers CLI command wiring (Typer entry points, helper utilities) and must stay ≥60% (currently ~66%).
- **GUI smoke** (future): PyInstaller build launched via `pytest-qt` or manual script.

## Running locally

```bash
make dev
bash scripts/smoke_test.sh
pytest
```

Key suites:

- `tests/test_cli.py`: Typer entry-point sanity checks.
- `tests/test_commands_*.py`: command assembly coverage (merge/split/reorder + metadata, optimize, OCR, forms, redact, sign, verify, audit parsing).
- `tests/test_utils_common.py`: helper-level validation.
- `tests/conftest.py`: `command_recorder` fixture short-circuits `require_tools` and records commands to assert against without invoking external binaries.
- Fixtures live under `tests/fixtures/`; `sample_multi.pdf` (two pages) exists for split/reorder smoke coverage.

Artifacts land in `build/`; inspect logs under `build/logs/` when failures occur.

## CI expectations

- GitHub Actions matrix (Ubuntu + Windows) runs formatting, pytest/coverage, and CLI smoke jobs. Both Linux and Windows merge the sample PDFs and split `sample_multi.pdf` to keep parity between runners.
- Docs workflow (`docs.yml`) must stay green to publish Pages site and runs markdown lint before mkdocs.
- Future GUI workflow will build PyInstaller bundles nightly.

## Troubleshooting failures

- Missing external tools → rerun `pdfsuite doctor` and install binaries.
- OCR/compare tests may require Tesseract languages and ImageMagick.
- Use `BUILD_DIR=/tmp/pdfsuite-smoke bash scripts/smoke_test.sh` to isolate reruns.

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [Troubleshooting FAQ](TROUBLESHOOTING_FAQ.md) · [Contributor Guide](CONTRIBUTOR_GUIDE.md)
