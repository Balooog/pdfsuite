# PDFSuite agent playbook

Central guide for Codex/AI agents working in this repo. Update it whenever workflows or gotchas evolve.

## 1. Quick orientation

- Mission: ship an all-FOSS, Acrobat-grade CLI plus future GUI that shells out to best-in-class tools (qpdf, pdfcpu, Ghostscript, OCRmyPDF/Tesseract, pdftk-java, jSignPdf, MAT2, diff-pdf, etc.).
- Entry point: `pdfsuite/__main__.py` wires Typer commands; each feature lives under `pdfsuite/commands/<feature>.py` and should stay as thin wrappers over helpers + external binaries.
- Read these first: `README.md` (setup + sample commands), `docs/OPERATOR_GUIDE.md` (task recipes), `docs/PROJECT_LAUNCH.md` (tool matrix), `docs/TROUBLESHOOTING_FAQ.md` (field issues).
- Keep `docs/DOCS_INDEX.md` handy; every doc links from there, including GUI plans and release process.
- Local Python deps live in `.venv/`; always `source .venv/bin/activate` before installing extras or running pytest so we keep tooling consistent.

## 2. Day-to-day workflow

1. **Sync context**
   - Skim `agents.md` + `CommonErrors.md` (new issues land there).
   - Check for dirty worktree instructions in the user prompt; never revert unrelated edits.
1. **Design the change**
   - For CLI features, sketch UX in `docs/CLI_REFERENCE/` before coding.
   - Reuse helpers in `pdfsuite/utils/common.py` (`run_or_exit`, `require_tools`, range parsing, temp dirs).
1. **Implement**
   - Keep Typer wiring minimal; business logic stays in command modules or `utils/`.
   - Shell out via helpers, require tools early (`require_tools("qpdf", ...)`) and pass descriptive errors.
1. **Validate**
   - Run targeted commands (`pdfsuite …`), then `bash scripts/smoke_test.sh` / `make smoke` / `just smoke`.
   - Artifacts land under `build/`; inspect logs if failures occur (see `docs/TESTING_HANDBOOK.md`).
1. **Document + retro**
   - Cross-link new behavior in docs (Operator Guide, CLI reference, Troubleshooting).
   - If you hit any reproducible hiccup, append it to `CommonErrors.md` so future agents ramp faster.

## 3. Coding & tooling conventions

- Python 3.9+, Typer + Rich. Format with Black (100 cols) + isort (black profile). Ruff lint optional but appreciated.
- Favor composition: wrap external binaries, don't reimplement PDF logic. Deterministic logs and clear stderr help users debug.
- Respect repository policies: no destructive git commands, no deleting user-owned code, mirror instructions about sandboxing/network access.
- When touching docs, follow MkDocs-friendly relative links and end each doc with a “Related docs” cluster if possible.

## 4. External dependencies

- Required binaries: `qpdf`, `pdfcpu`, `gs`, `ocrmypdf`, `tesseract`, `pdftk`, `java`, `pdfsig`, `mat2`, plus `diff-pdf` (or `diffpdf` GUI fallback).
- Use `pdfsuite doctor` or `scripts/doctor.py` to surface missing deps. Platform bootstrap scripts live in `scripts/install_linux.sh` and `scripts/install_windows.ps1`.
- Before executing a command that needs a binary, call `require_tools(...)` to fail fast with actionable copy. Document OS quirks in the relevant doc and in `CommonErrors.md` when they bite us.

## 5. Testing expectations

- **Smoke tests:** `bash scripts/smoke_test.sh` (or `make smoke` / `just smoke`) cover CLI end-to-end using `tests/fixtures/`. Required before handing work back.
- **Future pytest:** placeholder for unit coverage; stub new tests alongside helpers to seed the suite.
- CI vision: GitHub Actions job for formatter/lint + smoke (Linux now, Windows later) and a docs workflow (`mkdocs build`) before publishing.

## 6. Documentation touchpoints

- Operator workflows: `docs/OPERATOR_GUIDE.md`
- Architecture & roadmap: `docs/ARCHITECTURE_OVERVIEW.md`, `docs/ROADMAP.md`
- Testing/troubleshooting: `docs/TESTING_HANDBOOK.md`, `docs/TROUBLESHOOTING_FAQ.md`
- GUI planning: `docs/GUI_*`
- Release: `docs/RELEASE_PLAYBOOK.md`
- Whenever you add/change behavior, ensure the relevant doc (and CLI reference) reflects it. Mention new issues in `CommonErrors.md`.

## 7. Error intelligence feedback loop

- `CommonErrors.md` (root) tracks mistakes agents encounter (broken commands, missing deps, doc drift, process misreads).
- Each entry should include: context, repo state required to repro, impact, fix/workaround, and follow-up (docs/test updates).
- Skim it before starting work; add new entries right after debugging so knowledge stays fresh.

When in doubt, keep wrappers thin, make logs deterministic, and defer advanced behavior to the upstream tool that already does it best.
