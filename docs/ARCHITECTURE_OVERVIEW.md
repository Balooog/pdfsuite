# Architecture Overview

How pdfsuite components interact across CLI, GUI, and external toolchain.

## High-level diagram
```
PySide6 GUI  ──(subprocess)──>  pdfsuite CLI (Typer)  ──>  External tools
      │                                 │                    (qpdf, pdfcpu,
      │                                 │                     gs, etc.)
      ▼                                 ▼
 Job queue / logs                utils/common.py helpers
```

## Components
- **CLI (Typer):** Entry point + command modules under `pdfsuite/commands/` that shell out through shared helpers.
- **Utilities:** `pdfsuite/utils/common.py` centralizes process execution, temp dirs, range parsing.
- **GUI (planned):** PySide6 application calling CLI commands via background runner, streaming logs to panels.
- **External tools:** qpdf, pdfcpu, Ghostscript, OCRmyPDF/Tesseract, pdftk-java, jSignPdf, pdfsig, MAT2, diff-pdf, pdf-redact-tools, Poppler utilities.
- **Artifacts:**
  - Config: `~/.config/pdfsuite/config.yml` (Linux), `%APPDATA%\pdfsuite\config.yml` (Windows).
  - Temp/build: `build/<timestamp>/` (CLI) or user-specified output directories.
  - Logs: CLI prints via Rich; GUI stores per-job logs for auditability.

## Job execution
1. GUI or operator constructs command (e.g., merge range).
2. CLI validates args, calls `require_tools`, and shells to tool.
3. Tool writes to filesystem; CLI reports status code.
4. GUI runner captures stdout/stderr and updates progress.

## Future evolution
- Structured logging (JSON) for audits.
- Shared queue definitions so CLI pipelines can be serialized for GUI.
- Plugin hooks for additional external tools.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Project Launch](PROJECT_LAUNCH.md) · [GUI Technical Plan](GUI_TECH.md)
