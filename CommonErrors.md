# CommonErrors

Living log of issues Codex/AI agents hit while working in `pdfsuite`. Skim this before starting a task and extend it whenever you debug something reproducible. The goal is to shrink ramp-up time and bake fixes back into docs/tests quickly.

## How to add a new entry
1. Capture the **context** (command, environment, branch state). Mention any prerequisite fixtures or env vars.
2. Describe the **impact** (what broke, user-visible symptoms, logs).
3. Record the **root cause + fix/workaround** so the next agent can apply it immediately.
4. List the **follow-up**: doc updates, tests, or automation needed to prevent recurrence.
5. Link to related files/docs (e.g., `docs/TROUBLESHOOTING_FAQ.md`, `scripts/doctor.py`), and update those docs if the content belongs there too.

> Template:
> ```
> ### <Concise title>  _(date / agent optional)_
> - Context: …
> - Impact: …
> - Root cause: …
> - Fix/Workaround: …
> - Follow-up: …
> - Related docs: […]
> ```

## Current entries

### `pdfsuite doctor` flags missing `pdfcpu`
- Context: Fresh checkout, doctor command, Linux/macOS shells.
- Impact: CLI features that rely on pdfcpu (merge/split/inspect) fail even before runtime.
- Root cause: pdfcpu binary not installed or not on `PATH`.
- Fix/Workaround: Install the release binary, ensure it is executable, and export the install dir to `PATH`. Rerun `pdfsuite doctor`.
- Follow-up: Consider adding a doctor hint that links directly to the install instructions. Track in `docs/OPERATOR_GUIDE.md`.
- Related docs: `docs/TROUBLESHOOTING_FAQ.md`, `scripts/install_linux.sh`

### `pdfsuite redact safe` fails on Windows
- Context: Running `pdfsuite redact safe` from PowerShell or CMD.
- Impact: Command exits with ImageMagick/WSL errors.
- Root cause: `pdf-redact-tools` pipeline depends on ImageMagick/Poppler; easiest path is WSL.
- Fix/Workaround: Run inside WSL (Ubuntu) or install the required binaries via package manager. If Windows-native support matters, document the manual install path.
- Follow-up: Add Windows-specific notes to `docs/OPERATOR_GUIDE.md` redaction section and confirm the CLI surfaces a friendly error.
- Related docs: `docs/TROUBLESHOOTING_FAQ.md`

### `pdfsuite compare --headless` complains about `diff-pdf`
- Context: `pdfsuite compare a.pdf b.pdf --headless`.
- Impact: Command aborts before diffing.
- Root cause: Only GUI `diffpdf` is installed; CLI `diff-pdf` binary missing.
- Fix/Workaround: Install CLI `diff-pdf` (Homebrew, Chocolatey, or build from source). Alternatively run without `--headless` if GUI `diffpdf` is acceptable.
- Follow-up: Mention the dependency explicitly in the Compare CLI reference page.
- Related docs: `docs/TROUBLESHOOTING_FAQ.md`

### OCR output empty even though pages contain text
- Context: `pdfsuite ocr scan.pdf -o scan_ocr.pdf` on files that already contain selectable text.
- Impact: Output PDF appears unchanged; logs mention skipping text.
- Root cause: OCRmyPDF detects existing text and, combined with `--skip-text`, skips OCR.
- Fix/Workaround: Confirm the input truly needs OCR; force processing via environment flag or by removing `--skip-text`.
- Follow-up: Capture an explicit example in `docs/OPERATOR_GUIDE.md` OCR section.
- Related docs: `docs/TROUBLESHOOTING_FAQ.md`

### GUI launcher crashes with missing PySide6
- Context: Running experimental GUI entry point.
- Impact: Immediate import error; GUI does not boot.
- Root cause: Optional PySide6 dependency not installed.
- Fix/Workaround: Install GUI extras (future `pip install .[gui]`) or run the installer script once it exists.
- Follow-up: Track GUI dependency installation steps in `docs/GUI_TECH.md` and signal them from the CLI if GUI features are invoked.
- Related docs: `docs/TROUBLESHOOTING_FAQ.md`, `docs/GUI_TECH.md`
