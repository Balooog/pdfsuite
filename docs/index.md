# pdfsuite Documentation Portal

Welcome to the canonical documentation for the pdfsuite project. This portal is generated via MkDocs + Material and mirrors the markdown files in the repository. Use the navigation sidebar (or search) to jump to CLI guides, GUI plans, roadmap updates, and contributor notes.

## Quick start
- Read the [README](https://github.com/alex/pdfsuite/blob/main/README.md) for installation and sample commands.
- Run `pdfsuite doctor` to verify you have qpdf, pdfcpu, Ghostscript, OCRmyPDF, pdftk-java, jSignPdf, MAT2, and diff-pdf/diffpdf installed.
- Explore the [Operator Guide](OPERATOR_GUIDE.md) for recipes (merge, split, OCR, stamping, signing, etc.).

## Documentation sections
- **CLI & Workflows** – Operator Guide, Project Launch, and detailed command pages in `CLI_REFERENCE/`.
- **GUI** – Design overview, technical architecture, and wireframes for the PySide6 desktop application.
- **Engineering** – Roadmap, Docs Index, contributor expectations, and CI/testing plans.

## Contributing to the docs
- Every feature PR should update the relevant doc and add a “Related docs” section pointing back to the [Documentation Index](DOCS_INDEX.md).
- Use relative links so content renders correctly both on GitHub and the published site.
- Keep prose concise and actionable; prefer tables/step lists over paragraphs when covering procedures.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Roadmap](ROADMAP.md) · [GUI Overview](GUI_OVERVIEW.md)
