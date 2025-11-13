from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - optional dependency
    QWebEngineView = None  # type: ignore

from gui.services import get_asset_path


class ThreeDPanel(QWidget):
    """View glTF/GLB/HTML scenes and export snapshots to PDF."""

    def __init__(self, runner) -> None:
        super().__init__()
        self.runner = runner
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>3D Viewer</h2>"))

        if QWebEngineView is None:
            warn = QLabel(
                "Qt WebEngine is not available. Install PySide6 with WebEngine extras to enable the 3D panel."
            )
            warn.setWordWrap(True)
            layout.addWidget(warn)
            self.log = QTextEdit()
            self.log.setReadOnly(True)
            layout.addWidget(self.log)
            return

        file_row = QHBoxLayout()
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Select a .glb/.gltf or HTML viewer")
        file_row.addWidget(self.model_edit)
        browse_model = QPushButton("Choose model…")
        browse_model.clicked.connect(self._select_model)
        file_row.addWidget(browse_model)
        layout.addLayout(file_row)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("snapshot.pdf")
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit)
        browse_output = QPushButton("Snapshot output…")
        browse_output.clicked.connect(self._select_output)
        output_row.addWidget(browse_output)
        layout.addLayout(output_row)

        buttons = QHBoxLayout()
        load_button = QPushButton("Load in viewer")
        load_button.clicked.connect(self._load_model)
        buttons.addWidget(load_button)

        self.snapshot_button = QPushButton("Export snapshot to PDF")
        self.snapshot_button.clicked.connect(self._export_snapshot)
        buttons.addWidget(self.snapshot_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.view = QWebEngineView()
        layout.addWidget(self.view, 1)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("3D viewer logs.")
        layout.addWidget(self.log)

    def _append_log(self, message: str) -> None:
        self.log.append(message)

    def _select_model(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select model or viewer",
            filter="3D files (*.glb *.gltf *.html *.htm)",
        )
        if path:
            self.model_edit.setText(path)

    def _select_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select snapshot PDF output",
            filter="PDF files (*.pdf)",
        )
        if path:
            self.output_edit.setText(path)

    def _load_model(self) -> None:
        if QWebEngineView is None:
            return
        source = self.model_edit.text().strip()
        if not source:
            QMessageBox.information(self, "3D Viewer", "Choose a GLB/GLTF or HTML file.")
            return
        path = Path(source)
        if not path.exists():
            QMessageBox.warning(self, "3D Viewer", f"{path} does not exist.")
            return
        if path.suffix.lower() in {".html", ".htm"}:
            url = QUrl.fromLocalFile(str(path))
        else:
            template = get_asset_path("3d_viewer/index.html")
            url = QUrl.fromLocalFile(str(template))
            url.setQuery(f"model={QUrl.fromLocalFile(str(path)).toString()}")
        self.view.load(url)
        self._append_log(f"Loaded {source}")

    def _export_snapshot(self) -> None:
        if QWebEngineView is None:
            return
        output = self.output_edit.text().strip()
        if not output:
            QMessageBox.information(self, "3D Viewer", "Provide an output PDF path.")
            return
        if not shutil_which("pdfcpu"):
            QMessageBox.warning(self, "3D Viewer", "pdfcpu is required for snapshot export.")
            return
        target = Path(output)

        pixmap = self.view.grab()
        image = pixmap.toImage()
        fd, tmp_png = tempfile.mkstemp(prefix="pdfsuite-3d-", suffix=".png")
        os.close(fd)
        png_path = Path(tmp_png)
        image.save(str(png_path), "PNG")
        try:
            cmd = [
                "pdfcpu",
                "import",
                "-mode",
                "image",
                str(png_path),
                str(target),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self._append_log(f"Snapshot saved to {target}")
            else:
                self._append_log(f"pdfcpu failed: {result.stderr}")
        finally:
            png_path.unlink(missing_ok=True)


def shutil_which(cmd: str) -> bool:
    import shutil

    return shutil.which(cmd) is not None
