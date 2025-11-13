from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)

from gui.panels.base import CommandPanel


class SignPanel(CommandPanel):
    """Digitally sign PDFs via the jSignPdf-backed CLI helper."""

    def __init__(self, runner) -> None:
        super().__init__(
            runner,
            title="Sign & Verify",
            description="Wrap the pdfsuite signing helper so certificates, visible signatures, "
            "and outputs can be configured interactively.",
        )
        self.input_edit = QLineEdit()
        self.input_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow(
            "Input PDF",
            self._with_browse(self.input_edit, self._select_input, save_dialog=False),
        )

        self.output_edit = QLineEdit()
        self.output_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow(
            "Output PDF",
            self._with_browse(self.output_edit, self._select_output, save_dialog=True),
        )

        self.p12_edit = QLineEdit()
        self.p12_edit.setPlaceholderText("certificate.p12")
        self.p12_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow(
            "PKCS#12 bundle",
            self._with_browse(self.p12_edit, self._select_p12, save_dialog=False),
        )

        self.alias_edit = QLineEdit()
        self.alias_edit.textChanged.connect(self.update_command_preview)
        self.form_layout.addRow("Certificate alias", self.alias_edit)

        self.visible_checkbox = QCheckBox("Add visible signature block")
        self.visible_checkbox.toggled.connect(self._toggle_visible_fields)
        self.form_layout.addRow(self.visible_checkbox)

        self.visible_container = QWidget()
        self.visible_form = QFormLayout(self.visible_container)
        self.form_layout.addRow("Visible placement", self.visible_container)

        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setValue(1)
        self.page_spin.valueChanged.connect(self.update_command_preview)
        self.visible_form.addRow("Page", self.page_spin)

        self.x_spin = self._make_spin("X (pt)")
        self.y_spin = self._make_spin("Y (pt)")
        self.w_spin = self._make_spin("Width (pt)", default=200)
        self.h_spin = self._make_spin("Height (pt)", default=60)

        self._toggle_visible_fields(self.visible_checkbox.isChecked())

    def build_command_parts(self) -> Sequence[str] | None:
        pdf = self.input_edit.text().strip()
        output = self.output_edit.text().strip()
        p12 = self.p12_edit.text().strip()
        alias = self.alias_edit.text().strip()
        if not all([pdf, output, p12, alias]):
            return None

        parts = ["sign", pdf, "-o", output, "--p12", p12, "--alias", alias]
        if self.visible_checkbox.isChecked():
            visible = (
                f"p={self.page_spin.value()},"
                f"x={self.x_spin.value()},y={self.y_spin.value()},"
                f"w={self.w_spin.value()},h={self.h_spin.value()}"
            )
            parts.extend(["--visible", visible])
        return parts

    def _toggle_visible_fields(self, enabled: bool) -> None:
        for widget in [
            self.page_spin,
            self.x_spin,
            self.y_spin,
            self.w_spin,
            self.h_spin,
        ]:
            widget.setEnabled(enabled)
        self.visible_container.setEnabled(enabled)
        self.update_command_preview()

    def _make_spin(self, label: str, default: int = 0) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(0, 10000)
        spin.setValue(default)
        spin.valueChanged.connect(self.update_command_preview)
        self.visible_form.addRow(label, spin)
        return spin

    def _with_browse(
        self,
        line_edit: QLineEdit,
        callback,
        *,
        save_dialog: bool,
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
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF files (*.pdf)")
        if path:
            self.input_edit.setText(path)
        self.update_command_preview()

    def _select_output(self, *, save_dialog: bool = True) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
        if path:
            self.output_edit.setText(path)
        self.update_command_preview()

    def _select_p12(self, *, save_dialog: bool = False) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select PKCS#12 bundle", filter="PKCS#12 (*.p12 *.pfx)")
        if path:
            self.p12_edit.setText(path)
        self.update_command_preview()
