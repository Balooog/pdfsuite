from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command()
    def ocr(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Output PDF"),
    ):
        """Add searchable text layer using OCRmyPDF."""
        require_tools("ocrmypdf")
        cmd = f"ocrmypdf {shell_quote(input)} {shell_quote(output)}"
        run_or_exit(cmd)
