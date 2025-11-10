# Operator Guide

Run `pdfsuite doctor` first.  It will report missing tools and suggest `apt`, `winget`, or `choco` commands.

## Common tasks
- Merge: `pdfsuite merge A.pdf B.pdf -o merged.pdf`
- Split: `pdfsuite split in.pdf --pages 1-3,7,10- -o parts/`
- OCR: `pdfsuite ocr scan.pdf -o scan_ocr.pdf`
- Bates: `pdfsuite stamp --bates BN --start 1001 in.pdf -o out.pdf`
- Fill+flatten: `pdfsuite forms fill form.pdf data.fdf -o filled.pdf && pdfsuite forms flatten filled.pdf -o flat.pdf`
- Redact (safe): `pdfsuite redact safe in.pdf -o redacted.pdf`
- Sign: `pdfsuite sign in.pdf --p12 cert.p12 --alias you --visible "p=1,x=50,y=50,w=200,h=60" -o signed.pdf`
- Verify: `pdfsuite verify signed.pdf`
- Optimize: `pdfsuite optimize in.pdf -o small.pdf`

## Pipelines
- Scan inbox → OCR → optimize → linearize: `ocr -> optimize -> merge -> linearize`
- Review with annotations; then sanitize: `okular/xournal++ -> flatten -> redact safe -> ocr -> validate`
