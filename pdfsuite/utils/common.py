from __future__ import annotations

import contextlib
import shutil
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator, List

from rich import print
import typer


def shell_quote(value: str | Path) -> str:
    return shlex.quote(str(value))


def run(cmd: str) -> int:
    """Run a shell command, echoing it for visibility."""
    print(f"[dim]$ {cmd}[/dim]")
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def run_or_exit(cmd: str) -> None:
    """Run a command and exit the CLI if it fails."""
    code = run(cmd)
    if code != 0:
        raise typer.Exit(code)


def require_tools(*tools: str) -> None:
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        print(f"[red]Missing required tools:[/red] {' '.join(missing)}")
        raise typer.Exit(1)


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_file(path: Path, *, label: str | None = None) -> Path:
    """Abort early with a clear message if a required file is missing."""
    if path.is_file():
        return path
    target = (label or "file").capitalize()
    if not path.exists():
        typer.echo(f"{target} not found: {path}", err=True)
    else:
        typer.echo(f"{target} is not a file: {path}", err=True)
    raise typer.Exit(1)


@contextlib.contextmanager
def temporary_directory(prefix: str = "pdfsuite-") -> Iterator[Path]:
    tmp = tempfile.TemporaryDirectory(prefix=prefix)
    try:
        yield Path(tmp.name)
    finally:
        tmp.cleanup()


def parse_range_sequence(spec: str) -> List[str]:
    tokens = []
    for raw in spec.split(","):
        token = raw.strip()
        if not token:
            continue
        tokens.append(normalize_range_token(token))
    if not tokens:
        raise typer.BadParameter("Provide at least one page/range token.")
    return tokens


def normalize_range_token(token: str) -> str:
    token = token.strip()
    if not token:
        raise typer.BadParameter("Empty range token.")
    token = token.lower()
    token = token.replace("end", "z")
    if token.endswith("-"):
        token = f"{token}z"
    return token


def safe_range_name(token: str) -> str:
    sanitized = "".join(ch if ch.isalnum() else "-" for ch in token)
    while "--" in sanitized:
        sanitized = sanitized.replace("--", "-")
    return sanitized.strip("-") or "range"
