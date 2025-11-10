from pathlib import Path

import typer

from pdfsuite.utils.common import (
    ensure_output_dir,
    parse_range_sequence,
    require_tools,
    run_or_exit,
    safe_range_name,
    shell_quote,
)

split_app = typer.Typer(help="Split PDFs into page range slices.")


@split_app.callback(invoke_without_command=True)
def split_main(
    ctx: typer.Context,
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
):
    if ctx.invoked_subcommand is not None:
        return
    require_tools("qpdf")
    ranges = parse_range_sequence(pages)
    ensure_output_dir(output)
    for token in ranges:
        safe_name = safe_range_name(token)
        dest = output / f"{input.stem}_{safe_name}.pdf"
        cmd = (
            f"qpdf {shell_quote(input)} --pages {shell_quote(input)} "
            f"{token} -- {shell_quote(dest)}"
        )
        run_or_exit(cmd)


def register(app: typer.Typer) -> None:
    app.add_typer(split_app, name="split")
