## Summary

Close the v0.4.0 security/privacy gates by validating safe redaction, reviewing
signing key hygiene, and refreshing the Security & Privacy doc with the GUI
surface area.

## Acceptance criteria

- [ ] Produce a reproducible “redaction validation” demo (script + docs) that proves `pdfsuite redact safe` leaves no searchable text; include verification steps via `pdfsuite audit`.
- [ ] Expand `docs/SECURITY_PRIVACY.md` with GUI guidance (doctor reminders, temp file handling, queue hygiene) and link it from the GUI user guide.
- [ ] Add a signing key hygiene checklist (storage, password rotation, verification) to `docs/OPERATOR_GUIDE.md` or a new dedicated doc referenced from the Security notes.
- [ ] Ensure the checklist + demo steps are referenced from the release playbook so the gate is part of preflight.

## Notes

- Consider recording the validation demo output (logs/artifacts) under `docs/assets/` or `build/security/`.
- Capture dependencies (ocrmypdf, pdftotext) required to verify redaction so contributors can rerun locally.
- Coordinate with CI so at least metadata scrub + audit coverage runs on sample files during release candidates.
