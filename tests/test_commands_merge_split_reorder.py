from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from pdfsuite.__main__ import app
from pdfsuite.utils.common import shell_quote

runner = CliRunner()


def test_merge_builds_qpdf_concat(tmp_path, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.merge")
    a = tmp_path / "a.pdf"
    b = tmp_path / "b.pdf"
    for path in (a, b):
        path.write_text("pdf")
    output = tmp_path / "out.pdf"

    result = runner.invoke(app, ["merge", str(a), str(b), "-o", str(output)])

    assert result.exit_code == 0
    expected = (
        "qpdf --empty --pages "
        f"{shell_quote(a)} 1-z {shell_quote(b)} 1-z -- {shell_quote(output)}"
    )
    assert recorded == [expected]


def test_split_emits_slice_per_range(tmp_path, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.split")
    source = tmp_path / "source.pdf"
    source.write_text("pdf")
    output_dir = tmp_path / "split dir"

    result = runner.invoke(
        app,
        [
            "split",
            str(source),
            "--pages",
            "1 , 3-4 , 7-",
            "-o",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    expected_files = [
        output_dir / f"{source.stem}_1.pdf",
        output_dir / f"{source.stem}_3-4.pdf",
        output_dir / f"{source.stem}_7-z.pdf",
    ]
    expected_cmds = [
        (
            f"qpdf {shell_quote(source)} --pages {shell_quote(source)} "
            f"{shell_quote(token)} -- {shell_quote(dest)}"
        )
        for token, dest in zip(["1", "3-4", "7-z"], expected_files, strict=True)
    ]
    assert recorded == expected_cmds


def test_reorder_respects_requested_sequence(tmp_path, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.reorder")
    source = tmp_path / "input.pdf"
    source.write_text("pdf")
    output = tmp_path / "reordered.pdf"

    result = runner.invoke(
        app,
        [
            "reorder",
            str(source),
            "--order",
            "5-6 , 1-2 , 9-",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    expected_spec = "5-6,1-2,9-z"
    expected = (
        f"qpdf {shell_quote(source)} --pages {shell_quote(source)} "
        f"{shell_quote(expected_spec)} -- {shell_quote(output)}"
    )
    assert recorded == [expected]
