# pdfsuite ocr

**Purpose:** Add searchable text layers via OCRmyPDF.

**Syntax:**
```bash
pdfsuite ocr <input.pdf> -o <output.pdf>
```

**External tools:** ocrmypdf + Tesseract

**Behavior notes:**
- Respects OCRmyPDF defaults; pass LANG via environment (e.g., OCR_LANGUAGE).

**Examples:**
- `pdfsuite ocr scan.pdf -o scan_ocr.pdf`

---

Related docs: [Operator Guide](../OPERATOR_GUIDE.md) · [Documentation Index](../DOCS_INDEX.md)
