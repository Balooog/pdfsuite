from __future__ import annotations

from contextlib import contextmanager

from typer.testing import CliRunner

from pdfsuite.__main__ import app
from pdfsuite.utils.common import shell_quote

runner = CliRunner()


@contextmanager
def fake_tmp(path):
    yield path


def test_optimize_runs_single_pass(tmp_path, monkeypatch, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.optimize")
    source = tmp_path / "input.pdf"
    source.write_text("pdf")
    output = tmp_path / "out.pdf"
    temp_dir = tmp_path / "tmp"
    temp_dir.mkdir()

    monkeypatch.setattr(
        "pdfsuite.commands.optimize.temporary_directory",
        lambda prefix="pdfsuite-": fake_tmp(temp_dir),
    )
    monkeypatch.setattr("pdfsuite.commands.optimize.file_size", lambda path: 500000)

    result = runner.invoke(
        app,
        ["optimize", str(source), "-o", str(output), "--preset", "email"],
    )

    assert result.exit_code == 0
    intermediate = temp_dir / "optimized.pdf"
    assert recorded == [
        (
            "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 "
            "-dPDFSETTINGS=/screen -dDetectDuplicateImages=true -dDownsampleColorImages=true "
            "-dColorImageResolution=150 -dGrayImageResolution=150 -dMonoImageResolution=150 "
            f"-o {shell_quote(intermediate)} {shell_quote(source)}"
        ),
        f"qpdf --linearize {shell_quote(intermediate)} {shell_quote(output)}",
    ]


def test_optimize_retries_until_target_met(tmp_path, monkeypatch, command_recorder) -> None:
    recorded = command_recorder("pdfsuite.commands.optimize")
    source = tmp_path / "input.pdf"
    source.write_text("pdf")
    output = tmp_path / "out.pdf"
    temp_dir = tmp_path / "tmp"
    temp_dir.mkdir()

    monkeypatch.setattr(
        "pdfsuite.commands.optimize.temporary_directory",
        lambda prefix="pdfsuite-": fake_tmp(temp_dir),
    )
    sizes = iter([5 * 1024 * 1024, 500_000])
    monkeypatch.setattr(
        "pdfsuite.commands.optimize.file_size",
        lambda path: next(sizes),
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(source),
            "-o",
            str(output),
            "--preset",
            "email",
            "--target-size",
            "1",
        ],
    )

    assert result.exit_code == 0
    intermediate = temp_dir / "optimized.pdf"
    assert recorded[0].count("ColorImageResolution=150")
    assert recorded[2].count("ColorImageResolution=120")
    assert recorded == [
        (
            "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 "
            "-dPDFSETTINGS=/screen -dDetectDuplicateImages=true -dDownsampleColorImages=true "
            "-dColorImageResolution=150 -dGrayImageResolution=150 -dMonoImageResolution=150 "
            f"-o {shell_quote(intermediate)} {shell_quote(source)}"
        ),
        f"qpdf --linearize {shell_quote(intermediate)} {shell_quote(output)}",
        (
            "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 "
            "-dPDFSETTINGS=/screen -dDetectDuplicateImages=true -dDownsampleColorImages=true "
            "-dColorImageResolution=120 -dGrayImageResolution=120 -dMonoImageResolution=120 "
            f"-o {shell_quote(intermediate)} {shell_quote(source)}"
        ),
        f"qpdf --linearize {shell_quote(intermediate)} {shell_quote(output)}",
    ]
