from __future__ import annotations

from pathlib import Path

import pytest
import sys

from pdfsuite.core.document_session import DocumentSession


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, command, on_output, on_finished, *, job_name=None):
        self.commands.append(command)


def test_reorder_updates_order_and_builds_cli(tmp_path, monkeypatch):
    runner = FakeRunner()
    session = DocumentSession(path=Path("sample.pdf"), page_order=[1, 2, 3, 4])
    session.reorder([1, 2], 0)  # move pages 2,3 to front
    session.commit(runner, output_path=tmp_path / "out.pdf")

    assert session.page_order == [2, 3, 1, 4]
    command = runner.commands[0]
    expected_prefix = [sys.executable or "python3", "-m", "pdfsuite", "reorder"]
    assert command[:4] == expected_prefix
    assert command[-2:] == ["-o", str(tmp_path / "out.pdf")]
    assert "--order" in command
    order_index = command.index("--order") + 1
    assert command[order_index] == "2,3,1,4"


def test_undo_redo_tracks_history():
    session = DocumentSession(path=Path("sample.pdf"), page_order=[1, 2, 3])
    session.reorder([2], 0)  # move page 3 to front
    assert session.page_order == [3, 1, 2]
    session.undo()
    assert session.page_order == [1, 2, 3]
    session.redo()
    assert session.page_order == [3, 1, 2]


def test_set_order_replaces_sequence():
    session = DocumentSession(path=Path("sample.pdf"), page_order=[1, 2, 3, 4])
    session.set_order([4, 3, 2, 1])
    assert session.page_order == [4, 3, 2, 1]
    with pytest.raises(ValueError):
        session.set_order([1, 2, 3])  # missing page
