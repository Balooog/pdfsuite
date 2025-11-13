from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from gui.panels.base import CommandPanel


class RedactPanel(CommandPanel):
    """Safe redaction wrapper that enforces the rasterize + sanitize flow."""

    def __init__(self, runner) -> None:
        super().__init__(
            runner,
            title="Annotate & Redact",
            description="Use the safe pdfsuite redaction helper (pdf-redact-tools) so sensitive "
            "content is rasterized and sanitized before sharing.",
        )
        warning = QLabel(
            "This workflow always runs `pdfsuite redact safe` (rasterize + sanitize). "
            "Use the CLI directly if you need alternate pipelines."
        )
        warning.setWordWrap(True)
        self.form_layout.addRow(warning)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Path to input PDF")
        self.input_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow("Input PDF", self._with_browse(self.input_edit, self._select_input))

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("redacted.pdf")
        self.output_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow(
            "Output PDF",
            self._with_browse(self.output_edit, self._select_output, save_dialog=True),
        )

        self.update_command_preview()

    def build_command_parts(self) -> Sequence[str] | None:
        source = self.input_edit.text().strip()
        dest = self.output_edit.text().strip()
        if not source or not dest:
            return None
        return ["redact", "safe", source, "-o", dest]

    def _with_browse(
        self,
        line_edit: QLineEdit,
        callback,
        *,
        save_dialog: bool = False,
    ) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        button = QPushButton("Browse…")
        button.clicked.connect(lambda: callback(save_dialog=save_dialog))
        layout.addWidget(button)
        return row

    def _select_input(self, *, save_dialog: bool = False) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input PDF", filter="PDF files (*.pdf)")
        if path:
            self.input_edit.setText(path)
            self.update_command_preview()

    def _select_output(self, *, save_dialog: bool = False) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
        if path:
            self.output_edit.setText(path)
            self.update_command_preview()
