# pdfsuite forms fill

**Purpose:** Fill AcroForm fields from FDF/XFDF.

**Syntax:**

```bash
pdfsuite forms fill <form.pdf> <data.fdf> -o <output.pdf>
```

**External tools:** pdftk-java

**Behavior notes:**

- Supports FDF or XFDF; flatten afterwards for immutable output.

**Examples:**

- `pdfsuite forms fill form.pdf data.fdf -o filled.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
