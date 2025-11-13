from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, QRectF, QPointF
from PySide6.QtGui import QImage, QPainter, QPixmap

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdf import QPdfDocumentRenderOptions
except ImportError:  # pragma: no cover - PySide6 extras might be missing in tests
    QPdfDocument = None  # type: ignore[assignment]
    QPdfDocumentRenderOptions = None  # type: ignore[assignment]


class PdfPreviewProvider:
    """Helper to load PDFs and render thumbnails via QtPdf."""

    def __init__(self) -> None:
        self.available = QPdfDocument is not None

    def create_document(self, parent=None):
        if QPdfDocument is None:
            return None
        return QPdfDocument(parent)

    def render_thumbnail(self, document, page: int, size: QSize) -> QPixmap | None:
        if QPdfDocument is None or document is None:
            return None
        image = QImage(size.width(), size.height(), QImage.Format_ARGB32)
        image.fill(0xFFFFFFFF)
        painter = QPainter(image)
        options = QPdfDocumentRenderOptions() if QPdfDocumentRenderOptions else None
        target = QRectF(QPointF(0, 0), size)
        document.render(page, painter, target, QRectF(), options)
        painter.end()
        return QPixmap.fromImage(image)

    def page_count(self, document) -> int:
        if document is None or QPdfDocument is None:
            return 0
        return document.pageCount()

    def load(self, document, path: Path) -> bool:
        if document is None or QPdfDocument is None:
            return False
        status = document.load(str(path))
        return status == QPdfDocument.Status.Ready
