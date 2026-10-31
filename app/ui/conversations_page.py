from app.database import get_conversations, set_conversation_pinned
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QMessageBox,
    QSizePolicy,
    QMenu,
    QDialog,
)
import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtGui import QCursor
from app.ui.icons import safe_icon


class ConversationCard(QFrame):
    """Clickable conversation surface; action controls remain independent."""
    def __init__(self, conversation_id, callback, parent=None):
        super().__init__(parent)
        self.conversation_id = conversation_id
        self.callback = callback
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callback(self.conversation_id)
            event.accept()
            return
        super().mousePressEvent(event)

class RenameConversationDialog(QDialog):
    def __init__(self, current_title, parent=None):
        super().__init__(parent)

        self.setObjectName("conversationDialog")
        self.setWindowTitle("تغییر نام گفت‌وگو")
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("تغییر نام گفت‌وگو")
        title.setObjectName("dialogTitle")

        description = QLabel(
            "یک نام مناسب برای این گفت‌وگو انتخاب کن."
        )
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("renameInput")
        self.name_input.setText(current_title)
        self.name_input.selectAll()
        self.name_input.setPlaceholderText("نام جدید گفت‌وگو")

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("dialogSecondary")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("ذخیره تغییرات")
        save_button.setObjectName("dialogPrimary")
        save_button.setDefault(True)
        save_button.clicked.connect(self.accept)

        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.name_input)
        layout.addSpacing(4)
        layout.addLayout(buttons)

        self.name_input.returnPressed.connect(self.accept)

    def get_name(self):
        return self.name_input.text().strip()

class DeleteConversationDialog(QDialog):
    def __init__(self, conversation_title, parent=None):
        super().__init__(parent)

        self.setObjectName("conversationDialog")
        self.setWindowTitle("حذف گفت‌وگو")
        self.setModal(True)
        self.setMinimumWidth(390)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        icon_label = QLabel()
        icon_label.setObjectName("deleteWarningIcon")
        icon_label.setPixmap(
            qta.icon(
                "fa5s.trash-alt",
                color="#EF4444",
            ).pixmap(36, 36)
        )

        title = QLabel("حذف این گفت‌وگو؟")
        title.setObjectName("dialogTitle")

        description = QLabel(
            f"گفت‌وگوی «{conversation_title}» حذف خواهد شد. "
            "اگر حذف نهایی شود، ممکن است امکان بازیابی آن وجود نداشته باشد."
        )
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("dialogSecondary")
        cancel_button.setDefault(True)
        cancel_button.clicked.connect(self.reject)

        delete_button = QPushButton("حذف گفت‌وگو")
        delete_button.setObjectName("deleteConfirmButton")
        delete_button.setIcon(
            qta.icon("fa5s.trash-alt", color="#FFFFFF")
        )
        delete_button.clicked.connect(self.accept)

        buttons.addWidget(cancel_button)
        buttons.addWidget(delete_button)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(6)
        layout.addLayout(buttons)

