from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List

import typer

from pdfsuite.utils.common import require_tools


def register(app: typer.Typer) -> None:
    @app.command()
    def audit(
        input: Path,
        output: Path = typer.Option(
            None,
            "-o",
            help="Optional path to write JSON summary (also echoed).",
        ),
    ):
        """Summarize PDF metadata, fonts, encryption, and validation."""
        require_tools("pdfinfo", "pdffonts", "pdfcpu")

        info = run_capture(["pdfinfo", str(input)])
        fonts = run_capture(["pdffonts", str(input)])
        validation = run_capture(["pdfcpu", "validate", str(input)])

        summary = {
            "file": str(input),
            "pages": parse_pages(info.stdout),
            "encrypted": parse_encrypted(info.stdout),
            "pdfa": detect_pdfa(info.stdout),
            "fonts": parse_fonts(fonts.stdout),
            "pdfcpu_valid": validation.returncode == 0,
            "pdfcpu_message": (validation.stdout + validation.stderr).strip(),
        }

        text = json.dumps(summary, indent=2)
        if output:
            output.write_text(text)
        typer.echo(text)


def run_capture(args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True)


def parse_pages(info: str) -> int:
    for line in info.splitlines():
        if line.lower().startswith("pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return 0
    return 0


def parse_encrypted(info: str) -> bool:
    for line in info.splitlines():
        if line.lower().startswith("encrypted:"):
            return line.split(":", 1)[1].strip().lower().startswith("yes")
    return False


def detect_pdfa(info: str) -> str:
    for line in info.splitlines():
        if "PDF/A" in line:
            return line.split(":", 1)[-1].strip()
    return "No"


def parse_fonts(text: str) -> List[Dict[str, str]]:
    lines = text.splitlines()
    if len(lines) <= 2:
        return []
    fonts: List[Dict[str, str]] = []
    for line in lines[2:]:
        if not line.strip():
            continue
        tokens = line.split()
        if len(tokens) < 3:
            continue
        name = tokens[0]
        embedded = tokens[2].lower() == "yes"
        fonts.append({"name": name, "embedded": embedded})
    return fonts
