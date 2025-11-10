from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command("metadata_scrub")
    def metadata_scrub(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Metadata-clean output"),
    ):
        """Remove metadata using MAT2."""
        require_tools("mat2")
        cmd = f"mat2 --inplace=false -o {shell_quote(output)} {shell_quote(input)}"
        run_or_exit(cmd)
