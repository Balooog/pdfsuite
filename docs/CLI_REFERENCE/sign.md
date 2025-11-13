# pdfsuite sign

**Purpose:** Apply digital signatures via jSignPdf.

**Syntax:**

```bash
pdfsuite sign <input.pdf> --p12 <cert.p12> --alias <name> -o <output.pdf> [--visible p=1,x=50,y=50,w=200,h=60]
```

**External tools:** jSignPdf (Java)

**Behavior notes:**

- Prompted for keystore password; ensure Java + jSignPdf wrapper installed.

**Examples:**

- `pdfsuite sign contract.pdf --p12 signer.p12 --alias legal -o signed.pdf`

______________________________________________________________________

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
