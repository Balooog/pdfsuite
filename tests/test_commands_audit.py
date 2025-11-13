from textwrap import dedent

from pdfsuite.commands import audit


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
