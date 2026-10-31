import socket
from pathlib import Path

from PySide6.QtCore import (
    QObject,
    QRunnable,
    QThreadPool,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.config import get_base_host
from app.ui.icons import safe_icon

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"

# اگر به هرکدام از این‌ها وصل شویم، شبکه برقرار است.
FALLBACK_TARGETS = (("1.1.1.1", 443), ("8.8.8.8", 53))


def is_online(timeout=2.5):
    targets = [get_base_host(), *FALLBACK_TARGETS]

    for host, port in targets:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue

    return False


class _CheckSignals(QObject):
    done = Signal(bool)


class _CheckTask(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = _CheckSignals()

    def run(self):
        try:
            result = is_online()
        except Exception:
            result = False
        self.signals.done.emit(result)


class NetworkMonitor(QObject):
    """هر چند ثانیه اتصال شبکه را در پس‌زمینه بررسی می‌کند."""

    status_changed = Signal(bool)   # True = آنلاین

    FAILURES_BEFORE_OFFLINE = 2     # یک خطای لحظه‌ای صفحه را قطع نکند

    def __init__(self, interval_ms=5000, parent=None):
        super().__init__(parent)
        self.online = True
        self._failures = 0
        self._busy = False
        self._tasks = set()

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.check_now)

    def start(self):
        self._timer.start()
        self.check_now()

    def check_now(self):
        if self._busy:
            return

        self._busy = True
        task = _CheckTask()
        self._tasks.add(task)  # تا پایان کار زنده بماند
        task.signals.done.connect(
            lambda ok, t=task: self._on_result(ok, t)
        )
        QThreadPool.globalInstance().start(task)

    def _on_result(self, ok, task):
        self._busy = False
        self._tasks.discard(task)

        if ok:
            self._failures = 0
            new_state = True
        else:
            self._failures += 1
            new_state = (
                False
                if self._failures >= self.FAILURES_BEFORE_OFFLINE
                else self.online
            )

        if new_state != self.online:
            self.online = new_state
            self.status_changed.emit(new_state)

        # در حالت قطع، سریع‌تر بررسی کن
        if not ok and self.online:
            QTimer.singleShot(1200, self.check_now)


class OfflinePage(QWidget):
    """صفحه‌ی خالی با تصویر noWiFi و پیام قطع اتصال."""

    retry_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("offlinePage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)
        layout.addStretch(1)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_image()
        layout.addWidget(self.image_label)

        title = QLabel("ارتباط با شبکه قطع شده است")
        title.setObjectName("offlineTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        hint = QLabel(
            "اتصال اینترنت خود را بررسی کن. به‌محض برقراری دوباره‌ی اتصال، "
            "برنامه خودکار ادامه می‌دهد."
        )
        hint.setProperty("muted", True)
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        self.retry_button = QPushButton("تلاش دوباره")
        self.retry_button.setProperty("primary", True)
        self.retry_button.setProperty("centered", True)
        self.retry_button.setMinimumHeight(42)
        self.retry_button.setFixedWidth(180)
        self.retry_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.retry_button.clicked.connect(self.retry_requested.emit)
        layout.addWidget(self.retry_button, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

    def _find_image(self):
        for folder in (ASSETS_DIR, ASSETS_DIR / "images"):
            if not folder.is_dir():
                continue
            for file in folder.iterdir():
                if file.name.lower() == "nowifi.png":
                    return file
        return None

    def _load_image(self):
        image_path = self._find_image()
        pixmap = QPixmap(str(image_path)) if image_path else QPixmap()

        if pixmap.isNull():
            pixmap = safe_icon("ph.wifi-slash", "#94A3B8").pixmap(160, 160)
        else:
            pixmap = pixmap.scaled(
                280,
                280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.image_label.setPixmap(pixmap)
