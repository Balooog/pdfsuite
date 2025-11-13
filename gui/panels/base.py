from __future__ import annotations

import shlex
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.services import Runner


class CommandPanel(QWidget):
    """Base widget for panels that wrap a pdfsuite CLI command."""

    def __init__(
        self,
        runner: Runner,
        *,
        title: str,
        description: str,
        job_name: str | None = None,
    ) -> None:
        super().__init__()
        self.runner = runner
        self._current_command: list[str] = []
        self._job_name = job_name or title.lower().replace(" ", "-")

        layout = QVBoxLayout(self)
        header = QLabel(f"<h2>{title}</h2>")
        header.setTextFormat(Qt.RichText)
        layout.addWidget(header)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        command_group = QGroupBox("Command preview")
        command_layout = QVBoxLayout(command_group)
        self.command_preview = QPlainTextEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setPlaceholderText("Command will appear here once inputs are provided.")
        self.command_preview.setMaximumHeight(70)
        command_layout.addWidget(self.command_preview)
        layout.addWidget(command_group)

        actions_row = QHBoxLayout()
        self.run_button = QPushButton("Run command")
        self.run_button.clicked.connect(self._on_run_clicked)
        actions_row.addWidget(self.run_button)
        layout.addLayout(actions_row)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Command output will stream here.")
        layout.addWidget(self.log_output)

    def build_command_parts(self) -> Sequence[str] | None:
        """Return the pdfsuite arguments (without python -m prefix)."""
        raise NotImplementedError

    def build_command(self) -> list[str]:
        parts = self.build_command_parts()
        if not parts:
            return []
        # Derived panels return subcommand arguments (e.g., ["merge", ...]).
        from gui.services import build_cli_command  # local import to avoid cycles

        return build_cli_command(*parts)

    def update_command_preview(self) -> None:
        command = self.build_command()
        self._current_command = command
        if not command:
            self.command_preview.clear()
            return
        rendered = " ".join(shlex.quote(part) for part in command)
        self.command_preview.setPlainText(rendered)

    def append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)

    def _on_run_clicked(self) -> None:
        command = self.build_command()
        if not command:
            self.append_log("Provide the required inputs before running the command.")
            return
        self.run_button.setEnabled(False)
        self.log_output.clear()
        rendered = " ".join(shlex.quote(part) for part in command)
        self.append_log(f"$ {rendered}")

        def _finished(exit_code: int, job_dir: Path) -> None:
            status = "succeeded" if exit_code == 0 else f"failed (exit {exit_code})"
            self.append_log(f"[runner] Command {status}. Logs: {job_dir}")
            self.run_button.setEnabled(True)

        self.runner.run(
            command,
            self.append_log,
            _finished,
            job_name=self._job_name,
        )
