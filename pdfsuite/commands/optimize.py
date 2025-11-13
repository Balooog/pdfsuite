from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import typer

from pdfsuite.utils.common import (
    ensure_file,
    require_tools,
    run_or_exit,
    shell_quote,
    temporary_directory,
)

PRESETS: Dict[str, Dict[str, object]] = {
    "email": {
        "base_flags": [
            "-dPDFSETTINGS=/screen",
            "-dDetectDuplicateImages=true",
            "-dDownsampleColorImages=true",
        ],
        "resolutions": [150, 120, 96],
    },
    "report": {
        "base_flags": [
            "-dPDFSETTINGS=/printer",
            "-dDetectDuplicateImages=true",
            "-dDownsampleColorImages=true",
        ],
        "resolutions": [300, 240, 200],
    },
    "poster": {
        "base_flags": [
            "-dPDFSETTINGS=/prepress",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
        ],
        "resolutions": [400, 320, 240],
    },
}


def register(app: typer.Typer) -> None:
    @app.command()
    def optimize(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Optimized PDF output"),
        preset: str = typer.Option(
            "report",
            "--preset",
            case_sensitive=False,
            help="email/report/poster presets.",
        ),
        target_size: float = typer.Option(
            None,
            "--target-size",
            min=0.1,
            help="Optional size target in MB; retries with stronger compression if needed.",
        ),
    ):
        """Compress/flatten PDFs via Ghostscript + qpdf linearization."""
        preset_key = preset.lower()
        if preset_key not in PRESETS:
            raise typer.BadParameter(f"Unknown preset '{preset}'. Choose from {', '.join(PRESETS)}.")
        run_optimize_pipeline(
            ensure_file(input, label="input PDF"),
            output,
            preset_key,
            target_size_mb=target_size,
        )


def run_optimize_pipeline(
    source: Path,
    output: Path,
    preset: str,
    *,
    target_size_mb: float | None = None,
) -> None:
    require_tools("gs", "qpdf")
    config = PRESETS[preset]
    target_bytes = int(target_size_mb * 1024 * 1024) if target_size_mb else None
    attempts = len(config["resolutions"])
    achieved = False
    with temporary_directory("pdfsuite-optimize-") as tmpdir:
        intermediate = tmpdir / "optimized.pdf"
        for attempt in range(attempts):
            flags = build_gs_flags(config, attempt)
            gs_cmd = build_gs_command(source, intermediate, flags)
            run_or_exit(gs_cmd)
            linearize(intermediate, output)
            if not target_bytes:
                achieved = True
                break
            size = file_size(output)
            if size and size <= target_bytes:
                achieved = True
                break
        if target_bytes and not achieved:
            typer.echo(
                f"[yellow]Warning:[/yellow] target size "
                f"{target_size_mb:.1f} MB not reached (result {size_bytes_to_mb(file_size(output)):.1f} MB).",
                err=True,
            )


def build_gs_flags(config: Dict[str, object], attempt: int) -> List[str]:
    base_flags: List[str] = list(config["base_flags"])  # type: ignore[index]
    resolutions: List[int] = config["resolutions"]  # type: ignore[index]
    res = resolutions[min(attempt, len(resolutions) - 1)]
    if res:
        base_flags.extend(
            [
                f"-dColorImageResolution={res}",
                f"-dGrayImageResolution={res}",
                f"-dMonoImageResolution={res}",
            ]
        )
    return base_flags


def build_gs_command(source: Path, destination: Path, flags: List[str]) -> str:
    return (
        "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 "
        f"{' '.join(flags)} "
        f"-o {shell_quote(destination)} {shell_quote(source)}"
    )


def linearize(intermediate: Path, output: Path) -> None:
    run_or_exit(
        " ".join(
            [
                "qpdf",
                "--linearize",
                shell_quote(intermediate),
                shell_quote(output),
            ]
        )
    )


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def size_bytes_to_mb(size: int) -> float:
    return size / (1024 * 1024) if size else 0.0
