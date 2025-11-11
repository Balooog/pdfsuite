from pathlib import Path

import typer

from pdfsuite.utils.common import (
    ensure_file,
    ensure_output_dir,
    parse_range_sequence,
    require_tools,
    run_or_exit,
    safe_range_name,
    shell_quote,
)


def register(app: typer.Typer) -> None:
    @app.command(help="Split PDFs into page range slices.")
    def split(  # noqa: A003 - command name
        input: Path = typer.Argument(..., help="Source PDF to split."),
        pages: str = typer.Option(
            ...,
            "--pages",
            help="Comma separated ranges (e.g. 1-3,4,5-z).",
        ),
        output: Path = typer.Option(
            Path("splits"),
            "-o",
            help="Directory to place split PDFs (default: ./splits).",
        ),
    ) -> None:
        require_tools("qpdf")
        source = ensure_file(input, label="input PDF")
        ranges = parse_range_sequence(pages)
        ensure_output_dir(output)
        for token in ranges:
            safe_name = safe_range_name(token)
            dest = output / f"{source.stem}_{safe_name}.pdf"
            cmd = (
                f"qpdf {shell_quote(source)} --pages {shell_quote(source)} "
                f"{shell_quote(token)} -- {shell_quote(dest)}"
            )
            run_or_exit(cmd)
