from __future__ import annotations

import shlex
import subprocess
import sys
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence

from PySide6.QtCore import QObject, QThread, Signal, Slot, QProcess


def build_cli_command(*parts: str) -> list[str]:
    """Return a `python -m pdfsuite ...` invocation for the given parts."""
    executable = sys.executable or "python3"
    return [executable, "-m", "pdfsuite", *parts]


@dataclass
class Job:
    command: list[str]
    on_output: Callable[[str], None]
    on_finished: Callable[[int, Path], None]
    cwd: Path | None
    job_name: str


class CommandWorker(QObject):
    output = Signal(str)
    started = Signal(str)
    finished = Signal(int)
    error = Signal(str)

    def __init__(
        self,
        command: Sequence[str],
        cwd: Path | None = None,
        log_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.command = list(command)
        self.cwd = cwd
        self.log_path = log_path

    @Slot()
    def run(self) -> None:
        rendered = self.render_command()
        self.started.emit(rendered)
        log_file = None
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            log_file = self.log_path.open("w", encoding="utf-8")
            log_file.write(f"$ {rendered}\n")
        try:
            process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        except OSError as exc:
            message = f"Failed to start command: {exc}"
            self.error.emit(message)
            if log_file:
                log_file.write(f"{message}\n")
            self.finished.emit(1)
            if log_file:
                log_file.close()
            return

        assert process.stdout is not None  # for mypy/static checking
        for line in process.stdout:
            clean = line.rstrip()
            self.output.emit(clean)
            if log_file:
                log_file.write(f"{clean}\n")
        exit_code = process.wait()
        if log_file:
            log_file.write(f"[runner] exit {exit_code}\n")
            log_file.close()
        self.finished.emit(exit_code)

    def render_command(self) -> str:
        return " ".join(shlex.quote(part) for part in self.command)


class Runner(QObject):
    """Dispatch CLI commands on background threads, with queue + log files."""
    watch_output = Signal(str)
    job_finished = Signal(object, object, object, object, int)

    def __init__(self) -> None:
        super().__init__()
        self._queue: deque[Job] = deque()
        self._current: tuple[QThread, CommandWorker] | None = None
        self._build_root = Path.home() / "pdfsuite" / "build"
        self._build_root.mkdir(parents=True, exist_ok=True)
        self._watch_process: QProcess | None = None
        self.job_finished.connect(self._handle_job_finished)

    def start_watch(
        self,
        settings,
    ) -> None:
        """Start a background `pdfsuite watch` process if enabled."""
        self.stop_watch()
        if not settings.watch_enabled:
            self.watch_output.emit("[watch] disabled.")
            return
        args = [
            sys.executable,
            "-m",
            "pdfsuite",
            "watch",
            "--preset",
            settings.watch_preset,
        ]
        if settings.watch_folder:
            folder = Path(settings.watch_folder)
            folder.mkdir(parents=True, exist_ok=True)
            args.extend(["--path", str(folder)])
        if settings.watch_target_size:
            args.extend(["--target-size", str(settings.watch_target_size)])
        self.watch_output.emit(f"[watch] launching preset '{settings.watch_preset}'")
        process = QProcess(self)
        process.setProgram(sys.executable)
        process.setArguments(args[1:])
        process.readyReadStandardOutput.connect(
            lambda: self._emit_process_output(process)
        )
        process.finished.connect(self._handle_watch_finished)
        process.start()
        self._watch_process = process

    def stop_watch(self) -> None:
        if self._watch_process:
            self._watch_process.terminate()
            self._watch_process.waitForFinished(2000)
            self._watch_process = None

    def run(
        self,
        command: Sequence[str],
        on_output: Callable[[str], None],
        on_finished: Callable[[int, Path], None],
        *,
        cwd: Path | None = None,
        job_name: str | None = None,
    ) -> None:
        job = Job(
            command=list(command),
            on_output=on_output,
            on_finished=on_finished,
            cwd=cwd,
            job_name=job_name or "job",
        )
        self._queue.append(job)
        if self._current is None:
            self._start_next()

    def _start_next(self) -> None:
        if not self._queue:
            self._current = None
            return
        job = self._queue.popleft()
        job_dir = self._create_job_dir(job.job_name)
        log_path = job_dir / "command.log"

        worker = CommandWorker(job.command, cwd=job.cwd, log_path=log_path)
        thread = QThread()
        worker.moveToThread(thread)

        worker.output.connect(job.on_output)
        worker.error.connect(job.on_output)

        worker.finished.connect(
            lambda code, job=job, job_dir=job_dir, thread=thread, worker_obj=worker: self.job_finished.emit(
                job, job_dir, thread, worker_obj, code
            )
        )
        thread.started.connect(worker.run)

        self._current = (thread, worker)
        thread.start()

    def _create_job_dir(self, job_name: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in job_name.lower())
        slug = slug.strip("-_") or "job"
        candidate = self._build_root / f"{timestamp}-{slug}"
        counter = 1
        while candidate.exists():
            candidate = self._build_root / f"{timestamp}-{slug}-{counter}"
            counter += 1
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate

    def _emit_process_output(self, process: QProcess) -> None:
        data = process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        for line in data.splitlines():
            self.watch_output.emit(line.rstrip())

    def _handle_watch_finished(self, code: int, _status: QProcess.ExitStatus) -> None:
        self.watch_output.emit(f"[watch] exited ({code}).")
        self._watch_process = None

    @Slot(object, object, object, object, int)
    def _handle_job_finished(
        self,
        job: Job,
        job_dir: Path,
        thread: QThread,
        worker: CommandWorker,
        exit_code: int,
    ) -> None:
        try:
            job.on_finished(exit_code, job_dir)
        finally:
            thread.quit()
            thread.wait()
            worker.deleteLater()
            thread.deleteLater()
            self._current = None
            self._start_next()
