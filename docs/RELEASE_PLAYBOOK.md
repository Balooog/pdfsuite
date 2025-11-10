# Release Playbook

Repeatable checklist for tagging and publishing pdfsuite releases.

## Preflight
- Ensure `main` is green (CI + docs + smoke tests).
- Verify docs updated (Operator Guide, CLI reference, GUI docs).
- Confirm dependencies (`scripts/doctor.py`) pass on reference environment.

## Steps
| Step | Action |
| --- | --- |
| 1 | Update version in `pyproject.toml` and `pdfsuite/__init__.py`. |
| 2 | Document changes in `CHANGELOG.md` (adhere to Keep a Changelog). |
| 3 | Commit with `chore: release vX.Y.Z`. |
| 4 | Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"` |
| 5 | Push: `git push origin main --tags` |
| 6 | Build artifacts: `pip install -e .`, `python -m build`, PyInstaller GUI bundles. |
| 7 | Smoke test artifacts on Linux + Windows. |
| 8 | Sign artifacts if applicable (GPG/Sigstore). |
| 9 | Draft GitHub Release with highlights + attach binaries. |
| 10 | Publish release, announce in changelog and docs. |

## Changelog template
```
## [vX.Y.Z] - YYYY-MM-DD
### Added
- 
### Changed
- 
### Fixed
- 
### Removed
- 
```

## Post-release
- Merge back any hotfix branches.
- Update roadmap milestones.
- Monitor issues for regressions.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Contributor Guide](CONTRIBUTOR_GUIDE.md) · [Testing Handbook](TESTING_HANDBOOK.md)
