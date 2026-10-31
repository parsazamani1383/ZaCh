
from pathlib import Path
from PySide6.QtCore import Qt, QObject, QRunnable, QSize, QThreadPool, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QFileDialog,
    QScrollArea,
)

from app.ui.icons import file_icon, safe_icon

from app.document_reader import (
    FILE_DIALOG_FILTER,
    SUPPORTED_EXTENSIONS,
    read_document,
)


class ExtractionSignals(QObject):
    finished = Signal(str, str, str)


class ExtractionWorker(QRunnable):
    def __init__(self, file_path: Path):
        super().__init__()
        self.file_path = file_path
        self.signals = ExtractionSignals()

    def run(self):
        path_string = str(self.file_path)

        try:
            content = read_document(path_string)

            self.signals.finished.emit(path_string, content, "")

        except Exception as exc:
            self.signals.finished.emit(path_string, "", str(exc))


class HomePage(QWidget):
    SUPPORTED_EXTENSIONS = SUPPORTED_EXTENSIONS
    start_chat_requested = Signal()

    def __init__(self):
        super().__init__()

        # مسیر فایل‌ها، متن استخراج‌شده و وضعیت پردازش
        self.selected_files = {}
        self.extracted_texts = {}
        self.file_statuses = {}
        self.file_errors = {}
        self._workers = {}

        self.thread_pool = QThreadPool.globalInstance()

        self.setAcceptDrops(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(18)

        title = QLabel("سلام! به ZaCh خوش اومدی")
        title.setObjectName("heroTitle")
        layout.addWidget(title)

        subtitle = QLabel(
            "اسنادت رو انتخاب کن تا بعداً بتونی درباره محتوای اون‌ها سؤال بپرسی."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("muted", True)
        layout.addWidget(subtitle)

        # مراحل ساخت گفت‌وگو
        steps_row = QHBoxLayout()
        steps_row.setSpacing(10)

        self.step_labels = []
        for number, text in enumerate(
            ("انتخاب سند", "نام‌گذاری گفت‌وگو", "شروع پرسش و پاسخ"),
            start=1,
        ):
            step = QLabel(f"{number}  {text}")
            step.setObjectName("stepChip")
            step.setProperty("state", "todo")
            step.setAlignment(Qt.AlignmentFlag.AlignCenter)
            steps_row.addWidget(step, 1)
            self.step_labels.append(step)

        layout.addLayout(steps_row)

        card = QFrame()
        card.setObjectName("dropZone")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 26, 24, 24)
        card_layout.setSpacing(12)

        file_icon_label = QLabel()
        file_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_icon_label.setPixmap(
            safe_icon("ph.upload-simple", "#4C8DFF").pixmap(44, 44)
        )
        card_layout.addWidget(file_icon_label)

        card_title = QLabel("فایل‌های اسناد")
        card_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_title.setObjectName("cardTitle")
        card_layout.addWidget(card_title)

        description = QLabel(
            "فایل‌ها را اینجا رها کن یا با دکمه‌ی زیر انتخاب کن\n"
            "فرمت‌های پشتیبانی‌شده: PDF، Word، Excel و TXT"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setProperty("muted", True)
        card_layout.addWidget(description)

        self.add_files_button = QPushButton("  انتخاب فایل‌ها")
        self.add_files_button.setIcon(safe_icon("ph.plus", "#FFFFFF"))
        self.add_files_button.setIconSize(QSize(18, 18))
        self.add_files_button.setProperty("primary", True)
        self.add_files_button.setProperty("centered", True)
        self.add_files_button.setMinimumHeight(46)
        self.add_files_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.add_files_button.clicked.connect(self.choose_files)
        card_layout.addWidget(self.add_files_button)

        self.file_count_label = QLabel("هنوز فایلی انتخاب نشده")
        self.file_count_label.setProperty("muted", True)
        self.file_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.file_count_label)

        self.file_rows_layout = QVBoxLayout()
        self.file_rows_layout.setSpacing(8)
        self.file_rows_layout.setContentsMargins(0, 0, 4, 0)

        self.file_rows_widget = QWidget()
        self.file_rows_widget.setLayout(self.file_rows_layout)

        self.file_scroll = QScrollArea()
        self.file_scroll.setWidgetResizable(True)
        self.file_scroll.setWidget(self.file_rows_widget)
        self.file_scroll.setMinimumHeight(60)
        self.file_scroll.setMaximumHeight(210)
        card_layout.addWidget(self.file_scroll)

        layout.addWidget(card)

        # کارت مستقل گفت‌وگو با اسناد
        self.chat_card = QFrame()
        self.chat_card.setObjectName("surface")

        chat_card_layout = QVBoxLayout(self.chat_card)
        chat_card_layout.setContentsMargins(22, 18, 22, 18)
        chat_card_layout.setSpacing(10)

        chat_header = QHBoxLayout()
        chat_header.setSpacing(12)

        chat_icon = QLabel()
        chat_icon.setFixedSize(48, 48)
        chat_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chat_icon.setObjectName("accentIconBox")
        chat_icon.setPixmap(
            safe_icon("ph.chat-circle-dots", "#4C8DFF").pixmap(26, 26)
        )
        chat_header.addWidget(chat_icon)

        chat_titles = QVBoxLayout()
        chat_titles.setSpacing(4)

        chat_title = QLabel("شروع چت")
        chat_title.setObjectName("cardTitle")
        chat_titles.addWidget(chat_title)

        chat_description = QLabel(
            "از محتوای اسنادت سؤال بپرس و پاسخ بگیر."
        )
        chat_description.setWordWrap(True)
        chat_description.setProperty("muted", True)
        chat_titles.addWidget(chat_description)

        chat_header.addLayout(chat_titles, 1)
        chat_card_layout.addLayout(chat_header)

        self.chat_status_label = QLabel(
            "پس از استخراج متن اسناد، می‌تونی گفت‌وگو رو شروع کنی."
        )
        self.chat_status_label.setProperty("muted", True)
        self.chat_status_label.setWordWrap(True)
        chat_card_layout.addWidget(self.chat_status_label)

        self.start_chat_button = QPushButton("شروع گفت‌وگو")
        self.start_chat_button.setObjectName("startChatButton")
        self.start_chat_button.setMinimumHeight(48)
        self.start_chat_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.start_chat_button.setEnabled(False)
        self.start_chat_button.clicked.connect(
            self.start_chat_requested.emit
        )
        chat_card_layout.addWidget(self.start_chat_button)

        layout.addWidget(self.chat_card)
        layout.addStretch()

        self.refresh_file_list()

    # ----- drag & drop -------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(
            Path(url.toLocalFile()).suffix.lower() in self.SUPPORTED_EXTENSIONS
            for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ]
        self.add_files(paths)
        event.acceptProposedAction()

    # ----- state -------------------------------------------------------

    def clear_selected_files(self):
        self.selected_files.clear()
        self.extracted_texts.clear()
        self.file_statuses.clear()
        self.file_errors.clear()

        self.refresh_file_list()

    def suggested_title(self):
        """A friendly default chat name from the first selected file."""
        for path_string in self.get_ready_documents():
            return Path(path_string).stem
        return ""

    def choose_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "انتخاب اسناد",
            "",
            FILE_DIALOG_FILTER,
        )

        self.add_files(file_paths)

    def add_files(self, file_paths):
        if not file_paths:
            return

        for file_path in file_paths:
            path = Path(file_path)
            path_string = str(path)

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            # فایل تکراری دوباره پردازش نمی‌شود.
            if path_string in self.selected_files:
                continue

            self.selected_files[path_string] = path
            self.file_statuses[path_string] = "در حال استخراج..."
            self.file_errors.pop(path_string, None)

            worker = ExtractionWorker(path)
            worker.signals.finished.connect(self.on_extraction_finished)

            self._workers[path_string] = worker
            self.thread_pool.start(worker)

        self.refresh_file_list()

    def on_extraction_finished(self, path_string, content, error):
        # اگر فایل در حین پردازش حذف شده باشد، نتیجه نادیده گرفته می‌شود.
        if path_string not in self.selected_files:
            self._workers.pop(path_string, None)
            return

        self._workers.pop(path_string, None)

        if error:
            self.extracted_texts.pop(path_string, None)
            self.file_statuses[path_string] = "خطا در استخراج"
            self.file_errors[path_string] = error

        elif not content.strip():
            self.extracted_texts[path_string] = ""
            self.file_statuses[path_string] = "متنی پیدا نشد"
            self.file_errors.pop(path_string, None)

        else:
            self.extracted_texts[path_string] = content
            self.file_statuses[path_string] = "استخراج شد"
            self.file_errors.pop(path_string, None)

        self.refresh_file_list()

    def refresh_file_list(self):
        while self.file_rows_layout.count():
            item = self.file_rows_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        count = len(self.selected_files)

        if count == 0:
            self.file_count_label.setText("هنوز فایلی انتخاب نشده")
            self.file_scroll.hide()
            self.update_start_chat_button()
            return

        self.file_scroll.show()
        self.file_count_label.setText(f"{count} فایل انتخاب شده")

        for path_string, path in self.selected_files.items():
            row = QFrame()
            row.setObjectName("fileRow")

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 8, 8, 8)
            row_layout.setSpacing(10)

            icon_label = QLabel()
            icon_label.setPixmap(file_icon(path.suffix).pixmap(24, 24))
            icon_label.setFixedWidth(28)
            row_layout.addWidget(icon_label)

            name_label = QLabel(path.name)
            name_label.setToolTip(path_string)
            name_label.setWordWrap(True)
            row_layout.addWidget(name_label, 1)

            status = self.file_statuses.get(
                path_string, "در حال استخراج..."
            )

            status_label = QLabel(status)
            status_label.setObjectName("statusBadge")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if status == "خطا در استخراج":
                status_label.setProperty("state", "error")
                status_label.setToolTip(
                    self.file_errors.get(path_string, "")
                )
            elif status == "استخراج شد":
                status_label.setProperty("state", "ok")
            elif status == "متنی پیدا نشد":
                status_label.setProperty("state", "warn")
                status_label.setToolTip(
                    "ممکن است PDF اسکن‌شده باشد یا متن قابل استخراج نداشته باشد."
                )
            else:
                status_label.setProperty("state", "busy")

            row_layout.addWidget(status_label)

            remove_button = QPushButton()
            remove_button.setIcon(safe_icon("ph.x", "#EF4444"))
            remove_button.setIconSize(QSize(14, 14))
            remove_button.setFixedSize(30, 30)
            remove_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            remove_button.setToolTip("حذف فایل از فهرست")
            remove_button.setObjectName("removeFileButton")
            remove_button.clicked.connect(
                lambda checked=False, key=path_string:
                    self.remove_file(key)
            )
            row_layout.addWidget(remove_button)

            self.file_rows_layout.addWidget(row)

        self.file_rows_layout.addStretch()
        self.update_start_chat_button()

    def remove_file(self, path_string):
        if path_string not in self.selected_files:
            return

        del self.selected_files[path_string]
        self.extracted_texts.pop(path_string, None)
        self.file_statuses.pop(path_string, None)
        self.file_errors.pop(path_string, None)

        self.refresh_file_list()


    def update_start_chat_button(self):
        ready_documents = self.get_ready_documents()
        ready_count = len(ready_documents)

        self.start_chat_button.setEnabled(ready_count > 0)

        if ready_count == 0:
            self.chat_status_label.setText(
                "برای شروع گفت‌وگو، ابتدا یک سند انتخاب کن "
                "و منتظر استخراج متنش بمون."
            )
        else:
            self.chat_status_label.setText(
                f"{ready_count} سند آماده‌ی گفت‌وگو است. "
                "با زدن «شروع گفت‌وگو» نام چت را وارد می‌کنی."
            )

        self.update_steps(ready_count > 0)

    def update_steps(self, documents_ready):
        states = (
            ["done", "current", "todo"]
            if documents_ready
            else ["current", "todo", "todo"]
        )

        for label, state in zip(self.step_labels, states):
            label.setProperty("state", state)
            label.style().unpolish(label)
            label.style().polish(label)


    def get_ready_documents(self):
        return {
            path: text
            for path, text in self.extracted_texts.items()
            if path in self.selected_files and text.strip()
        }
