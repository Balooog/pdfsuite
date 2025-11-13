# Project Board

GitHub Projects keeps pdfsuite’s roadmap items visible between releases. We use the
repo-scoped board at https://github.com/Balooog/pdfsuite/projects/1.

## Column layout

- **Backlog** – raw ideas and roadmap slices that still need grooming.
- **In Progress** – work with an assigned owner and an active branch/PR.
- **QA / Review** – code complete work that still needs reviews, tests, or docs sign-off.
- **Done** – merged & released work (close the linked issue once the release ships).

## Automation

- Every issue/PR tagged with the `v0.3.0` milestone auto-lands in Backlog.
- Closing an issue automatically moves its card to Done.
- Cards without issues are allowed (for chores), but convert them into issues before moving to QA.

## Seeding the backlog

Use the helper script to open issues (one per seed card) and place them in Backlog:

```bash
./scripts/seed_project_board.sh
```

Environment variables:

- `REPO` (default `Balooog/pdfsuite`)
- `MILESTONE` (default `v0.3.0`)

Each issue body lives under `project_board_seed/` if you prefer manual commands, e.g.:

```bash
gh issue create \
  --repo Balooog/pdfsuite \
  --title "CLI coverage expansion" \
  --body-file project_board_seed/cli_coverage_expansion.md \
  --milestone v0.3.0
```

Seed cards to create:

- **v0.3.0 quality gates**
  1. **CLI coverage expansion** – more pytest slices to push coverage past 60%.
  1. **Windows smoke parity** – replicate Linux smoke breadth on Windows runners.
  1. **Docs lint enforcement** – formalize contributor hooks to match CI’s doc gate.
  1. **Contributor Guide refresh** – teach new contributors how to use the board + CI.
- **v0.4.0 GUI + security gates**
  1. **GUI shell MVP** – PySide6 shell plus Dashboard/Pages/OCR/Redact/Sign panels wired to the CLI.
  1. **GUI smoke CI + PyInstaller** – xvfb + pytest-qt smokes and artifact builds in GitHub Actions.
  1. **Security & privacy gate** – redaction validation demo + signing key hygiene checklist updates.

Link each issue to the roadmap milestone so the board reflects progress automatically.

______________________________________________________________________

Related docs: [Roadmap](ROADMAP.md) · [Project Launch](PROJECT_LAUNCH.md) ·
[Testing Handbook](TESTING_HANDBOOK.md)
