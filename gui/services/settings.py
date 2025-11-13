from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import user_config_dir


@dataclass
class GuiSettings:
    external_viewer: str = ""
    default_output_dir: str = str(Path.home() / "pdfsuite" / "build")
    run_doctor_on_launch: bool = True
    watch_folder: str = ""
    watch_preset: str = "report"
    watch_target_size: float | None = None
    watch_enabled: bool = False
    reader_zoom_step: int = 10
    reader_pan_speed: int = 64
    reader_thumbnail_size: int = 96
    remember_reader_layout: bool = True


class SettingsStore:
    """Minimal JSON-backed settings storage."""

    def __init__(self) -> None:
        config_dir = Path(user_config_dir("pdfsuite", "pdfsuite"))
        config_dir.mkdir(parents=True, exist_ok=True)
        self.path = config_dir / "gui_settings.json"
        self.data = GuiSettings()
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        self.data = GuiSettings(
            external_viewer=payload.get("external_viewer", self.data.external_viewer),
            default_output_dir=payload.get("default_output_dir", self.data.default_output_dir),
            run_doctor_on_launch=payload.get(
                "run_doctor_on_launch",
                self.data.run_doctor_on_launch,
            ),
            watch_folder=payload.get("watch_folder", self.data.watch_folder),
            watch_preset=payload.get("watch_preset", self.data.watch_preset),
            watch_target_size=payload.get("watch_target_size", self.data.watch_target_size),
            watch_enabled=payload.get("watch_enabled", self.data.watch_enabled),
            reader_zoom_step=payload.get("reader_zoom_step", self.data.reader_zoom_step),
            reader_pan_speed=payload.get("reader_pan_speed", self.data.reader_pan_speed),
            reader_thumbnail_size=payload.get(
                "reader_thumbnail_size",
                self.data.reader_thumbnail_size,
            ),
            remember_reader_layout=payload.get(
                "remember_reader_layout",
                self.data.remember_reader_layout,
            ),
        )

    def save(self) -> None:
        self.path.write_text(json.dumps(asdict(self.data), indent=2), encoding="utf-8")
