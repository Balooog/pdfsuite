from __future__ import annotations

import shlex
from functools import partial
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.services import Runner, build_cli_command


class DashboardPanel(QWidget):
    """Landing view with quick actions and a shared log console."""

    def __init__(self, runner: Runner) -> None:
        super().__init__()
        self.runner = runner

        layout = QVBoxLayout(self)
        header = QLabel("<h1>Dashboard</h1>")
        header.setTextFormat(Qt.RichText)
        layout.addWidget(header)

        intro = QLabel(
            "Kick off common CLI workflows or monitor recent jobs. Buttons below "
            "shell out to the pdfsuite CLI via the shared runner so logs stay consistent "
            "with headless usage."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        quick_actions = QGroupBox("Quick actions")
        quick_layout = QVBoxLayout(quick_actions)

        actions = [
            ("Doctor (dependency check)", ["doctor"]),
            ("Show version", ["--version"]),
            ("List commands", ["--help"]),
        ]

        for label, parts in actions:
            button = QPushButton(label)
            button.clicked.connect(partial(self._run_action, parts))
            quick_layout.addWidget(button)

        layout.addWidget(quick_actions)

        self.watch_log = QPlainTextEdit()
        self.watch_log.setReadOnly(True)
        self.watch_log.setPlaceholderText("Watch-folder logs will appear here once enabled.")
        layout.addWidget(self.watch_log)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs from quick actions appear here.")
        layout.addWidget(self.log_output)

    def _run_action(self, parts: Sequence[str]) -> None:
        command = build_cli_command(*parts)
        rendered = " ".join(shlex.quote(part) for part in command)
        self.log_output.appendPlainText(f"$ {rendered}")

        def _finished(code: int, job_dir: Path) -> None:
            status = "succeeded" if code == 0 else f"failed (exit {code})"
            self.log_output.appendPlainText(f"[runner] Command {status}. Logs: {job_dir}")

        self.runner.run(
            command,
            self.log_output.appendPlainText,
            _finished,
            job_name=f"dashboard-{parts[0]}",
        )

    def append_watch_log(self, message: str) -> None:
        self.watch_log.appendPlainText(message)
