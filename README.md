# pdfsuite

All‑FOSS, modular replacement for Acrobat‑grade workflows driven by a unified CLI.  Runs on Linux and Windows.  Wraps best‑in‑class tools: qpdf, pdfcpu, Ghostscript, OCRmyPDF/Tesseract, pdftk‑java, jSignPdf, Poppler, MAT2, diff-pdf, and more.

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
```

## System deps
See **docs/OPERATOR_GUIDE.md** and run `pdfsuite doctor` for per‑OS guidance.

## Philosophy
Thin wrappers.  Predictable logs.  Composable pipelines.  Prefer stable, well‑maintained utilities.  Keep the door open to swap implementations.
