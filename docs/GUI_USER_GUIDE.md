# GUI User Guide

Walkthrough for the PySide6 desktop shell that wraps the `pdfsuite` CLI. Every action shows the exact command it runs and streams logs so workflows stay reproducible.

## Launching the GUI

```bash
make gui              # installs pdfsuite[gui] and runs python -m gui.main
# or
python -m gui.main --check   # headless smoke (for CI/xvfb)
```

On launch, the Settings toggle determines whether `pdfsuite doctor` runs automatically. Logs for that run (and every other job) land in `~/pdfsuite/build/<timestamp>-<slug>/command.log`.

## Reader panel

1. Click **Open PDF…** and choose a file. The Reader loads it via QtPdf and shows Single/Continuous toggles plus zoom presets (Fit Width/Page/Actual, 100 %, 150 %, 200 %).
1. Navigate with the **thumbnail strip** (left dock) or the **outline/bookmarks tree** (right dock). Thumbnails lazy-load per page and highlight the current selection; the outline is sourced via `pdfsuite bookmarks dump`.
1. Use the **Find** box (`pdftotext` backed) to search inside the document. `Next`/`Prev` buttons move through hits and keep thumbnails synced.
1. Drag thumbnails to reorder pages inline. Each move updates the shared document session, marks the status bar as **Unsaved**, and enables **Save** / **Save As**.
1. Choose **Save** to write the reordered file in-place (background job via qpdf). Choose **Save As** to create a copy (default folder is the Settings output path). Logs stay hidden unless an error occurs; the command preview shows the exact `pdfsuite` call.
1. Use the toolbar actions to toggle **Single/Continuous**, change zoom, or click **Open externally** (respects the Settings “External viewer” path; falls back to OS default when blank).
1. Click **Open in Pages…** to push the live session into the Pages panel. pdfsuite switches to Pages automatically and you can continue editing (crop placeholders, Bates preview, Save/Save As) without reloading the PDF from disk.
1. Press `T` or `B` (or use the toolbar toggles) to hide/show the thumbnail strip and bookmarks dock when you need extra canvas.

> **Default app helper:** open Settings → Reader → **Default app helper…**. The dialog shows the registry/xdg-mime snippets so you can apply them manually; nothing is changed automatically.

### Default app integration

| Platform | Steps | | --- | --- | | **Windows** | Use the helper dialog to copy the `.reg` snippet, update the `Exec` path if needed, save it, then double-click to import. Revert from Windows Settings ▸ Apps ▸ Default apps. | | **Linux** | Use the helper dialog to copy the `.desktop` snippet and `xdg-mime` command. Save it under `~/.local/share/applications/pdfsuite.desktop`, then run `xdg-mime default pdfsuite.desktop application/pdf`. | | **Fallback** | Skip the helper to keep your current default; you can always click **Open externally** from Reader to hand a PDF to your existing viewer. |

## Bookmarks panel

1. Choose the source PDF and an output path.
1. Click **Load from PDF** to import the existing outline (runs `pdfsuite bookmarks dump`). Alternatively use **Import dump…** to load a saved pdftk file.
1. Edit bookmarks via the tree controls: change title/page, add children, indent/outdent, or move items up/down.
1. **Export dump…** writes the current outline to a UTF‑8 file compatible with `pdftk dump_data_utf8`.
1. **Apply to PDF** saves the tree to a temp file and runs `pdfsuite bookmarks apply input dump.txt -o output.pdf`. Progress and the log folder show in the lower console.

## Pages / Forms / Compare / OCR & Optimize / Redact / Sign panels

These panels wrap the existing CLI commands with form controls:

- **Pages:** merge, split ranges, or reorder by composing the CLI arguments (`pdfsuite merge`, `split`, `reorder`). Provide input files, ranges, and output path, then hit **Run command**. When a live Reader session is attached (via **Open in Pages…**), a dedicated panel appears showing the session path, editable comma-separated page order, Bates prefix preview, crop placeholder, and Save / Save As buttons that call the same background writer as Reader. Use **Apply order** to sync the text box back to the session, **Refresh** to pull new changes from Reader, and **Detach** to return to manual CLI mode.
- **Forms:** choose fill vs flatten; the fill flow requires a PDF + FDF/XFDF data file and runs `pdfsuite forms fill … -o …`, while flattening simply takes an input/output pair. Use the browse buttons to find files, then run.
- **Compare:** select `first.pdf`, `second.pdf`, and an output path. Leave headless off to prefer diff-pdf (CLI or GUI fallback), or toggle it on to run the Poppler/ImageMagick pipeline (`pdfsuite compare --headless`).
- **OCR & Optimize:** choose *OCR only* to run `pdfsuite ocr`, or switch to *Optimize only* to unlock preset + target-size controls that call the enhanced `pdfsuite optimize` CLI. The panel exposes the preset dropdown (Email/Report/Poster), **Target size (MB)**, optional **Max tries**, and a **Linearize only** checkbox so you can skip Ghostscript when you just need `qpdf --linearize`. Logs stream each retry and the final size for auditability.
- **Annotate & Redact:** focuses on the safe rasterize workflow (`pdfsuite redact safe`). Provide input/output and click **Run**.
- **Sign:** choose the PDF, PKCS#12 bundle, alias, optional visible signature block geometry, and output. The panel runs `pdfsuite sign` and shows the command preview so you can copy/paste it into scripts if needed.

