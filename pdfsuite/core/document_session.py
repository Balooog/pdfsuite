from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Sequence


@dataclass
class DocumentSession:
    path: Path
    page_order: List[int]
    selection: set[int] = field(default_factory=set)
    _undo: List[List[int]] = field(default_factory=list, init=False)
    _redo: List[List[int]] = field(default_factory=list, init=False)
    _max_history: int = 20
    dirty: bool = field(default=False, init=False)

    def reorder(self, indices: Sequence[int], new_pos: int) -> None:
        normalized = self._normalize_indices(indices)
        if not normalized:
            return
        self._push_undo()
        selected = [self.page_order[i] for i in normalized]
        remaining = [p for idx, p in enumerate(self.page_order) if idx not in normalized]
        clamped_pos = max(0, min(new_pos, len(remaining)))
        self.page_order = remaining[:clamped_pos] + selected + remaining[clamped_pos:]
        self._redo.clear()
        self.dirty = True

    def rotate(self, indices: Sequence[int], angle: int) -> None:
        if angle % 90 != 0:
            raise ValueError("Rotation must be a multiple of 90 degrees.")
        normalized = self._normalize_indices(indices)
        if not normalized:
            return
        self._push_undo()
        # rotation metadata stored elsewhere (placeholder)
        self._redo.clear()
        self.dirty = True

    def delete(self, indices: Sequence[int]) -> None:
        normalized = self._normalize_indices(indices)
        if not normalized:
            return
        self._push_undo()
        to_drop = {self.page_order[i] for i in normalized}
        self.page_order = [p for p in self.page_order if p not in to_drop]
        self.selection.difference_update(to_drop)
        self._redo.clear()
        self.dirty = True

    def set_order(self, new_order: Sequence[int]) -> None:
        if sorted(new_order) != sorted(self.page_order):
            raise ValueError("New order must contain the same pages.")
        self._push_undo()
        self.page_order = list(new_order)
        self._redo.clear()
        self.dirty = True

    def commit(
        self,
        runner,
        output_path: Path | None = None,
        *,
        job_name: str = "reader-save",
        on_output: Callable[[str], None] | None = None,
        on_finished: Callable[[int, Path], None] | None = None,
    ) -> None:
        dest = output_path or self._default_output_path()
        command = self._build_cli_command(dest)
        def _finished(code: int, job_dir: Path) -> None:
            if code == 0:
                self.dirty = False
            if on_finished:
                on_finished(code, job_dir)

        runner.run(
            command,
            on_output or (lambda line: None),
            _finished,
            job_name=job_name,
        )

    def undo(self) -> None:
        if not self._undo:
            return
        self._redo.append(self.page_order.copy())
        self.page_order = self._undo.pop()

    def redo(self) -> None:
        if not self._redo:
            return
        self._undo.append(self.page_order.copy())
        self.page_order = self._redo.pop()

    def _push_undo(self) -> None:
        self._undo.append(self.page_order.copy())
        if len(self._undo) > self._max_history:
            self._undo.pop(0)

    def _normalize_indices(self, indices: Sequence[int]) -> List[int]:
        normalized = sorted(set(i for i in indices if 0 <= i < len(self.page_order)))
        return normalized

    def _build_cli_command(self, destination: Path) -> list[str]:
        order_spec = ",".join(str(number) for number in self.page_order)
        executable = sys.executable or "python3"
        return [
            executable,
            "-m",
            "pdfsuite",
            "reorder",
            str(self.path),
            "--order",
            order_spec,
            "-o",
            str(destination),
        ]

    def _default_output_path(self) -> Path:
        build_root = Path.home() / "pdfsuite" / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        folder = build_root / f"{timestamp}-reader"
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{self.path.stem}-session.pdf"
