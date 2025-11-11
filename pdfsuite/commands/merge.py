from pathlib import Path

import typer

from pdfsuite.utils.common import ensure_file, run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command(help="Merge PDFs with qpdf.")
    def merge(
        inputs: list[Path] = typer.Argument(..., help="Input PDFs in desired order."),
        output: Path = typer.Option(..., "-o", help="Merged PDF output."),
    ) -> None:
        require_tools("qpdf")
        safe_inputs = [ensure_file(path, label="input PDF") for path in inputs]
        segments = " ".join(f"{shell_quote(path)} 1-z" for path in safe_inputs)
        cmd = f"qpdf --empty --pages {segments} -- {shell_quote(output)}"
        run_or_exit(cmd)
