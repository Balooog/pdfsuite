from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote

merge_app = typer.Typer(help="Merge PDFs with qpdf.")


@merge_app.callback(invoke_without_command=True)
def merge_main(
    ctx: typer.Context,
    inputs: list[Path] = typer.Argument(None, help="Input PDFs in desired order."),
    output: Path = typer.Option(None, "-o", help="Merged PDF output."),
):
    if ctx.invoked_subcommand is not None:
        return
    if not inputs or output is None:
        raise typer.Exit(code=2)
    require_tools("qpdf")
    segments = " ".join(f"{shell_quote(path)} 1-z" for path in inputs)
    cmd = f"qpdf --empty --pages {segments} -- {shell_quote(output)}"
    run_or_exit(cmd)


def register(app: typer.Typer) -> None:
    app.add_typer(merge_app, name="merge")
