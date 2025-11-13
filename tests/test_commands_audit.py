import json
from textwrap import dedent
from types import SimpleNamespace

from typer.testing import CliRunner

from pdfsuite.__main__ import app
from pdfsuite.commands import audit

runner = CliRunner()


def test_parse_pages_reads_integer() -> None:
    info = dedent(
        """
        Title: sample
        Pages: 12
        """
    )

    assert audit.parse_pages(info) == 12


def test_parse_pages_handles_bad_values() -> None:
    info = "Pages: not-a-number"

    assert audit.parse_pages(info) == 0


def test_parse_encrypted_normalizes_yes_token() -> None:
    info = "Encrypted:   Yes (print:yes copy:no)"

    assert audit.parse_encrypted(info) is True


def test_detect_pdfa_extracts_version() -> None:
    info = "PDF/A: 2b compliance"

    assert audit.detect_pdfa(info) == "2b compliance"


def test_parse_fonts_extracts_rows() -> None:
    table = dedent(
        """
        name flags  embedded
        ---  -----  --------
        Helvetica 0 Yes
        Courier 0 No
        """
    )

    assert audit.parse_fonts(table) == [
        {"name": "Helvetica", "embedded": True},
        {"name": "Courier", "embedded": False},
    ]


def test_audit_command_emits_summary(tmp_path, monkeypatch) -> None:
    source = tmp_path / "sample.pdf"
    source.write_text("pdf")
    output = tmp_path / "audit.json"

    def fake_run_capture(args, *, allow_failure=False):
        cmd = args[0]
        if cmd == "pdfinfo":
            return SimpleNamespace(
                stdout="Title: sample\nPages: 5\nEncrypted: no\nPDF/A: 2b",
                stderr="",
                returncode=0,
            )
        if cmd == "pdffonts":
            return SimpleNamespace(
                stdout="name flags embedded\n--- --- ---\nFontA 0 Yes",
                stderr="",
                returncode=0,
            )
        if cmd == "pdfcpu":
            assert allow_failure is True
            return SimpleNamespace(
                stdout="validated",
                stderr="",
                returncode=0,
            )
        raise AssertionError(f"Unexpected command {args}")

    monkeypatch.setattr("pdfsuite.commands.audit.run_capture", fake_run_capture)

    result = runner.invoke(app, ["audit", str(source), "-o", str(output)])

    assert result.exit_code == 0
    payload = json.loads(output.read_text())
    assert payload["file"] == str(source)
    assert payload["pages"] == 5
    assert payload["encrypted"] is False
    assert payload["pdfa"] == "2b"
    assert payload["fonts"] == [{"name": "FontA", "embedded": True}]
    assert payload["pdfcpu_valid"] is True
