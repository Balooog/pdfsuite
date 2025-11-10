# pdfsuite audit

**Purpose:** Summarize metadata, fonts, encryption, and validation.

**Syntax:**
```bash
pdfsuite audit <input.pdf> [-o summary.json]
```

**External tools:** pdfinfo, pdffonts, pdfcpu

**Behavior notes:**
- Returns JSON summary; exit non-zero if pdfcpu validation fails.

**Examples:**
- `pdfsuite audit filing.pdf -o audit.json`

---

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
