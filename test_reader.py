
from app.document_reader import read_docx_file

docx_path = input("مسیر کامل فایل Word را وارد کن: ").strip().strip('"')

try:
    text = read_docx_file(docx_path)

    if text.strip():
        print("\n--- متن استخراج‌شده از Word ---\n")
        print(text)
    else:
        print("فایل خوانده شد، اما متن قابل استخراجی پیدا نشد.")

except Exception as error:
    print(f"خطا: {error}")
