from pathlib import Path

import typer

from pdfsuite.utils.common import run_or_exit, require_tools, shell_quote

forms_app = typer.Typer(help="Forms operations via pdftk-java.")


@forms_app.command("fill")
def forms_fill(
    form: Path,
    fdf: Path,
    output: Path = typer.Option(..., "-o", help="Filled PDF output"),
):
    require_tools("pdftk")
    cmd = (
        f"pdftk {shell_quote(form)} fill_form {shell_quote(fdf)} "
        f"output {shell_quote(output)}"
    )
    run_or_exit(cmd)


@forms_app.command("flatten")
def forms_flatten(
    input: Path,
    output: Path = typer.Option(..., "-o", help="Flattened PDF output"),
):
    require_tools("pdftk")
    cmd = f"pdftk {shell_quote(input)} output {shell_quote(output)} flatten"
    run_or_exit(cmd)


def register(app: typer.Typer) -> None:
    app.add_typer(forms_app, name="forms")
