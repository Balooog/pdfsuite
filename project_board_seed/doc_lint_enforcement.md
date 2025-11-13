## Summary

Ensure every contributor runs the same markdown formatting checks locally to match the CI doc lint gate.

## Acceptance criteria

- [ ] Add a pre-commit hook (or document a `pre-commit` config) that runs `mdformat`.
- [ ] Update `docs/CONTRIBUTOR_GUIDE.md` with the workflow and troubleshooting tips.
- [ ] Confirm `make doclint` remains the single source of truth and mention it in the Contributor Guide.

## Notes

- Consider adding an optional `pre-commit` entry in `pyproject.toml` extras for easy installation.
- Keep hook configuration minimal so it works cross-platform.
