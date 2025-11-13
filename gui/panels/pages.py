from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.panels.base import CommandPanel


class PagesPanel(CommandPanel):
    """Merge, split, or reorder PDFs via qpdf helpers."""

    def __init__(self, runner) -> None:
        super().__init__(
            runner,
            title="Pages",
            description="Manage PDF pages (merge, split ranges, reorder) before sending files "
            "through downstream workflows.",
        )
        self.mode = QComboBox()
        self.mode.addItem("Merge PDFs", "merge")
        self.mode.addItem("Split ranges", "split")
        self.mode.addItem("Reorder pages", "reorder")
        self.mode.currentIndexChanged.connect(self.update_command_preview)
        self.form_layout.addRow("Action", self.mode)

        self.inputs_edit = QPlainTextEdit()
        self.inputs_edit.setPlaceholderText("One PDF path per line.")
        self.inputs_edit.textChanged.connect(self.update_command_preview)

        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.addWidget(self.inputs_edit)
        add_files = QPushButton("Choose PDFs…")
        add_files.clicked.connect(self._select_inputs)
        input_layout.addWidget(add_files)
        self.form_layout.addRow("Input PDFs", input_container)

        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("1-3,4,5-z")
        self.range_input.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow("Ranges / order", self.range_input)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Output file or directory")
        self.output_edit.textChanged.connect(self.update_command_preview)
        output_row = QWidget()
        output_layout = QHBoxLayout(output_row)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.addWidget(self.output_edit)
        browse_output = QPushButton("Browse…")
        browse_output.clicked.connect(self._select_output)
        output_layout.addWidget(browse_output)
        self.form_layout.addRow("Output", output_row)

        self.update_command_preview()

    def build_command_parts(self) -> Sequence[str] | None:
        mode = self.mode.currentData()
        inputs = self._input_list()
        output = self.output_edit.text().strip()
        ranges = self.range_input.text().strip()

        if mode == "merge":
            if len(inputs) < 2 or not output:
                return None
            return ["merge", *inputs, "-o", output]

        if mode == "split":
            if len(inputs) != 1 or not ranges:
                return None
            target = output or "splits"
            return ["split", inputs[0], "--pages", ranges, "-o", target]

        if mode == "reorder":
            if len(inputs) != 1 or not output or not ranges:
                return None
            return ["reorder", inputs[0], "--order", ranges, "-o", output]

        return None

    def _input_list(self) -> list[str]:
        text = self.inputs_edit.toPlainText().strip()
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _select_inputs(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", filter="PDF files (*.pdf)")
        if files:
            self.inputs_edit.setPlainText("\n".join(files))
            self.update_command_preview()

    def _select_output(self) -> None:
        mode = self.mode.currentData()
        if mode == "split":
            directory = QFileDialog.getExistingDirectory(self, "Select output directory")
            if directory:
                self.output_edit.setText(directory)
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
            if path:
                self.output_edit.setText(path)
        self.update_command_preview()
