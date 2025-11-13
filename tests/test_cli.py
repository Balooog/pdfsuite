from typer.testing import CliRunner

from pdfsuite import __version__
from pdfsuite.__main__ import app


runner = CliRunner()


def test_version_command_reports_current_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert f"pdfsuite {__version__}" in result.stdout
