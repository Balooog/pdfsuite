from __future__ import annotations

import os
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.services import (
    BookmarkNode,
    Runner,
    SettingsStore,
    build_cli_command,
    parse_dump,
    serialize_nodes,
)


class BookmarksPanel(QWidget):
    """Create/edit bookmarks then apply via the CLI `bookmarks` helpers."""

    def __init__(self, runner: Runner, settings: SettingsStore | None = None) -> None:
        super().__init__()
        self.runner = runner
        self.current_pdf: Path | None = None
        self.output_pdf: Path | None = None
        self._temp_dump: Path | None = None
        self.settings = settings

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("manual.pdf")
        form.addRow("Input PDF", self._with_browse(self.input_field, self._select_input))

        default_output = settings.data.default_output_dir if settings else ""
        self.output_field = QLineEdit(default_output)
        self.output_field.setPlaceholderText("manual_with_bookmarks.pdf")
        form.addRow("Output PDF", self._with_browse(self.output_field, self._select_output, save=True))

        layout.addLayout(form)

        buttons = QHBoxLayout()
        load_btn = QPushButton("Load from PDF")
        load_btn.clicked.connect(self._load_from_pdf)
        buttons.addWidget(load_btn)

        import_btn = QPushButton("Import dump…")
        import_btn.clicked.connect(self._import_dump)
        buttons.addWidget(import_btn)

        export_btn = QPushButton("Export dump…")
        export_btn.clicked.connect(self._export_dump)
        buttons.addWidget(export_btn)

        apply_btn = QPushButton("Apply to PDF")
        apply_btn.clicked.connect(self._apply_to_pdf)
        buttons.addWidget(apply_btn)

        buttons.addStretch()
        layout.addLayout(buttons)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Title", "Page"])
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        layout.addWidget(self.tree, 1)

        editor_row = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.page_edit = QLineEdit()
        self.page_edit.setPlaceholderText("1")
        editor_row.addWidget(QLabel("Title"))
        editor_row.addWidget(self.title_edit)
        editor_row.addWidget(QLabel("Page"))
        editor_row.addWidget(self.page_edit)
        update_btn = QPushButton("Update selected")
        update_btn.clicked.connect(self._update_selected)
        editor_row.addWidget(update_btn)
        add_btn = QPushButton("Add bookmark")
        add_btn.clicked.connect(self._add_bookmark)
        editor_row.addWidget(add_btn)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_selected)
        editor_row.addWidget(remove_btn)
        layout.addLayout(editor_row)

        move_row = QHBoxLayout()
        indent_btn = QPushButton("Indent")
        indent_btn.clicked.connect(lambda: self._adjust_level(1))
        outdent_btn = QPushButton("Outdent")
        outdent_btn.clicked.connect(lambda: self._adjust_level(-1))
        up_btn = QPushButton("Move Up")
        up_btn.clicked.connect(lambda: self._move_selected(-1))
        down_btn = QPushButton("Move Down")
        down_btn.clicked.connect(lambda: self._move_selected(1))
        for btn in (indent_btn, outdent_btn, up_btn, down_btn):
            move_row.addWidget(btn)
        move_row.addStretch()
        layout.addLayout(move_row)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Bookmarks CLI output appears here.")
        layout.addWidget(self.log_view)

    def _with_browse(self, field: QLineEdit, callback, *, save: bool = False) -> QWidget:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(field)
        btn = QPushButton("Browse…")
        btn.clicked.connect(lambda: callback(save))
        row_layout.addWidget(btn)
        return row

    def _append_log(self, message: str) -> None:
        self.log_view.appendPlainText(message)

    def _select_input(self, save: bool = False) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF files (*.pdf)")
        if file_path:
            self.input_field.setText(file_path)
            self.current_pdf = Path(file_path)

    def _select_output(self, save: bool = True) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Select output PDF", filter="PDF files (*.pdf)")
        if file_path:
            self.output_field.setText(file_path)
            self.output_pdf = Path(file_path)

    def _load_from_pdf(self) -> None:
        if not self.input_field.text().strip():
            QMessageBox.information(self, "Bookmarks", "Select an input PDF first.")
            return
        path = Path(self.input_field.text().strip())
        if not path.exists():
            QMessageBox.warning(self, "Bookmarks", f"{path} not found.")
            return
        fd, tmp_path = tempfile.mkstemp(prefix="pdfsuite-bookmarks-", suffix=".txt")
        os.close(fd)
        self._temp_dump = Path(tmp_path)
        command = build_cli_command(
            "bookmarks",
            "dump",
            str(path),
            "-o",
            tmp_path,
        )

        def _finished(code: int, job_dir: Path, tmp=Path(tmp_path)) -> None:
            if code == 0 and tmp.exists():
                text = tmp.read_text(encoding="utf-8", errors="ignore")
                self._populate_tree(parse_dump(text))
            else:
                self._append_log("[bookmarks] Failed to dump bookmarks.")
            if tmp.exists():
                tmp.unlink()

        self.runner.run(
            command,
            self._append_log,
            _finished,
            job_name="bookmarks-dump",
        )

    def _populate_tree(self, nodes: list[BookmarkNode]) -> None:
        self.tree.clear()
        for node in nodes:
            self.tree.addTopLevelItem(self._node_to_item(node))
        self.tree.expandToDepth(1)

    def _node_to_item(self, node: BookmarkNode) -> QTreeWidgetItem:
        item = QTreeWidgetItem([node.title, str(node.page)])
        item.setData(0, Qt.UserRole, node)
        for child in node.children:
            item.addChild(self._node_to_item(child))
        return item

    def _item_to_node(self, item: QTreeWidgetItem, level: int) -> BookmarkNode:
        node = BookmarkNode(
            title=item.text(0),
            level=level,
            page=int(item.text(1) or 1),
        )
        for idx in range(item.childCount()):
            child = item.child(idx)
            node.children.append(self._item_to_node(child, level + 1))
        return node

    def _selected_item(self) -> QTreeWidgetItem | None:
        items = self.tree.selectedItems()
        return items[0] if items else None

    def _update_selected(self) -> None:
        item = self._selected_item()
        if not item:
            return
        title = self.title_edit.text().strip()
        page = self.page_edit.text().strip()
        if title:
            item.setText(0, title)
        if page.isdigit():
            item.setText(1, page)

    def _add_bookmark(self) -> None:
        title = self.title_edit.text().strip() or "Untitled"
        page = self.page_edit.text().strip() or "1"
        new_item = QTreeWidgetItem([title, page])
        target = self._selected_item()
        if target:
            target.addChild(new_item)
            target.setExpanded(True)
        else:
            self.tree.addTopLevelItem(new_item)

    def _remove_selected(self) -> None:
        item = self._selected_item()
        if not item:
            return
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            idx = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(idx)

    def _adjust_level(self, delta: int) -> None:
        item = self._selected_item()
        if not item:
            return
        parent = item.parent()
        if delta > 0 and parent is not None:
            # indent as child of previous sibling
            index = parent.indexOfChild(item)
            if index > 0:
                new_parent = parent.child(index - 1)
                parent.removeChild(item)
                new_parent.addChild(item)
                new_parent.setExpanded(True)
        elif delta < 0 and parent is not None:
            grand = parent.parent()
            parent.removeChild(item)
            if grand:
                grand.addChild(item)
            else:
                self.tree.addTopLevelItem(item)

    def _move_selected(self, delta: int) -> None:
        item = self._selected_item()
        if not item:
            return
        parent = item.parent()
        if parent:
            siblings = parent
            idx = parent.indexOfChild(item)
            new_idx = max(0, min(parent.childCount() - 1, idx + delta))
            parent.takeChild(idx)
            parent.insertChild(new_idx, item)
        else:
            idx = self.tree.indexOfTopLevelItem(item)
            new_idx = max(0, min(self.tree.topLevelItemCount() - 1, idx + delta))
            self.tree.takeTopLevelItem(idx)
            self.tree.insertTopLevelItem(new_idx, item)

    def _import_dump(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Import bookmarks", filter="Text files (*.txt)")
        if not file_path:
            return
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        self._populate_tree(parse_dump(text))

    def _export_dump(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Export bookmarks", filter="Text files (*.txt)")
        if not file_path:
            return
        nodes = self._collect_nodes()
        Path(file_path).write_text(serialize_nodes(nodes), encoding="utf-8")

    def _collect_nodes(self) -> list[BookmarkNode]:
        nodes: list[BookmarkNode] = []
        for idx in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(idx)
            nodes.append(self._item_to_node(item, 1))
        return nodes

    def _apply_to_pdf(self) -> None:
        if not self.input_field.text().strip() or not self.output_field.text().strip():
            QMessageBox.information(self, "Bookmarks", "Select input and output paths first.")
            return
        nodes = self._collect_nodes()
        fd, tmp_path = tempfile.mkstemp(prefix="pdfsuite-bookmarks-", suffix=".txt")
        os.close(fd)
        tmp = Path(tmp_path)
        tmp.write_text(serialize_nodes(nodes), encoding="utf-8")

        command = build_cli_command(
            "bookmarks",
            "apply",
            self.input_field.text().strip(),
            tmp_path,
            "-o",
            self.output_field.text().strip(),
        )

        def _finished(code: int, job_dir: Path, temp_file: Path = tmp) -> None:
            if code == 0:
                self._append_log(f"[bookmarks] Applied successfully (logs: {job_dir})")
            else:
                self._append_log("[bookmarks] Failed to apply bookmarks.")
            if temp_file.exists():
                temp_file.unlink()

        self.runner.run(
            command,
            self._append_log,
            _finished,
            job_name="bookmarks-apply",
        )
