# GUI Overview

High-level blueprint for `pdfsuite-gui`, the optional desktop companion that wraps the CLI workflows with a PySide6 interface. The GUI remains a thin client: every action shells out to the existing `pdfsuite` commands so behavior stays identical between headless and interactive modes.

## Core UX principles

- **One window, left-nav navigation** – users pick a workflow from an icon list (Dashboard, Pages, OCR & Optimize, Annotate & Redact, Forms, Stamp & Bates, Sign & Verify, Compare, Settings).
- **CLI transparency** – each screen shows the exact `pdfsuite …` command before execution and streams logs in a side panel.
- **Safety-first defaults** – prominent warnings for redaction (rasterize!) and signing (visible placement preview) with guardrails such as running `doctor` automatically on first launch.
- **Cross-platform parity** – same layout and behavior on Linux and Windows; relies on the same external tools checked by `pdfsuite doctor`.

## Navigation overview

- **Dashboard** – recent jobs, quick-actions (“Merge PDFs”, “OCR Scan”, “Optimize for email”, “Bates batch”), and fast access to the job queue/history.
- **Pages** – thumbnail grid with drag-drop reorder, range selector input (`1-3,7,10-`), delete/duplicate controls, rotate/crop adjustments, and split/merge buttons.
- **OCR & Optimize** – toggles for OCR language packs, deskew/clean, PDF/A, followed by Ghostscript optimize presets (screen/printer/custom).
- **Annotate & Redact** – launch buttons for Okular/Xournal++ (annotation) plus a large “Safe Redaction” card explaining the rasterize→OCR pipeline with a proceed button that runs `pdfsuite redact safe`.
- **Forms** – selects PDF + FDF/XFDF, checkboxes to flatten after filling, table preview of form fields if `pdftk` output is available.
- **Stamp & Bates** – text/Bates templates, starting number, per-page range, preview of sample stamp, batch mode for directories.
- **Sign & Verify** – file picker for `.p12`, alias entry, visible signature geometry with on-canvas preview, timestamp server URL. Includes “Verify” tab for `pdfsig`.
- **Compare** – choose doc A/B, toggle `diff-pdf` vs “Headless” raster compare, output path field, preview of diff pages if available.
- **Settings** – configure locations of external tools, default output directory, theme, doctor status chips, toggles for log verbosity and temp artifact retention.

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

1. Scaffold the PySide6 shell (`gui/main.py`, navigation stack, status bar) and land the sidebar + dashboard layout.
1. Implement the job-runner service that streams CLI logs so every panel can remain thin wrappers over `pdfsuite`.
1. Wire at least one panel end-to-end (Pages or OCR) to validate UX before replicating the pattern across the remaining workflows.

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [GUI Technical Plan](GUI_TECH.md) · [GUI Wireframes](GUI_WIREFRAMES.md)
