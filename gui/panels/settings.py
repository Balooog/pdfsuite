from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
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

        layout.addWidget(QLabel("<h3>Reader preferences</h3>"))
        reader_form = QFormLayout()
        self.zoom_step_spin = QSpinBox()
        self.zoom_step_spin.setRange(1, 50)
        self.zoom_step_spin.setValue(settings.data.reader_zoom_step)
        reader_form.addRow("Zoom step (%)", self.zoom_step_spin)

        self.pan_speed_spin = QSpinBox()
        self.pan_speed_spin.setRange(16, 512)
        self.pan_speed_spin.setValue(settings.data.reader_pan_speed)
        reader_form.addRow("Pan speed (px)", self.pan_speed_spin)

        self.thumb_size_spin = QSpinBox()
        self.thumb_size_spin.setRange(48, 256)
        self.thumb_size_spin.setValue(settings.data.reader_thumbnail_size)
        reader_form.addRow("Thumbnail size (px)", self.thumb_size_spin)

        self.reader_layout_check = QCheckBox("Remember dock layout")
        self.reader_layout_check.setChecked(settings.data.remember_reader_layout)
        reader_form.addRow(self.reader_layout_check)

        self.default_helper_button = QPushButton("Default app helper…")
        self.default_helper_button.clicked.connect(self._show_default_helper)
        reader_form.addRow(self.default_helper_button)
        layout.addLayout(reader_form)

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
        self.settings.data.reader_zoom_step = self.zoom_step_spin.value()
        self.settings.data.reader_pan_speed = self.pan_speed_spin.value()
        self.settings.data.reader_thumbnail_size = self.thumb_size_spin.value()
        self.settings.data.remember_reader_layout = self.reader_layout_check.isChecked()
        Path(output).mkdir(parents=True, exist_ok=True)
        self.settings.save()
        if self._on_save:
            self._on_save()

    def _show_default_helper(self) -> None:
        if sys.platform.startswith("win"):
            message = (
                "Generate a .reg file with the following contents (update the exe path) and double-click it:\n\n"
                'Windows Registry Editor Version 5.00\n\n'
                '[HKEY_CURRENT_USER\\Software\\Classes\\pdfsuite.pdf]\n'
                '@="pdfsuite PDF"\n'
                '"FriendlyTypeName"="pdfsuite PDF"\n'
                '[HKEY_CURRENT_USER\\Software\\Classes\\.pdf]\n'
                '@="pdfsuite.pdf"\n'
                '[HKEY_CURRENT_USER\\Software\\Classes\\pdfsuite.pdf\\shell\\open\\command]\n'
                f'@="\\"{sys.executable}\\" -m gui.main \\"%1\\""\n\n'
                "You can revert via Windows Settings ▸ Apps ▸ Default apps."
            )
        else:
            desktop_path = Path.home() / ".local" / "share" / "applications" / "pdfsuite.desktop"
            message = (
                "Create ~/.local/share/applications/pdfsuite.desktop with:\n\n"
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=pdfsuite GUI\n"
                f"Exec={sys.executable} -m gui.main %f\n"
                "MimeType=application/pdf;\n\n"
                f"Then run: xdg-mime default pdfsuite.desktop application/pdf\n"
                f"(desktop file path: {desktop_path})"
            )
        QMessageBox.information(self, "Default PDF helper", message)
