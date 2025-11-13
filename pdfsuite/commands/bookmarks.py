from pathlib import Path

import typer

from pdfsuite.utils.common import (
    ensure_file,
    run_or_exit,
    require_tools,
    shell_quote,
)

bookmarks_app = typer.Typer(help="Bookmark import/export helpers.")


@bookmarks_app.command("dump")
def dump_bookmarks(
    input: Path = typer.Argument(..., help="Source PDF with bookmarks."),
    output: Path = typer.Option(..., "-o", help="Destination UTF-8 text file."),
) -> None:
    """Export bookmarks to pdftk-compatible dump format."""
    require_tools("pdftk")
    source = ensure_file(input, label="input PDF")
    cmd = (
        f"pdftk {shell_quote(source)} dump_data_utf8 "
        f"output {shell_quote(output)}"
    )
    run_or_exit(cmd)


@bookmarks_app.command("apply")
def apply_bookmarks(
    input: Path = typer.Argument(..., help="Source PDF to update."),
    bookmark_file: Path = typer.Argument(..., help="Bookmark dump file."),
    output: Path = typer.Option(..., "-o", help="Updated PDF with bookmarks."),
) -> None:
    """Apply exported bookmarks back to a PDF."""
    require_tools("pdftk")
    source = ensure_file(input, label="input PDF")
    info = ensure_file(bookmark_file, label="bookmark file")
    cmd = (
        f"pdftk {shell_quote(source)} update_info_utf8 {shell_quote(info)} "
        f"output {shell_quote(output)}"
    )
    run_or_exit(cmd)


def register(app: typer.Typer) -> None:
    app.add_typer(bookmarks_app, name="bookmarks")
