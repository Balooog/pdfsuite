from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.services import SettingsStore


class SettingsPanel(QWidget):
    """Configure tool paths, defaults, watch-folder automation, and launch behavior."""

    def __init__(self, settings: SettingsStore, on_save_callback=None) -> None:
        super().__init__()
        self.settings = settings
        self._on_save = on_save_callback
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Settings</h2>"))

        form = QFormLayout()
        self.external_viewer_edit = QLineEdit(settings.data.external_viewer)
        self.external_viewer_edit.setPlaceholderText("Leave blank to use OS default viewer")
        form.addRow(
            "External viewer",
            self._with_browse(self.external_viewer_edit, self._select_external),
        )

        self.output_dir_edit = QLineEdit(settings.data.default_output_dir)
        form.addRow(
            "Default output dir",
            self._with_browse(self.output_dir_edit, self._select_output_dir, directory=True),
        )

        self.run_doctor_check = QCheckBox("Run `pdfsuite doctor` on launch")
        self.run_doctor_check.setChecked(settings.data.run_doctor_on_launch)
        form.addRow(self.run_doctor_check)

        layout.addLayout(form)

        layout.addWidget(QLabel("<h3>Watch-folder automation</h3>"))
        watch_form = QFormLayout()
        self.watch_enable = QCheckBox("Enable `pdfsuite watch` on startup")
        self.watch_enable.setChecked(settings.data.watch_enabled)
        watch_form.addRow(self.watch_enable)

        self.watch_folder_edit = QLineEdit(settings.data.watch_folder)
        watch_form.addRow(
            "Folder",
            self._with_browse(self.watch_folder_edit, self._select_output_dir, directory=True),
        )

        self.watch_preset_combo = QComboBox()
        self.watch_preset_combo.addItems(["email", "report", "poster"])
        index = self.watch_preset_combo.findText(settings.data.watch_preset)
        if index >= 0:
            self.watch_preset_combo.setCurrentIndex(index)
        watch_form.addRow("Preset", self.watch_preset_combo)

        self.watch_target_edit = QLineEdit(
            "" if settings.data.watch_target_size is None else str(settings.data.watch_target_size)
        )
        self.watch_target_edit.setPlaceholderText("e.g., 3 (MB)")
        watch_form.addRow("Target size (MB)", self.watch_target_edit)

        layout.addLayout(watch_form)

        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _with_browse(self, field: QLineEdit, callback, directory: bool = False) -> QWidget:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(field)
        button = QPushButton("Browse…")
        button.clicked.connect(lambda: callback(field, directory))
        row_layout.addWidget(button)
        return row

    def _select_external(self, field: QLineEdit, directory: bool) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select viewer executable")
        if file_path:
            field.setText(file_path)

    def _select_output_dir(self, field: QLineEdit, directory: bool) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select output directory")
        if selected:
            field.setText(selected)

    def _save(self) -> None:
        self.settings.data.external_viewer = self.external_viewer_edit.text().strip()
        output = self.output_dir_edit.text().strip() or self.settings.data.default_output_dir
        self.settings.data.default_output_dir = output
        self.settings.data.run_doctor_on_launch = self.run_doctor_check.isChecked()
        self.settings.data.watch_enabled = self.watch_enable.isChecked()
        self.settings.data.watch_folder = self.watch_folder_edit.text().strip()
        self.settings.data.watch_preset = self.watch_preset_combo.currentText()
        target_text = self.watch_target_edit.text().strip()
        self.settings.data.watch_target_size = float(target_text) if target_text else None
        Path(output).mkdir(parents=True, exist_ok=True)
        self.settings.save()
        if self._on_save:
            self._on_save()
