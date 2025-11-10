from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command()
    def stamp(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Stamped PDF output"),
        bates: str = typer.Option(None, "--bates", help="Bates prefix text."),
        start: int = typer.Option(1, "--start", help="Starting Bates number."),
    ):
        """Stamp/watermark/Bates using pdfcpu."""
        require_tools("pdfcpu")
        text = shell_quote(f"{bates}:%04d") if bates else shell_quote("CONFIDENTIAL")
        extra = f"-s {start} " if bates else ""
        cmd = (
            "pdfcpu stamp add -mode text "
            f"{text} -p 1- {extra}"
            f"-o {shell_quote(output)} {shell_quote(input)}"
        )
        run_or_exit(cmd)
