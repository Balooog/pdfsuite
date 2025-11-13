# pdfsuite merge

**Purpose:** Combine multiple PDFs into a single document using qpdf.

**Syntax:**

```bash
pdfsuite merge <input1.pdf> <input2.pdf> ... -o <output.pdf>
```

**External tools:** qpdf

**Behavior notes:**

- Accepts any number of inputs; order matters.
- Outputs linearized PDF mirroring qpdf behavior.

**Examples:**

- `pdfsuite merge A.pdf B.pdf -o merged.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
