# Operator Guide

Run `pdfsuite doctor` first. It will report missing tools and suggest `apt`, `winget`, or `choco` commands. For deep command syntax see [`docs/CLI_REFERENCE`](CLI_REFERENCE/merge.md).

## Common tasks

- Merge: `pdfsuite merge A.pdf B.pdf -o merged.pdf`
- Split: `pdfsuite split in.pdf --pages 1-3,7,10- -o parts/`
- Reorder: `pdfsuite reorder in.pdf --order 5-7,1-4,8-z -o reordered.pdf`
- OCR: `pdfsuite ocr scan.pdf -o scan_ocr.pdf`
- Bates: `pdfsuite stamp --bates BN --start 1001 in.pdf -o out.pdf`
- Fill+flatten: `pdfsuite forms fill form.pdf data.fdf -o filled.pdf && pdfsuite forms flatten filled.pdf -o flat.pdf`
- Redact (safe): `pdfsuite redact safe in.pdf -o redacted.pdf`
- Sign: `pdfsuite sign in.pdf --p12 cert.p12 --alias you --visible "p=1,x=50,y=50,w=200,h=60" -o signed.pdf`
- Verify: `pdfsuite verify signed.pdf`
- Optimize: `pdfsuite optimize in.pdf -o small.pdf`
- Compare: `pdfsuite compare A.pdf B.pdf --headless -o diff.pdf`
- Audit: `pdfsuite audit doc.pdf -o audit.json`

## Pipelines

- Scan inbox → OCR → optimize → linearize: `ocr -> optimize -> merge -> linearize`
- Review with annotations; then sanitize: `okular/xournal++ -> flatten -> redact safe -> ocr -> validate`
- Regression checks: `merge -> split -> reorder -> compare -> audit`

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [Project Launch](PROJECT_LAUNCH.md) · [GUI Overview](GUI_OVERVIEW.md)
