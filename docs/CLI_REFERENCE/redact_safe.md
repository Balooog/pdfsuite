# pdfsuite redact safe

**Purpose:** Perform rasterize-and-sanitize redaction.

**Syntax:**

```bash
pdfsuite redact safe <input.pdf> -o <output.pdf>
```

**External tools:** pdf-redact-tools

**Behavior notes:**

- Requires ImageMagick/Poppler dependencies installed by pdf-redact-tools.

**Examples:**

- `pdfsuite redact safe evidence.pdf -o evidence_redacted.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
