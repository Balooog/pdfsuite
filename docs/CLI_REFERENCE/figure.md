# figure

Auto-selects an optimization preset for figure-heavy PDFs (e.g., exported plots, Surfer figures) and applies it with optional size targets.

## Syntax

```
pdfsuite figure <input.pdf> -o <output.pdf> [--target-size <MB>]
```

**External tools:** `pdfimages` (analysis), `gs`, `qpdf`

## Behavior

- Inspects the PDF with `pdfimages -list` to gauge image count/size.
- Chooses a preset:
  - `email` for raster-heavy docs (≥5 images or multiple ≥2000 px assets).
  - `report` for mixed vector/raster (default).
  - `poster` when no images are detected.
- Calls `pdfsuite optimize … --preset <choice>` internally. Logs show the preset and log directory.
- `--target-size` (MB) behaves like the optimize command: reruns with stricter downsampling until the size goal is met or the preset tiers are exhausted.

## Examples

- `pdfsuite figure surfer_export.pdf -o surfer_web.pdf`
- `pdfsuite figure map.pdf -o map_3mb.pdf --target-size 3`

______________________________________________________________________

Related docs: [Optimize](optimize.md) · [Surfer Figure Export](../SURFER_FIGURE_EXPORT.md) · [Documentation Index](../DOCS_INDEX.md)
