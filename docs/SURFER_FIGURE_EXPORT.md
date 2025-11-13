# Surfer Figure Export Playbook

Keep Surfer (and other raster-heavy) figures sharable without blowing past mail or submission limits.

## Goals

- Maintain crisp labels/contours.
- Keep deliverables ≤2–5 MB unless stakeholders request higher fidelity.
- Preserve a copy of the source PSD/QGIS/Surfer file in case regeneration is needed.

## Presets & CLI helpers

1. **Baseline**: export from Surfer as PDF with fonts embedded.

1. Run `pdfsuite figure source.pdf -o figure_small.pdf --target-size 3`.

   - The command inspects the PDF via `pdfimages -list` + `pdfinfo` to determine whether it is raster-heavy or mostly vector.
   - It selects one of the optimize presets (`email`, `report`, `poster`) and retries with progressively lower resolutions (up to `--max-tries`) until the target size is met.

1. If the output is still too large, rerun with an explicit preset:

   ```
   pdfsuite optimize source.pdf -o figure_email.pdf --preset email --target-size 2
   ```

1. For vector-centric posters, use the `poster` preset (minimal downsampling) and skip the target-size flag so curves stay precise.

## Workflow tips

- **Vector first**: whenever possible, keep vector data (contours, annotations) in the source so Ghostscript can preserve it. Rasterize only photography.
- **Raster-heavy exports**: if your Surfer preset flattens everything to a bitmap, start with `pdfsuite figure … --target-size 3`. If labels still look soft, lower the target (e.g., `--target-size 4`) or use `--max-tries 5` so the ladder explores more intermediate DPI tiers.
- **Vector-centric exports**: when `pdfsuite figure` reports `poster` in the logs, the document is mostly vector. Consider skipping `--target-size` or using `--linearize-only` to keep gradients pristine while still enabling fast web view.
- **Batch processing**: drop exported PDFs in a dedicated folder and run `pdfsuite watch --preset email --target-size 3` to auto-optimize as you work.
- **Verification**: open the result in the GUI Reader or `pdfsuite audit` to confirm fonts remain embedded and the size meets expectations.

## Before/after examples

| Input | Size | Command | Output | Notes | |-------|------|---------|--------|-------| | `surfer_raw.pdf` | 22 MB | `pdfsuite figure surfer_raw.pdf -o surfer_web.pdf --target-size 3` | 2.8 MB | Raster-heavy export; `figure` chose the `email` preset automatically. | | `well_log.pdf` | 12 MB | `pdfsuite optimize well_log.pdf -o well_report.pdf --preset report --target-size 5` | 4.6 MB | Mixed vector/raster; labels remain sharp. | | `poster_final.pdf` | 18 MB | `pdfsuite optimize poster_final.pdf -o poster_print.pdf --preset poster` | 17 MB | Vector-dense poster; no size target to keep gradients pristine. |

## Troubleshooting

- **Jagged labels**: rerun with a higher preset (`report` or `poster`) and a larger target-size.
- **Watcher not firing**: ensure the `pdfsuite watch` process points at the correct folder and that files are fully written (settle time default is 2 s).
- **Artifacts near transparency**: Surfer exports sometimes include soft masks; try re-exporting as PDF/A or flatten transparencies before running the optimizer.
- **Still too big**: send the CLI output to logs and check the fallback order. If the ladder exhausted all tries, run `pdfsuite optimize … --preset email --max-tries 6 --target-size 2` to force tighter downsampling.

______________________________________________________________________

Related docs: [CLI Reference – optimize](CLI_REFERENCE/optimize.md) · [CLI Reference – figure](CLI_REFERENCE/figure.md) · [GUI User Guide](GUI_USER_GUIDE.md)
