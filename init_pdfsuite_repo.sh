#!/usr/bin/env bash
# init_pdfsuite_repo.sh — create a cross-platform FOSS "Acrobat-grade" PDF suite repo scaffold
# Usage:  bash init_pdfsuite_repo.sh pdfsuite
# The script creates a new folder with a minimal Typer-based CLI and helper scripts for Linux & Windows.
# Safe to re-run; will not overwrite existing files.

set -euo pipefail
REPO_NAME=${1:-pdfsuite}
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"

mkdir -p pdfsuite/commands pdfsuite/utils docs scripts .github/workflows

# --- .gitignore ---
if [ ! -f .gitignore ]; then cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.venv/
.env
.build/
dist/
*.egg-info/
.vscode/
.idea/
.DS_Store
EOF
fi

# --- LICENSE (MIT placeholder) ---
if [ ! -f LICENSE ]; then cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
fi

# --- README ---
if [ ! -f README.md ]; then cat > README.md << 'EOF'
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
EOF
fi

# --- pyproject ---
if [ ! -f pyproject.toml ]; then cat > pyproject.toml << 'EOF'
[project]
name = "pdfsuite"
version = "0.1.0"
description = "All-FOSS Acrobat-grade PDF toolkit with a unified CLI"
readme = "README.md"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = ">=3.9"
dependencies = [
  "typer[all]",
  "rich",
]

[project.scripts]
pdfsuite = "pdfsuite.__main__:app"

[tool.black]
line-length = 100

[tool.isort]
profile = "black"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
EOF
fi

# --- Makefile ---
if [ ! -f Makefile ]; then cat > Makefile << 'EOF'
.PHONY: venv install dev doctor format lint test

venv:
	python3 -m venv .venv
	. .venv/bin/activate; pip install -U pip

install: venv
	. .venv/bin/activate; pip install -e .

dev: install
	. .venv/bin/activate; pip install black isort ruff

doctor:
	. .venv/bin/activate; python scripts/doctor.py

format:
	. .venv/bin/activate; black . && isort .

lint:
	. .venv/bin/activate; ruff check . || true

EOF
fi

# --- justfile (optional) ---
if [ ! -f justfile ]; then cat > justfile << 'EOF'
set shell := ["bash", "-uc"]

doctor:
	python scripts/doctor.py

run *args:
	pdfsuite {{args}}
EOF
fi

# --- Operator Guide ---
if [ ! -f docs/OPERATOR_GUIDE.md ]; then cat > docs/OPERATOR_GUIDE.md << 'EOF'
# Operator Guide

Run `pdfsuite doctor` first.  It will report missing tools and suggest `apt`, `winget`, or `choco` commands.

## Common tasks
- Merge: `pdfsuite merge A.pdf B.pdf -o merged.pdf`
- Split: `pdfsuite split in.pdf --pages 1-3,7,10- -o parts/`
- OCR: `pdfsuite ocr scan.pdf -o scan_ocr.pdf`
- Bates: `pdfsuite stamp --bates BN --start 1001 in.pdf -o out.pdf`
- Fill+flatten: `pdfsuite forms fill form.pdf data.fdf -o filled.pdf && pdfsuite forms flatten filled.pdf -o flat.pdf`
- Redact (safe): `pdfsuite redact safe in.pdf -o redacted.pdf`
- Sign: `pdfsuite sign in.pdf --p12 cert.p12 --alias you --visible "p=1,x=50,y=50,w=200,h=60" -o signed.pdf`
- Verify: `pdfsuite verify signed.pdf`
- Optimize: `pdfsuite optimize in.pdf -o small.pdf`

## Pipelines
- Scan inbox → OCR → optimize → linearize: `ocr -> optimize -> merge -> linearize`
- Review with annotations; then sanitize: `okular/xournal++ -> flatten -> redact safe -> ocr -> validate`
EOF
fi

# --- scripts/doctor.py ---
if [ ! -f scripts/doctor.py ]; then cat > scripts/doctor.py << 'EOF'
#!/usr/bin/env python3
import shutil, sys

