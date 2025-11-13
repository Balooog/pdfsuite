# figure

Auto-selects an optimization preset for figure-heavy PDFs (e.g., exported plots, Surfer figures) and applies it with optional size targets.

## Syntax

```
pdfsuite figure <input.pdf> -o <output.pdf>
                [--target-size <MB>]
                [--max-tries <N>]
```

**External tools:** `pdfimages`, `pdfinfo` (analysis), `gs`, `qpdf`

## Behavior

- Inspects the PDF with `pdfimages -list` + `pdfinfo` to gauge image count, dimensions, and whether all pages are vector.
- Chooses a preset:
  - `email` for raster-heavy docs (≥5 images or multiple ≥2000 px assets).
  - `report` for mixed vector/raster (default).
  - `poster` when no images are detected (vector-first workflow).
- Calls `pdfsuite optimize … --preset <choice>` internally. Logs show the preset, retry ladder, and final size.
- `--target-size` (MB) behaves like the optimize command: reruns with stricter downsampling until the size goal is met or tries are exhausted. Use `--max-tries` to override the default ladder depth (3).

## Examples

- `pdfsuite figure surfer_export.pdf -o surfer_web.pdf`
- `pdfsuite figure map.pdf -o map_3mb.pdf --target-size 3`
- `pdfsuite figure deck.pdf -o deck_email.pdf --target-size 2 --max-tries 5`

______________________________________________________________________

Related docs: [Optimize](optimize.md) · [Surfer Figure Export](../SURFER_FIGURE_EXPORT.md) · [Documentation Index](../DOCS_INDEX.md)
