from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.services import Runner, SettingsStore


class AutomationPanel(QWidget):
    """Monitor and control watch-folder automation."""

    def __init__(self, runner: Runner, settings: SettingsStore) -> None:
        super().__init__()
        self.runner = runner
        self.settings = settings

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Automation</h2>"))

        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        button_row = QWidget()
        row_layout = QHBoxLayout(button_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.start_button = QPushButton("Start watch")
        self.start_button.clicked.connect(self._start)
        row_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop watch")
        self.stop_button.clicked.connect(self._stop)
        row_layout.addWidget(self.stop_button)
        row_layout.addStretch()
        layout.addWidget(button_row)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Watch-folder logs streamed from `pdfsuite watch`.")
        layout.addWidget(self.log_view)

        self.runner.watch_output.connect(self.log_view.appendPlainText)
        self.refresh()

    def refresh(self) -> None:
        data = self.settings.data
        enabled = "Enabled" if data.watch_enabled else "Disabled"
        folder = data.watch_folder or "default platform folder"
        target = f"{data.watch_target_size} MB" if data.watch_target_size else "no cap"
        self.summary.setText(
            f"Status: {enabled}\nFolder: {folder}\nPreset: {data.watch_preset}\nTarget: {target}"
        )

    def _start(self) -> None:
        self.settings.data.watch_enabled = True
        self.settings.save()
        self.runner.start_watch(self.settings.data)
        self.refresh()
    def _stop(self) -> None:
        self.settings.data.watch_enabled = False
        self.settings.save()
        self.runner.stop_watch()
        self.refresh()
