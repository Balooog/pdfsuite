# pdfsuite split

**Purpose:** Export page ranges into separate PDFs.

**Syntax:**

```bash
pdfsuite split <input.pdf> --pages <ranges> -o <directory>
```

**External tools:** qpdf

**Behavior notes:**

- Ranges use qpdf syntax (e.g., 1-3,7,10-). Output files named <stem>\_<range>.pdf.

**Examples:**

- `pdfsuite split brief.pdf --pages 1-3,5 -o splits/`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
