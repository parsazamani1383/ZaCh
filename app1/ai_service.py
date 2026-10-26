
import os
from openai import OpenAI


def ask_ai(question: str) -> str:
    """ارسال سؤال به سرویس GapGPT و دریافت پاسخ."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "کلید API پیدا نشد. متغیر OPENAI_API_KEY را بررسی کن."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.gapgpt.app/v1",
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("هوش مصنوعی پاسخ متنی برنگرداند.")

    return answer.strip()
