## Summary

Bring Windows CI smoke coverage in line with Linux by running additional pdfsuite commands once fixtures are available.

## Acceptance criteria

- [ ] Extend `.github/workflows/ci.yml` Windows job to execute at least one additional command flow (`split` or `compare`).
- [ ] Provide any new fixture PDFs under `tests/fixtures/` with clear naming.
- [ ] Update `docs/TESTING_HANDBOOK.md` with the new smoke coverage expectations.

## Notes

- Prefer commands that do not require proprietary dependencies so they run cleanly on GitHub-hosted Windows runners.
- Coordinate with CLI coverage work so fixtures are reused when possible.
