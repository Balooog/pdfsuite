from pathlib import Path
import subprocess
import sys

import typer
from rich import print

from pdfsuite import __version__
from pdfsuite.commands import (
    audit,
    compare,
    forms,
    merge,
    metadata,
    ocr,
    optimize,
    reorder,
    redact,
    sign,
    split,
    stamp,
    verify,
)

app = typer.Typer(add_completion=False, help="All‑FOSS Acrobat‑grade PDF toolkit")


def _register_commands() -> None:
    modules = [
        audit,
        compare,
        forms,
        merge,
        metadata,
        ocr,
        optimize,
        reorder,
        redact,
        sign,
        split,
        stamp,
        verify,
    ]
    for module in modules:
        module.register(app)


_register_commands()


@app.command()
def version() -> None:
    """Show version."""
    print(f"pdfsuite {__version__}")


@app.command()
def doctor() -> None:
    """Check external tool availability."""
    scripts = Path(__file__).resolve().parent.parent / "scripts"
    doctor_path = scripts / "doctor.py"
    sys.exit(subprocess.call([sys.executable, str(doctor_path)]))


if __name__ == "__main__":
    app()
