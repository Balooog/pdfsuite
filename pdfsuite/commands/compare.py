from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List

import typer

from pdfsuite.utils.common import (
    ensure_output_dir,
    require_tools,
    run_or_exit,
    shell_quote,
    temporary_directory,
)


def register(app: typer.Typer) -> None:
    @app.command()
    def compare(
        first: Path,
        second: Path,
        output: Path = typer.Option(..., "-o", help="Diff PDF output."),
        headless: bool = typer.Option(
            False,
            "--headless",
            help="Force Poppler/ImageMagick pipeline instead of diff-pdf.",
        ),
    ):
        """Compare PDFs via diff-pdf (preferred) or Poppler/ImageMagick."""
        if headless:
            headless_diff(first, second, output)
            return

        diff_pdf = shutil.which("diff-pdf")
        diffpdf_gui = shutil.which("diffpdf")
        if diff_pdf:
            require_tools("diff-pdf")
            cmd = (
                f"diff-pdf --output-diff={shell_quote(output)} "
                f"{shell_quote(first)} {shell_quote(second)}"
            )
            run_or_exit(cmd)
            return

        if diffpdf_gui:
            require_tools("diffpdf")
            typer.echo(
                "diff-pdf CLI not found. Launching diffpdf GUI "
                "for manual comparison.",
                err=True,
            )
            cmd = f"diffpdf {shell_quote(first)} {shell_quote(second)}"
            run_or_exit(cmd)
            return

        typer.echo(
            "No compare tools found. Install diff-pdf or run with --headless "
            "after installing pdftocairo, compare, and img2pdf.",
            err=True,
        )
        raise typer.Exit(1)


def headless_diff(first: Path, second: Path, output: Path) -> None:
    require_tools("pdftocairo", "compare", "img2pdf")
    with temporary_directory("pdfsuite-compare-") as tmp:
        a_dir = ensure_output_dir(tmp / "a")
        b_dir = ensure_output_dir(tmp / "b")
        diff_dir = ensure_output_dir(tmp / "diff")

        a_pages = render_pngs(first, a_dir / "page")
        b_pages = render_pngs(second, b_dir / "page")

        if len(a_pages) != len(b_pages):
            typer.echo(
                "Inputs have different page counts; cannot compare headlessly.",
                err=True,
            )
            raise typer.Exit(1)

        diff_pages: List[Path] = []
        for idx, (a_img, b_img) in enumerate(zip(a_pages, b_pages), start=1):
            diff_img = diff_dir / f"diff-{idx:03d}.png"
            cmd = (
                f"compare -highlight-color blue "
                f"{shell_quote(a_img)} {shell_quote(b_img)} {shell_quote(diff_img)}"
            )
            result = subprocess.run(cmd, shell=True)
            if result.returncode not in (0, 1):
                raise typer.Exit(result.returncode)
            if not diff_img.exists():
                diff_img.touch()
            diff_pages.append(diff_img)

        if not diff_pages:
            typer.echo("No diff images produced.", err=True)
            raise typer.Exit(1)

        files = " ".join(shell_quote(path) for path in sorted(diff_pages))
        cmd = f"img2pdf {files} -o {shell_quote(output)}"
        run_or_exit(cmd)


def render_pngs(pdf: Path, prefix: Path) -> List[Path]:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    cmd = f"pdftocairo -png {shell_quote(pdf)} {shell_quote(prefix)}"
    run_or_exit(cmd)
    parent = prefix.parent
    images = sorted(parent.glob(f"{prefix.name}-*.png"))
    if not images:
        typer.echo(f"No rasterized pages produced for {pdf}", err=True)
        raise typer.Exit(1)
    return images
