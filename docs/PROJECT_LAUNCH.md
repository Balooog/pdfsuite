# Project Initiation:

Here's a pragmatic, **all-FOSS “Acrobat-grade” stack** that can be driven from Codex CLI on Ubuntu and bundle for **Linux + Windows**.  Every major Acrobat Pro DC job is mapped to one or more robust open tools and then outlined how to package them behind a single wrapper CLI.

# The Stack (core CLI-first)

**Documents**

* **qpdf** — structural edits (split/merge, pages, encrypt/decrypt, permissions), linearize, inspect.
* **pdfcpu** — stamp/watermark, page numbers/Bates, crop/trim/box edits, optimize, validate (single static binary; great cross-platform).
* **Ghostscript** — compress/flatten, rasterize, convert (PDF↔images/PS/PDF-A).
* **pdftk-java** — fill/flatten AcroForms, burst, cat, background/overlay; FDF/XFDF I/O.
* **Apache PDFBox (pdfbox-app.jar)** — extract text/images, metadata ops, repair; helpful where qpdf/pdftk fall short.

**OCR & scans**

* **OCRmyPDF** (+ **Tesseract** & language packs) — searchable text layer, deskew, clean scans, PDF/A.
* **img2pdf** — lossless image→PDF assembly (when you don’t want Ghostscript’s re-encoding).

**Security, signing, redaction**

* **jSignPdf** (CLI) — digital signatures (PAdES), visible signature appearances, timestamp server support.
* **pdfsig** (Poppler) — verify signatures.
* **MAT2** — metadata stripping (PDF + other file types) for privacy.
* **pdf-redact-tools** (Freedom of the Press) — safe redaction via rasterize→OCR pipeline (prevents “black box but text still there” mistakes).
  *(Use for high-assurance redaction; for visual markout only, pair Okular/Xournal++ then sanitize with this.)*

**Forms & content editing (FOSS reality check)**

* **Scribus** — *create* professional PDF forms (AcroForms/XFA-like), set actions, export.
* **LibreOffice Draw** — *light* page/content edits on many PDFs; surprisingly handy for quick fixes.
* **Inkscape** — precise single-page vector edits (logos, marks).
* **PDF4QT** — evolving GPL editor with growing native text-edit features (good to include as optional).

**Compare & QA**

* **diff-pdf** or **DiffPDF** — visual/structural compare for review workflows.
* **pdffonts/pdfinfo/pdftotext** (Poppler) — audit fonts/text extraction, quick QA gates.

**GUI helpers (optional but nice)**

* **PDF Arranger** — visual merge/split/reorder.
* **Okular** or **Xournal++** — annotation & pen signing; save back to PDF (then flatten/sanitize via Ghostscript/Redact Tools).

---

# Feature → Tool Map (quick lookup)

* **Merge / Split / Reorder** → qpdf, pdfcpu, pdftk-java, PDF Arranger (GUI)
* **Rotate / Crop / Resize / Rebox** → pdfcpu, qpdf
* **Bookmarks/Outlines** → pdfcpu (import/export), qpdf (JSON qdf edits)
* **Watermarks / Stamps / Bates** → pdfcpu (best), pdftk-java (background/overlay)
* **Encrypt / Decrypt / Permissions** → qpdf, pdfcpu, pdftk-java
* **Forms (fill/flatten)** → pdftk-java; **Forms (create)** → Scribus
* **OCR / Deskew / PDF/A** → OCRmyPDF (+ Tesseract)
* **Optimize / Compress / Flatten** → Ghostscript, pdfcpu
* **Digital Sign / Verify** → jSignPdf (sign), pdfsig (verify)
* **Redaction (safe)** → pdf-redact-tools (+ OCRmyPDF pass afterward)
* **Extract text/images/metadata** → PDFBox, Poppler utils
* **Compare** → diff-pdf / DiffPDF

---

# How to drive all of this from **Codex CLI** (Ubuntu)