TOOLS = {
    "qpdf": "qpdf --version",
    "pdfcpu": "pdfcpu version",
    "gs": "gs --version",
    "ocrmypdf": "ocrmypdf --version",
    "tesseract": "tesseract --version",
    "pdftk": "pdftk --version",
    "java": "java -version",
    "pdfsig": "pdfsig -v",
    "mat2": "mat2 --version",
    "diff-pdf": "diff-pdf --version",
}

missing = []
for t in TOOLS:
    if shutil.which(t) is None:
        missing.append(t)

if not missing:
    print("All core tools present.  You're good to go.")
    sys.exit(0)

print("Missing tools:\n  - " + "\n  - ".join(missing))
print("\nInstall hints (Linux): sudo apt install qpdf ghostscript ocrmypdf tesseract-ocr pdftk-java \")
print("  default-jre poppler-utils mat2 diffpdf")
print("Install hints (Windows): winget/choco for qpdf, ghostscript, tesseract; pdfcpu from GitHub releases; pdftk-java + Java.")
sys.exit(1)
EOF
chmod +x scripts/doctor.py
fi

# --- scripts/install_linux.sh ---
if [ ! -f scripts/install_linux.sh ]; then cat > scripts/install_linux.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y qpdf ghostscript poppler-utils ocrmypdf tesseract-ocr tesseract-ocr-eng \
  pdftk-java default-jre mat2 diffpdf
# pdfcpu: manual install
if ! command -v pdfcpu >/dev/null 2>&1; then
  echo "Install pdfcpu from https://github.com/pdfcpu/pdfcpu/releases and put on PATH"
fi
EOF
chmod +x scripts/install_linux.sh
fi

# --- scripts/install_windows.ps1 ---
if [ ! -f scripts/install_windows.ps1 ]; then cat > scripts/install_windows.ps1 << 'EOF'
# Install core tools via winget/choco (run in elevated PowerShell)
$ErrorActionPreference = 'Stop'
winget install GnuWin32.QPDF -e --id GnuWin32.QPDF || choco install qpdf -y
winget install GnuWin32.Ghostscript -e --id ArtifexSoftware.Ghostscript || choco install ghostscript -y
winget install TesseractOCR.Tesseract -e --id TesseractOCR.Tesseract
# pdfcpu: download from https://github.com/pdfcpu/pdfcpu/releases and add to PATH
# pdftk-java + Java
choco install openjdk -y
choco install pdftk-java -y
EOF
fi

# --- pdfsuite/__init__.py ---
if [ ! -f pdfsuite/__init__.py ]; then cat > pdfsuite/__init__.py << 'EOF'
__all__ = ["__version__"]
__version__ = "0.1.0"
EOF
fi

# --- pdfsuite/__main__.py (Typer app) ---
if [ ! -f pdfsuite/__main__.py ]; then cat > pdfsuite/__main__.py << 'EOF'
from pathlib import Path
import subprocess, sys, shlex
import typer
from rich import print
from pdfsuite import __version__

app = typer.Typer(add_completion=False, help="All‑FOSS Acrobat‑grade PDF toolkit")

# subcommand groups
merge_app = typer.Typer(help="Merge/split/reorder")
forms_app = typer.Typer(help="Forms operations")
redact_app = typer.Typer(help="Redaction helpers")

app.add_typer(merge_app, name="merge")
app.add_typer(forms_app, name="forms")
app.add_typer(redact_app, name="redact")


def run(cmd: str) -> int:
    print(f"[dim]$ {cmd}[/dim]")
    return subprocess.call(cmd, shell=True)


@app.command()
def version():
    """Show version."""
    print(f"pdfsuite {__version__}")


@app.command()
def doctor():
    """Check external tool availability."""
    sys.exit(subprocess.call([sys.executable, "scripts/doctor.py"]))


@app.command()
def ocr(input: Path, output: Path = typer.Option(..., "-o", help="Output PDF")):
    """Add searchable text layer using OCRmyPDF."""
    sys.exit(run(f"ocrmypdf {shlex.quote(str(input))} {shlex.quote(str(output))}"))


@merge_app.callback(invoke_without_command=True)
def merge_main(ctx: typer.Context, inputs: list[Path] = typer.Argument(None), output: Path = typer.Option(None, "-o")):
    """Merge PDFs with qpdf.  Example: pdfsuite merge in1.pdf in2.pdf -o out.pdf"""
    if ctx.invoked_subcommand is not None:
        return
    if not inputs or not output:
        raise typer.Exit(code=2)
    files = " ".join(shlex.quote(str(p)) + " 1-z" for p in inputs)
    cmd = f"qpdf --empty --pages {files} -- {shlex.quote(str(output))}"
    sys.exit(run(cmd))


@app.command()
def optimize(input: Path, output: Path = typer.Option(..., "-o")):
    """Optimize/compress via Ghostscript."""
    cmd = (
        f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 -dPDFSETTINGS=/printer "
        f"-dDetectDuplicateImages=true -dDownsampleColorImages=true -dColorImageResolution=150 "
        f"-o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    )
    sys.exit(run(cmd))


@app.command()
def stamp(input: Path, output: Path = typer.Option(..., "-o"), bates: str = typer.Option(None, "--bates"), start: int = 1):
    """Stamp/watermark/Bates using pdfcpu."""
    if bates:
        cmd = f"pdfcpu stamp add -mode text '{bates}:%04d' -p 1- -s {start} -o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    else:
        cmd = f"pdfcpu stamp add 'CONFIDENTIAL' -p 1- -o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    sys.exit(run(cmd))


@forms_app.command("fill")
def forms_fill(form: Path, fdf: Path, output: Path = typer.Option(..., "-o")):
    """Fill forms with pdftk-java (FDF/XFDF)."""
    cmd = f"pdftk {shlex.quote(str(form))} fill_form {shlex.quote(str(fdf))} output {shlex.quote(str(output))}"
    sys.exit(run(cmd))


@forms_app.command("flatten")
def forms_flatten(input: Path, output: Path = typer.Option(..., "-o")):
    cmd = f"pdftk {shlex.quote(str(input))} output {shlex.quote(str(output))} flatten"
    sys.exit(run(cmd))


@redact_app.command("safe")
def redact_safe(input: Path, output: Path = typer.Option(..., "-o")):
    """Rasterize+sanitize redaction using pdf-redact-tools (requires WSL on Windows)."""
    cmd = f"pdf-redact-tools --sanitize -i {shlex.quote(str(input))} -o {shlex.quote(str(output))}"
    sys.exit(run(cmd))


@app.command()
def sign(input: Path, output: Path = typer.Option(..., "-o"), p12: Path = typer.Option(..., "--p12"), alias: str = typer.Option(..., "--alias"), visible: str = typer.Option(None, "--visible", help="p=<page>,x=,y=,w=,h=")):
    """Digitally sign via jSignPdf."""
    vis = ""
    if visible:
        vis = " --visible " + shlex.quote(visible)
    cmd = f"jsignpdf -ks {shlex.quote(str(p12))} -ksPass ask -a {shlex.quote(str(alias))}{vis} -o {shlex.quote(str(output))} {shlex.quote(str(input))}"
    sys.exit(run(cmd))


@app.command()
def verify(input: Path):
    """Verify signatures via pdfsig."""
    sys.exit(run(f"pdfsig {shlex.quote(str(input))}"))


@app.command()
def metadata_scrub(input: Path, output: Path = typer.Option(..., "-o")):
    """Remove metadata using MAT2."""
    sys.exit(run(f"mat2 --inplace=false -o {shlex.quote(str(output))} {shlex.quote(str(input))}"))


if __name__ == "__main__":
    app()
EOF
fi

# --- commands placeholders (extend later) ---
for f in split reorder compare audit; do
  path="pdfsuite/commands/${f}.py"
  if [ ! -f "$path" ]; then cat > "$path" << 'EOF'
# Placeholder for future subcommand implementation.  See __main__.py for examples.
EOF
  fi
done

# --- CI workflow ---
if [ ! -f .github/workflows/ci.yml ]; then cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push, pull_request]
jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          python -m venv .venv
          . .venv/bin/activate
          pip install -e . black isort ruff
      - run: . .venv/bin/activate && black --check . && isort --check-only . && ruff check .
      - name: Doctor (non-blocking)
        run: |
          . .venv/bin/activate
          python scripts/doctor.py || true
EOF
fi

printf "\nScaffold created.  Next steps:\n"
echo "  cd $REPO_NAME"
echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -e ."
echo "  make doctor  # or: just doctor"
echo "  pdfsuite --help"
