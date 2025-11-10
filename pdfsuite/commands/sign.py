from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote


def register(app: typer.Typer) -> None:
    @app.command()
    def sign(
        input: Path,
        output: Path = typer.Option(..., "-o", help="Signed PDF output"),
        p12: Path = typer.Option(..., "--p12", help="PKCS#12 keystore"),
        alias: str = typer.Option(..., "--alias", help="Certificate alias"),
        visible: str = typer.Option(
            None,
            "--visible",
            help="Optional placement p=<page>,x=,y=,w=,h=",
        ),
    ):
        """Digitally sign via jSignPdf."""
        require_tools("jsignpdf")
        vis = f" --visible {shell_quote(visible)}" if visible else ""
        cmd = (
            "jsignpdf "
            f"-ks {shell_quote(p12)} -ksPass ask -a {shell_quote(alias)}"
            f"{vis} -o {shell_quote(output)} {shell_quote(input)}"
        )
        run_or_exit(cmd)
