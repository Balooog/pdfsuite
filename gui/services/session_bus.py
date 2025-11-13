from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class SessionBus(QObject):
    session_shared = Signal(object)
    session_committed = Signal(object)

    def share(self, session):
        self.session_shared.emit(session)

    def announce_commit(self, session):
        self.session_committed.emit(session)


_bus: SessionBus | None = None


def get_session_bus() -> SessionBus:
    global _bus
    if _bus is None:
        _bus = SessionBus()
    return _bus
