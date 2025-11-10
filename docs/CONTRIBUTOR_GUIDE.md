# Contributor Guide

Guidelines for building and maintaining pdfsuite.

## Branching & commits
- `main` stays green; feature branches named `feat/<topic>` or `fix/<issue>`.
- Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`) with concise scopes.
- Rebase before pushing to keep history linear.

## Development workflow
1. `make dev` (creates venv, installs deps).
2. Implement changes in `pdfsuite/commands/` or GUI modules.
3. Run format/lint: `make format && make lint`.
4. Execute smoke tests: `bash scripts/smoke_test.sh`.
5. Update docs (CLI reference, guides) for any user-visible change.
6. Open PR referencing issues; fill template (scope, tests, rollback plan).

## Code style
- Python 3.9+, Black (100 cols), isort (black profile).
- Type hints required; avoid implicit Any.
- Shell interactions go through `pdfsuite.utils.common.run_or_exit`.
- Prefer small modules; commands live in `pdfsuite/commands/<name>.py`.

## Reviews
- At least one maintainer approval + passing CI (lint, smoke, docs).
- Address review feedback via follow-up commits (no force-push after review unless requested).

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Testing Handbook](TESTING_HANDBOOK.md) · [Release Playbook](RELEASE_PLAYBOOK.md)
