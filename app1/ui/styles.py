
def get_stylesheet(theme: str = "dark") -> str:
    """Return the application stylesheet for the selected theme."""

    if theme == "light":
        colors = {
            "window": "#F5F7FB",
            "sidebar": "#FFFFFF",
            "surface": "#FFFFFF",
            "surface_hover": "#EDF3FF",
            "border": "#E2E8F0",
            "text": "#172033",
            "muted": "#64748B",
            "accent": "#3978F6",
            "accent_hover": "#2563EB",
            "selected": "#E8F0FF",
            "assistant": "#F1F5F9",
            "user_message": "#E8F0FF",
            "input": "#FFFFFF",
        }
    else:
        colors = {
            "window": "#10141D",
            "sidebar": "#151B27",
            "surface": "#1B2332",
            "surface_hover": "#263247",
            "border": "#2B3547",
            "text": "#F1F5F9",
            "muted": "#9AA8BC",
            "accent": "#4C8DFF",
            "accent_hover": "#70A3FF",
            "selected": "#243A5D",
            "assistant": "#222C3D",
            "user_message": "#263B5C",
            "input": "#151B27",
        }

    return f"""
        * {{
            font-family: "Vazirmatn", "Segoe UI", sans-serif;
            font-size: 10pt;
        }}

        QMainWindow, QWidget#centralWidget {{
            background-color: {colors["window"]};
            color: {colors["text"]};
        }}

        QWidget#sidebar {{
            background-color: {colors["sidebar"]};
            border-right: 1px solid {colors["border"]};
        }}

        QWidget {{
            color: {colors["text"]};
        }}

        QLabel {{
            color: {colors["text"]};
            background: transparent;
        }}

        QLabel[muted="true"] {{
            color: {colors["muted"]};
        }}

        QPushButton {{
            background-color: transparent;
            color: {colors["text"]};
            border: 1px solid transparent;
            border-radius: 9px;
            padding: 10px 12px;
            text-align: left;
        }}

        QPushButton:hover {{
            background-color: {colors["surface_hover"]};
        }}

        QPushButton[active="true"] {{
            background-color: {colors["selected"]};
            color: {colors["accent"]};
            font-weight: 600;
        }}

        QPushButton[primary="true"] {{
            background-color: {colors["accent"]};
            color: #FFFFFF;
            font-weight: 600;
        }}

        QPushButton[primary="true"]:hover {{
            background-color: {colors["accent_hover"]};
        }}

        QFrame#surface {{
            background-color: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 14px;
        }}

        QFrame#composerSurface {{
            background-color: {colors["input"]};
            border: 1px solid {colors["border"]};
            border-radius: 29px;
        }}

        QLineEdit#chatInput {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 8px 10px;
        }}

        QLineEdit#chatInput:focus {{
            border: none;
        }}

        QPushButton#sendButton {{
            background-color: {colors["accent"]};
            color: #FFFFFF;
            border: none;
            border-radius: 21px;
            padding: 0;
            font-size: 22pt;
            font-weight: 600;
            text-align: center;
        }}

        QPushButton#sendButton:hover {{
            background-color: {colors["accent_hover"]};
        }}

        QFrame#assistantMessage {{
            background: transparent;
            border: none;
        }}

        QFrame#userMessage {{
            background-color: {colors["user_message"]};
            border: none;
            border-radius: 18px;
        }}

        QLineEdit,
        QTextEdit,
        QPlainTextEdit,
        QComboBox {{
            background-color: {colors["input"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 10px;
            selection-background-color: {colors["accent"]};
        }}

        QLineEdit:focus,
        QTextEdit:focus {{
            border: 1px solid {colors["accent"]};
        }}

        /* Conversation cards */

        QFrame#conversationCard {{
            background-color: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 14px;
        }}

        QFrame#conversationCard:hover {{
            background-color: {colors["surface_hover"]};
            border: 1px solid {colors["accent"]};
        }}

        QLabel#conversationTitle {{
            color: {colors["text"]};
            font-size: 11pt;
            font-weight: 600;
            background: transparent;
        }}

        QLabel#conversationDetails {{
            color: {colors["muted"]};
            font-size: 9pt;
            background: transparent;
        }}

        /* Conversation search */

        QLineEdit#conversationSearch {{
            background-color: {colors["input"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 12px;
            padding: 12px 14px;
            min-height: 22px;
        }}

        QLineEdit#conversationSearch:focus {{
            border: 1px solid {colors["accent"]};
        }}

        /* Open conversation button */

        QPushButton#openConversationButton {{
            background-color: {colors["selected"]};
            color: {colors["accent"]};
            border: none;
            border-radius: 9px;
            padding: 9px 14px;
            font-weight: 600;
        }}

        QPushButton#openConversationButton:hover {{
            background-color: {colors["surface_hover"]};
        }}

        /* Conversation menu button */

        QPushButton#conversationMenuButton {{
            background-color: transparent;
            border: none;
            border-radius: 9px;
            padding: 4px;
            font-size: 18pt;
        }}

        QPushButton#conversationMenuButton:hover {{
            background-color: {colors["surface_hover"]};
        }}

        /* Popup menu */

        QMenu {{
            background-color: {colors["surface"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 5px;
        }}

        QMenu::item {{
            padding: 8px 12px;
            margin: 2px;
            border-radius: 6px;
            spacing: 4px;
        }}

        QMenu::item:selected {{
            background-color: {colors["surface_hover"]};
            color: {colors["accent"]};
        }}
        
        /* Conversation menu icons and actions */
        QMenu::item {{
            padding: 9px 22px;
            border-radius: 6px;
        }}

        QMenu::item:selected {{
            background-color: {colors["surface_hover"]};
            color: {colors["accent"]};
        }}

        /* Dialogs */
        QDialog#conversationDialog {{
            background-color: {colors["window"]};
        }}

        QLabel#dialogTitle {{
            font-size: 14pt;
            font-weight: 700;
        }}

        QLabel#dialogDescription {{
            color: {colors["muted"]};
        }}

        QLineEdit#renameInput {{
            background-color: {colors["input"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 11px 13px;
            min-height: 22px;
        }}

        QLineEdit#renameInput:focus {{
            border: 1px solid {colors["accent"]};
        }}

        QPushButton#dialogPrimary {{
            background-color: {colors["accent"]};
            color: #FFFFFF;
            border: none;
            border-radius: 9px;
            padding: 10px 18px;
            font-weight: 600;
            text-align: center;
        }}

        QPushButton#dialogPrimary:hover {{
            background-color: {colors["accent_hover"]};
        }}

        QPushButton#dialogSecondary {{
            background-color: {colors["surface_hover"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 9px;
            padding: 10px 18px;
            text-align: center;
        }}

        QPushButton#dialogSecondary:hover {{
            border: 1px solid {colors["accent"]};
        }}

        QPushButton#deleteConfirmButton {{
            background-color: #DC2626;
            color: #FFFFFF;
            border: none;
            border-radius: 9px;
            padding: 10px 18px;
            font-weight: 600;
            text-align: center;
        }}

        QPushButton#deleteConfirmButton:hover {{
            background-color: #B91C1C;
        }}

        QLabel#deleteWarningIcon {{
            color: #EF4444;
            font-size: 25pt;
        }}
        
        /* Scroll area */

        QScrollArea {{
            background-color: transparent;
            border: none;
        }}

        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors["border"]};
            border-radius: 4px;
            min-height: 24px;
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
    """
