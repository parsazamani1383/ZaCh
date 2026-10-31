from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


class ConversationTitleDialog(QDialog):
    """Asks for the name of a new conversation (shown after documents are chosen)."""

    def __init__(self, suggested_title="", file_count=0, parent=None):
        super().__init__(parent)

        self.setObjectName("conversationDialog")
        self.setWindowTitle("نام گفت‌وگو")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("این گفت‌وگو را چه بنامیم؟")
        title.setObjectName("dialogTitle")

        if file_count:
            text = (
                f"{file_count} سند آماده شد. یک نام برای این گفت‌وگو "
                "انتخاب کن تا بعداً راحت پیدایش کنی."
            )
        else:
            text = "یک نام برای این گفت‌وگو انتخاب کن."

        description = QLabel(text)
        description.setObjectName("dialogDescription")
        description.setWordWrap(True)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("renameInput")
        self.name_input.setPlaceholderText("مثلاً: قرارداد همکاری")
        self.name_input.setText(suggested_title)
        self.name_input.selectAll()
        self.name_input.returnPressed.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel_button = QPushButton("انصراف")
        cancel_button.setObjectName("dialogSecondary")
        cancel_button.clicked.connect(self.reject)

        start_button = QPushButton("شروع گفت‌وگو")
        start_button.setObjectName("dialogPrimary")
        start_button.setDefault(True)
        start_button.clicked.connect(self.accept)

        buttons.addWidget(cancel_button)
        buttons.addWidget(start_button)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.name_input)
        layout.addSpacing(4)
        layout.addLayout(buttons)

    def get_title(self):
        return self.name_input.text().strip() or "گفت‌وگوی جدید"
