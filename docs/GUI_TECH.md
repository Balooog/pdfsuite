# GUI Technical Plan

Engineering notes for the PySide6-based desktop front-end that orchestrates `pdfsuite` CLI commands.

## Stack & rationale

- **PySide6 (Qt for Python):** Native look on Linux/Windows, LGPL, excellent file dialogs and thumbnail widgets. Keeps the project in Python, sharing tooling with the CLI.
- **PyInstaller packaging:** Single-folder distributions for both OSes; later wrap Linux build as an AppImage and Windows build with installer (MSIX/Inno).
- **CLI-first integration:** GUI never bypasses `pdfsuite`. Every action invokes `subprocess.Popen(["pdfsuite", …])` so behavior/messaging match headless workflows.
- **Optional alternative:** Tauri (Rust + HTML/JS) remains Plan B if we ever need a web-tech UI, but PySide6 keeps complexity low for now.

## Process architecture

- **Main thread:** Hosts the Qt event loop and UI widgets.
- **Background worker:** Single-shot `Runner` service (thread or QRunnable) that executes CLI commands, streams stdout/stderr to a signal, and publishes completion/failure events.
- **Job queue:** Simple FIFO; Dashboard can enqueue multiple tasks (e.g., OCR → Optimize). Each queued job records command, inputs, outputs, and log excerpts.
- **Logging:** Every job writes `build/<timestamp>/<task>/command.log` plus outputs; UI tail panel mirrors the same stream.

## Module layout

```
gui/
  main.py             # QApplication bootstrap, sidebar, navigation stack
  widgets/
    dashboard_panel.py
    pages_panel.py
    ocr_panel.py
    redact_panel.py
    forms_panel.py
    stamp_panel.py
    sign_panel.py
    compare_panel.py
    settings_panel.py
  services/
    runner.py         # wraps subprocess, emits signals for log/output
    preview.py        # uses pdftocairo to render thumbnails
    config.py         # load/save per-user settings
  assets/
    icons/*.svg
```

## External tool integration

- **Doctor check:** On first launch (and via Settings), run `pdfsuite doctor`. Parse missing tools and display green/yellow/red chip in status bar.
- **Tool paths:** Allow overrides in Settings. Store config in `~/.config/pdfsuite/config.yml` (Linux) or `%APPDATA%\pdfsuite\config.yml` (Windows) using `platformdirs`.
- **Headless compare:** When `diff-pdf` is absent or user toggles `--headless`, call the CLI’s headless pipeline (pdftocairo + ImageMagick `compare` + img2pdf). GUI surfaces prerequisites and command logs.
- **Visible signature preview:** Map rectangle drawn in PySide6 canvas to jSignPdf args: `p=<page>,x=<pt>,y=<pt>,w=<pt>,h=<pt>`; convert from pixels to points using DPI of the preview.

## Packaging steps

1. Ensure virtualenv with `pdfsuite[gui]` (PySide6, platformdirs, etc.).
1. Run PyInstaller spec that includes GUI modules plus ensures the `pdfsuite` CLI entry is available (either bundled or relying on system install).
1. Post-process: on Linux, wrap dist into AppImage (use `linuxdeploy`); on Windows, sign binaries if necessary and include `jsignpdf.jar`/wrapper.
1. Ship instructions reminding users to install external tools via `pdfsuite doctor` or OS-specific installers.

## Configuration & persistence

- **Config file:** YAML storing paths, default output dir, theme, log verbosity, queue preferences.
- **Recent jobs:** Stored in `~/.local/share/pdfsuite/jobs.json` (Linux) or `%LOCALAPPDATA%/pdfsuite/jobs.json`.
- **Temp artifacts:** `runner` writes to `build/<timestamp>/`. Option in Settings to clean automatically.

## Testing strategy

- **Unit tests:** For widgets/services (Qt Test + pytest-qt) validating signals, command assembly, config IO.
- **Snapshot tests:** Optional golden images of key panels using Qt’s grabFramebuffer in CI.
- **Integration smoke:** Run GUI headlessly (xvfb on Linux) to execute a queue of commands, verifying logs and outputs exist.

## Future enhancements

- Optional WebView for documentation/help.
- Tauri-based shell if we need web theming later.
- Plugin system for custom pipelines (user-defined command sequences).

## Next steps

1. Create the `gui/` package with `main.py`, `services/runner.py`, and a stub `dashboard_panel.py`; wire a minimal PySide6 window that can run `pdfsuite version`.
1. Add dependency extras (`pdfsuite[gui]`) in `pyproject.toml` and document PyInstaller build commands.
1. Prototype the GitHub Actions job that builds the GUI with PyInstaller on Linux/Windows to catch packaging regressions early.

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [GUI Overview](GUI_OVERVIEW.md) · [GUI Wireframes](GUI_WIREFRAMES.md)
