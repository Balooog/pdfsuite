from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from pdfsuite.__main__ import app
from pdfsuite.utils.common import shell_quote

runner = CliRunner()


def test_bookmarks_dump_invokes_pdftk(tmp_path, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.bookmarks")
    source = tmp_path / "manual.pdf"
    source.write_text("pdf")
    dump = tmp_path / "bookmarks.txt"

    result = runner.invoke(
        app,
        ["bookmarks", "dump", str(source), "-o", str(dump)],
    )

    assert result.exit_code == 0
    expected = (
        "pdftk "
        f"{shell_quote(source)} dump_data_utf8 output {shell_quote(dump)}"
    )
    assert recorded == [expected]


def test_bookmarks_apply_updates_pdf(tmp_path, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.bookmarks")
    source = tmp_path / "manual.pdf"
    source.write_text("pdf")
    info = tmp_path / "bookmarks.txt"
    info.write_text("BookmarkBegin")
    output = tmp_path / "with-bookmarks.pdf"

    result = runner.invoke(
        app,
        [
            "bookmarks",
            "apply",
            str(source),
            str(info),
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    expected = (
        "pdftk "
        f"{shell_quote(source)} update_info_utf8 {shell_quote(info)} "
        f"output {shell_quote(output)}"
    )
    assert recorded == [expected]
