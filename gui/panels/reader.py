from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollBar,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from PySide6.QtPdfWidgets import QPdfView
except ImportError:  # pragma: no cover - optional dependency
    QPdfView = None  # type: ignore

from gui.services import (
    BookmarkNode,
    PdfPreviewProvider,
    Runner,
    SettingsStore,
    build_cli_command,
    parse_dump,
)
from gui.widgets.page_strip import PageStrip
from pdfsuite.core.document_session import DocumentSession


class ReaderPanel(QWidget):
    """PDF reader with docks for thumbnails and outline plus shared document session."""

    def __init__(self, runner: Runner, settings: SettingsStore, session_bus) -> None:
        super().__init__()
        self.runner = runner
        self.settings = settings
        self.session_bus = session_bus
        self.preview = PdfPreviewProvider()
        self.document = self.preview.create_document(self) if self.preview.available else None
        self.current_pdf: Path | None = None
        self.session: DocumentSession | None = None
        self._outline_tmp: Path | None = None
        self._search_hits: list[int] = []
        self._search_index = -1
        self._last_search = ""
        self._thumbs_visible = True
        self._outline_visible = True
        self.zoom_factor = 1.0
        self.zoom_step = max(1, settings.data.reader_zoom_step or 10)
        self.pan_speed = max(16, settings.data.reader_pan_speed or 64)
        self.thumbnail_size = settings.data.reader_thumbnail_size or 96

        layout = QVBoxLayout(self)
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

        self._build_toolbar(layout)
        self._build_body(layout)
        self._build_status(layout)
        self._build_logs(layout)
        self._install_shortcuts()
        if self.session_bus:
            self.session_bus.session_committed.connect(self._handle_session_committed)

    # ------------------------------------------------------------------ UI builders
    def _build_toolbar(self, layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.open_button = QPushButton("Open…")
        self.open_button.clicked.connect(self._select_pdf)
        row.addWidget(self.open_button)

        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(lambda: self._save_session(save_as=False))
        row.addWidget(self.save_button)

        self.save_as_button = QPushButton("Save As…")
        self.save_as_button.setEnabled(False)
        self.save_as_button.clicked.connect(lambda: self._save_session(save_as=True))
        row.addWidget(self.save_as_button)

        self.open_in_pages_button = QPushButton("Open in Pages…")
        self.open_in_pages_button.setEnabled(False)
        self.open_in_pages_button.clicked.connect(self._share_session_with_pages)
        row.addWidget(self.open_in_pages_button)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Single Page", "Continuous"])
        self.mode_combo.currentIndexChanged.connect(self._apply_view_mode)
        row.addWidget(self.mode_combo)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["Fit Width", "Fit Page", "100%", "150%", "200%", "Custom"])
        self.zoom_combo.currentIndexChanged.connect(self._apply_zoom_choice)
        row.addWidget(self.zoom_combo)

        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.clicked.connect(lambda: self._step_zoom(-1))
        row.addWidget(self.zoom_out_button)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.clicked.connect(lambda: self._step_zoom(1))
        row.addWidget(self.zoom_in_button)

        row.addWidget(QLabel("Find:"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search text…")
        row.addWidget(self.search_field)
        self.search_prev = QPushButton("Prev")
        self.search_prev.clicked.connect(lambda: self._search(-1))
        row.addWidget(self.search_prev)
        self.search_next = QPushButton("Next")
        self.search_next.clicked.connect(lambda: self._search(1))
        row.addWidget(self.search_next)

        self.external_button = QPushButton("Open externally")
        self.external_button.clicked.connect(self._open_external)
        self.external_button.setEnabled(False)
        row.addWidget(self.external_button)

        row.addStretch()
        layout.addLayout(row)

    def _build_body(self, layout: QVBoxLayout) -> None:
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter, 1)

        self.thumbnail_container = QWidget()
        thumb_layout = QVBoxLayout(self.thumbnail_container)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        self.page_strip = PageStrip(self.preview, self.thumbnail_size)
        self.page_strip.selectionChangedSignal.connect(self._on_strip_selection)
        self.page_strip.reordered.connect(self._on_pages_reordered)
        self.page_strip.deleteRequested.connect(self._on_delete_pages)
        self.page_strip.rotateRequested.connect(self._on_rotate_pages)
        self.page_strip.extractRequested.connect(self._on_extract_pages)
        thumb_layout.addWidget(self.page_strip)
        self.splitter.addWidget(self.thumbnail_container)

        self.pdf_view = QPdfView()
        self.pdf_view.setDocument(self.document)
        self._pdf_viewport = self.pdf_view.viewport()
        self._pdf_viewport.installEventFilter(self)
        self.splitter.addWidget(self.pdf_view)

        self.outline_container = QWidget()
        outline_layout = QVBoxLayout(self.outline_container)
        outline_layout.setContentsMargins(0, 0, 0, 0)
        self.outline_tree = QTreeWidget()
        self.outline_tree.setHeaderLabels(["Bookmark", "Page"])
        self.outline_tree.itemActivated.connect(self._outline_activated)
        outline_layout.addWidget(self.outline_tree)
        self.splitter.addWidget(self.outline_container)
        self.splitter.setStretchFactor(1, 4)

    def _build_status(self, layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.status_label = QLabel("No document loaded.")
        row.addWidget(self.status_label, 1)
        self.unsaved_chip = QLabel()
        self.unsaved_chip.setStyleSheet("color: #d9822b; font-weight: bold;")
        row.addWidget(self.unsaved_chip, 0, Qt.AlignRight)
        layout.addLayout(row)

    def _build_logs(self, layout: QVBoxLayout) -> None:
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Reader logs appear here (bookmarks dump/apply/save).")
        layout.addWidget(self.log_view)

    def _install_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+S"), self, activated=lambda: self._save_session(False))
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, activated=lambda: self._save_session(True))
        QShortcut(QKeySequence("T"), self, activated=self._toggle_thumbnails)
        QShortcut(QKeySequence("B"), self, activated=self._toggle_outline)

    # ------------------------------------------------------------------ Event filter
    def eventFilter(self, obj, event) -> bool:  # type: ignore[override]
        if getattr(self, "_pdf_viewport", None) is obj and event.type() == QEvent.Type.Wheel:
            modifiers = event.modifiers()
            if modifiers == Qt.ControlModifier:
                self._step_zoom(1 if event.angleDelta().y() > 0 else -1)
                return True
            if modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
                delta = self.pan_speed if event.angleDelta().y() > 0 else -self.pan_speed
                bar: QScrollBar = self.pdf_view.horizontalScrollBar()
                bar.setValue(bar.value() - delta)
                return True
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------ File handling
    def _select_pdf(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", filter="PDF files (*.pdf)")
        if file_path:
            self._load_pdf(Path(file_path))

    def _load_pdf(self, path: Path) -> None:
        if self.document is None:
            return
        status = QPdfDocument.Status.Ready if self.preview.load(self.document, path) else self.document.status()
        if status != QPdfDocument.Status.Ready:
            QMessageBox.warning(self, "Reader", f"Failed to load {path} (status: {status}).")
            self._append_log(f"[reader] QtPdf load failure ({status}) for {path}")
            return
        self.current_pdf = path
        pages = self.document.pageCount()
        self.session = DocumentSession(path=path, page_order=list(range(1, pages + 1)))
        self.page_strip.set_session(self.session, self.document)
        self.save_button.setEnabled(True)
        self.save_as_button.setEnabled(True)
        self.open_in_pages_button.setEnabled(True)
        self.external_button.setEnabled(True)
        self.unsaved_chip.clear()
        self._fetch_outline()
        self._apply_view_mode()
        self._apply_zoom_choice()
        self._update_status()
        self._append_log(f"[reader] Loaded {path} ({pages} pages).")

    def _save_session(self, save_as: bool) -> None:
        if not self.session or not self.current_pdf:
            return
        if save_as:
            target, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF as…",
                str(self.current_pdf.with_name(f"{self.current_pdf.stem}_reordered.pdf")),
                "PDF files (*.pdf)",
            )
            if not target:
                return
            destination = Path(target)
        else:
            destination = None

        self._append_log("[reader] Saving session…")

        def _finished(code: int, job_dir: Path) -> None:
            if code == 0:
                self._append_log(f"[reader] Saved (logs: {job_dir})")
                self.unsaved_chip.clear()
                if destination:
                    self._append_log(f"[reader] Output → {destination}")
                if self.session_bus and self.session:
                    self.session_bus.announce_commit(self.session)
            else:
                self._append_log(f"[reader] Save failed (see {job_dir})")

        self.session.commit(
            self.runner,
            output_path=destination,
            job_name="reader-save",
            on_output=self._append_log,
            on_finished=_finished,
        )

    def _share_session_with_pages(self) -> None:
        if self.session and self.session_bus:
            self.session_bus.share(self.session)

    def _handle_session_committed(self, session: DocumentSession) -> None:
        if not self.session or session is not self.session:
            return
        self._append_log("[reader] Session updated from Pages.")
        self.unsaved_chip.clear()
        self._reload_document_view()

    def _reload_document_view(self) -> None:
        if not self.session or not self.document:
            return
        self.preview.load(self.document, self.session.path)
        self.page_strip.refresh()
        self._update_status()

    # ------------------------------------------------------------------ Page strip callbacks
    def _on_strip_selection(self, rows: list[int]) -> None:
        if not self.session or not rows:
            return
        page_numbers = [self.session.page_order[row] for row in rows]
        self.session.selection = set(page_numbers)
        self._jump_to_page_number(page_numbers[0])

    def _on_pages_reordered(self) -> None:
        if not self.session:
            return
        self._append_log("[reader] Page order updated.")
        self.page_strip.refresh()
        self.unsaved_chip.setText("● Unsaved changes")

    def _on_delete_pages(self, rows: list[int]) -> None:
        if not self.session:
            return
        self.session.delete(rows)
        self.page_strip.refresh()
        self.unsaved_chip.setText("● Unsaved changes")
        self._append_log(f"[reader] Marked {len(rows)} page(s) for deletion.")

    def _on_rotate_pages(self, rows: list[int], angle: int) -> None:
        if not self.session:
            return
        try:
            self.session.rotate(rows, angle)
            self.unsaved_chip.setText("● Unsaved changes")
            self._append_log(f"[reader] Rotation {angle}° queued for {len(rows)} page(s).")
        except ValueError as exc:
            self._append_log(f"[reader] {exc}")

    def _on_extract_pages(self, rows: list[int]) -> None:
        self._append_log("[reader] Extract workflow coming soon (use Pages panel for now).")

    # ------------------------------------------------------------------ View helpers
    def _jump_to_page_number(self, page_number: int) -> None:
        if self.document is None or self.pdf_view is None:
            return
        navigator = self.pdf_view.pageNavigator()
        navigator.jump(max(0, page_number - 1))
        self._update_status(current_page=page_number)

    def _apply_view_mode(self) -> None:
        if not hasattr(self, "pdf_view") or self.pdf_view is None:
            return
        choice = self.mode_combo.currentText()
        mode = QPdfView.PageMode.MultiPage if choice == "Continuous" else QPdfView.PageMode.SinglePage
        self.pdf_view.setPageMode(mode)

    def _apply_zoom_choice(self) -> None:
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
        percent = int(choice.rstrip("%")) if choice.endswith("%") else 100
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.zoom_factor = max(0.1, min(8.0, percent / 100))
        self.pdf_view.setZoomFactor(self.zoom_factor)

    def _step_zoom(self, direction: int) -> None:
        if not hasattr(self, "pdf_view") or self.pdf_view is None:
            return
        delta = (self.zoom_step / 100) * direction
        self.zoom_factor = max(0.1, min(8.0, self.zoom_factor + delta))
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.pdf_view.setZoomFactor(self.zoom_factor)
        self._update_zoom_combo()
        self._update_status()

    def _update_zoom_combo(self) -> None:
        if not hasattr(self, "zoom_combo"):
            return
        percent = int(self.zoom_factor * 100)
        text = f"{percent}%"
        idx = self.zoom_combo.findText(text)
        self.zoom_combo.blockSignals(True)
        if idx >= 0:
            self.zoom_combo.setCurrentIndex(idx)
        else:
            custom_index = self.zoom_combo.findText("Custom")
            if custom_index >= 0:
                self.zoom_combo.setCurrentIndex(custom_index)
        self.zoom_combo.blockSignals(False)

    # ------------------------------------------------------------------ Search
    def _search(self, direction: int) -> None:
        if not self.document or not self.current_pdf:
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
        target_page = self._search_hits[self._search_index]
        self._focus_page(target_page)

    def _collect_search_hits(self, query: str) -> list[int]:
        hits: list[int] = []
        pages = self.document.pageCount() if self.document else 0
        lower_query = query.lower()
        for page in range(1, pages + 1):
            text = self._extract_page_text(page).lower()
            if lower_query in text:
                hits.append(page)
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

    def _focus_page(self, page_number: int) -> None:
        if not self.session:
            self._jump_to_page_number(page_number)
            return
        try:
            row = self.session.page_order.index(page_number)
        except ValueError:
            row = page_number - 1
        index = self.page_strip.model().index(row, 0)
        self.page_strip.setCurrentIndex(index)
        self._jump_to_page_number(page_number)

    # ------------------------------------------------------------------ Outline
    def _outline_activated(self, item: QTreeWidgetItem) -> None:
        try:
            page_number = int(item.data(0, Qt.UserRole))
        except (TypeError, ValueError):
            page_number = item.data(0, Qt.DisplayRole)
            if isinstance(page_number, str) and page_number.isdigit():
                page_number = int(page_number)
        if isinstance(page_number, int):
            self._focus_page(page_number)

    def _fetch_outline(self) -> None:
        if not self.current_pdf:
            return
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        self._outline_tmp = tmp_path
        command = [
            "pdftk",
            str(self.current_pdf),
            "dump_data_utf8",
            "output",
            str(tmp_path),
        ]
        if shutil.which("pdftk") is None:
            self._append_log("[reader] pdftk is required for outline export.")
            return
        proc = subprocess.run(command, capture_output=True, text=True)
        if proc.returncode != 0:
            self._append_log("[reader] Failed to export outline.")
            return
        nodes = parse_dump(tmp_path.read_text(encoding="utf-8"))
        self._populate_outline(nodes)

    def _populate_outline(self, nodes: list[BookmarkNode]) -> None:
        self.outline_tree.clear()
        for node in nodes:
            item = QTreeWidgetItem([node.title, str(node.page)])
            item.setData(0, Qt.UserRole, node.page)
            self.outline_tree.addTopLevelItem(item)
            self._append_outline_children(item, node.children)

    def _append_outline_children(self, parent: QTreeWidgetItem, children: list[BookmarkNode]) -> None:
        for child in children:
            item = QTreeWidgetItem([child.title, str(child.page)])
            item.setData(0, Qt.UserRole, child.page)
            parent.addChild(item)
            self._append_outline_children(item, child.children)

    # ------------------------------------------------------------------ Misc helpers
    def _toggle_thumbnails(self) -> None:
        self._thumbs_visible = not self._thumbs_visible
        self.thumbnail_container.setVisible(self._thumbs_visible)

    def _toggle_outline(self) -> None:
        self._outline_visible = not self._outline_visible
        self.outline_container.setVisible(self._outline_visible)

    def _update_status(self, current_page: int | None = None) -> None:
        if not self.document or not self.current_pdf:
            self.status_label.setText("No document loaded.")
            return
        page = current_page or self.pdf_view.pageNavigator().currentPage() + 1
        total = self.document.pageCount()
        zoom = int(self.zoom_factor * 100)
        self.status_label.setText(f"{self.current_pdf.name} — Page {page}/{total} @ {zoom}%")

    def _open_external(self) -> None:
        if not self.current_pdf:
            return
        override = self.settings.data.external_viewer.strip()
        if override:
            subprocess.Popen([override, str(self.current_pdf)])
            return
        if sys.platform.startswith("win"):
            os.startfile(str(self.current_pdf))  # type: ignore[attr-defined]
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.Popen([opener, str(self.current_pdf)])

    def _append_log(self, message: str) -> None:
        self.log_view.appendPlainText(message)
