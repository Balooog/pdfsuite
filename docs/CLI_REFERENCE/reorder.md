# pdfsuite reorder

**Purpose:** Re-sequence pages within a document.

**Syntax:**
```bash
pdfsuite reorder <input.pdf> --order <ranges> -o <output.pdf>
```

**External tools:** qpdf

**Behavior notes:**
- Supports duplication/dropping by repeating or omitting ranges.

**Examples:**
- `pdfsuite reorder deck.pdf --order 5-7,1-4,8-z -o deck_seq.pdf`

---

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
