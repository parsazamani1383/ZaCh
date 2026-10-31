"""ذخیره‌ی تنظیمات کاربر (کلید API و آدرس سرویس) در یک فایل JSON ساده."""

import json
import os
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_BASE_URL = "https://api.gapgpt.app/v1"

CONFIG_DIR = Path(os.getenv("ZACH_CONFIG_DIR", Path.home() / ".zach"))
CONFIG_PATH = CONFIG_DIR / "config.json"


def _load():
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        CONFIG_PATH.chmod(0o600)  # کلید فقط برای خود کاربر قابل خواندن باشد
    except OSError:
        pass


def get_api_key():
    """کلید ذخیره‌شده در برنامه؛ اگر نبود متغیر محیطی OPENAI_API_KEY."""
    return (_load().get("api_key") or os.getenv("OPENAI_API_KEY") or "").strip()


def get_base_url():
    return (_load().get("base_url") or DEFAULT_BASE_URL).strip().rstrip("/")


def save_api_settings(api_key, base_url):
    data = _load()
    data["api_key"] = (api_key or "").strip()
    data["base_url"] = (base_url or "").strip().rstrip("/") or DEFAULT_BASE_URL
    _save(data)


def get_base_host():
    """نام میزبان سرویس، برای بررسی اتصال شبکه."""
    parsed = urlparse(get_base_url())
    return parsed.hostname or "api.gapgpt.app", parsed.port or (
        80 if parsed.scheme == "http" else 443
    )
