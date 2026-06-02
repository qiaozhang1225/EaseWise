from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Final

APP_TITLE: Final = "EaseWise API"
APP_VERSION: Final = "0.3.0"


def get_database_path() -> Path:
    raw_path = os.getenv("EASEWISE_DB_PATH", "").strip()
    if raw_path:
        return Path(raw_path).expanduser().resolve()
    return (Path(__file__).resolve().parent / "data" / "app.db").resolve()


def get_cors_origins() -> list[str]:
    raw_value = os.getenv("EASEWISE_CORS_ORIGINS", "*")
    origins = [item.strip() for item in raw_value.split(",") if item.strip()]
    return origins or ["*"]


def get_wechat_app_id() -> str:
    return os.getenv("EASEWISE_WECHAT_APP_ID", "").strip()


def get_wechat_app_secret() -> str:
    return os.getenv("EASEWISE_WECHAT_APP_SECRET", "").strip()


def get_wechat_oa_app_id() -> str:
    return os.getenv("EASEWISE_WECHAT_OA_APP_ID", "").strip()


def get_wechat_oa_app_secret() -> str:
    return os.getenv("EASEWISE_WECHAT_OA_APP_SECRET", "").strip()


def get_public_base_url() -> str:
    return os.getenv("EASEWISE_PUBLIC_BASE_URL", "").strip().rstrip("/")


def allow_mock_wechat_login() -> bool:
    return _parse_bool_env("EASEWISE_ALLOW_MOCK_WECHAT_LOGIN", default=False)


def get_initial_points() -> int:
    return _parse_int_env("EASEWISE_INITIAL_POINTS", default=10000, minimum=0)


def get_phone_review_base_points_cost() -> int:
    return _parse_int_env("EASEWISE_PHONE_REVIEW_BASE_POINTS_COST", default=100, minimum=0)


def get_voice_mode() -> str:
    value = os.getenv("EASEWISE_VOICE_MODE", "hybrid").strip().lower()
    return value if value in {"hybrid", "browser", "cloud"} else "hybrid"


def get_voice_provider() -> str:
    value = os.getenv("EASEWISE_TTS_PROVIDER", "aliyun").strip().lower()
    return value or "aliyun"


def get_voice_default_voice_key() -> str:
    return os.getenv("EASEWISE_TTS_DEFAULT_VOICE", "zhiyan_emo").strip() or "zhiyan_emo"


def get_voice_cache_enabled() -> bool:
    return _parse_bool_env("EASEWISE_TTS_CACHE_ENABLED", default=True)


def get_voice_autoplay_default_enabled() -> bool:
    return _parse_bool_env("EASEWISE_VOICE_AUTOPLAY_DEFAULT_ENABLED", default=True)


def get_voice_max_chars_per_request() -> int:
    return _parse_int_env("EASEWISE_TTS_MAX_CHARS", default=1800, minimum=120)


def get_voice_cache_dir() -> Path:
    raw_path = os.getenv("EASEWISE_TTS_CACHE_DIR", "").strip()
    if raw_path:
        return Path(raw_path).expanduser().resolve()
    return (Path(__file__).resolve().parent / "static" / "voice").resolve()


def _get_configured_service_secret(*, provider: str, model: str) -> str | None:
    try:
        from .database import get_enabled_llm_api_key

        configured_key = get_enabled_llm_api_key(provider=provider, model=model)
    except Exception:
        return None
    if not configured_key:
        return None
    secret_value = str(configured_key.get("secret_value") or "").strip()
    return secret_value or None


def _looks_like_bailian_api_key(value: str | None) -> bool:
    return bool(value and value.strip().startswith("sk-"))


def get_bailian_tts_api_key() -> str:
    configured_key = (
        _get_configured_service_secret(provider="aliyun", model="bailian_api_key")
        or _get_configured_service_secret(provider="bailian", model="api_key")
    )
    if configured_key:
        return configured_key
    # Compatibility: early admin UI exposed only tts_app_key, so an sk-* value there
    # is treated as a Bailian/DashScope API key instead of an NLS AppKey.
    aliased_key = _get_configured_service_secret(provider="aliyun", model="tts_app_key")
    if _looks_like_bailian_api_key(aliased_key):
        return aliased_key or ""
    return os.getenv("EASEWISE_TTS_BAILIAN_API_KEY", "").strip() or os.getenv("DASHSCOPE_API_KEY", "").strip()


