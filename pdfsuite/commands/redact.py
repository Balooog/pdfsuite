from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote

redact_app = typer.Typer(help="Redaction helpers.")


@redact_app.command("safe")
def redact_safe(
    input: Path,
    output: Path = typer.Option(..., "-o", help="Redacted PDF output"),
):
    """Secure rasterize+sanitize redaction using pdf-redact-tools."""
    require_tools("pdf-redact-tools")
    cmd = (
        "pdf-redact-tools --sanitize "
        f"-i {shell_quote(input)} -o {shell_quote(output)}"
    )
    run_or_exit(cmd)


def register(app: typer.Typer) -> None:
    app.add_typer(redact_app, name="redact")
