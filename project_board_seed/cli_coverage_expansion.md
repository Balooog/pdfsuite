## Summary

Expand the CLI coverage suite so merge/split/reorder helpers and adjacent utilities drive
overall coverage beyond 60%.

## Acceptance criteria

- [ ] Add pytest cases for `pdfsuite.commands.merge`, `split`, and `reorder`, plus any shared helpers they rely on.
- [ ] Ensure coverage gates in `pyproject.toml` pass locally and on CI with the new tests.
- [ ] Document any new fixtures or helper utilities in `docs/TESTING_HANDBOOK.md`.

## Notes

- Use `pytest --cov=pdfsuite --cov-report=term-missing` to confirm deltas.
- Reference `tests/test_commands_merge_split_reorder.py` for stub patterns if further helpers are added.
