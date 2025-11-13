from __future__ import annotations

from typer.testing import CliRunner

from pdfsuite.__main__ import app
from pdfsuite.utils.common import shell_quote


runner = CliRunner()


def test_compare_prefers_diff_pdf(tmp_path, monkeypatch, command_recorder) -> None:
    first = tmp_path / "a.pdf"
    second = tmp_path / "b.pdf"
    output = tmp_path / "diff.pdf"
    for path in (first, second):
        path.write_text("pdf")
    recorded = command_recorder("pdfsuite.commands.compare")

    def fake_which(tool: str) -> str | None:
        if tool == "diff-pdf":
            return "/usr/bin/diff-pdf"
        return None

    monkeypatch.setattr("pdfsuite.commands.compare.shutil.which", fake_which)

    result = runner.invoke(
        app, ["compare", str(first), str(second), "-o", str(output)]
    )

    assert result.exit_code == 0
    expected = (
        f"diff-pdf --output-diff={shell_quote(output)} "
        f"{shell_quote(first)} {shell_quote(second)}"
    )
    assert recorded == [expected]


def test_compare_falls_back_to_diffpdf_gui(tmp_path, monkeypatch, command_recorder):
    first = tmp_path / "a.pdf"
    second = tmp_path / "b.pdf"
    output = tmp_path / "diff.pdf"
    for path in (first, second):
        path.write_text("pdf")
    recorded = command_recorder("pdfsuite.commands.compare")

    def fake_which(tool: str) -> str | None:
        if tool == "diffpdf":
            return "/usr/bin/diffpdf"
        return None

    monkeypatch.setattr("pdfsuite.commands.compare.shutil.which", fake_which)

    result = runner.invoke(
        app, ["compare", str(first), str(second), "-o", str(output)]
    )

    assert result.exit_code == 0
    assert recorded == [
        f"diffpdf {shell_quote(first)} {shell_quote(second)}"
    ]
