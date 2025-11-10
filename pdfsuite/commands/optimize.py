from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command()
    def optimize(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Optimized PDF output"),
    ):
        """Compress/flatten using Ghostscript presets."""
        require_tools("gs")
        cmd = (
            "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 "
            "-dPDFSETTINGS=/printer -dDetectDuplicateImages=true "
            "-dDownsampleColorImages=true -dColorImageResolution=150 "
            f"-o {shell_quote(output)} {shell_quote(input)}"
        )
        run_or_exit(cmd)
