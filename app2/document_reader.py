
from pathlib import Path


def read_txt_file(file_path: str) -> str:
    """
    Read a UTF-8 text file and return its contents.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"فایل پیدا نشد: {path.name}")

    if path.suffix.lower() != ".txt":
        raise ValueError("در این مرحله فقط فایل‌های TXT پشتیبانی می‌شوند.")

    # utf-8-sig also handles text files that begin with a UTF-8 BOM.
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"فایل «{path.name}» با کدگذاری UTF-8 قابل خواندن نیست."
        ) from exc

from pypdf import PdfReader


def read_pdf_file(file_path: str) -> str:
    """Extract text from a text-based PDF file."""
    try:
        reader = PdfReader(file_path)
        pages_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        return "\n\n".join(pages_text)

    except Exception as error:
        raise RuntimeError(f"خطا در خواندن فایل PDF: {error}") from error

from docx import Document
from zipfile import ZipFile
from lxml import etree


def read_docx_file(file_path: str) -> str:
    """Extract text from Word paragraphs and text boxes."""
    try:
        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        # Read text inside text boxes from the DOCX XML.
        with ZipFile(file_path, "r") as docx_zip:
            xml_content = docx_zip.read("word/document.xml")

        root = etree.fromstring(xml_content)
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

        text_boxes = root.xpath(
            ".//w:txbxContent//w:p",
            namespaces=namespaces,
        )

        for paragraph in text_boxes:
            text = "".join(
                paragraph.xpath(".//w:t/text()", namespaces=namespaces)
            ).strip()

            if text:
                paragraphs.append(text)

        return "\n".join(paragraphs)

    except Exception as error:
        raise RuntimeError(
            f"خطا در خواندن فایل Word: {error}"
        ) from error
