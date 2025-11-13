from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple

import typer

from pdfsuite.utils.common import ensure_file, require_tools
from pdfsuite.commands.optimize import run_optimize_pipeline


def register(app: typer.Typer) -> None:
    @app.command()
    def figure(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Output PDF"),
        target_size: float = typer.Option(
            None,
            "--target-size",
            min=0.1,
            help="Optional size target (MB).",
        ),
    ):
        """Auto-pick optimization preset for figure-heavy PDFs."""
        require_tools("pdfimages")
        source = ensure_file(input, label="input PDF")
        preset = detect_preset(source)
        typer.echo(f"[dim]figure[/dim] Selected preset '{preset}'.")
        run_optimize_pipeline(source, output, preset, target_size_mb=target_size)


def detect_preset(path: Path) -> str:
    listings = run_pdfimages_list(path)
    image_count = len(listings)
    large_images = sum(1 for img in listings if img[0] >= 2000 or img[1] >= 2000)
    if image_count == 0:
        return "poster"
    if large_images >= 2 or image_count >= 5:
        return "email"
    return "report"


def run_pdfimages_list(path: Path) -> list[Tuple[int, int]]:
    result = subprocess.run(
        ["pdfimages", "-list", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        typer.echo("pdfimages failed to inspect PDF.", err=True)
        raise typer.Exit(result.returncode)
    lines = result.stdout.splitlines()
    data = []
    for line in lines[2:]:
        tokens = line.split()
        if len(tokens) < 5:
            continue
        try:
            width = int(tokens[3])
            height = int(tokens[4])
        except ValueError:
            continue
        data.append((width, height))
    return data