class ConversationsPage(QWidget):
    conversation_selected = Signal(int)
    new_conversation_requested = Signal()
    delete_conversation_requested = Signal(int)
    rename_conversation_requested = Signal(int, str)

    def __init__(self):
        super().__init__()

        self.conversations = [
            {
                "id": "demo-1",
                "title": "گفت‌وگوی نمونه",
                "details": "برای شروع، یک گفت‌وگوی جدید بساز",
            },
        ]

        self.setObjectName("conversationsPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        title = QLabel("گفت‌وگوهای من")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "گفت‌وگوهایت را پیدا کن یا یک گفت‌وگوی جدید شروع کن."
        )
        subtitle.setProperty("muted", True)
        subtitle.setWordWrap(True)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.new_button = QPushButton("  گفت‌وگوی جدید")
        self.new_button.setIcon(safe_icon("ph.note-pencil", "#FFFFFF", fallback="fa5s.edit"))
        self.new_button.setIconSize(QSize(19, 19))
        self.new_button.setProperty("primary", True)
        self.new_button.setProperty("centered", True)
        self.new_button.setMinimumHeight(44)
        self.new_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_button.clicked.connect(
            self.new_conversation_requested.emit
        )

        header.addLayout(title_layout, 1)
        header.addWidget(self.new_button, 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setObjectName("conversationSearch")
        self.search_input.setPlaceholderText(
            "جست‌وجو در گفت‌وگوها..."
        )
        self.search_input.setMinimumHeight(44)
        self.search_input.textChanged.connect(self.refresh_list)

        layout.addWidget(self.search_input)

        self.count_label = QLabel()
        self.count_label.setProperty("muted", True)
        layout.addWidget(self.count_label)

        # Conversation list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 6, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll, 1)

        self.refresh_list()

    def refresh_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        query = self.search_input.text().strip().casefold()

        self.conversations = get_conversations()

        filtered = [
            conversation
            for conversation in self.conversations
            if query in conversation["title"].casefold()
               or query in conversation["created_at"].casefold()
        ]

        self.count_label.setText(
            f"{len(filtered)} گفت‌وگو"
        )

        for conversation in filtered:
            conversation_id = conversation["id"]
            card = ConversationCard(
                conversation_id,
                lambda cid: self.conversation_selected.emit(cid),
            )
            card.setObjectName("conversationCard")
            card.setToolTip("برای باز کردن گفت‌وگو کلیک کن")

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            card_layout.setSpacing(12)

            icon = QLabel()
            icon.setObjectName("accentIconBox")
            icon.setPixmap(
                safe_icon(
                    "ph.chat-circle-dots",
                    "#4C8DFF",
                    fallback="fa5s.comment-dots",
                ).pixmap(24, 24)
            )
            icon.setFixedSize(44, 44)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(5)

            name = QLabel(conversation["title"])
            name.setObjectName("conversationTitle")
            name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            details = QLabel(
                f"تاریخ ایجاد: {conversation['created_at']}"
            )
            details.setObjectName("conversationDetails")
            details.setProperty("muted", True)
            details.setWordWrap(True)
            details.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            text_layout.addWidget(name)
            text_layout.addWidget(details)

            menu_button = QPushButton()
            menu_button.setIcon(safe_icon("ph.dots-three-vertical", fallback="fa5s.ellipsis-v"))
            menu_button.setIconSize(QSize(18, 18))
            menu_button.setObjectName("conversationMenuButton")
            menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
            menu_button.setToolTip("گزینه‌های گفت‌وگو")
            menu_button.setFixedWidth(40)

            menu = QMenu(menu_button)

            rename_action = menu.addAction(
                safe_icon("ph.pencil-simple", fallback="fa5s.edit"),
                "تغییر نام"
            )

            pin_label = "برداشتن سنجاق" if conversation.get("is_pinned") else "سنجاق کردن"
            pin_action = menu.addAction(
                safe_icon("ph.push-pin", "#4C8DFF", fallback="fa5s.thumbtack"),
                pin_label,
            )
            delete_action = menu.addAction(
                safe_icon("ph.trash", "#EF4444", fallback="fa5s.trash-alt"),
                "حذف گفت‌وگو"
            )


            rename_action.triggered.connect(
                lambda checked=False, cid=conversation_id:
                self.request_rename_conversation(cid)
            )

            pin_action.triggered.connect(
                lambda checked=False, cid=conversation_id, value=not bool(conversation.get("is_pinned")):
                self.toggle_pin_conversation(cid, value)
            )
            delete_action.triggered.connect(
                lambda checked=False, cid=conversation_id:
                self.confirm_delete_conversation(cid)
            )

            menu_button.clicked.connect(
                lambda checked=False, btn=menu_button, m=menu:
                m.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
            )

            icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            card_layout.addWidget(icon)
            card_layout.addLayout(text_layout, 1)
            if conversation.get("is_pinned"):
                pinned_icon = QLabel()
                pinned_icon.setPixmap(
                    safe_icon("ph.push-pin-fill", "#4C8DFF", fallback="fa5s.thumbtack").pixmap(17, 17)
                )
                pinned_icon.setToolTip("گفت‌وگوی سنجاق‌شده")
                pinned_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                card_layout.addWidget(pinned_icon)
            card_layout.addWidget(menu_button)

            self.list_layout.addWidget(card)

        if not filtered:
            empty = QLabel("گفت‌وگویی با این عبارت پیدا نشد.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setProperty("muted", True)
            self.list_layout.addWidget(empty)

        self.list_layout.addStretch()

    def toggle_pin_conversation(self, conversation_id, pinned):
        set_conversation_pinned(conversation_id, pinned)
        self.refresh_list()

    def confirm_delete_conversation(self, conversation_id):
        conversation = next(
            (
                item for item in self.conversations
                if item["id"] == conversation_id
            ),
            None,
        )

        if conversation is None:
            return

        dialog = DeleteConversationDialog(
            conversation["title"],
            self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.delete_conversation_requested.emit(conversation_id)

    def request_rename_conversation(self, conversation_id):
        conversation = next(
            (
                item for item in self.conversations
                if item["id"] == conversation_id
            ),
            None,
        )

        if conversation is None:
            return

        dialog = RenameConversationDialog(
            conversation["title"],
            self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_title = dialog.get_name()

            if new_title and new_title != conversation["title"]:
                self.rename_conversation_requested.emit(
                    conversation_id,
                    new_title,
                )

