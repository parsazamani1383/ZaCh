import qtawesome as qta
import sys
from app.ui.conversations_page import ConversationsPage
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
    QStyle,
QInputDialog,
)
from PySide6.QtGui import QPixmap
from app.database import (
    create_conversation,
    delete_conversation,
)
from app.ui.styles import get_stylesheet
from app.ui.home_page import HomePage
from app.ui.chats_page import ChatsPage
from app.ui.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_theme = "light"
        self.logo_label = None

        self.setWindowTitle("ZaCh")
        self.resize(1100, 720)
        self.setMinimumSize(850, 560)

        self.setStyleSheet(get_stylesheet(self.current_theme))

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 22, 16, 18)
        sidebar_layout.setSpacing(10)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.logo_label.setFixedHeight(65)

        sidebar_layout.addWidget(self.logo_label)
        self.update_logo()

        tagline = QLabel("دستیار هوشمند اسناد")
        tagline.setProperty("muted", True)
        sidebar_layout.addWidget(tagline)

        sidebar_layout.addSpacing(24)

        self.home_button = self.make_nav_button(
            " خانه ", "ph.house"
        )
        self.chats_button = self.make_nav_button(
            " چت‌ها ", "ph.chats"
        )
        self.settings_button = self.make_nav_button(
            " تنظیمات ", "ph.sliders-horizontal"
        )

        sidebar_layout.addWidget(self.home_button)
        sidebar_layout.addWidget(self.chats_button)
        sidebar_layout.addWidget(self.settings_button)
        sidebar_layout.addStretch()

        # Main content
        self.pages = QStackedWidget()

        self.home_page = HomePage()
        self.conversations_page = ConversationsPage()
        self.chats_page = ChatsPage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(self.home_page)  # index 0
        self.pages.addWidget(self.conversations_page)  # index 1
        self.pages.addWidget(self.chats_page)  # index 2
        self.pages.addWidget(self.settings_page)  # index 3

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.pages, 1)

        self.home_button.clicked.connect(lambda: self.navigate(0))
        self.chats_button.clicked.connect(lambda: self.navigate(1))
        self.settings_button.clicked.connect(lambda: self.navigate(3))

        # Settings page will notify this window when theme changes.
        if hasattr(self.settings_page, "theme_changed"):
            self.settings_page.theme_changed.connect(self.set_theme)

        self.active_documents = {}

        self.active_conversation_id = None

        self.home_page.start_chat_requested.connect(
            self.start_chat_with_documents
        )

        self.conversations_page.new_conversation_requested.connect(
            self.create_new_conversation
        )

        self.conversations_page.conversation_selected.connect(
            self.open_conversation
        )

        self.conversations_page.delete_conversation_requested.connect(
            self.delete_selected_conversation
        )

        self.conversations_page.rename_conversation_requested.connect(
            self.rename_selected_conversation
        )

        self.navigate(0)

    def ask_conversation_title(self):
        title, accepted = QInputDialog.getText(
            self,
            "گفت‌وگوی جدید",
            "اسم گفت‌وگو رو وارد کن:",
        )

        if not accepted:
            return None

        title = title.strip()

        if not title:
            return "گفت‌وگوی جدید"

        return title

    def update_logo(self):
        from pathlib import Path

        base_dir = Path(__file__).resolve().parents[2]

        if self.current_theme == "dark":
            filename = "logo_dark.png"
        else:
            filename = "logo.png"

        logo_path = base_dir / "assets" / "images" / filename
        pixmap = QPixmap(str(logo_path))

        if not pixmap.isNull():
            self.logo_label.setPixmap(
                pixmap.scaled(
                    200,
                    90,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def create_new_conversation(self):
        title = self.ask_conversation_title()

        if title is None:
            return

        self.home_page.clear_selected_files()
        self.active_conversation_id = create_conversation(title)

        self.chats_page.set_conversation(
            self.active_conversation_id
        )

        self.active_documents = {}
        self.chats_page.set_documents({})

        self.conversations_page.refresh_list()
        self.navigate(0)

    def start_chat_with_documents(self):
        documents = self.home_page.get_ready_documents()

        if not documents:
            return

        title = self.ask_conversation_title()

        if title is None:
            return

        self.active_conversation_id = create_conversation(title)
        self.conversations_page.refresh_list()

        self.active_documents = documents

        self.chats_page.set_conversation(
            self.active_conversation_id
        )
        self.chats_page.set_documents(self.active_documents)

        self.home_page.clear_selected_files()

        self.navigate(2)

    def open_conversation(self, conversation_id):
        self.active_conversation_id = conversation_id

        self.chats_page.set_conversation(conversation_id)

        # بازیابی اسناد مربوط به این گفت‌وگو
        self.chats_page.load_documents(conversation_id)
        self.active_documents = dict(self.chats_page.documents)

        # بازیابی پیام‌های گفت‌وگو
        self.chats_page.load_messages(conversation_id)

        self.navigate(2)

    def delete_selected_conversation(self, conversation_id):
        deleted = delete_conversation(conversation_id)

        if not deleted:
            return

        # اگر گفت‌وگوی فعال حذف شده، وضعیت چت را پاک کن
        if self.active_conversation_id == conversation_id:
            self.active_conversation_id = None
            self.active_documents = {}

            self.chats_page.set_conversation(None)
            self.chats_page.set_documents({})

        self.conversations_page.refresh_list()

    def rename_selected_conversation(self, conversation_id, new_title):
        from app.database import rename_conversation

        renamed = rename_conversation(conversation_id, new_title)

        if renamed:
            self.conversations_page.refresh_list()

    def make_nav_button(self, text, icon_name):
        button = QPushButton(text)

        button.setProperty("icon_name", icon_name)
        button.setIconSize(QSize(20, 20))
        button.setMinimumHeight(50)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setProperty("active", False)

        self.set_button_icon(button)

        return button

    def set_button_icon(self, button):
        if button.property("active"):
            color = "#3984FF"
        elif self.current_theme == "dark":
            color = "#C5CEDB"
        else:
            color = "#64748B"

        button.setIcon(
            qta.icon(
                button.property("icon_name"),
                color=color,
            )
        )

    def navigate(self, index):
        self.pages.setCurrentIndex(index)

        # مشخص می‌کنیم کدام دکمه در منو فعال باشد
        active_button_index = {
            0: 0,  # خانه
            1: 1,  # فهرست چت‌ها
            2: 1,  # صفحه گفت‌وگو؛ دکمه چت‌ها فعال بماند
            3: 2,  # تنظیمات
        }

        buttons = [
            self.home_button,
            self.chats_button,
            self.settings_button,
        ]

        selected_button = active_button_index.get(index)

        for i, button in enumerate(buttons):
            button.setProperty("active", i == selected_button)

            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def set_theme(self, theme):
        if theme not in ("light", "dark"):
            return

        self.current_theme = theme
        self.setStyleSheet(get_stylesheet(theme))
        self.update_logo()
        for button in (
                self.home_button,
                self.chats_button,
                self.settings_button,
        ):
            self.set_button_icon(button)
