"""Panel widgets for the GUI shell."""

from .dashboard import DashboardPanel
from .ocr_optimize import OcrOptimizePanel
from .pages import PagesPanel
from .reader import ReaderPanel
from .bookmarks import BookmarksPanel
from .forms import FormsPanel
from .compare import ComparePanel
from .redact import RedactPanel
from .sign import SignPanel
from .settings import SettingsPanel
from .three_d import ThreeDPanel
from .automation import AutomationPanel

__all__ = [
    "DashboardPanel",
    "ReaderPanel",
    "BookmarksPanel",
    "OcrOptimizePanel",
    "PagesPanel",
    "FormsPanel",
    "ComparePanel",
    "RedactPanel",
    "SignPanel",
    "SettingsPanel",
    "ThreeDPanel",
    "AutomationPanel",
]
