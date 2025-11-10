#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y qpdf ghostscript poppler-utils ocrmypdf tesseract-ocr tesseract-ocr-eng \
  pdftk-java default-jre mat2 diffpdf
# pdfcpu: manual install
if ! command -v pdfcpu >/dev/null 2>&1; then
  echo "Install pdfcpu from https://github.com/pdfcpu/pdfcpu/releases and put on PATH"
fi