## Automation panel

- Shows the currently configured watch-folder preset/folder/target size/max tries pulled from Settings.
- Streams live output from the background `pdfsuite watch` process so you can confirm when files are optimized (each file logs before/after sizes).
- Use **Start watch** / **Stop watch** to toggle the service without visiting Settings. Dropping a file into the configured folder should produce an optimized copy under `~/pdfsuite/build/watch/…` within a few seconds.

## 3D Viewer panel

- Load `.glb`/`.gltf` models (or a custom HTML viewer bundle) via the picker. The GUI writes a query string into the bundled three.js template under `gui/assets/3d_viewer/`.
- Orbit/pan/zoom via mouse drag or scroll; use the toolbar toggle to swap between dark/light backgrounds.
- **Export snapshot to PDF** captures the viewport, saves a PNG to a temp file, and runs `pdfcpu import -mode image <png> <output.pdf>`. Ensure `pdfcpu` is installed and set the output path beforehand.

## Settings panel

- **External viewer:** optional absolute path. When set, the Reader panel uses it instead of the OS default for “Open externally.”
- **Default output directory:** path used to prefill panels (Reader Save As, Bookmarks, watch-folder helpers). The folder is created if it doesn’t exist.
- **Reader preferences:** adjust zoom-step %, pan speed, thumbnail size, dock persistence, and open the Default app helper dialog noted above.
- **Run doctor on launch:** toggles whether `pdfsuite doctor` runs automatically when the GUI starts. Results show in the status bar with a link to the log directory.
- **Watch-folder automation:** enable/disable `pdfsuite watch`, specify the folder (Windows default is `%USERPROFILE%\Documents\Printed PDFs`; Linux defaults to `~/PDF` or the detected CUPS-PDF output), pick an optimize preset, and optionally set target size/max tries. Logs stream into the Dashboard watch console so you can verify each file that gets optimized.

Settings are stored in `~/.config/pdfsuite/gui_settings.json` (Linux; equivalent platform path elsewhere) via `platformdirs`, so they follow the user profile.

## Controls & shortcuts

| Gesture / Shortcut | Behavior | Default | Adjust in Settings | | --- | --- | --- | --- | | `Ctrl` + mouse wheel | Zoom in/out in 10 % steps | 10 % per tick, clamped 10 %–800 % | Settings → Reader → “Zoom step (%)” | | `Ctrl` + `Shift` + wheel | Horizontal pan proportional to zoom (useful for wide pages) | 64 px × zoom factor | Settings → Reader → “Pan speed (px)” | | Mouse wheel | Vertical scroll (smooth in Continuous mode, per-page in Single) | OS default delta | Settings → Reader → “Scroll mode” | | `Ctrl` + `S` | Save current session (background write) | — | n/a | | `Ctrl` + `Shift` + `S` | Save As (opens file dialog) | — | n/a | | `T` / `B` | Toggle Thumbnails / Bookmarks docks | Visible | Settings → Reader → “Remember dock layout” |

All gestures fall back to OS defaults if QtPdf is unavailable; the Settings panel exposes the same sliders so power users can match their preferred ergonomics.

## Logs & troubleshooting

- Every Run produces a deterministic job folder under `~/pdfsuite/build/<timestamp>-<slug>`. Panels echo the path when work completes.
- If a CLI command fails, copy the rendered command from the preview box and try it in a terminal for full context.
- Missing external tools (e.g., `pdftotext` for Reader search) appear in the panel logs. Install them and rerun `pdfsuite doctor`.
- Need unattended compression? Use the CLI `pdfsuite watch --preset email --target-size 3` to monitor a “Printed PDFs” folder and drop optimized copies in `~/pdfsuite/build/watch/…`. Settings → Default output dir is respected by future GUI watch-folder helpers.

______________________________________________________________________

Related docs: [GUI Overview](GUI_OVERVIEW.md) · [GUI Technical Plan](GUI_TECH.md) · [Documentation Index](DOCS_INDEX.md)
