# Contributor Guide

Guidelines for building and maintaining pdfsuite.

## Branching & commits

- `main` stays green; feature branches named `feat/<topic>` or `fix/<issue>`.
- Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`) with concise scopes.
- Rebase before pushing to keep history linear.

## Development workflow

1. `make dev` (creates venv, installs deps).
1. Implement changes in `pdfsuite/commands/` or GUI modules.
1. Run format/lint: `make format && make lint`.
1. Run doc lint: `make doclint` (mdformat `--wrap no` check for every Markdown file).
1. Execute smoke tests: `bash scripts/smoke_test.sh`.
1. Update docs (CLI reference, guides) for any user-visible change and log recurring hiccups in [`CommonErrors.md`](../CommonErrors.md) so future contributors can self-serve fixes.
1. Open PR referencing issues; fill template (scope, tests, rollback plan).

## Code style

- Python 3.9+, Black (100 cols), isort (black profile).
- Type hints required; avoid implicit Any.
- Shell interactions go through `pdfsuite.utils.common.run_or_exit`.
- Prefer small modules; commands live in `pdfsuite/commands/<name>.py`.

## Docs lint & hooks

- Markdown must pass `make doclint` before review; it runs `mdformat --wrap no --check` against every tracked `.md`.
- Install docs tooling once per clone: `. .venv/bin/activate && pip install -e .[docs] && pre-commit install`.
- To fix lint issues manually, run `mdformat --wrap no path/to/file.md` or `pre-commit run mdformat --all-files`.
- If mdformat rewrites large sections (tables, lists), skim the diff and commit—this is the canonical style that CI enforces.
- Pre-commit also runs trailing whitespace, EOF, YAML/JSON sanity, and large-file checks—rerun `pre-commit run --all-files` if any of these fail.

## Reviews

- At least one maintainer approval + passing CI (lint, smoke, docs).
- Address review feedback via follow-up commits (no force-push after review unless requested).

______________________________________________________________________

Related docs: [Documentation Index](DOCS_INDEX.md) · [Testing Handbook](TESTING_HANDBOOK.md) · [Common Errors](../CommonErrors.md) · [Release Playbook](RELEASE_PLAYBOOK.md)
