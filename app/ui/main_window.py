from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QSettings,
    QSize,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.database import (
    create_conversation,
    delete_conversation,
    initialize_database,
)
from app.ui.chats_page import ChatsPage
from app.ui.conversations_page import ConversationsPage
from app.ui.dialogs import ConversationTitleDialog
from app.ui.home_page import HomePage
from app.ui.icons import safe_icon
from app.ui.network import NetworkMonitor, OfflinePage
from app.ui.settings_page import SettingsPage
from app.ui.styles import get_stylesheet
from app.rag import reset_embeddings

# Sidebar geometry
SIDEBAR_COLLAPSED_WIDTH = 72
SIDEBAR_MIN_WIDTH = 190
SIDEBAR_MAX_WIDTH = 420
SIDEBAR_DEFAULT_WIDTH = 240
# Dragging the sidebar narrower than this collapses it to the icon rail.
SIDEBAR_SNAP_WIDTH = 140


class SidebarHandle(QFrame):
    """Thin draggable strip on the sidebar edge (double-click toggles)."""

    dragged = Signal(int)          # global x of the mouse
    released = Signal()
    double_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarHandle")
        self.setFixedWidth(6)
        self.setCursor(Qt.CursorShape.SplitHCursor)
        self.setToolTip("برای تغییر اندازه بکش • دابل‌کلیک: باز/بسته")
        self._dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self.setProperty("dragging", True)
            self.style().unpolish(self)
            self.style().polish(self)
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.dragged.emit(int(event.globalPosition().x()))
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self.setProperty("dragging", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.released.emit()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        initialize_database()

        self.settings = QSettings("ZaCh", "ZaCh")

        self.current_theme = "light"
        self.logo_label = None

        self.setWindowTitle("ZaCh")
        self.resize(1180, 760)
        self.setMinimumSize(820, 560)

        self.setStyleSheet(get_stylesheet(self.current_theme))

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ------------------------------------------------------------ Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(14, 18, 14, 16)
        sidebar_layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(6)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.logo_label.setObjectName("logoText")
        self.logo_label.setFixedHeight(56)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("sidebarToggle")
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setIconSize(QSize(22, 22))
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        header.addWidget(self.logo_label, 1)
        header.addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignVCenter)
        sidebar_layout.addLayout(header)

        self.update_logo()

        self.tagline = QLabel("دستیار هوشمند اسناد")
        self.tagline.setProperty("muted", True)
        sidebar_layout.addWidget(self.tagline)

        sidebar_layout.addSpacing(20)

        self.home_button = self.make_nav_button("خانه", "ph.house")
        self.chats_button = self.make_nav_button("چت‌ها", "ph.chats")
        self.settings_button = self.make_nav_button(
            "تنظیمات", "ph.sliders-horizontal"
        )

        self.nav_buttons = [
            self.home_button,
            self.chats_button,
            self.settings_button,
        ]

        for button in self.nav_buttons:
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        self.sidebar_handle = SidebarHandle()
        self.sidebar_handle.dragged.connect(self.on_sidebar_dragged)
        self.sidebar_handle.released.connect(self.save_sidebar_state)
        self.sidebar_handle.double_clicked.connect(self.toggle_sidebar)

        self._sidebar_anim = None
        self._sidebar_collapsed = False
        self._expanded_width = SIDEBAR_DEFAULT_WIDTH
        self.load_sidebar_state()

        # --------------------------------------------------------- Main content
        self.pages = QStackedWidget()

        self.home_page = HomePage()
        self.conversations_page = ConversationsPage()
        self.chats_page = ChatsPage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(self.home_page)  # index 0
        self.pages.addWidget(self.conversations_page)  # index 1
        self.pages.addWidget(self.chats_page)  # index 2
        self.pages.addWidget(self.settings_page)  # index 3

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.sidebar_handle)

        # صفحه‌ی قطع شبکه؛ جای محتوا نشان داده می‌شود (به‌جز تنظیمات)
        self.offline_page = OfflinePage()
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.pages)
        self.content_stack.addWidget(self.offline_page)
        root_layout.addWidget(self.content_stack, 1)

        self.network_online = True
        self.network_monitor = NetworkMonitor(parent=self)
        self.network_monitor.status_changed.connect(
            self.on_network_status_changed
        )
        self.offline_page.retry_requested.connect(
            self.network_monitor.check_now
        )

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

        self.settings_page.api_settings_saved.connect(
            self.on_api_settings_saved
        )

        self.navigate(0)
        self.network_monitor.start()

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def on_network_status_changed(self, online):
        self.network_online = online

        if online:
            reset_embeddings()

        self.update_offline_view()

    def on_api_settings_saved(self):
        reset_embeddings()
        self.network_monitor.check_now()

    def update_offline_view(self):
        show_offline = (
            not self.network_online
            and self.pages.currentIndex() != 3  # تنظیمات همیشه در دسترس
        )
        self.content_stack.setCurrentWidget(
            self.offline_page if show_offline else self.pages
        )

    # ------------------------------------------------------------------
    # Sidebar: collapse / expand / resize
    # ------------------------------------------------------------------

    def load_sidebar_state(self):
        try:
            width = int(
                self.settings.value("sidebar/width", SIDEBAR_DEFAULT_WIDTH)
            )
        except (TypeError, ValueError):
            width = SIDEBAR_DEFAULT_WIDTH

        collapsed = str(
            self.settings.value("sidebar/collapsed", "false")
        ).lower() in ("true", "1")

        self._expanded_width = max(
            SIDEBAR_MIN_WIDTH, min(SIDEBAR_MAX_WIDTH, width)
        )
        self.apply_sidebar_mode(collapsed)
        self.sidebar.setFixedWidth(
            SIDEBAR_COLLAPSED_WIDTH if collapsed else self._expanded_width
        )

    def save_sidebar_state(self):
        self.settings.setValue("sidebar/width", self._expanded_width)
        self.settings.setValue("sidebar/collapsed", self._sidebar_collapsed)

    def apply_sidebar_mode(self, collapsed):
        """Switch between the full sidebar and the icon-only rail."""
        self._sidebar_collapsed = collapsed

        self.logo_label.setVisible(not collapsed)
        self.tagline.setVisible(not collapsed)

        self.toggle_button.setIcon(self.sidebar_toggle_icon())
        self.toggle_button.setToolTip(
            "باز کردن منو" if collapsed else "بستن منو"
        )

        for button in self.nav_buttons:
            button.setText(
                "" if collapsed else f"  {button.property('label')}"
            )
            button.setToolTip(button.property("label") if collapsed else "")
            button.setProperty("collapsed", collapsed)
            self.refresh_style(button)

    def toggle_sidebar(self):
        collapsing = not self._sidebar_collapsed

        if collapsing:
            target = SIDEBAR_COLLAPSED_WIDTH
            # Hide labels first so text does not get squeezed while animating.
            self.apply_sidebar_mode(True)
        else:
            target = self._expanded_width

        self.animate_sidebar_width(target, expanding=not collapsing)
        self.save_sidebar_state()

    def animate_sidebar_width(self, target, expanding):
        if self._sidebar_anim is not None:
            self._sidebar_anim.stop()

        animation = QVariantAnimation(self)
        animation.setStartValue(self.sidebar.width())
        animation.setEndValue(target)
        animation.setDuration(180)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.valueChanged.connect(
            lambda value: self.sidebar.setFixedWidth(int(value))
        )

        if expanding:
            # Show labels once there is enough room for them.
            animation.finished.connect(
                lambda: self.apply_sidebar_mode(False)
            )

        self._sidebar_anim = animation
        animation.start()

    def on_sidebar_dragged(self, global_x):
        if self._sidebar_anim is not None:
            self._sidebar_anim.stop()
            self._sidebar_anim = None

        origin_x = self.sidebar.mapToGlobal(
            self.sidebar.rect().topLeft()
        ).x()

        if self.sidebar.isRightToLeft():
            origin_x = self.sidebar.mapToGlobal(
                self.sidebar.rect().topRight()
            ).x()
            raw_width = origin_x - global_x
        else:
            raw_width = global_x - origin_x

        if raw_width < SIDEBAR_SNAP_WIDTH:
            if not self._sidebar_collapsed:
                self.apply_sidebar_mode(True)
            self.sidebar.setFixedWidth(SIDEBAR_COLLAPSED_WIDTH)
            return

        width = max(SIDEBAR_MIN_WIDTH, min(SIDEBAR_MAX_WIDTH, raw_width))
        self._expanded_width = width

        if self._sidebar_collapsed:
            self.apply_sidebar_mode(False)

        self.sidebar.setFixedWidth(width)

    # ------------------------------------------------------------------
    # Conversation flow
    # ------------------------------------------------------------------

    def ask_conversation_title(self, suggested="", file_count=0):
        dialog = ConversationTitleDialog(
            suggested_title=suggested,
            file_count=file_count,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        return dialog.get_title()

    def update_logo(self):
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
                    170,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            # No logo file available: show the app name instead.
            self.logo_label.setText("ZaCh")

    def create_new_conversation(self):
        """«گفت‌وگوی جدید»: اول فقط به صفحه‌ی انتخاب سند می‌رویم.

        نام گفت‌وگو بعد از انتخاب اسناد و با زدن «شروع گفت‌وگو» پرسیده
        می‌شود (start_chat_with_documents)، تا فقط یک گفت‌وگو ساخته شود.
        """
        self.home_page.clear_selected_files()
        self.navigate(0)

    def start_chat_with_documents(self):
        documents = self.home_page.get_ready_documents()

        if not documents:
            return

        title = self.ask_conversation_title(
            suggested=self.home_page.suggested_title(),
            file_count=len(documents),
        )

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

    # ------------------------------------------------------------------
    # Navigation & theme
    # ------------------------------------------------------------------

    def make_nav_button(self, label, icon_name):
        button = QPushButton(f"  {label}")

        button.setObjectName("navButton")
        button.setProperty("label", label)
        button.setProperty("icon_name", icon_name)
        button.setProperty("collapsed", False)
        button.setIconSize(QSize(22, 22))
        button.setMinimumHeight(48)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setProperty("active", False)

        self.set_button_icon(button)

        return button

    def icon_color(self, active):
        if active:
            return "#3984FF"
        if self.current_theme == "dark":
            return "#C5CEDB"
        return "#64748B"

    def set_button_icon(self, button):
        if button.property("icon_name"):
            button.setIcon(
                safe_icon(
                    button.property("icon_name"),
                    self.icon_color(bool(button.property("active"))),
                )
            )

    @staticmethod
    def refresh_style(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        self.update_offline_view()

        # مشخص می‌کنیم کدام دکمه در منو فعال باشد
        active_button_index = {
            0: 0,  # خانه
            1: 1,  # فهرست چت‌ها
            2: 1,  # صفحه گفت‌وگو؛ دکمه چت‌ها فعال بماند
            3: 2,  # تنظیمات
        }

        selected_button = active_button_index.get(index)

        for i, button in enumerate(self.nav_buttons):
            button.setProperty("active", i == selected_button)
            self.set_button_icon(button)
            self.refresh_style(button)

    def set_theme(self, theme):
        if theme not in ("light", "dark"):
            return

        self.current_theme = theme
        self.setStyleSheet(get_stylesheet(theme))
        self.update_logo()

        self.toggle_button.setIcon(self.sidebar_toggle_icon())

        for button in self.nav_buttons:
            self.set_button_icon(button)

    def sidebar_toggle_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(
            QColor(self.icon_color(False)),
            4,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # قاب اصلی سایدبار
        painter.drawRoundedRect(
            QRectF(10, 10, 44, 44),
            8, 8
        )

        # خط جداکننده پنل کناری
        painter.drawLine(27, 12, 27, 52)

        painter.end()

        return QIcon(pixmap)