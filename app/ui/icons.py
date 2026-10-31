"""Safe icon helpers: a missing icon name never crashes the app."""

import qtawesome as qta
from PySide6.QtGui import QIcon

MUTED = "#94A3B8"

# file type -> (icon name, color)
FILE_ICONS = {
    ".pdf": ("ph.file-pdf", "#EF4444"),
    ".docx": ("ph.file-doc", "#3B82F6"),
    ".txt": ("ph.file-text", "#94A3B8"),
    ".xlsx": ("ph.file-xls", "#22A06B"),
    ".xlsm": ("ph.file-xls", "#22A06B"),
    ".xls": ("ph.file-xls", "#22A06B"),
}


def safe_icon(name, color=MUTED, fallback="fa5s.file"):
    for candidate in (name, fallback):
        try:
            return qta.icon(candidate, color=color)
        except Exception:
            continue
    return QIcon()


def file_icon(extension, size=None):
    name, color = FILE_ICONS.get(
        str(extension).lower(), ("ph.file", MUTED)
    )
    return safe_icon(name, color)


def file_pixmap(extension, size=22):
    return file_icon(extension).pixmap(size, size)
