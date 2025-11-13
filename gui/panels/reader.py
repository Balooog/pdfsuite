from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
)
from PySide6.QtGui import QIcon

try:
    from PySide6.QtPdfWidgets import QPdfView
except ImportError:  # pragma: no cover - optional dependency
    QPdfView = None  # type: ignore

from gui.services import (
    BookmarkNode,
    PdfPreviewProvider,
    Runner,
    build_cli_command,
    parse_dump,
    SettingsStore,
)


class ReaderPanel(QWidget):
    """PDF reader with thumbnails + outline powered by QtPdf and CLI bookmarks."""

    def __init__(self, runner: Runner, settings: SettingsStore) -> None:
        super().__init__()
        self.runner = runner
        self.preview = PdfPreviewProvider()
        self.document = self.preview.create_document(self) if self.preview.available else None
        self.current_pdf: Path | None = None
        self._outline_tmp: Path | None = None
        self.settings = settings
        self._search_hits: list[int] = []
        self._search_index = -1
        self._last_search = ""

        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.open_button = QPushButton("Open PDF…")
        self.open_button.clicked.connect(self._select_pdf)
        toolbar.addWidget(self.open_button)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Single Page", "single")
        self.mode_combo.addItem("Continuous", "multi")
        self.mode_combo.currentIndexChanged.connect(self._apply_view_mode)
        toolbar.addWidget(self.mode_combo)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["Fit Width", "Fit Page", "100%", "150%", "200%"])
        self.zoom_combo.currentIndexChanged.connect(self._apply_zoom)
        toolbar.addWidget(self.zoom_combo)

        toolbar.addWidget(QLabel("Find:"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search text…")
        toolbar.addWidget(self.search_field)
        self.search_next = QPushButton("Next")
        self.search_prev = QPushButton("Prev")
        self.search_next.clicked.connect(lambda: self._search(direction=1))
        self.search_prev.clicked.connect(lambda: self._search(direction=-1))
        toolbar.addWidget(self.search_prev)
        toolbar.addWidget(self.search_next)

        self.external_button = QPushButton("Open externally")
        self.external_button.clicked.connect(self._open_external)
        toolbar.addWidget(self.external_button)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        if QPdfView is None or self.document is None:
            warning = QLabel(
                "QtPdf modules are unavailable. Install PySide6 with QtPdf extras to enable the reader."
            )
            warning.setWordWrap(True)
            layout.addWidget(warning)
            self.log_view = QPlainTextEdit()
            self.log_view.setReadOnly(True)
            layout.addWidget(self.log_view)
            return

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, 1)

        self.thumbnail_list = QListWidget()
        self.thumbnail_list.currentRowChanged.connect(self._jump_to_page)
        splitter.addWidget(self.thumbnail_list)

        self.pdf_view = QPdfView()
        self.pdf_view.setDocument(self.document)
        splitter.addWidget(self.pdf_view)

        self.outline_tree = QTreeWidget()
        self.outline_tree.setHeaderLabels(["Bookmark", "Page"])
        splitter.addWidget(self.outline_tree)

        self.status_label = QLabel("No document loaded.")
        layout.addWidget(self.status_label)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Reader logs appear here (bookmarks dump/apply).")
        layout.addWidget(self.log_view)

    # UI helpers
    def _append_log(self, message: str) -> None:
        self.log_view.appendPlainText(message)

    def _select_pdf(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", filter="PDF files (*.pdf)")
        if file_path:
            self._load_pdf(Path(file_path))

    def _load_pdf(self, path: Path) -> None:
        if self.document is None:
            return
        if not self.preview.load(self.document, path):
            QMessageBox.warning(self, "Reader", f"Failed to load {path}")
            return
        self.current_pdf = path
        self.status_label.setText(f"Loaded {path.name} ({self.document.pageCount()} pages)")
        self._populate_thumbnails()
        self._apply_view_mode()
        self._apply_zoom()
        self._fetch_outline()

    def _populate_thumbnails(self) -> None:
        if self.document is None:
            return
        self.thumbnail_list.clear()
        pages = self.document.pageCount()
        for idx in range(pages):
            label = f"Page {idx + 1}"
            item = QListWidgetItem(label)
            pixmap = self.preview.render_thumbnail(self.document, idx, QSize(96, 128))
            if pixmap:
                item.setIcon(QIcon(pixmap))
            item.setToolTip(f"Page {idx + 1}")
            self.thumbnail_list.addItem(item)

    def _jump_to_page(self, row: int) -> None:
        if row < 0 or self.document is None or self.pdf_view is None:
            return
        navigator = self.pdf_view.pageNavigator()
        navigator.jump(row)

    def _apply_view_mode(self) -> None:
        if not hasattr(self, "pdf_view") or self.pdf_view is None:
            return
        mode = self.mode_combo.currentData()
        if mode == "multi":
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        else:
            self.pdf_view.setPageMode(QPdfView.PageMode.SinglePage)

    def _apply_zoom(self) -> None:
        if not hasattr(self, "pdf_view") or self.pdf_view is None:
            return
        choice = self.zoom_combo.currentText()
        mapping = {
            "Fit Width": QPdfView.ZoomMode.FitToWidth,
            "Fit Page": QPdfView.ZoomMode.FitInView,
        }
        if choice in mapping:
            self.pdf_view.setZoomMode(mapping[choice])
            return
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        percent = int(choice.rstrip("%"))
        self.pdf_view.setZoomFactor(percent / 100)

    def _search(self, direction: int) -> None:
        if (
            self.document is None
            or not self.current_pdf
            or not hasattr(self, "pdf_view")
            or self.pdf_view is None
        ):
            return
        query = self.search_field.text().strip()
        if not query:
            return
        if shutil.which("pdftotext") is None:
            self._append_log("[reader] pdftotext is required for search.")
            return
        if query != self._last_search or not self._search_hits:
            self._search_hits = self._collect_search_hits(query)
            self._search_index = 0
            self._last_search = query
        else:
            self._search_index = (self._search_index + direction) % max(1, len(self._search_hits))
        if not self._search_hits:
            self._append_log(f"[reader] No matches found for '{query}'.")
            return
        target = self._search_hits[self._search_index]
        self.thumbnail_list.setCurrentRow(target)
        navigator = self.pdf_view.pageNavigator()
        navigator.jump(target)

    def _collect_search_hits(self, query: str) -> list[int]:
        hits: list[int] = []
        pages = self.document.pageCount() if self.document else 0
        lower_query = query.lower()
        for page in range(1, pages + 1):
            text = self._extract_page_text(page).lower()
            if lower_query in text:
                hits.append(page - 1)
        return hits

    def _extract_page_text(self, page: int) -> str:
        if not self.current_pdf:
            return ""
        result = subprocess.run(
            [
                "pdftotext",
                "-enc",
                "UTF-8",
                "-f",
                str(page),
                "-l",
                str(page),
                str(self.current_pdf),
                "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout or ""

    def _open_external(self) -> None:
        if not self.current_pdf:
            return
        override = self.settings.data.external_viewer.strip()
        if override:
            subprocess.Popen([override, str(self.current_pdf)])
            return
        if os.name == "nt":
            os.startfile(str(self.current_pdf))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(self.current_pdf)])
        else:
            subprocess.Popen(["xdg-open", str(self.current_pdf)])

    def _fetch_outline(self) -> None:
        if not self.current_pdf:
            return
        tmp_handle, tmp_path = tempfile.mkstemp(prefix="pdfsuite-bookmarks-", suffix=".txt")
        os.close(tmp_handle)
        dump_path = Path(tmp_path)
        self._outline_tmp = dump_path
        command = build_cli_command(
            "bookmarks",
            "dump",
            str(self.current_pdf),
            "-o",
            str(dump_path),
        )

        def _finished(code: int, job_dir: Path, tmp=dump_path) -> None:
            if code == 0 and tmp.exists():
                text = tmp.read_text(encoding="utf-8", errors="ignore")
                self._populate_outline(parse_dump(text))
            else:
                self._append_log("[reader] Failed to fetch outline.")
            if tmp.exists():
                tmp.unlink()

        self.runner.run(
            command,
            self._append_log,
            _finished,
            job_name="reader-outline",
        )

    def _populate_outline(self, nodes: list[BookmarkNode]) -> None:
        self.outline_tree.clear()
        for node in nodes:
            self.outline_tree.addTopLevelItem(self._build_item(node))
        self.outline_tree.expandToDepth(1)

    def _build_item(self, node: BookmarkNode) -> QTreeWidgetItem:
        item = QTreeWidgetItem([node.title, str(node.page)])
        for child in node.children:
            item.addChild(self._build_item(child))
        return item
