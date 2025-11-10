# GUI Wireframes (Text)

ASCII sketches of the primary screens to anchor early design discussions. Real implementation will use PySide6 widgets, but these wireframes illustrate layout and hierarchy.

## 1. Dashboard
```
+--------------------------------------------------------------------------------+
| PDFSUITE ▸ Dashboard     [Open File] [Run Queue ▼]                 [Doctor ✅] |
|--------------------------------------------------------------------------------|
| Quick Actions:                     | Recent Jobs                               |
| [ Merge PDFs ] [ OCR Scan ]        | • Merge A+B → merged.pdf (2m ago)         |
| [ Optimize for Email ]             | • OCR invoices.pdf (Today 09:12)          |
| [ Bates Batch ] [ Safe Redact ]    | • Compare draft-v1.pdf (Yesterday)        |
|------------------------------------+-------------------------------------------|
| Job Queue (drag to reorder)                                                     |
| 1. OCR invoices.pdf → ocr_out.pdf                                              |
| 2. Optimize ocr_out.pdf → ocr_small.pdf                                        |
| 3. Bates stamping…                                                               |
| [Add Action] [Start Queue]                                                     |
+--------------------------------------------------------------------------------+
| Status: No jobs running. Output dir: ~/pdfsuite/build                          |
+--------------------------------------------------------------------------------+
```

## 2. Pages Panel (Merge/Split/Reorder)
```
+--------------------------------------------------------------------------------+
| PDFSUITE ▸ Pages            [Add PDFs] [Export Selected]             [Doctor ✅]|
|--------------------------------------------------------------------------------|
| Thumbnails (drag to reorder, multi-select)                                     |
| [p1] [p2] [p3] [p4] [p5] ...                                                   |
|--------------------------------------------------------------------------------|
| Range Input: [ 1-3, 5, 8- ]     Apply To: ( ) Split  (•) Reorder  ( ) Delete   |
| Rotate: [↻90] [↻180]  Crop: X:[____] Y:[____] W:[____] H:[____]                |
| Output: [ merged.pdf        ][Browse]                                          |
| Command Preview: qpdf --empty --pages ...                                      |
| [Run Now] [Enqueue]                                                            |
+--------------------------------------------------------------------------------+
| Logs ▸                                                                        |
| $ pdfsuite merge inputA.pdf inputB.pdf -o merged.pdf                           |
| ...                                                                            |
+--------------------------------------------------------------------------------+
```

## 3. Sign & Verify
```
+--------------------------------------------------------------------------------+
| PDFSUITE ▸ Sign & Verify        [Open PDF] [Save As]               [Doctor ⚠️] |
|--------------------------------------------------------------------------------|
| PDF Preview (page canvas)      | Certificate                          | Logs   |
| [visible rectangle overlay]    | P12 File: [ choose.p12 ] [Browse]    | $ ...  |
| Page: [ 1 ]  X:[ 50 ] Y:[ 60 ] | Alias: [ text field ]                |        |
| Width:[200] Height:[60]        | Visible Signature? [✓]               |        |
| Timestamp URL: [ optional ]    | PKCS#12 Password: [••••]             |        |
|--------------------------------+--------------------------------------+--------|
| Output: [ signed.pdf ][Browse]     [Run Sign] [Verify Existing…]               |
+--------------------------------------------------------------------------------+
| Status: Ready to sign. Missing: jsignpdf.jar (click Doctor for help).         |
+--------------------------------------------------------------------------------+
```

## 4. Compare
```
+--------------------------------------------------------------------------------+
| PDFSUITE ▸ Compare              [Open A] [Open B]                [Doctor ✅]  |
|--------------------------------------------------------------------------------|
| File A: [ version-old.pdf  ][Browse]                                           |
| File B: [ version-new.pdf  ][Browse]                                           |
| Mode: (•) diff-pdf  ( ) Headless (pdftocairo + compare + img2pdf)              |
| Output diff: [ diff.pdf ][Browse]                                              |
|--------------------------------------------------------------------------------|
| Preview (if available)                     | Logs                               |
| [page thumbnails with highlights]          | diff-pdf --output-diff=diff.pdf ... |
|                                            | ...                                |
|--------------------------------------------------------------------------------|
| [Run Compare] [Enqueue]                                                         |
+--------------------------------------------------------------------------------+
```

## 5. Settings
```
+--------------------------------------------------------------------------------+
| PDFSUITE ▸ Settings                                              [Doctor ✅]   |
|--------------------------------------------------------------------------------|
| General                       | External Tools                    | Appearance |
| Default output dir: [path]    | qpdf:      [/usr/bin/qpdf   ]     | Theme: (•) |
| Keep temp artifacts: [✓]      | pdfcpu:    [/usr/local/pdfcpu]    | Dark      |
| Log verbosity: [Normal ▼]     | Ghostscript: [ auto ]             | ( ) Light |
| Run doctor on launch: [✓]     | ocrmypdf:  [ auto ]               +-----------+
|--------------------------------+-----------------------------------------------|
| Config file: ~/.config/pdfsuite/config.yml  [Open Config] [Reset to defaults] |
+--------------------------------------------------------------------------------+
```

## Next steps
1. Translate these ASCII layouts into PySide6 UI classes (one per panel) with placeholder widgets so navigation can be exercised early.
2. Capture screenshot wireframes (Figma/Qt Designer) to replace the ASCII sketches once components stabilize.
3. Keep wireframes synced with actual functionality: update this document whenever panels gain new controls or workflows shift.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [GUI Overview](GUI_OVERVIEW.md) · [GUI Technical Plan](GUI_TECH.md)
