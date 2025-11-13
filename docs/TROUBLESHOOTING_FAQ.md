# Troubleshooting FAQ

Common issues, root causes, and fixes.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `pdfsuite doctor` reports missing `pdfcpu` | pdfcpu not installed or PATH mismatch | Install from GitHub releases; ensure binary is executable and on PATH. |
| `pdfsuite redact safe` fails on Windows | pdf-redact-tools requires WSL/ImageMagick | Run within WSL or install dependencies via package manager; consider Linux VM. |
| `diff-pdf` not found | Only GUI `diffpdf` installed | Install CLI `diff-pdf` or run `pdfsuite compare --headless`. |
| OCR output empty | Source already searchable; `--skip-text` engaged | Use `--force-ocr` via environment or confirm file truly needs OCR. |
| GUI won't launch | PySide6 missing | Install GUI extras (pip install `pdfsuite[gui]`) or rerun installer. |
| 3D viewer shows blank page | Qt WebEngine not available or GPU blocked | Install PySide6 with WebEngine wheels; disable GPU sandbox via `QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu` if needed. |
| Snapshot export fails (`pdfcpu import` error) | pdfcpu missing or output path unwritable | Install pdfcpu and ensure the destination folder exists/has write permissions. |
| `pdfsuite watch` never processes files | Folder path incorrect or files still being written | Use `--path` to point at the correct directory and increase `--settle` so files finish printing before optimization. |
| Optimize still above target size | Retry ladder exhausted | Increase `--max-tries`, bump target size slightly, or confirm the doc is vector-heavy (poster preset) so you can skip aggressive downsampling. |
| Ghostscript/qpdf missing | OS packages not installed | Install `ghostscript` + `qpdf` via apt/choco/brew; rerun `pdfsuite doctor`. |
| Watch-folder loops/duplicates | Input and output folders overlap | Use a dedicated input folder; the GUI writes outputs to `~/pdfsuite/build/watch/...` to avoid recursion. |
| Reader shows “Failed to load” but displays page 1 | QtPdf missing; falling back to limited preview | Install PySide6 QtPdf wheels (`pip install pdfsuite[gui]`), then restart. The Settings panel lists detected Qt modules. |
| Reader thumbnails blurry on HiDPI | Thumbnail cache rendered at 1× | Increase “Thumbnail size” + enable HiDPI flag in Settings → Reader. Clearing the session reloads thumbnails at devicePixelRatio. |
| Reader search unavailable | `pdftotext` absent | Install poppler-utils (Linux) or Poppler for Windows, rerun `pdfsuite doctor`, and restart the GUI. |
| Default-app helper has no effect (Linux) | `.desktop` file missing or mimetype not updated | Click “Default app helper…” in Settings → Reader, regenerate the snippet, then run `xdg-mime default pdfsuite.desktop application/pdf`. |

### Platform-specific tips

- **Windows PATH:** add `%PROGRAMFILES%\pdfcpu` etc., restart shell.
- **Tesseract languages:** `sudo apt install tesseract-ocr-eng` or install `.traineddata` under `tessdata`.
- **Temp directories:** set `TMPDIR` if default fill-level causes failures.

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [Testing Handbook](TESTING_HANDBOOK.md) · [Security & Privacy](SECURITY_PRIVACY.md)
