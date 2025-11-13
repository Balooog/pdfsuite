# GUI Technical Plan

Engineering notes for the PySide6-based desktop front-end that orchestrates `pdfsuite` CLI commands.

## Stack & rationale

- **PySide6 (Qt for Python):** Native look on Linux/Windows, LGPL, excellent file dialogs and thumbnail widgets. Keeps the project in Python, sharing tooling with the CLI.
- **PyInstaller packaging:** Single-folder distributions for both OSes; later wrap Linux build as an AppImage and Windows build with installer (MSIX/Inno).
- **CLI-first integration:** GUI never bypasses `pdfsuite`. Every action invokes `subprocess.Popen(["pdfsuite", …])` so behavior/messaging match headless workflows.
- **Optional alternative:** Tauri (Rust + HTML/JS) remains Plan B if we ever need a web-tech UI, but PySide6 keeps complexity low for now.

## Process architecture

- **Main thread:** Hosts the Qt event loop and UI widgets.
- **Background worker:** `Runner` service manages a FIFO queue of CLI jobs, spawns a QThread per command, streams stdout/stderr to the target panel, and writes logs.
- **Job directories:** Every run gets `~/pdfsuite/build/<timestamp>-<slug>/command.log` plus any artifacts the CLI generates. Panels display the log path when work finishes.
- **Status hooks:** `make gui` can pass `--check`; Settings panel toggles “run doctor on launch,” which enqueues `pdfsuite doctor` via the same runner (the `--check` flag disables those background jobs so headless CI never leaves stray QThreads).

## Module layout (current MVP)

```
gui/
  main.py                 # QApplication bootstrap, nav stack, doctor-on-launch hook
  panels/
    base.py               # shared command preview/log scaffolding
    dashboard.py          # doctor/help quick actions
    reader.py             # QtPdf view, thumbnails, outline via CLI `bookmarks`
    bookmarks.py          # tree editor + pdftk dump/apply bridges
    pages.py              # merge/split/reorder controls
    ocr.py                # wraps `pdfsuite ocr`
    redact.py             # safe redaction CTA
    sign.py               # PKCS#12 helper + visible placement geometry
    settings.py           # external viewer path, default output dir, doctor toggle
  services/
    runner.py             # queued subprocess runner writing build/<timestamp>-<slug>
    pdf_preview.py        # QtPdf thumbnail helper (falls back gracefully)
    bookmarks_io.py       # parse/serialize pdftk dump_data_utf8 format
    settings.py           # JSON-backed config via `platformdirs`
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

- **Settings:** Stored at `~/.config/pdfsuite/gui_settings.json` (via `platformdirs`). Today it tracks the external viewer command, default output directory, and whether `pdfsuite doctor` should auto-run.
- **Runner outputs:** Deterministic job folders (`~/pdfsuite/build/<timestamp>-<slug>`) contain command logs so QA can cross-reference GUI vs CLI runs.
- **Reader search cache:** Uses `pdftotext` per page on-demand; future work will add persistent per-document text caches and thumbnail storage.

## Testing strategy

- **Unit tests:** For widgets/services (Qt Test + pytest-qt) validating signals, command assembly, config IO.
- **Snapshot tests:** Optional golden images of key panels using Qt’s grabFramebuffer in CI.
- **Integration smoke:** Run GUI headlessly (xvfb on Linux) to execute a queue of commands, verifying logs and outputs exist.

## Future enhancements

- Optional WebView for documentation/help.
- Tauri-based shell if we need web theming later.
- Plugin system for custom pipelines (user-defined command sequences).

## Repository layout

```
gui/
  main.py             # QApplication bootstrap, sidebar navigation, doctor hook
  panels/
    base.py           # shared command panel scaffold w/ preview + log streaming
    dashboard.py      # quick actions (doctor, help) + shared log console
    reader.py         # QtPdf thumbnails/outline/search
    bookmarks.py      # pdftk dump/apply editor
    pages.py          # merge/split/reorder helpers
    forms.py          # fill + flatten panels
    compare.py        # diff-pdf/headless wrapper
    ocr_optimize.py   # wraps `pdfsuite ocr`/`optimize` with presets
    three_d.py        # Qt WebEngine + three.js viewer + snapshot exporter
    redact.py         # locked to `pdfsuite redact safe`
    sign.py           # pkcs#12 wiring + visible signature geometry helper
    settings.py       # platformdirs-backed GUI config
  services/
    runner.py         # queued subprocess runner streaming stdout/stderr to Qt
    pdf_preview.py    # QtPdf thumbnail helper
    bookmarks_io.py   # parse/serialize pdftk dump_data_utf8 format
    settings.py       # JSON-backed config via `platformdirs`
    assets.py         # resolve packaged static assets (three.js bundle, icons)
  assets/
    3d_viewer/        # three.min.js, OrbitControls, GLTFLoader, template HTML
```

The runner always shells out through `python -m pdfsuite …` so the GUI mirrors the CLI behavior and inherits the current virtualenv.

### 3D viewer pipeline

- `gui/panels/three_d.py` relies on Qt WebEngine to host `gui/assets/3d_viewer/index.html`, a bundled three.js template (OrbitControls + GLTFLoader).
- GLB/GLTF files are passed via query parameters (`?model=file:///…`); HTML bundles can be loaded directly for advanced clients.
- Snapshot export captures the WebEngine viewport (`QWebEngineView.grab()`), writes a PNG to a temp directory, then runs `pdfcpu import -mode image <png> <output.pdf>` so the captured frame lands in a standalone PDF.
- Assets are shipped inside the wheel via `importlib.resources`; see `gui/services/assets.py`.

## Running the shell locally

- Install gui extras and launch the app: `make gui` (creates `.venv`, installs `pdfsuite[gui]`, and runs `python -m gui.main`). PySide6 wheels include QtPdf + WebEngine modules for the Reader/3D panels.
- Headless wiring check: `python -m gui.main --check` (initializes Qt widgets without opening the window; skips doctor/watch to avoid lingering jobs in CI).
- Panels stream logs via a shared console; command previews show the exact CLI invocation and the runner reports the log directory when finished.

## Next steps

1. Prototype the GitHub Actions job that builds the GUI with PyInstaller on Linux/Windows to catch packaging regressions early.
1. Layer in additional panels (Forms, Compare, Watch Folder automation) now that the base runner/preview/widgets exist.
1. Tighten the Dashboard queue builder so multiple CLI jobs can be enqueued before dispatching through the runner.

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [GUI Overview](GUI_OVERVIEW.md) · [GUI Wireframes](GUI_WIREFRAMES.md)
