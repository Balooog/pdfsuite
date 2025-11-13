import pytest
import typer

from pdfsuite.utils import common


def test_ensure_file_returns_existing_path(tmp_path) -> None:
    sample = tmp_path / "input.pdf"
    sample.write_text("data")

    assert common.ensure_file(sample) == sample


def test_ensure_file_exits_on_missing_path(tmp_path) -> None:
    missing = tmp_path / "missing.pdf"

    with pytest.raises(typer.Exit) as exc:
        common.ensure_file(missing, label="input PDF")

    assert exc.value.exit_code == 1


def test_parse_range_sequence_normalizes_tokens() -> None:
    tokens = common.parse_range_sequence("1, 3-5 , END- , 7-")

    assert tokens == ["1", "3-5", "z-z", "7-z"]


def test_parse_range_sequence_requires_token() -> None:
    with pytest.raises(typer.BadParameter):
        common.parse_range_sequence(" , ")


def test_normalize_range_token_handles_suffixes() -> None:
    assert common.normalize_range_token("END") == "z"
    assert common.normalize_range_token("5-") == "5-z"


def test_safe_range_name_sanitizes_and_defaults() -> None:
    assert common.safe_range_name("Page 1/2") == "Page-1-2"
    assert common.safe_range_name("!!!") == "range"
