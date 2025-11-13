# pdfsuite optimize

**Purpose:** Compress/linearize PDFs using Ghostscript presets with optional target sizes.

## Syntax

```
pdfsuite optimize <input.pdf> -o <output.pdf>
                  [--preset {email,report,poster}]
                  [--target-size <MB>]
```

**External tools:** Ghostscript (`gs`), qpdf

## Presets

| Preset  | Use case                                    | Details |
|---------|---------------------------------------------|---------|
| `email` | aggressive downsampling for inbox-friendly attachments | `/screen` profile + image downsample to 150/120/96 dpi (auto-tightens when `--target-size` is used) |
| `report`| general-purpose reports with charts/text    | `/printer` profile + 300/240/200 dpi tiers |
| `poster`| minimal touch for vector-heavy posters      | `/prepress` profile + higher-resolution floor |

With `--target-size`, the command retries with increasingly lower resolutions until the output is ≤ target MB (or all tiers are exhausted). Outputs are linearized via `qpdf --linearize`.

## Examples

- `pdfsuite optimize brochure.pdf -o brochure_small.pdf --preset email`
- `pdfsuite optimize deck.pdf -o deck_8mb.pdf --preset report --target-size 8`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
