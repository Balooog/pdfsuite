from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QAbstractListModel, QModelIndex, QSize, Qt, Signal
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QListView,
    QMenu,
    QStyle,
    QStyleOptionViewItem,
)

from gui.services import PdfPreviewProvider
from pdfsuite.core.document_session import DocumentSession


class PageStripModel(QAbstractListModel):
    page_role = Qt.UserRole + 1

    def __init__(self, preview: PdfPreviewProvider, thumbnail_size: int) -> None:
        super().__init__()
        self.preview = preview
        self._size = QSize(thumbnail_size, int(thumbnail_size * 1.35))
        self.session: Optional[DocumentSession] = None
        self.document = None
        self._cache: dict[int, QPixmap] = {}

    def set_session(self, session: DocumentSession | None, document) -> None:
        self.beginResetModel()
        self.session = session
        self.document = document
        self._cache.clear()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if parent and parent.isValid():
            return 0
        if not self.session:
            return 0
        return len(self.session.page_order)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not self.session:
            return None
        page_number = self.session.page_order[index.row()]
        if role == Qt.DisplayRole:
            return f"Page {page_number}"
        if role == PageStripModel.page_role:
            return page_number
        if role == Qt.DecorationRole:
            return self._thumbnail(page_number)
        return None

    def refresh(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def _thumbnail(self, page_number: int) -> QPixmap | None:
        if page_number in self._cache:
            return self._cache[page_number]
        if not self.preview.available or self.document is None:
            return None
        pixmap = self.preview.render_thumbnail(self.document, page_number - 1, self._size)
        if pixmap:
            self._cache[page_number] = pixmap
        return pixmap


class PageStrip(QListView):
    reordered = Signal()
    selectionChangedSignal = Signal(list)
    rotateRequested = Signal(list, int)
    deleteRequested = Signal(list)
    extractRequested = Signal(list)

    def __init__(self, preview: PdfPreviewProvider, thumbnail_size: int) -> None:
        super().__init__()
        self.preview = preview
        self.thumbnail_size = thumbnail_size
        self.setSelectionMode(QListView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSpacing(4)
        self.setUniformItemSizes(True)
        self.model_obj = PageStripModel(preview, thumbnail_size)
        self.setModel(self.model_obj)
        self.session: Optional[DocumentSession] = None

        self.selectionModel().selectionChanged.connect(self._emit_selection)

    def set_session(self, session: DocumentSession | None, document) -> None:
        self.session = session
        self.model_obj.set_session(session, document)

    def refresh(self) -> None:
        self.model_obj.refresh()

    def selected_rows(self) -> List[int]:
        if not self.selectionModel():
            return []
        indexes = self.selectedIndexes()
        if not indexes:
            return []
        return sorted({index.row() for index in indexes})

    def dropEvent(self, event) -> None:
        if not self.session:
            return super().dropEvent(event)
        target = self.indexAt(event.position().toPoint()).row()
        if target < 0:
            target = self.model().rowCount()
        rows = self.selected_rows()
        if rows:
            self.session.reorder(rows, target)
            self.refresh()
            self.reordered.emit()
            event.acceptProposedAction()
            return
        super().dropEvent(event)

    def contextMenuEvent(self, event) -> None:
        if not self.session:
            return
        rows = self.selected_rows()
        if not rows:
            idx = self.indexAt(event.pos())
            if not idx.isValid():
                return
            self.selectionModel().select(idx, self.selectionModel().Select)
            rows = [idx.row()]
        menu = QMenu(self)
        for angle, label in ((90, "Rotate +90°"), (-90, "Rotate -90°"), (180, "Rotate 180°")):
            action = QAction(label, menu)
            action.triggered.connect(lambda _, a=angle, r=rows: self.rotateRequested.emit(r, a))
            menu.addAction(action)
        delete_action = QAction("Delete pages", menu)
        delete_action.triggered.connect(lambda _, r=rows: self.deleteRequested.emit(r))
        menu.addAction(delete_action)
        extract_action = QAction("Extract to new PDF", menu)
        extract_action.triggered.connect(lambda _, r=rows: self.extractRequested.emit(r))
        menu.addAction(extract_action)
        menu.exec(event.globalPos())

    def _emit_selection(self, *_args) -> None:
        self.selectionChangedSignal.emit(self.selected_rows())
