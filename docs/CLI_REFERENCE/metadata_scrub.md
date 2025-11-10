# pdfsuite metadata_scrub

**Purpose:** Strip metadata and embedded info.

**Syntax:**
```bash
pdfsuite metadata_scrub <input.pdf> -o <output.pdf>
```

**External tools:** MAT2

**Behavior notes:**
- Operates non-destructively (writes new file) and supports additional filetypes.

**Examples:**
- `pdfsuite metadata_scrub report.pdf -o report_clean.pdf`

---

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
