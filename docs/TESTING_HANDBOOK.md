# Testing Handbook

Reference for running and interpreting tests across pdfsuite.

## Test layers
- **Smoke**: `bash scripts/smoke_test.sh` (CLI end-to-end using fixtures). Required before PR.
- **Unit/pytest** (planned): `pytest` will cover command helpers and future GUI services.
- **GUI smoke** (future): PyInstaller build launched via `pytest-qt` or manual script.

## Running locally
```bash
make dev
bash scripts/smoke_test.sh
pytest  # once tests exist
```

Artifacts land in `build/`; inspect logs under `build/logs/` when failures occur.

## CI expectations
- GitHub Actions matrix (Ubuntu + Windows) runs lint, smoke, docs build.
- Docs workflow (`docs.yml`) must stay green to publish Pages site.
- Future GUI workflow will build PyInstaller bundles nightly.

## Troubleshooting failures
- Missing external tools → rerun `pdfsuite doctor` and install binaries.
- OCR/compare tests may require Tesseract languages and ImageMagick.
- Use `BUILD_DIR=/tmp/pdfsuite-smoke bash scripts/smoke_test.sh` to isolate reruns.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Troubleshooting FAQ](TROUBLESHOOTING_FAQ.md) · [Contributor Guide](CONTRIBUTOR_GUIDE.md)
