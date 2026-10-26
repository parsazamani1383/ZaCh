
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.current_theme = "light"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(20)

        title = QLabel("تنظیمات")
        title.setStyleSheet("font-size: 24pt; font-weight: 700;")
        layout.addWidget(title)

        subtitle = QLabel("ظاهر برنامه را مطابق سلیقه خودت تنظیم کن.")
        subtitle.setProperty("muted", True)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        card = QFrame()
        card.setObjectName("surface")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(14)

        section_title = QLabel("ظاهر برنامه")
        section_title.setStyleSheet("font-size: 14pt; font-weight: 600;")
        card_layout.addWidget(section_title)

        description = QLabel("تم موردنظرت را انتخاب کن.")
        description.setProperty("muted", True)
        card_layout.addWidget(description)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.light_button = QPushButton("☀  تم روشن")
        self.dark_button = QPushButton("☾  تم تاریک")

        for button in (self.light_button, self.dark_button):
            button.setMinimumHeight(46)
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
