from __future__ import annotations

from typer.testing import CliRunner

from pdfsuite.__main__ import app

runner = CliRunner()


def test_figure_selects_preset_based_on_images(tmp_path, monkeypatch):
    source = tmp_path / "figure.pdf"
    source.write_text("pdf")
    output = tmp_path / "out.pdf"
    recorded: list[tuple[str, str, str, float | None]] = []

    monkeypatch.setattr("pdfsuite.commands.figure.require_tools", lambda *args: None)
    monkeypatch.setattr(
        "pdfsuite.commands.figure.run_pdfimages_list",
        lambda path: [(2100, 2000), (1500, 1500), (500, 500), (400, 400), (300, 300)],
    )
    monkeypatch.setattr(
        "pdfsuite.commands.figure.run_optimize_pipeline",
        lambda source, output, preset, target_size_mb=None: recorded.append(
            (str(source), str(output), preset, target_size_mb)
        ),
    )

    result = runner.invoke(app, ["figure", str(source), "-o", str(output), "--target-size", "2"])

    assert result.exit_code == 0
    assert recorded == [(str(source), str(output), "email", 2.0)]