Use a single wrapper repo (e.g., **pdfsuite/**) that exposes unified subcommands and delegates to the tools above.

**Suggested CLI shape**

```
pdfsuite
  ocr            # OCRmyPDF
  merge          # qpdf/pdfcpu
  split
  reorder
  rotate
  crop
  stamp          # watermark/Bates via pdfcpu
  forms fill     # pdftk-java
  forms flatten
  redact safe    # pdf-redact-tools -> OCRmyPDF
  sign           # jSignPdf
  verify         # pdfsig
  optimize       # Ghostscript/pdfcpu
  compare        # diff-pdf
  metadata scrub # MAT2
  audit          # pdfinfo/pdffonts/pdfbox checks
```

Each subcommand is a thin Python (or Go) shim that:

1. validates inputs,
2. composes the right toolchain,
3. writes deterministic logs/artifacts (great for CI),
4. returns clean non-zero exit codes on failure.

Given your Codex CLI workflow, keep the code surface lean and **let the external tools do the heavy lifting**.

---

# Install recipes

## Ubuntu (22.04/24.04+)

```bash
sudo apt update
sudo apt install -y qpdf ghostscript poppler-utils tesseract-ocr tesseract-ocr-eng \
  imagemagick scribus libreoffice inkscape mat2 diffpdf \
  python3-pip default-jre

# OCRmyPDF + img2pdf + pdfcpu (via pip/Go-prebuilt)
python3 -m pip install --user ocrmypdf img2pdf
# pdfcpu: grab prebuilt release (Linux x86_64) and put on PATH:
#   https://github.com/pdfcpu/pdfcpu/releases  (unzip to ~/.local/bin/)

# pdftk-java
sudo apt install -y pdftk-java || true

# jSignPdf (CLI jar)
#   https://github.com/kwart/jSignPdf/releases  (put jSignPdf.jar in ~/.local/share/pdfsuite/)
#   expose a wrapper script `jsignpdf` that calls: java -jar ... "$@"
```

## Windows 10/11 (PowerShell, with winget/choco)

```powershell
winget install GnuWin32.Ghostscript || choco install ghostscript
winget install GnuWin32.QPDF || choco install qpdf
winget install TesseractOCR.Tesseract
winget install GnuPG.Gpg4win  # helpful for cert tooling
winget install PDFBox.PDFBox
winget install KDE.Okular
# pdfcpu: download exe from GitHub releases -> add to PATH
# pdftk-java: choco install pdftk-java  (or manual jar)
# jSignPdf: download jar -> add wrapper .cmd that calls java -jar
# ocrmypdf: install Python, then `pip install ocrmypdf` (needs Ghostscript & Tesseract in PATH)
```

*(For Windows, `pdf-redact-tools` is easiest via WSL; or package a Docker/Podman task for that subcommand. If you need native Windows redaction, keep a WSL dependency just for `redact safe`.)*

---

# Packaging into a single “program” (Linux + Windows)

**Option A (recommended): Python wrapper + preflight + per-OS dependencies**

* Repo delivers `pdfsuite` (Python, Click/Typer).
* First run: `pdfsuite doctor` checks for qpdf/pdfcpu/gs/tesseract/etc., prints install hints or offers one-shot installers (apt/winget/choco).
* Distribute with:

  * **pipx** (`pipx install pdfsuite`) for devs, or
  * **PyInstaller** to ship a self-contained exe on Windows and an AppImage on Linux (you’ll still ship the external binaries or fetch on first run).
* Pros: simplest dev UX, transparent logs, great with Codex CLI & CI.
* Cons: relies on system tools (but that’s also a feature—modular & replaceable).

**Option B: Go monolith wrapper**

* Write the CLI in Go; embed **pdfcpu** directly, shell out for others.
* Pros: single native binary per platform.
* Cons: still need to bundle Ghostscript/Tesseract/pdftk-java/jre for full parity.

**Option C: Nix/Flake**

* Provide a `flake.nix` that pins exact versions across platforms.
* Pros: perfect reproducibility, CI heaven.
* Cons: steeper learning curve for Windows users (though Nix on Windows is improving).

**Signing & trust**

* Keep **jSignPdf** + **pdfsig** as separate signed artifacts in your release page.
* Provide SHA256 sums and an SBOM (Syft) so teams can audit.

---

# Opinionated defaults (good presets)

* **OCR**: `ocrmypdf --optimize 3 --deskew --clean --skip-text`.
* **Optimize**: Ghostscript `-dPDFSETTINGS=/printer` + `-dDetectDuplicateImages=true`.
* **Bates**: `pdfcpu stamp add -mode text "BN:%04d" -p 1- -o out.pdf in.pdf`.
* **Flatten forms**: `pdftk in.pdf output out.pdf flatten`.
* **Secure redaction**: `pdf-redact-tools` → `ocrmypdf` → `pdfcpu validate`.
* **Linearize for web**: `qpdf --linearize in.pdf out.pdf`.
* **Encrypt**: `qpdf --encrypt userpass ownerpass 256 -- in.pdf out.pdf`.

---

# Minimal wrapper flow (example)

* `pdfsuite merge a.pdf b.pdf -o merged.pdf` → `qpdf --empty --pages a.pdf 1-z b.pdf 1-z -- merged.pdf`
* `pdfsuite ocr scan.pdf -o scan_ocr.pdf` → `ocrmypdf scan.pdf scan_ocr.pdf`
* `pdfsuite stamp --bates BN --start 1001 in.pdf -o stamped.pdf` → `pdfcpu`
* `pdfsuite forms fill form.pdf data.fdf -o filled.pdf` → `pdftk-java`
* `pdfsuite sign in.pdf --p12 cert.p12 --alias me --visible "p=1,x=50,y=50,w=200,h=60" -o signed.pdf` → `jSignPdf`
* `pdfsuite redact safe in.pdf -o redacted.pdf` → `pdf-redact-tools` (+ OCR pass)

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Operator Guide](OPERATOR_GUIDE.md) · [Roadmap](ROADMAP.md)
