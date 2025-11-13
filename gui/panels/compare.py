from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.panels.base import CommandPanel


class ComparePanel(CommandPanel):
    """Diff two PDFs via diff-pdf or the headless pipeline."""

    def __init__(self, runner) -> None:
        super().__init__(
            runner,
            title="Compare",
            description="Wrap the CLI compare helper (diff-pdf or Poppler/ImageMagick fallback).",
            job_name="compare",
        )
        self.first_edit = QLineEdit()
        self.form_layout.addRow("First PDF", self._with_browse(self.first_edit))

        self.second_edit = QLineEdit()
        self.form_layout.addRow("Second PDF", self._with_browse(self.second_edit))

        self.output_edit = QLineEdit()
        self.form_layout.addRow("Diff PDF", self._with_browse(self.output_edit, save=True))

        self.headless_check = QCheckBox("Force headless compare (pdftocairo + ImageMagick)")
        self.headless_check.toggled.connect(self.update_command_preview)
        self.form_layout.addRow(self.headless_check)

        warning = QLabel(
            "Install diff-pdf for best results. Headless mode requires pdftocairo, compare, and img2pdf on PATH."
        )
        warning.setWordWrap(True)
        self.form_layout.addRow(warning)

        self.update_command_preview()

    def build_command_parts(self) -> Sequence[str] | None:
        first = self.first_edit.text().strip()
        second = self.second_edit.text().strip()
        output = self.output_edit.text().strip()
        if not first or not second or not output:
            return None
        parts = ["compare", first, second, "-o", output]
        if self.headless_check.isChecked():
            parts.append("--headless")
        return parts

    def _with_browse(self, field: QLineEdit, save: bool = False) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(field)
        button = QPushButton("Browse…")
        button.clicked.connect(lambda: self._select_file(field, save))
        layout.addWidget(button)
        return row

    def _select_file(self, field: QLineEdit, save: bool) -> None:
        if save:
            path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF files (*.pdf)")
        if path:
            field.setText(path)
        self.update_command_preview()
