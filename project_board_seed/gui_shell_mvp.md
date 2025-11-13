## Summary

Stand up the PySide6 GUI shell with the core navigation stack plus a background
runner that shells out to the existing CLI workflows.

## Acceptance criteria

- [ ] Add a `gui/` package with `main.py`, `services/runner.py`, and panel modules for Dashboard, Pages, OCR, Redact, and Sign.
- [ ] Each panel must invoke the `pdfsuite` CLI via the shared runner and surface the command preview/log stream.
- [ ] Document launch instructions (`make gui`, dev deps) in `docs/GUI_TECH.md` or `docs/GUI_OVERVIEW.md`.
- [ ] Landing page (`README.md` or `docs/index.md`) links to the GUI docs so contributors can exercise the shell.

## Notes

- Mirror the layout described in `docs/GUI_WIREFRAMES.md`.
- Keep the GUI thin—panels enqueue jobs and let the runner handle all subprocess work.
- Ensure doctor status + quick actions are visible on the Dashboard before wiring secondary panels.
