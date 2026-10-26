from app.ai_service import ask_ai

try:
    answer = ask_ai("سلام! فقط در یک جمله خودت را معرفی کن.")
    print("\nپاسخ هوش مصنوعی:")
    print(answer)

except Exception as e:
    print("\nخطا در اتصال:")
    print(e)