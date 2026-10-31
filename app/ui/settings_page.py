
from PySide6.QtCore import Signal, Qt, QThread
from PySide6.QtWidgets import (
    QLineEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)
from PySide6.QtCore import QSize

from app.ui.icons import safe_icon


class ConnectionTestWorker(QThread):
    result = Signal(bool, str)

    def run(self):
        try:
            from app.ai_service import test_connection

            test_connection()
            self.result.emit(True, "اتصال برقرار است و کلید معتبر است.")
        except Exception as error:
            self.result.emit(False, f"اتصال ناموفق بود: {error}")


class SettingsPage(QWidget):
    theme_changed = Signal(str)
    api_settings_saved = Signal()

    def __init__(self):
        super().__init__()

        self.current_theme = "light"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)

        title = QLabel("تنظیمات")
        title.setObjectName("heroTitle")
        layout.addWidget(title)

        subtitle = QLabel("ظاهر برنامه را مطابق سلیقه خودت تنظیم کن.")
        subtitle.setProperty("muted", True)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        layout.addWidget(self.build_api_card())

        card = QFrame()
        card.setObjectName("surface")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(14)

        section_title = QLabel("ظاهر برنامه")
        section_title.setObjectName("cardTitle")
        card_layout.addWidget(section_title)

        description = QLabel("تم موردنظرت را انتخاب کن.")
        description.setProperty("muted", True)
        card_layout.addWidget(description)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.light_button = QPushButton("  تم روشن")
        self.dark_button = QPushButton("  تم تاریک")
        self.light_button.setIcon(safe_icon("ph.sun", "#F59E0B"))
        self.dark_button.setIcon(safe_icon("ph.moon", "#6366F1"))

        for button in (self.light_button, self.dark_button):
            button.setObjectName("themeOption")
            button.setIconSize(QSize(22, 22))
            button.setMinimumHeight(64)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)
            buttons_layout.addWidget(button)

        card_layout.addLayout(buttons_layout)
        layout.addWidget(card)
        layout.addStretch()

        self.light_button.clicked.connect(
            lambda: self.select_theme("light")
        )
        self.dark_button.clicked.connect(
            lambda: self.select_theme("dark")
        )

        self.update_buttons()

    # ----- API key ------------------------------------------------------

    def build_api_card(self):
        from app.config import get_api_key, get_base_url

        card = QFrame()
        card.setObjectName("surface")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(12)

        title = QLabel("اتصال به هوش مصنوعی")
        title.setObjectName("cardTitle")
        card_layout.addWidget(title)

        description = QLabel(
            "کلید API سرویس را وارد کن تا ZaCh به آن وصل شود. "
            "کلید فقط روی همین کامپیوتر ذخیره می‌شود."
        )
        description.setProperty("muted", True)
        description.setWordWrap(True)
        card_layout.addWidget(description)

        key_label = QLabel("کلید API")
        card_layout.addWidget(key_label)

        key_row = QHBoxLayout()
        key_row.setSpacing(8)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setText(get_api_key())
        self.api_key_input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.api_key_input.setMinimumHeight(44)

        self.show_key_button = QPushButton("نمایش")
        self.show_key_button.setCheckable(True)
        self.show_key_button.setProperty("centered", True)
        self.show_key_button.setMinimumHeight(44)
        self.show_key_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_key_button.toggled.connect(self.toggle_key_visibility)

        key_row.addWidget(self.api_key_input, 1)
        key_row.addWidget(self.show_key_button)
        card_layout.addLayout(key_row)

        url_label = QLabel("آدرس سرویس (اختیاری)")
        card_layout.addWidget(url_label)

        self.base_url_input = QLineEdit()
        self.base_url_input.setText(get_base_url())
        self.base_url_input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.base_url_input.setMinimumHeight(44)
        card_layout.addWidget(self.base_url_input)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        self.test_button = QPushButton("آزمایش اتصال")
        self.test_button.setObjectName("dialogSecondary")
        self.test_button.setMinimumHeight(44)
        self.test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_button.clicked.connect(self.test_api_connection)

        self.save_api_button = QPushButton("ذخیره")
        self.save_api_button.setProperty("primary", True)
        self.save_api_button.setProperty("centered", True)
        self.save_api_button.setMinimumHeight(44)
        self.save_api_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_api_button.clicked.connect(self.save_api_settings)

        buttons.addWidget(self.test_button, 1)
        buttons.addWidget(self.save_api_button, 1)
        card_layout.addLayout(buttons)

        self.api_status_label = QLabel("")
        self.api_status_label.setWordWrap(True)
        self.api_status_label.setProperty("muted", True)
        card_layout.addWidget(self.api_status_label)

        return card

    def toggle_key_visibility(self, visible):
        self.api_key_input.setEchoMode(
            QLineEdit.EchoMode.Normal
            if visible
            else QLineEdit.EchoMode.Password
        )
        self.show_key_button.setText("پنهان" if visible else "نمایش")

    def set_api_status(self, text, state="muted"):
        self.api_status_label.setText(text)
        self.api_status_label.setProperty("muted", state == "muted")
        color = {"ok": "#22A06B", "error": "#EF4444"}.get(state)
        self.api_status_label.setStyleSheet(
            f"color: {color};" if color else ""
        )
        self.style().unpolish(self.api_status_label)
        self.style().polish(self.api_status_label)

    def save_api_settings(self):
        from app.config import save_api_settings

        save_api_settings(
            self.api_key_input.text(),
            self.base_url_input.text(),
        )
        self.set_api_status("تنظیمات ذخیره شد.", "ok")
        self.api_settings_saved.emit()

    def test_api_connection(self):
        # قبل از آزمایش، مقدارهای فعلی فرم ذخیره می‌شوند.
        self.save_api_settings()
        self.test_button.setEnabled(False)
        self.set_api_status("در حال آزمایش اتصال...")

        self.test_worker = ConnectionTestWorker()
        self.test_worker.result.connect(self.on_test_result)
        self.test_worker.finished.connect(
            lambda: self.test_button.setEnabled(True)
        )
        self.test_worker.start()

    def on_test_result(self, ok, message):
        self.set_api_status(message, "ok" if ok else "error")

    def select_theme(self, theme):
        if theme not in ("light", "dark"):
            return

        self.current_theme = theme
        self.update_buttons()
        self.theme_changed.emit(theme)

    def update_buttons(self):
        self.light_button.setChecked(self.current_theme == "light")
        self.dark_button.setChecked(self.current_theme == "dark")

        self.light_button.setProperty(
            "active", self.current_theme == "light"
        )
        self.dark_button.setProperty(
            "active", self.current_theme == "dark"
        )

        for button in (self.light_button, self.dark_button):
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
