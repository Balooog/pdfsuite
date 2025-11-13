# pdfsuite verify

**Purpose:** Check digital signatures.

**Syntax:**

```bash
pdfsuite verify <input.pdf>
```

**External tools:** pdfsig (Poppler)

**Behavior notes:**

- Exit 0 when signatures are valid; non-zero if invalid or missing.

**Examples:**

- `pdfsuite verify signed.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
