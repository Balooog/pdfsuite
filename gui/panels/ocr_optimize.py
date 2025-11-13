from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from gui.panels.base import CommandPanel

OPTIMIZE_PRESETS = [
    ("Email (≤150 dpi)", "email"),
    ("Report (300 dpi)", "report"),
    ("Poster (minimal changes)", "poster"),
]


class OcrOptimizePanel(CommandPanel):
    """Combine OCR and optimize helpers with preset controls."""

    def __init__(self, runner) -> None:
        super().__init__(
            runner,
            title="OCR & Optimize",
            description="Add a searchable text layer or shrink PDFs with built-in presets.",
            job_name="ocr-optimize",
        )
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("OCR only", "ocr")
        self.mode_combo.addItem("Optimize only", "optimize")
        self.mode_combo.currentIndexChanged.connect(self._refresh_visibility)
        self.form_layout.addRow("Action", self.mode_combo)

        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Path to input PDF")
        self.input_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow("Input PDF", self._with_browse(self.input_edit, self._select_input))

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("output.pdf")
        self.output_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow("Output PDF", self._with_browse(self.output_edit, self._select_output, save=True))

        self.preset_combo = QComboBox()
        for label, value in OPTIMIZE_PRESETS:
            self.preset_combo.addItem(label, value)
        self.preset_combo.currentIndexChanged.connect(self.update_command_preview)

        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("e.g., 3 (MB)")
        self.target_edit.textChanged.connect(self.update_command_preview)

        optimize_fields = QWidget()
        optimize_layout = QFormLayout(optimize_fields)
        optimize_layout.setContentsMargins(0, 0, 0, 0)
        optimize_layout.addRow("Preset", self.preset_combo)
        optimize_layout.addRow("Target size (MB)", self.target_edit)
        self.form_layout.addRow(optimize_fields)

        self._optimize_fields = optimize_fields
        self._refresh_visibility()
        self.update_command_preview()

    def build_command_parts(self) -> Sequence[str] | None:
        mode = self.mode_combo.currentData()
        source = self.input_edit.text().strip()
        dest = self.output_edit.text().strip()
        if not source or not dest:
            return None
        if mode == "ocr":
            return ["ocr", source, "-o", dest]
        preset = self.preset_combo.currentData()
        parts = ["optimize", source, "-o", dest, "--preset", preset]
        target = self.target_edit.text().strip()
        if target:
            parts.extend(["--target-size", target])
        return parts

    def _refresh_visibility(self) -> None:
        is_optimize = self.mode_combo.currentData() == "optimize"
        self._optimize_fields.setVisible(is_optimize)
        self.update_command_preview()

    def _with_browse(self, field: QLineEdit, callback, save: bool = False) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(field)
        button = QPushButton("Browse…")
        button.clicked.connect(lambda: callback(save))
        layout.addWidget(button)
        return row

    def _select_input(self, save: bool = False) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select input PDF", filter="PDF files (*.pdf)")
        if path:
            self.input_edit.setText(path)
        self.update_command_preview()

    def _select_output(self, save: bool = True) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
        if path:
            self.output_edit.setText(path)
        self.update_command_preview()
