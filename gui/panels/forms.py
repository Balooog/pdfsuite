from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QWidget,
)

from gui.panels.base import CommandPanel


class FormsPanel(CommandPanel):
    """Fill or flatten forms using the CLI helpers."""

    def __init__(self, runner) -> None:
        super().__init__(
            runner,
            title="Forms",
            description="Fill PDF forms from FDF/XFDF data or flatten existing form fields.",
            job_name="forms",
        )
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Fill form", "fill")
        self.mode_combo.addItem("Flatten form", "flatten")
        self.mode_combo.currentIndexChanged.connect(self._refresh_visibility)
        self.form_layout.addRow("Action", self.mode_combo)

        self.input_edit = QLineEdit()
        self.form_layout.addRow("Input PDF", self._with_browse(self.input_edit, self._select_pdf))

        self.data_edit = QLineEdit()
        self.form_layout.addRow("FDF/XFDF data", self._with_browse(self.data_edit, self._select_data))

        self.output_edit = QLineEdit()
        self.form_layout.addRow("Output PDF", self._with_browse(self.output_edit, self._select_output, save=True))

        self._refresh_visibility()
        self.update_command_preview()

    def build_command_parts(self) -> Sequence[str] | None:
        mode = self.mode_combo.currentData()
        input_pdf = self.input_edit.text().strip()
        output_pdf = self.output_edit.text().strip()
        if not input_pdf or not output_pdf:
            return None
        if mode == "fill":
            data_path = self.data_edit.text().strip()
            if not data_path:
                return None
            return ["forms", "fill", input_pdf, data_path, "-o", output_pdf]
        return ["forms", "flatten", input_pdf, "-o", output_pdf]

    def _refresh_visibility(self) -> None:
        is_fill = self.mode_combo.currentData() == "fill"
        self.data_edit.parent().setVisible(is_fill)
        self.update_command_preview()

    def _with_browse(self, line_edit: QLineEdit, callback, save: bool = False) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        button = QPushButton("Browse…")
        button.clicked.connect(lambda: callback(line_edit, save))
        layout.addWidget(button)
        return row

    def _select_pdf(self, field: QLineEdit, save: bool = False) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF files (*.pdf)")
        if path:
            field.setText(path)
        self.update_command_preview()

    def _select_data(self, field: QLineEdit, save: bool = False) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select FDF/XFDF",
            filter="Form data (*.fdf *.xfdf)",
        )
        if path:
            field.setText(path)
        self.update_command_preview()

    def _select_output(self, field: QLineEdit, save: bool = True) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
        if path:
            field.setText(path)
        self.update_command_preview()
