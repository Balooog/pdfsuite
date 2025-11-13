from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Set

import typer

from pdfsuite.commands.optimize import run_optimize_pipeline, PRESETS
from pdfsuite.utils.common import ensure_output_dir


def register(app: typer.Typer) -> None:
    @app.command()
    def watch(  # noqa: PLR0913
        path: Path = typer.Option(
            None,
            "--path",
            "-p",
            help="Directory to monitor for PDFs (defaults to OS-specific printed folder).",
        ),
        preset: str = typer.Option(
            "report",
            "--preset",
            case_sensitive=False,
            help="Optimize preset to apply (email/report/poster).",
        ),
        target_size: float = typer.Option(
            None,
            "--target-size",
            help="Optional size goal in MB for the optimizer.",
        ),
        poll_interval: float = typer.Option(
            5.0,
            "--poll-interval",
            help="Seconds between scans.",
        ),
        settle_seconds: float = typer.Option(
            2.0,
            "--settle",
            help="Wait time after file modification before processing.",
        ),
        once: bool = typer.Option(
            False,
            "--once",
            help="Scan directory once and exit (useful for tests).",
        ),
    ):
        """Watch a folder for new PDFs and auto-optimize them."""
        preset_key = preset.lower()
        if preset_key not in PRESETS:
            raise typer.BadParameter(f"Unknown preset '{preset}'. Choose from {', '.join(PRESETS)}.")
        directory = path or default_watch_dir()
        ensure_output_dir(directory)
        typer.echo(f"[dim]watch[/dim] Monitoring {directory} using preset '{preset_key}'. Ctrl+C to stop.")
        processed: Set[str] = set()
        try:
            while True:
                processed |= process_directory(
                    directory,
                    processed,
                    preset_key,
                    target_size,
                    settle_seconds,
                )
                if once:
                    break
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            typer.echo("Stopping watch.")


def default_watch_dir() -> Path:
    home = Path.home()
    if typersys() == "Windows":
        candidate = home / "Documents" / "Printed PDFs"
    else:
        candidate = home / "PDF"
    return candidate


def typersys() -> str:
    import platform

    return platform.system()


def process_directory(
    directory: Path,
    processed: Set[str],
    preset: str,
    target_size: float | None,
    settle_seconds: float,
) -> Set[str]:
    new_processed: Set[str] = set()
    now = time.time()
    for entry in sorted(directory.glob("*.pdf")):
        key = str(entry.resolve())
        if key in processed:
            continue
        age = now - entry.stat().st_mtime
        if age < settle_seconds:
            continue
        output = build_watch_output(entry)
        typer.echo(f"[dim]watch[/dim] Optimizing {entry.name} → {output.name}")
        run_optimize_pipeline(entry, output, preset, target_size_mb=target_size)
        new_processed.add(key)
    return new_processed


def build_watch_output(source: Path) -> Path:
    build_root = ensure_output_dir(Path.home() / "pdfsuite" / "build" / "watch")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = build_root / f"{source.stem}_{timestamp}.pdf"
    return dest
