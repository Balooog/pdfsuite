from __future__ import annotations

from typing import Sequence

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.panels.base import CommandPanel
from pdfsuite.core.document_session import DocumentSession


class PagesPanel(CommandPanel):
    """Merge, split, or reorder PDFs via qpdf helpers."""

    def __init__(self, runner, session_bus=None) -> None:
        super().__init__(
            runner,
            title="Pages",
            description="Manage PDF pages (merge, split ranges, reorder) before sending files "
            "through downstream workflows.",
        )
        self.session_bus = session_bus
        self.session: DocumentSession | None = None

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
        self._build_session_box()
        if self.session_bus:
            self.session_bus.session_shared.connect(self.attach_session)

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

    # ------------------------------------------------------------------ Live session bridge
    def _build_session_box(self) -> None:
        self.session_box = QGroupBox("Live Reader session")
        session_layout = QFormLayout(self.session_box)

        self.session_info = QLabel("No session attached. Use Reader → Open in Pages.")
        session_layout.addRow(self.session_info)

        self.session_order_edit = QLineEdit()
        session_layout.addRow("Page order", self.session_order_edit)
        apply_row = QHBoxLayout()
        self.session_apply_button = QPushButton("Apply order")
        self.session_apply_button.clicked.connect(self._apply_session_order)
        apply_row.addWidget(self.session_apply_button)
        self.session_refresh_button = QPushButton("Refresh")
        self.session_refresh_button.clicked.connect(self._refresh_session_fields)
        apply_row.addWidget(self.session_refresh_button)
        session_layout.addRow(apply_row)

        self.bates_prefix_edit = QLineEdit()
        self.bates_prefix_edit.setPlaceholderText("e.g., BN")
        self.bates_start_edit = QLineEdit()
        self.bates_start_edit.setPlaceholderText("1001")
        bates_row = QHBoxLayout()
        bates_row.addWidget(self.bates_prefix_edit)
        bates_row.addWidget(self.bates_start_edit)
        session_layout.addRow("Bates preview", bates_row)
        self.bates_preview = QLabel("Sample: —")
        session_layout.addRow(self.bates_preview)
        self.bates_prefix_edit.textChanged.connect(self._update_bates_preview)
        self.bates_start_edit.textChanged.connect(self._update_bates_preview)

        self.crop_input = QLineEdit()
        self.crop_input.setPlaceholderText("x,y,w,h (points) — not yet applied")
        session_layout.addRow("Crop box", self.crop_input)

        action_row = QHBoxLayout()
        self.session_save_button = QPushButton("Save")
        self.session_save_button.clicked.connect(lambda: self._save_live_session(False))
        action_row.addWidget(self.session_save_button)
        self.session_save_as_button = QPushButton("Save As…")
        self.session_save_as_button.clicked.connect(lambda: self._save_live_session(True))
        action_row.addWidget(self.session_save_as_button)
        self.session_detach_button = QPushButton("Detach")
        self.session_detach_button.clicked.connect(self._detach_session)
        action_row.addWidget(self.session_detach_button)
        session_layout.addRow(action_row)

        layout_obj = self.layout()
        if isinstance(layout_obj, QVBoxLayout):
            layout_obj.insertWidget(2, self.session_box)
        self.session_box.setEnabled(False)

    def attach_session(self, session: DocumentSession) -> None:
        self.session = session
        self.session_box.setEnabled(True)
        self._refresh_session_fields()
        self.append_log(f"[pages] Attached Reader session for {session.path}")

    def _detach_session(self) -> None:
        self.session = None
        self.session_box.setEnabled(False)
        self.session_info.setText("No session attached. Use Reader → Open in Pages.")
        self.session_order_edit.clear()

    def _refresh_session_fields(self) -> None:
        if not self.session:
            return
        self.session_info.setText(
            f"{self.session.path.name} — {len(self.session.page_order)} pages"
        )
        self.session_order_edit.setText(",".join(str(n) for n in self.session.page_order))
        self._update_bates_preview()

    def _apply_session_order(self) -> None:
        if not self.session:
            self.append_log("[pages] No session attached.")
            return
        raw = self.session_order_edit.text().strip()
        if not raw:
            self.append_log("[pages] Provide a comma-separated page order.")
            return
        try:
            new_order = [int(token.strip()) for token in raw.split(",") if token.strip()]
        except ValueError:
            self.append_log("[pages] Invalid order string.")
            return
        try:
            self.session.set_order(new_order)
            self.append_log("[pages] Updated session page order.")
        except ValueError as exc:
            self.append_log(f"[pages] {exc}")

    def _save_live_session(self, save_as: bool) -> None:
        if not self.session:
            self.append_log("[pages] No session attached.")
            return
        destination: Path | None = None
        if save_as:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save session as…",
                str(self.session.path.with_name(f"{self.session.path.stem}_pages.pdf")),
                "PDF files (*.pdf)",
            )
            if not path:
                return
            destination = Path(path)

        def _finished(code: int, job_dir: Path) -> None:
            status = "saved" if code == 0 else "failed"
            self.append_log(f"[pages] Session {status} (logs: {job_dir})")
            if code == 0 and self.session_bus:
                self.session_bus.announce_commit(self.session)

        self.session.commit(
            self.runner,
            output_path=destination,
            job_name="pages-session",
            on_output=self.append_log,
            on_finished=_finished,
        )

    def _update_bates_preview(self) -> None:
        prefix = self.bates_prefix_edit.text().strip()
        start = self.bates_start_edit.text().strip()
        if not prefix or not start.isdigit():
            self.bates_preview.setText("Sample: —")
            return
        self.bates_preview.setText(f"Sample: {prefix}:{start.zfill(4)}")
