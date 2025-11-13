# pdfsuite forms flatten

**Purpose:** Flatten form fields to static content.

**Syntax:**

```bash
pdfsuite forms flatten <input.pdf> -o <output.pdf>
```

**External tools:** pdftk-java

**Behavior notes:**

- Removes interactive fields; run after filling or annotation.

**Examples:**

- `pdfsuite forms flatten filled.pdf -o flat.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
