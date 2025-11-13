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

- **Open PDF…** loads the document in QtPdf. Use the Single/Continuous toggle plus zoom presets (Fit Width/Page or fixed percentages).
- **Thumbnails pane** lets you jump to any page; hover to see page numbers.
- **Outline/bookmarks tree** is populated by calling `pdfsuite bookmarks dump` under the hood. Expanding nodes mirrors what you would see in other readers.
- **Search** textbox shells out to `pdftotext` per page. Use Next/Prev to cycle through hits; the current thumbnail is selected automatically.
- **Open externally** honors the path set in the Settings panel (falls back to the OS default viewer when blank).

## Bookmarks panel

1. Choose the source PDF and an output path.
2. Click **Load from PDF** to import the existing outline (runs `pdfsuite bookmarks dump`). Alternatively use **Import dump…** to load a saved pdftk file.
3. Edit bookmarks via the tree controls: change title/page, add children, indent/outdent, or move items up/down.
4. **Export dump…** writes the current outline to a UTF‑8 file compatible with `pdftk dump_data_utf8`.
5. **Apply to PDF** saves the tree to a temp file and runs `pdfsuite bookmarks apply input dump.txt -o output.pdf`. Progress and the log folder show in the lower console.

## Pages / Forms / Compare / OCR & Optimize / Redact / Sign panels

These panels wrap the existing CLI commands with form controls:

- **Pages:** merge, split ranges, or reorder by composing the CLI arguments (`pdfsuite merge`, `split`, `reorder`). Provide input files, ranges, and output path, then hit **Run command**.
- **Forms:** choose fill vs flatten; the fill flow requires a PDF + FDF/XFDF data file and runs `pdfsuite forms fill … -o …`, while flattening simply takes an input/output pair. Use the browse buttons to find files, then run.
- **Compare:** select `first.pdf`, `second.pdf`, and an output path. Leave headless off to prefer diff-pdf (CLI or GUI fallback), or toggle it on to run the Poppler/ImageMagick pipeline (`pdfsuite compare --headless`).
- **OCR & Optimize:** choose *OCR only* to run `pdfsuite ocr`, or switch to *Optimize only* to unlock preset + target-size controls that call the enhanced `pdfsuite optimize` CLI. Preset descriptions (Email/Report/Poster) map directly to the CLI flags, and the target-size field adds `--target-size` so retries are visible in the log.
- **Annotate & Redact:** focuses on the safe rasterize workflow (`pdfsuite redact safe`). Provide input/output and click **Run**.
- **Sign:** choose the PDF, PKCS#12 bundle, alias, optional visible signature block geometry, and output. The panel runs `pdfsuite sign` and shows the command preview so you can copy/paste it into scripts if needed.

## Automation panel

- Shows the currently configured watch-folder preset/folder/target size.
- Streams live output from the background `pdfsuite watch` process so you can confirm when files are optimized.
- Use **Start watch** / **Stop watch** to toggle the service without visiting Settings (the toggle also persists via the stored configuration).

## 3D Viewer panel

- Load `.glb`/`.gltf` models (or a custom HTML viewer bundle) via the picker. The GUI writes a query string into the bundled three.js template under `gui/assets/3d_viewer/`.
- Orbit/pan/zoom via mouse drag or scroll; use the toolbar toggle to swap between dark/light backgrounds.
- **Export snapshot to PDF** captures the viewport, saves a PNG to a temp file, and runs `pdfcpu import -mode image <png> <output.pdf>`. Ensure `pdfcpu` is installed and set the output path beforehand.

## Settings panel

- **External viewer:** optional absolute path. When set, the Reader panel uses it instead of the OS default for “Open externally.”
- **Default output directory:** path used to prefill panels (Bookmarks, future watch-folder builders). The folder is created if it doesn’t exist.
- **Run doctor on launch:** toggles whether `pdfsuite doctor` runs automatically when the GUI starts. Results show in the status bar with a link to the log directory.
- **Watch-folder automation:** enable/disable `pdfsuite watch`, specify the folder (e.g., Windows “Printed PDFs”), pick an optimize preset, and optionally cap the size. Logs stream into the Dashboard watch console so you can verify each file that gets optimized.

Settings are stored in `~/.config/pdfsuite/gui_settings.json` (Linux; equivalent platform path elsewhere) via `platformdirs`, so they follow the user profile.

## Logs & troubleshooting

- Every Run produces a deterministic job folder under `~/pdfsuite/build/<timestamp>-<slug>`. Panels echo the path when work completes.
- If a CLI command fails, copy the rendered command from the preview box and try it in a terminal for full context.
- Missing external tools (e.g., `pdftotext` for Reader search) appear in the panel logs. Install them and rerun `pdfsuite doctor`.
- Need unattended compression? Use the CLI `pdfsuite watch --preset email --target-size 3` to monitor a “Printed PDFs” folder and drop optimized copies in `~/pdfsuite/build/watch/…`. Settings → Default output dir is respected by future GUI watch-folder helpers.

______________________________________________________________________

Related docs: [GUI Overview](GUI_OVERVIEW.md) · [GUI Technical Plan](GUI_TECH.md) · [Documentation Index](DOCS_INDEX.md)
