# Project Roadmap

Strategic milestones for pdfsuite as we transition from the v0.1.0 baseline into a hardened, GUI-ready release. Each phase lists owned areas (CLI, GUI, testing, docs, release) plus acceptance criteria.

## Versioning & branching

- **Semantic versioning** – bump minor for new features (v0.2, v0.3), patch for fixes.
- **Branches** – `main` stays releasable; create topic branches `feature/<slug>` and merge via PR with required status checks (lint, smoke, docs).
- **Tags** – we still create annotated tags (`v0.2.0`, `v0.3.0`, …) as internal checkpoints, but we only push/publish them when we’re ready for a public release (target: v1.0 or whenever we explicitly call it).
- **Release cadence** – checkpoints can happen as often as needed; formal releases (GitHub notes + artifacts) start once the GUI hardening is ready around v1.0.

## Milestones

### v0.1.0 – Baseline (✅)

- Core CLI commands (merge, OCR, optimize, stamp, forms, redact, sign, verify, doctor).
- README + Project Launch + Operator Guide published.
- `pip install -e .` / pipx install instructions verified.

### v0.2.0 – CLI Expansion

- Implement remaining commands (split, reorder, compare, audit) with shared helpers.
- Enhance doctor/install scripts; ensure run-logging consistency.
- Manual testing of new commands; documentation updated accordingly.

### v0.3.0 – Quality & Documentation

- Introduce pytest scaffolding + coverage (target ≥40%) and run smoke tests in CI (Ubuntu+Windows).
- Launch CLI Reference library + Contributor Guide + GitHub Project board (Backlog/In Progress/QA/Done).
- Add doc linting (markdownlint/mdformat) so builds fail on syntax/link errors.

### v0.4.0 – GUI MVP + Security

- PySide6 shell with Dashboard, Reader, Bookmarks, Pages, OCR/Optimize (presets), 3D Viewer, Redact, Sign, and Settings panels wired to the CLI runner with per-job logs.
- GUI smoke tests (pytest-qt under xvfb) integrate with CI; `make gui` builds PyInstaller bundles ready for AppImage/Windows experiments.
- Security & Privacy doc reviewed; redaction validation demo ensures no residual text; signing key hygiene checklist.
- Watch-folder CLI (`pdfsuite watch`) lands for automated optimize workflows; GUI exposes corresponding presets in Settings ahead of a dedicated automation panel.

### v0.5.0 – Docs & Distribution

- Testing Handbook, Troubleshooting FAQ, Release Playbook, and Surfer Figure Export guide fully populated and lint-clean.
- Automated changelog + GitHub Release workflow (attach AppImage + Windows bundle, sign artifacts).
- Documentation portal considered frozen for v1 scope; doc lint is mandatory gate.

### v0.6.0 – Usability Polish

- GUI preferences (tool paths, doctor dialog), logging viewer, progress bar, queue persistence.
- Platform-specific fixes ensuring GUI parity on Linux/Windows; expanded integration smoke coverage.
- Issue triage via GitHub Project board; all UX bugs tracked/closed before v1 freeze.

### v1.0.0 – Hardened Release

- Full GUI feature set (OCR/Optimize, Redact, Forms, Stamp, Sign, Compare, Settings) and job queue persistence.
- Reproducible installers (pipx, AppImage, Windows installer) with signed artifacts and SBOM.
- CI includes nightly regression suite plus documentation link validation; docs at 100%.

## Supporting tracks

| Track | Description | Target start | | --- | --- | --- | | Docs infrastructure | MkDocs site, CLI Reference, Contributor Guide, doc linting | v0.3.0 | | Testing escalation | Pytest coverage + GUI smoke tests; coverage target increases each release | v0.3.0 → v0.4.0 | | Reader MVP polish | Default-app UX (thumbnails, outline, drag reorder, Save/Save As), shared document session, smooth zoom/pan gestures | v0.4.0 | | Release automation | Auto changelog + release artifacts (AppImage/Windows zip) via GitHub Actions | v0.5.0 | | Security validation | Redaction verification routine; signing key hygiene audits | v0.4.0 → v0.5.0 | | Project management | GitHub Project board (Backlog/In Progress/QA/Done) + milestone labels | v0.3.0 |

## Next actions

1. Cut the v0.2.0 checkpoint tag locally (CLI expansion) once smoke + docs sign-off land; keep it private until we decide to publish a full release.
1. Stand up GitHub Project board + pytest scaffolding; integrate doc lint + smoke workflow in CI (v0.3.0 gate). See [Project Board](PROJECT_BOARD.md) for column layout and seed issues.
1. Begin PySide6 skeleton + GUI doc updates once CI foundations are stable (pre-v0.4.0). Reader MVP polish work (default-app gestures + document session) lives in this lane so it can feed the Pages integration.

## Future work / v1.x+ backlog

v1.0 delivers Acrobat-grade parity with a stable GUI, CI, and distribution pipeline. Subsequent releases will focus on advanced workflows, extensibility, and automation.

### Reader continuous improvements

- Multi-tab Reader + split-view compare modes.
- Snapshot/export helpers (PNG/PDF), auto-bookmarks from heading detection, HiDPI thumbnail tiling.
- Accessibility: keyboard-first navigation, announcing page/zoom changes, high-contrast theme.

| Track | Summary | Target range | | --- | --- | --- | | Advanced GUI | Native annotation enhancements, multi-document workspace, visual diff heatmaps | v1.1–v1.2 | | Workflow automation | Saved pipelines, watch folders, scheduling, queue templates | v1.2–v1.3 | | Collaboration & audit | Shared configs, audit logs, optional DMS/cloud integrations | v1.3–v2.0 | | Plugin API | User-defined tool adapters/pipelines for additional utilities | v1.4–v2.0 | | Localization & accessibility | GUI translations, keyboard shortcuts, accessibility improvements | v1.1–v1.2 |

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [Project Launch](PROJECT_LAUNCH.md) · [GUI Technical Plan](GUI_TECH.md)
