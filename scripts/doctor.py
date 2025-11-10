#!/usr/bin/env python3
import shutil, sys

def which_any(names):
    return next((n for n in names if shutil.which(n)), None)

CORE = ["qpdf","pdfcpu","gs","ocrmypdf","tesseract","pdftk","java","pdfsig","mat2"]
missing = [t for t in CORE if shutil.which(t) is None]

# Accept either 'diff-pdf' (CLI) or 'diffpdf' (GUI)
if which_any(["diff-pdf","diffpdf"]) is None:
    missing.append("diff-pdf (or diffpdf)")

if not missing:
    print("All core tools present. You're good to go.")
    sys.exit(0)

print("Missing tools:\n  - " + "\n  - ".join(missing))
print(
    "\nInstall hints (Linux): "
    "sudo apt install qpdf ghostscript ocrmypdf tesseract-ocr pdftk-java "
    "default-jre poppler-utils mat2 diffpdf"
)
print(
    "Install hints (Windows): "
    "winget/choco for qpdf, ghostscript, tesseract; pdfcpu from GitHub releases; pdftk-java + Java."
)
sys.exit(1)
