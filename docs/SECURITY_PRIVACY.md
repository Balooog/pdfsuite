# Security & Privacy Notes

Principles for handling sensitive documents with pdfsuite.

## Redaction
- Always use `pdfsuite redact safe` for sensitive removals (rasterize + sanitize).
- Follow with `pdfsuite ocr` if you need searchable output; validate via `pdfsuite audit`.

## Signing
- Store `.p12` files outside the repo; never commit credentials.
- Prefer strong passwords; use environment prompts rather than inline arguments.

## Metadata & temp files
- Run `pdfsuite metadata_scrub` on outbound documents.
- Temp artifacts live under `build/` by default; configure secure locations (e.g., `~/.cache/pdfsuite/<job>` with restricted permissions).
- Recommend `umask 077` during sensitive workflows.

## Toolchain trust
- Install binaries from official sources; verify checksums when possible.
- Keep track of versions via `pdfsuite doctor` output for audits.

---

Related docs: [Documentation Index](DOCS_INDEX.md) · [Troubleshooting FAQ](TROUBLESHOOTING_FAQ.md) · [GUI User Guide](GUI_USER_GUIDE.md)
