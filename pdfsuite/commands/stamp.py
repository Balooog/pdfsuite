import shutil
import subprocess
from pathlib import Path

import typer

from pdfsuite.utils.common import (
    ensure_file,
    run_or_exit,
    require_tools,
    shell_quote,
    temporary_directory,
)


def register(app: typer.Typer) -> None:
    @app.command()
    def stamp(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Stamped PDF output"),
        bates: str = typer.Option(None, "--bates", help="Bates prefix text."),
        start: int = typer.Option(1, "--start", help="Starting Bates number."),
    ):
        """Stamp/watermark/Bates using pdfcpu."""
        source = ensure_file(input, label="input PDF")
        if bates:
            require_tools("pdfcpu", "qpdf")
            stamp_bates(source, output, bates, start)
            return

        require_tools("pdfcpu")
        stamp_text(source, output, "1-", "CONFIDENTIAL")


def stamp_text(input_pdf: Path, output_pdf: Path, pages: str, text: str) -> None:
    cmd = (
        "pdfcpu stamp add -mode text "
        f"-p {shell_quote(pages)} -- {shell_quote(text)} {shell_quote('')} "
        f"{shell_quote(input_pdf)} {shell_quote(output_pdf)}"
    )
    run_or_exit(cmd)


def stamp_bates(input_pdf: Path, output_pdf: Path, prefix: str, start: int) -> None:
    total = get_page_count(input_pdf)
    if total <= 0:
        typer.echo("Unable to detect page count for Bates stamping.", err=True)
        raise typer.Exit(1)

    with temporary_directory("pdfsuite-stamp-") as tmpdir:
        working = tmpdir / "work.pdf"
        shutil.copy2(input_pdf, working)
        current_input = working
        for idx in range(total):
            page_num = idx + 1
            label = f"{prefix}:{start + idx:04d}"
            next_output = tmpdir / f"pass-{page_num}.pdf"
            stamp_text(current_input, next_output, str(page_num), label)
            current_input = next_output
        shutil.copy2(current_input, output_pdf)


def get_page_count(pdf: Path) -> int:
    result = subprocess.run(
        ["qpdf", "--show-npages", str(pdf)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0
