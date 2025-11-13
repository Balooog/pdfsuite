# pdfsuite stamp

**Purpose:** Apply text stamps or Bates numbering using pdfcpu.

**Syntax:**

```bash
pdfsuite stamp <input.pdf> --bates <prefix> --start <n> -o <output.pdf>
```

**External tools:** pdfcpu

**Behavior notes:**

- Without --bates, applies default CONFIDENTIAL text across pages.

**Examples:**

- `pdfsuite stamp case.pdf --bates BN --start 1001 -o stamped.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
