
from openai import OpenAI

from app.config import get_api_key, get_base_url

AI_NAME = "ZaCh"

SYSTEM_PROMPT = (
    f"اسم تو {AI_NAME} است؛ یک دستیار هوشمند برای تحلیل اسناد. "
    f"اگر کاربر اسمت را پرسید یا خواست خودت را معرفی کنی، بگو «{AI_NAME}» هستی. "
    "هرگز خودت را به‌عنوان ChatGPT یا محصول شرکت دیگری معرفی نکن. "
    "به زبان کاربر (پیش‌فرض: فارسی) پاسخ بده."
)


def get_client(timeout=60.0):
    """کلاینت OpenAI با کلید و آدرسِ تنظیم‌شده در برنامه."""
    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "کلید API وارد نشده است. از بخش «تنظیمات» کلید API را وارد کن."
        )

    return OpenAI(
        api_key=api_key,
        base_url=get_base_url(),
        timeout=timeout,
        max_retries=1,
    )


def test_connection():
    """اتصال و اعتبار کلید را آزمایش می‌کند؛ در صورت خطا استثنا می‌دهد."""
    client = get_client(timeout=20.0)
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=1,
    )


def ask_ai(question: str) -> str:
    """ارسال سؤال به سرویس هوش مصنوعی و دریافت پاسخ."""

    client = get_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("هوش مصنوعی پاسخ متنی برنگرداند.")

    return answer.strip()
