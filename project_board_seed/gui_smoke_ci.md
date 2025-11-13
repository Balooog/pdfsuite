## Summary

Add GUI build + smoke coverage so PyInstaller bundles stay healthy and key flows
can run headlessly on CI.

## Acceptance criteria

- [ ] Provide a `make gui` (or equivalent) target that builds PyInstaller bundles on Linux and Windows using the GUI extras.
- [ ] Land a GitHub Actions workflow that runs `pytest-qt` smoke tests under xvfb and archives the PyInstaller artifacts.
- [ ] Cover at least Dashboard → queue job execution plus one panel workflow (e.g., OCR) in the smoke so subprocess piping is exercised.
- [ ] Document the workflow updates in `docs/TESTING_HANDBOOK.md` and `docs/GUI_TECH.md` (build steps, troubleshooting).

## Notes

- Reuse the existing `scripts/smoke_test.sh` fixtures where possible.
- Ensure cacheable dependencies (PySide6, PyInstaller) are pinned to keep CI reproducible.
- Include artifact signing/timestamp placeholders if full release automation is deferred to v0.5.0.
