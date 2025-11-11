import shutil
from pathlib import Path

import typer

from pdfsuite.utils.common import ensure_file, run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command("metadata_scrub")
    def metadata_scrub(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Metadata-clean output"),
    ):
        """Remove metadata using MAT2."""
        require_tools("mat2")
        source = ensure_file(input, label="input PDF")
        shutil.copy2(source, output)
        cmd = f"mat2 --inplace {shell_quote(output)}"
        run_or_exit(cmd)
