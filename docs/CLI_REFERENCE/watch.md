# watch

Monitor a directory for new PDFs and automatically run `pdfsuite optimize` with the chosen preset. Useful for “Printed PDFs” folders on Windows or CUPS-PDF output on Linux.

## Syntax

```
pdfsuite watch [--path <dir>] [--preset <email|report|poster>]
               [--target-size <MB>] [--poll-interval <sec>]
               [--settle <sec>] [--once]
```

**External tools:** same as `optimize` (Ghostscript + qpdf)

## Options

- `--path` – directory to monitor (defaults to `~/PDF` on Linux or `~/Documents/Printed PDFs` on Windows; created if missing).
- `--preset` – optimization profile applied to new files.
- `--target-size` – optional MB goal; triggers retries just like the CLI optimize command.
- `--poll-interval` – how often to rescan for fresh PDFs (default 5s).
- `--settle` – minimum age (seconds) before treating a file as stable to avoid processing in-progress prints (default 2s).
- `--once` – scan immediately, process anything new, then exit (handy for scripts/tests).

Processed files are written to `~/pdfsuite/build/watch/<original_name>_<timestamp>.pdf` so the originals remain untouched.

## Example

```
pdfsuite watch --preset email --target-size 3
```

Watches the default folder and compresses every new PDF to ≈3 MB or less, logging progress to stdout.

______________________________________________________________________

Related docs: [Optimize](optimize.md) · [Surfer Figure Export](../SURFER_FIGURE_EXPORT.md) · [Documentation Index](../DOCS_INDEX.md)
