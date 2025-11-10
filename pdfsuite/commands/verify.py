from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command()
    def verify(input: Path):
        """Verify existing signatures via pdfsig."""
        require_tools("pdfsig")
        cmd = f"pdfsig {shell_quote(input)}"
        run_or_exit(cmd)
