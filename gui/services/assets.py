from __future__ import annotations

from importlib import resources
from pathlib import Path


def get_asset_path(relative: str) -> Path:
    """Return an absolute path inside the gui/assets package."""
    package = "gui"
    with resources.as_file(resources.files(package) / "assets" / relative) as path:
        return Path(path)