def get_bailian_tts_model() -> str:
    return os.getenv("EASEWISE_TTS_BAILIAN_MODEL", "cosyvoice-v3-flash").strip() or "cosyvoice-v3-flash"


def get_bailian_tts_endpoint() -> str:
    return os.getenv("EASEWISE_TTS_BAILIAN_ENDPOINT", "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer").strip()


def get_aliyun_tts_app_key() -> str:
    return _get_configured_service_secret(provider="aliyun", model="tts_app_key") or os.getenv("EASEWISE_TTS_ALIYUN_APP_KEY", "").strip()


def get_aliyun_tts_token() -> str:
    return _get_configured_service_secret(provider="aliyun", model="tts_token") or os.getenv("EASEWISE_TTS_ALIYUN_TOKEN", "").strip()


def get_aliyun_nls_access_key_id() -> str:
    return _get_configured_service_secret(provider="aliyun", model="nls_access_key_id") or os.getenv("EASEWISE_TTS_ALIYUN_ACCESS_KEY_ID", "").strip()


def get_aliyun_nls_access_key_secret() -> str:
    return _get_configured_service_secret(provider="aliyun", model="nls_access_key_secret") or os.getenv("EASEWISE_TTS_ALIYUN_ACCESS_KEY_SECRET", "").strip()


def get_aliyun_tts_endpoint() -> str:
    return os.getenv("EASEWISE_TTS_ALIYUN_ENDPOINT", "https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/tts").strip()


def get_tts_timeout_seconds() -> int:
    return _parse_int_env("EASEWISE_TTS_TIMEOUT_SECONDS", default=30, minimum=1)


def get_recharge_packages() -> list[dict[str, Any]]:
    raw_value = os.getenv("EASEWISE_RECHARGE_PACKAGES_JSON", "").strip()
    if not raw_value:
        return []
    try:
        parsed_value = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed_value, list):
        return []
    return [item for item in parsed_value if isinstance(item, dict)]


def get_customer_service_contact_url() -> str | None:
    return _parse_optional_text_env("EASEWISE_CUSTOMER_SERVICE_CONTACT_URL")


def get_customer_service_qr_code_url() -> str | None:
    return _parse_optional_text_env("EASEWISE_CUSTOMER_SERVICE_QR_CODE_URL")


def get_customer_service_guidance_text() -> str:
    return _parse_optional_text_env("EASEWISE_CUSTOMER_SERVICE_GUIDANCE_TEXT") or "联系客服获取充值与服务支持"


def get_compliance_safe_mode_enabled() -> bool:
    return _parse_bool_env("EASEWISE_COMPLIANCE_SAFE_MODE_ENABLED", default=False)


def get_compliance_safe_modules() -> list[str]:
    modules = _parse_csv_env("EASEWISE_COMPLIANCE_SAFE_MODULES")
    return modules or ["almanac", "five_elements"]


def get_compliance_hidden_modules() -> list[str]:
    return _parse_csv_env("EASEWISE_COMPLIANCE_HIDDEN_MODULES")


def get_compliance_hidden_pages() -> list[str]:
    return _parse_csv_env("EASEWISE_COMPLIANCE_HIDDEN_PAGES")


def get_internal_admin_token() -> str:
    return os.getenv("EASEWISE_INTERNAL_ADMIN_TOKEN", "").strip()


def get_auth_token_ttl_hours() -> int:
    return _parse_int_env("EASEWISE_AUTH_TOKEN_TTL_HOURS", default=720, minimum=1)


def _parse_int_env(name: str, *, default: int, minimum: int) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        return max(minimum, int(raw_value))
    except ValueError:
        return default


def _parse_bool_env(name: str, *, default: bool) -> bool:
    raw_value = os.getenv(name, "").strip().lower()
    if not raw_value:
        return default
    return raw_value in {"1", "true", "yes", "on"}


def _parse_optional_text_env(name: str) -> str | None:
    raw_value = os.getenv(name, "")
    text = raw_value.strip()
    return text or None


def _parse_csv_env(name: str) -> list[str]:
    raw_value = os.getenv(name, "")
    return [item.strip() for item in raw_value.split(",") if item.strip()]
