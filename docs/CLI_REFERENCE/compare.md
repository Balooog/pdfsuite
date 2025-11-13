# pdfsuite compare

**Purpose:** Compare two PDFs using diff-pdf or headless raster pipeline.

**Syntax:**

```bash
pdfsuite compare <a.pdf> <b.pdf> -o <diff.pdf> [--headless]
```

**External tools:** diff-pdf (preferred) or pdftocairo + ImageMagick compare + img2pdf

**Behavior notes:**

- GUI diffpdf launched when CLI tool absent; use --headless for deterministic diff outputs.

**Examples:**

- `pdfsuite compare v1.pdf v2.pdf --headless -o diff.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
