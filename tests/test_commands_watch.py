from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from pdfsuite.__main__ import app

runner = CliRunner()


def test_watch_processes_new_files_once(tmp_path, monkeypatch):
    source_dir = tmp_path / "watch"
    source_dir.mkdir()
    pdf = source_dir / "doc.pdf"
    pdf.write_text("pdf")
    recorded: list[tuple[str, str, str, float | None]] = []

    monkeypatch.setattr("pdfsuite.commands.watch.default_watch_dir", lambda: source_dir)
    monkeypatch.setattr(
        "pdfsuite.commands.watch.run_optimize_pipeline",
        lambda src, dest, preset, target_size_mb=None: recorded.append(
            (str(src), str(dest), preset, target_size_mb)
        ),
    )

    result = runner.invoke(
        app,
        [
            "watch",
            "--preset",
            "email",
            "--target-size",
            "2",
            "--once",
            "--settle",
            "0",
        ],
    )

    assert result.exit_code == 0
    assert len(recorded) == 1
    src, dest, preset, target = recorded[0]
    assert src == str(pdf)
    assert preset == "email"
    assert target == 2.0
    assert dest.endswith(".pdf")
