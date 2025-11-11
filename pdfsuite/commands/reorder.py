from pathlib import Path

import typer

from pdfsuite.utils.common import (
    ensure_file,
    parse_range_sequence,
    require_tools,
    run_or_exit,
    shell_quote,
)


def register(app: typer.Typer) -> None:
    @app.command()
    def reorder(
        input: Path,
        order: str = typer.Option(
            ...,
            "--order",
            help="Comma separated page ranges (e.g. 5-7,1-4,8-z).",
        ),
        output: Path = typer.Option(..., "-o", help="Reordered PDF output."),
    ):
        """Reorder, duplicate, or drop pages using qpdf."""
        require_tools("qpdf")
        source = ensure_file(input, label="input PDF")
        ranges = parse_range_sequence(order)
        spec = ",".join(ranges)
        cmd = (
            f"qpdf {shell_quote(source)} --pages {shell_quote(source)} "
            f"{shell_quote(spec)} -- {shell_quote(output)}"
        )
        run_or_exit(cmd)
