from collections.abc import Callable
from typing import List

import pytest


@pytest.fixture
def command_recorder(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], List[str]]:
    """Replace require_tools/run_or_exit in a command module and capture commands."""

    def _stub(module_path: str) -> List[str]:
        recorded: List[str] = []
        monkeypatch.setattr(f"{module_path}.require_tools", lambda *args: None)
        monkeypatch.setattr(f"{module_path}.run_or_exit", recorded.append)
        return recorded

    return _stub
