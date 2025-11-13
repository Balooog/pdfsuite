from __future__ import annotations

import argparse
import sys

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSplitter,
    QStackedWidget,
)

from gui.panels import (
    DashboardPanel,
    ReaderPanel,
    BookmarksPanel,
    FormsPanel,
    ComparePanel,
    OcrOptimizePanel,
    PagesPanel,
    RedactPanel,
    SignPanel,
    AutomationPanel,
    SettingsPanel,
    ThreeDPanel,
)
from gui.services import Runner, SettingsStore, build_cli_command, get_session_bus


class MainWindow(QMainWindow):
    status_requested = Signal(str, int)
    """Primary window with sidebar navigation and stacked panels."""

    def __init__(self, *, test_mode: bool = False) -> None:
        super().__init__()
        self.setWindowTitle("pdfsuite GUI MVP")
        self.resize(1280, 800)

        self.runner = Runner()
        self.settings = SettingsStore()
        self.session_bus = get_session_bus()
        self._panels: list[tuple[str, object]] = []

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.nav = QListWidget()
        self.nav.setMinimumWidth(220)
        splitter.addWidget(self.nav)

        self.stack = QStackedWidget()
        splitter.addWidget(self.stack)

        panel_definitions = [
            ("Dashboard", lambda: DashboardPanel(self.runner)),
            ("Reader", lambda: ReaderPanel(self.runner, self.settings, self.session_bus)),
            ("Bookmarks", lambda: BookmarksPanel(self.runner, self.settings)),
            ("Pages", lambda: PagesPanel(self.runner, self.session_bus)),
            ("Forms", lambda: FormsPanel(self.runner)),
            ("Compare", lambda: ComparePanel(self.runner)),
            ("OCR / Optimize", lambda: OcrOptimizePanel(self.runner)),
            ("3D Viewer", lambda: ThreeDPanel(self.runner)),
            ("Redact", lambda: RedactPanel(self.runner)),
            ("Sign", lambda: SignPanel(self.runner)),
            ("Automation", lambda: AutomationPanel(self.runner, self.settings)),
            ("Settings", lambda: SettingsPanel(self.settings, self._restart_watch)),
        ]

        for idx, (name, factory) in enumerate(panel_definitions):
            item = QListWidgetItem(name)
            self.nav.addItem(item)
            panel = factory()
            self.stack.addWidget(panel)
            self._panels.append((name, panel))
            if idx == 0:
                self.stack.setCurrentWidget(panel)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        status_bar = self.statusBar()
        self.status_requested.connect(status_bar.showMessage)
        self.status_requested.emit("Ready", 0)
        self._test_mode = test_mode
        if self.settings.data.run_doctor_on_launch and not self._test_mode:
            self._queue_doctor_check()

        self.runner.watch_output.connect(self._watch_log)
        if not self._test_mode:
            QTimer.singleShot(0, self._start_watch_if_enabled)
        self.session_bus.session_shared.connect(self._handle_session_share)

    def _queue_doctor_check(self) -> None:
        command = build_cli_command("doctor")

        def _log(message: str) -> None:
            self.status_requested.emit(message, 5000)

        def _finished(code: int, job_dir: Path) -> None:
            status = "Doctor OK" if code == 0 else "Doctor reported issues"
            self.status_requested.emit(f"{status} (logs: {job_dir})", 10000)

        self.runner.run(command, lambda line: None, _finished, job_name="doctor")

    def _watch_log(self, line: str) -> None:
        dashboard = self._get_panel("Dashboard")
        if dashboard and hasattr(dashboard, "append_watch_log"):
            dashboard.append_watch_log(line)

    def _restart_watch(self) -> None:
        self._start_watch_if_enabled()
        self._refresh_automation_panel()

    def _get_panel(self, name: str):
        for panel_name, widget in self._panels:
            if panel_name == name:
                return widget
        return None

    def _focus_panel(self, name: str) -> None:
        for idx, (panel_name, _) in enumerate(self._panels):
            if panel_name == name:
                self.nav.setCurrentRow(idx)
                return

    def _refresh_automation_panel(self) -> None:
        panel = self._get_panel("Automation")
        if panel and hasattr(panel, "refresh"):
            panel.refresh()

    def _start_watch_if_enabled(self) -> None:
        if self._test_mode:
            return
        if self.settings.data.watch_enabled:
            self.runner.start_watch(self.settings.data)
        else:
            self.runner.stop_watch()

    def _handle_session_share(self, session) -> None:
        pages = self._get_panel("Pages")
        if pages and hasattr(pages, "attach_session"):
            pages.attach_session(session)
            self._focus_panel("Pages")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the pdfsuite GUI shell.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Initialize the Qt application and exit (used for smoke tests).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    qt_args = [sys.argv[0]]
    app = QApplication(qt_args)
    window = MainWindow(test_mode=args.check)

    if args.check:
        # Process a few events to ensure widgets wire up, then exit cleanly.
        app.processEvents()
        window.runner.stop_watch()
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
