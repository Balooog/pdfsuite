# pdfsuite optimize

**Purpose:** Compress/linearize PDFs using Ghostscript presets with optional target sizes.

## Syntax

```
pdfsuite optimize <input.pdf> -o <output.pdf>
                  [--preset {email,report,poster}]
                  [--target-size <MB>]
                  [--max-tries <N>]
                  [--linearize-only]
```

**External tools:** Ghostscript (`gs`), qpdf

## Presets

| Preset | Use case | Details | |---------|---------------------------------------------|---------| | `email` | aggressive downsampling for inbox-friendly attachments | `/screen` profile + image downsample to 150/120/96 dpi (auto-tightens when `--target-size` is used) | | `report`| general-purpose reports with charts/text | `/printer` profile + 300/240/200 dpi tiers | | `poster`| minimal touch for vector-heavy posters | `/prepress` profile + higher-resolution floor |

With `--target-size`, the command retries with increasingly lower resolutions until the output is ≤ target MB (or all tiers are exhausted). The retry ladder is bound by `--max-tries` (default 3). Outputs are always linearized via `qpdf --linearize`; pass `--linearize-only` to skip Ghostscript compression when you only need fast web view.

### Exit codes

| Code | Meaning | | --- | --- | | `0` | Success (target met or best-effort if retries exhausted). | | `1` | Source/output path issues or Ghostscript/qpdf failure. | | `2` | Missing external tools (Ghostscript/qpdf). | | `3` | Target size never reached (`--target-size`), final size is logged for reference. |

## Examples

- `pdfsuite optimize brochure.pdf -o brochure_small.pdf --preset email`
- `pdfsuite optimize deck.pdf -o deck_8mb.pdf --preset report --target-size 8 --max-tries 5`
- `pdfsuite optimize storyboard.pdf -o storyboard_linearized.pdf --linearize-only`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
