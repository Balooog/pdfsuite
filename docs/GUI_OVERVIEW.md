# GUI Overview

High-level blueprint for `pdfsuite-gui`, the optional desktop companion that wraps the CLI workflows with a PySide6 interface. The GUI remains a thin client: every action shells out to the existing `pdfsuite` commands so behavior stays identical between headless and interactive modes.

## Core UX principles

- **One window, left-nav navigation** – users pick a workflow from an icon list (Dashboard, Pages, OCR & Optimize, Annotate & Redact, Forms, Stamp & Bates, Sign & Verify, Compare, Settings).
- **CLI transparency** – each screen shows the exact `pdfsuite …` command before execution and streams logs in a side panel.
- **Safety-first defaults** – prominent warnings for redaction (rasterize!) and signing (visible placement preview) with guardrails such as running `doctor` automatically on first launch.
- **Cross-platform parity** – same layout and behavior on Linux and Windows; relies on the same external tools checked by `pdfsuite doctor`.

## MVP shell status

- `gui/main.py` hosts the PySide6 shell with a sidebar + stacked panels.
- Panels implemented today: Dashboard (doctor/help quick actions), **Reader** (QtPdf viewer + thumbnails/search + outline via `bookmarks dump`), **Bookmarks** (tree editor + pdftk apply), Pages (merge/split/reorder), **Forms** (fill + flatten), **Compare** (diff-pdf or headless), **OCR & Optimize** (presets + target sizing), **3D Viewer** (Qt WebEngine + three.js template with snapshot export), Redact (safe pipeline), Sign (PKCS#12 + visible block helper), **Automation** (watch-folder controls), and **Settings** (external viewer path, output dir, doctor/watch toggles).
- Every panel relies on the shared runner in `gui/services/runner.py`, which shells out via `python -m pdfsuite …`, queues jobs, and writes `~/pdfsuite/build/<timestamp>-<job>/command.log`.
- Launch locally with `make gui` (installs the `gui` extra and runs `python -m gui.main`). Use `python -m gui.main --check` for a headless smoke test (it bypasses the automatic doctor/watch jobs so CI can exit cleanly).

## Navigation overview

- **Dashboard** – recent jobs, quick-actions (“Merge PDFs”, “OCR Scan”, “Optimize for email”, “Bates batch”), and fast access to the job queue/history.
- **Reader** – QtPdf viewer with Single/Continuous toggle, Fit Width/Page zoom, thumbnails, outline/bookmarks tree (fed by the CLI), search powered by `pdftotext`, and “Open externally” button honoring the Settings panel.
- **Bookmarks** – tree editor for titles/pages, add/edit/indent/outdent controls, import/export of pdftk dump format, and one-click apply back to a PDF (runs `pdfsuite bookmarks apply` under the hood).
- **OCR & Optimize** – toggles between OCR-only (`pdfsuite ocr`) and optimize-only (`pdfsuite optimize`) with presets/target size fields to mirror the CLI flags.
- **3D Viewer** – loads `.glb/.gltf` (or user-supplied HTML) into a bundled three.js template running in Qt WebEngine; offers orbit/pan/zoom plus a “snapshot to PDF” action that captures the viewport and shells out to `pdfcpu import`.
- **Pages** – thumbnail grid with drag-drop reorder, range selector input (`1-3,7,10-`), delete/duplicate controls, rotate/crop adjustments, and split/merge buttons.
- **Forms** – fill PDFs from FDF/XFDF data or flatten in-place using the pdftk-based CLI.
- **Compare** – pick two PDFs, set an output path, and choose diff-pdf vs headless fallback.
- **OCR & Optimize** – toggles for OCR language packs, deskew/clean, PDF/A, followed by Ghostscript optimize presets (screen/printer/custom).
- **Annotate & Redact** – launch buttons for Okular/Xournal++ (annotation) plus a large “Safe Redaction” card explaining the rasterize→OCR pipeline with a proceed button that runs `pdfsuite redact safe`.
- **Forms** – selects PDF + FDF/XFDF, checkboxes to flatten after filling, table preview of form fields if `pdftk` output is available.
- **Stamp & Bates** – text/Bates templates, starting number, per-page range, preview of sample stamp, batch mode for directories.
- **Sign & Verify** – file picker for `.p12`, alias entry, visible signature geometry with on-canvas preview, timestamp server URL. Includes “Verify” tab for `pdfsig`.
- **Compare** – choose doc A/B, toggle `diff-pdf` vs “Headless” raster compare, output path field, preview of diff pages if available.
- **Automation** – start/stop the watch-folder service, inspect the current folder/preset/target, and tail the live log from `pdfsuite watch`.
- **Settings** – configure the external viewer command, default output directory, and whether `pdfsuite doctor` or watch-folder automation should run on launch.

## Job execution model

- Actions enqueue tasks executed by a single background worker so the UI remains responsive.
- Each task produces logs (shown live) and writes outputs under `build/<timestamp>/<task>.pdf` unless overridden.
- Users can chain tasks (e.g., OCR → Optimize → Bates) via the Dashboard queue builder.
- All jobs reuse the CLI entry point, ensuring reproducible behavior between GUI and CLI usage.

## Safety notes

- **Redaction:** Emphasize that only the “Safe Redaction” workflow (pdf-redact-tools + OCR) guarantees content removal; visual markups must be flattened/cleaned before sharing.
- **Signing:** Warn users to verify certificate alias/passwords; visible signature rectangles must match intended location.
- **Compare:** For the headless pipeline, remind users to install Poppler + ImageMagick + img2pdf; GUI indicates availability via doctor chip.

## Next steps

1. Expand panel coverage (Forms, Stamp/Bates, Compare, watch-folder automation) now that the shell/runner exist.
1. Persist richer panel state (recent files, queue presets, 3D defaults) via `platformdirs`.
1. Layer in queue builder UX on the Dashboard so multiple CLI jobs can be chained before dispatch.

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [GUI Technical Plan](GUI_TECH.md) · [GUI Wireframes](GUI_WIREFRAMES.md) · [GUI Screenshots](GUI_SCREENSHOTS.md)
