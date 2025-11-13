# pdfsuite

A pragmatic, **all-FOSS PDF stack**. All‑FOSS, modular replacement for Acrobat‑grade workflows driven by a unified CLI. Runs on Linux and Windows. Wraps best‑in‑class tools: qpdf, pdfcpu, Ghostscript, OCRmyPDF/Tesseract, pdftk‑java, jSignPdf, Poppler, MAT2, diff-pdf, and more.

## Quick start

```bash
# create virtual env and install
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# check dependencies
pdfsuite doctor

# examples
pdfsuite merge a.pdf b.pdf -o out.pdf
pdfsuite ocr scan.pdf -o scan_ocr.pdf
pdfsuite stamp --bates BN --start 1001 in.pdf -o stamped.pdf
pdfsuite forms fill form.pdf data.fdf -o filled.pdf
pdfsuite split in.pdf --pages 1-3,4-z -o parts/
pdfsuite reorder in.pdf --order 5-7,1-4,8-z -o reordered.pdf
pdfsuite compare a.pdf b.pdf --headless -o diff.pdf
pdfsuite audit in.pdf -o audit.json
pdfsuite optimize brochure.pdf -o brochure_small.pdf --preset email
pdfsuite figure surfer.pdf -o surfer_small.pdf --target-size 3
pdfsuite watch --preset email --target-size 3   # monitor Printed PDFs folder
```

## System deps

See **docs/OPERATOR_GUIDE.md** and run `pdfsuite doctor` for per‑OS guidance.

## GUI shell preview

The PySide6 desktop shell lives under `gui/` and mirrors the CLI workflows (Reader, Bookmarks,
Pages, OCR, Redact, Sign, Settings) with live log streaming. Launch it locally with:

```bash
make gui           # installs the gui extra and runs python -m gui.main
# or:
python -m gui.main --check   # smoke-test the Qt wiring without showing a window (skips doctor/watch)
```

Refer to [`docs/GUI_OVERVIEW.md`](docs/GUI_OVERVIEW.md) for panel details and roadmap context.

## Philosophy

Thin wrappers. Predictable logs. Composable pipelines. Prefer stable, well‑maintained utilities. Keep the door open to swap implementations.

## Smoke tests

Once dependencies are installed you can exercise the CLI end-to-end:

```bash
bash scripts/smoke_test.sh    # or: make smoke / just smoke
```

The script writes artifacts to `build/` and relies on the fixtures in `tests/fixtures/`.

## Documentation portal

Project docs (CLI guide, GUI plans, roadmap, etc.) are published via MkDocs + GitHub Pages:

- Live site: https://alex.github.io/pdfsuite/ (updated on every `main` push)
- Source docs live in `docs/`; see [`docs/DOCS_INDEX.md`](docs/DOCS_INDEX.md) for the catalog + publishing workflow, including per-command references under `docs/CLI_REFERENCE/`.
