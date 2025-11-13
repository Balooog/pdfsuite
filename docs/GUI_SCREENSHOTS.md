# GUI Screenshot Guide

Reference sheet for capturing and curating screenshots that appear across the GUI
docs (Overview, User Guide, Troubleshooting).

## Capture checklist

- Use the dark theme (default) with the window sized around 1366×768 so panels
  resemble the MkDocs layout.
- Ensure `pdfsuite watch` is running (Automation panel shows “Enabled”) so the
  dashboard log demonstrates real output.
- Use sample PDFs from `tests/fixtures/` (or docs/fixtures later) to keep images
  reproducible and safe to publish.
- Obscure any user-specific paths by setting `HOME=/tmp/pdfsuite-demo` when
  launching the GUI, or manually trimming the breadcrumbs before taking the shot.
- Export PNGs at 1× scale, then optimize with `oxipng -o 4 <file>.png`.

## Panels & file names

| Panel | File name | Notes |
| --- | --- | --- |
| Dashboard (quick actions + watch log) | `docs/assets/screenshots/dashboard.png` | Show doctor status chip + watch output. |
| Reader | `docs/assets/screenshots/reader.png` | Highlight thumbnails + outline + search bar. |
| Bookmarks | `docs/assets/screenshots/bookmarks.png` | Include tree editing controls + Apply button. |
| Pages | `docs/assets/screenshots/pages.png` | Demonstrate merge mode with multiple inputs. |
| Forms | `docs/assets/screenshots/forms.png` | Capture both fill and flatten (two shots or annotated callouts). |
| Compare | `docs/assets/screenshots/compare.png` | One image per mode if needed (diff-pdf vs headless toggle). |
| OCR & Optimize | `docs/assets/screenshots/ocr_optimize.png` | Show optimize-only mode with preset dropdown + target size. |
| 3D Viewer | `docs/assets/screenshots/3d_viewer.png` | Use a public GLB sample (e.g., Cesium Man). Include snapshot log line. |
| Automation | `docs/assets/screenshots/automation.png` | Show watch summary + log streaming. |
| Settings | `docs/assets/screenshots/settings.png` | Highlight watch-folder toggle + external viewer path. |

## Embedding in docs

- Prefer Markdown image syntax with short captions, e.g.
  `![Automation panel showing watch logs](assets/screenshots/automation.png)`.
- When referencing multiple screenshots in one section, add a short paragraph
  describing each to keep the text accessible.
- Keep image widths consistent (Material theme auto-scales to fit content) and
  avoid placing more than two screenshots per section to limit page weight.

______________________________________________________________________

Related docs: [GUI Overview](GUI_OVERVIEW.md) · [GUI User Guide](GUI_USER_GUIDE.md) · [Documentation Index](DOCS_INDEX.md)
