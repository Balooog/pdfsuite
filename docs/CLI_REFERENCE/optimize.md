# pdfsuite optimize

**Purpose:** Compress and normalize PDFs with Ghostscript presets.

**Syntax:**

```bash
pdfsuite optimize <input.pdf> -o <output.pdf>
```

**External tools:** Ghostscript (gs)

**Behavior notes:**

- Uses /printer preset; adjust command manually for alternative targets.

**Examples:**

- `pdfsuite optimize brochure.pdf -o brochure_small.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
