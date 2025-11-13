from contextlib import contextmanager
from pathlib import Path

from typer.testing import CliRunner

from pdfsuite.__main__ import app
from pdfsuite.utils.common import shell_quote

runner = CliRunner()


def test_metadata_scrub_copies_and_runs(tmp_path, command_recorder, monkeypatch):
    recorded = command_recorder("pdfsuite.commands.metadata")
    source = tmp_path / "input.pdf"
    source.write_text("data")
    output = tmp_path / "clean.pdf"
    copied: list[tuple[Path, Path]] = []
    monkeypatch.setattr(
        "pdfsuite.commands.metadata.shutil.copy2",
        lambda src, dest: copied.append((Path(src), Path(dest))),
    )

    result = runner.invoke(
        app,
        [
            "metadata_scrub",
            str(source),
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert copied == [(source, output)]
    assert recorded == [f"mat2 --inplace {shell_quote(output)}"]


def test_optimize_builds_gs_command(tmp_path, command_recorder, monkeypatch):
    recorded = command_recorder("pdfsuite.commands.optimize")
    source = tmp_path / "source.pdf"
    source.write_text("pdf")
    output = tmp_path / "opt.pdf"
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()

    @contextmanager
    def fake_tmp(prefix="pdfsuite-"):
        yield tmpdir

    monkeypatch.setattr("pdfsuite.commands.optimize.temporary_directory", fake_tmp)
    monkeypatch.setattr("pdfsuite.commands.optimize.file_size", lambda path: 0)

    result = runner.invoke(app, ["optimize", str(source), "-o", str(output)])

    assert result.exit_code == 0
    intermediate = tmpdir / "optimized.pdf"
    assert recorded == [
        (
            "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 "
            "-dPDFSETTINGS=/printer -dDetectDuplicateImages=true -dDownsampleColorImages=true "
            "-dColorImageResolution=300 -dGrayImageResolution=300 -dMonoImageResolution=300 "
            f"-o {shell_quote(intermediate)} {shell_quote(source)}"
        ),
        f"qpdf --linearize {shell_quote(intermediate)} {shell_quote(output)}",
    ]


def test_ocr_invokes_ocrmypdf(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.ocr")
    source = tmp_path / "scan.pdf"
    output = tmp_path / "searchable.pdf"

    result = runner.invoke(app, ["ocr", str(source), "-o", str(output)])

    assert result.exit_code == 0
    assert recorded == [f"ocrmypdf {shell_quote(source)} {shell_quote(output)}"]


def test_forms_fill_uses_pdftk(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.forms")
    form = tmp_path / "form.pdf"
    fdf = tmp_path / "data.fdf"
    output = tmp_path / "filled.pdf"

    result = runner.invoke(
        app,
        ["forms", "fill", str(form), str(fdf), "-o", str(output)],
    )

    assert result.exit_code == 0
    assert recorded == [
        (
            f"pdftk {shell_quote(form)} fill_form {shell_quote(fdf)} "
            f"output {shell_quote(output)}"
        )
    ]


def test_forms_flatten_invokes_pdftk(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.forms")
    source = tmp_path / "filled.pdf"
    output = tmp_path / "flat.pdf"

    result = runner.invoke(
        app,
        ["forms", "flatten", str(source), "-o", str(output)],
    )

    assert result.exit_code == 0
    assert recorded == [
        f"pdftk {shell_quote(source)} output {shell_quote(output)} flatten"
    ]


def test_redact_safe_builds_sanitize_command(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.redact")
    source = tmp_path / "input.pdf"
    output = tmp_path / "redacted.pdf"

    result = runner.invoke(
        app, ["redact", "safe", str(source), "-o", str(output)]
    )

    assert result.exit_code == 0
    assert recorded == [
        (
            "pdf-redact-tools --sanitize "
            f"-i {shell_quote(source)} -o {shell_quote(output)}"
        )
    ]


def test_sign_without_visible(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.sign")
    source = tmp_path / "input.pdf"
    output = tmp_path / "signed.pdf"
    keystore = tmp_path / "key.p12"

    result = runner.invoke(
        app,
        [
            "sign",
            str(source),
            "-o",
            str(output),
            "--p12",
            str(keystore),
            "--alias",
            "Signer",
        ],
    )

    assert result.exit_code == 0
    alias_token = shell_quote("Signer")
    expected = (
        "jsignpdf "
        f"-ks {shell_quote(keystore)} -ksPass ask -a {alias_token}"
        f" -o {shell_quote(output)} {shell_quote(source)}"
    )
    assert recorded == [expected]


def test_sign_with_visible_block(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.sign")
    source = tmp_path / "input.pdf"
    output = tmp_path / "signed.pdf"
    keystore = tmp_path / "key.p12"

    result = runner.invoke(
        app,
        [
            "sign",
            str(source),
            "-o",
            str(output),
            "--p12",
            str(keystore),
            "--alias",
            "Signer",
            "--visible",
            "p=1,x=10,y=10,w=100,h=50",
        ],
    )

    assert result.exit_code == 0
    alias_token = shell_quote("Signer")
    visible_token = shell_quote("p=1,x=10,y=10,w=100,h=50")
    expected = (
        "jsignpdf "
        f"-ks {shell_quote(keystore)} -ksPass ask -a {alias_token}"
        f" --visible {visible_token}"
        f" -o {shell_quote(output)} {shell_quote(source)}"
    )
    assert recorded == [expected]


def test_verify_calls_pdfsig(tmp_path, command_recorder):
    recorded = command_recorder("pdfsuite.commands.verify")
    source = tmp_path / "signed.pdf"

    result = runner.invoke(app, ["verify", str(source)])

    assert result.exit_code == 0
    assert recorded == [f"pdfsig {shell_quote(source)}"]
