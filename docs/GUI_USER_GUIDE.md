# GUI User Guide (Planned)

User-facing documentation for the upcoming PySide6 desktop app.

## Overview
- Left navigation surfaces Dashboard, Pages, OCR & Optimize, Annotate & Redact, Forms, Stamp & Bates, Sign & Verify, Compare, Settings.
- Top bar exposes Open/Save, job queue toggle, progress indicator.

## Panels
- **Dashboard:** quick actions + recent jobs.
- **Pages:** thumbnails with drag reorder, split ranges, rotate/crop controls.
- **OCR & Optimize:** language dropdowns, presets, combined pipelines.
- **Annotate & Redact:** launch helpers (Okular, Xournal++) and safe redaction card.
- **Forms:** load PDF + FDF/XFDF, flatten toggle.
- **Stamp & Bates:** text template preview, numbering controls.
- **Sign & Verify:** certificate picker, visible signature preview, verify tab.
- **Compare:** select A/B, choose diff-pdf vs headless, view diff output.
- **Settings:** doctor status, tool paths, theme, output dir, telemetry preferences.

## Running jobs
- Queue tasks; monitor log pane in each panel for `pdfsuite` command output.
- On first launch, run Doctor to confirm external tools.

## Future additions
- Screenshots / gifs once panels exist.
- Keyboard shortcuts table, accessibility tips.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [GUI Overview](GUI_OVERVIEW.md) · [GUI Technical Plan](GUI_TECH.md)
