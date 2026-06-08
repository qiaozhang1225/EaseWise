from __future__ import annotations

from typing import Any

from .config import (
    get_compliance_hidden_modules,
    get_compliance_hidden_pages,
    get_compliance_safe_mode_enabled,
    get_compliance_safe_modules,
    get_customer_service_contact_url,
    get_customer_service_guidance_text,
    get_customer_service_qr_code_url,
    get_customer_service_wechat_id,
    get_initial_points,
    get_phone_review_base_points_cost,
    get_recharge_packages,
    get_voice_autoplay_default_enabled,
    get_voice_cache_enabled,
    get_voice_default_voice_key,
    get_voice_max_chars_per_request,
    get_voice_mode,
    get_voice_provider,
)
from .database import list_runtime_config_entries
from .phone_review_view import PUBLIC_ASPECT_ORDER
from features.four_pillars.engine import FOUR_PILLARS_ASPECT_ORDER

GLOBAL_SCOPE_TYPE = "global"
CHANNEL_SCOPE_TYPE = "channel"
DEFAULT_SCOPE_KEY = "default"

DEFAULT_PHONE_REVIEW_ASPECT_ORDER = [
    "career",
    "wealth",
    "love",
    "health",
    "acad",
    "fortune",
    "investment",
    "travel",
    "social",
    "family",
    "personality",
    "fengshui",
]

CONFIG_KEY_POINTS_INITIAL_GRANT = "points.initial_grant"
CONFIG_KEY_RECHARGE_PACKAGES = "recharge.packages"
CONFIG_KEY_PHONE_REVIEW_BASE_POINTS_COST = "phone_review.base_points_cost"
CONFIG_KEY_PHONE_REVIEW_ASPECT_UNLOCK_POINTS_COST = "phone_review.aspect_unlock_points_cost"
CONFIG_KEY_PHONE_REVIEW_FREE_ASPECT_KEYS = "phone_review.free_aspect_keys"
CONFIG_KEY_PHONE_REVIEW_ASPECT_ORDER = "phone_review.aspect_order"
CONFIG_KEY_PHONE_REVIEW_UNLOCK_ENFORCEMENT_ENABLED = "phone_review.unlock_enforcement_enabled"
CONFIG_KEY_FOUR_PILLARS_BASE_POINTS_COST = "four_pillars.base_points_cost"
CONFIG_KEY_FOUR_PILLARS_ASPECT_UNLOCK_POINTS_COST = "four_pillars.aspect_unlock_points_cost"
CONFIG_KEY_FOUR_PILLARS_FREE_ASPECT_KEYS = "four_pillars.free_aspect_keys"
CONFIG_KEY_FOUR_PILLARS_ASPECT_ORDER = "four_pillars.aspect_order"
CONFIG_KEY_FOUR_PILLARS_UNLOCK_ENFORCEMENT_ENABLED = "four_pillars.unlock_enforcement_enabled"
CONFIG_KEY_FOUR_PILLARS_LUCK_CYCLE_POINTS_COST = "four_pillars.luck_cycle_points_cost"
CONFIG_KEY_FOUR_PILLARS_LUCK_YEAR_POINTS_COST = "four_pillars.luck_year_points_cost"
CONFIG_KEY_FOUR_PILLARS_LUCK_GENERATION_ENABLED = "four_pillars.luck_generation_enabled"
CONFIG_KEY_CUSTOMER_SERVICE_CONTACT_URL = "customer_service.contact_url"
CONFIG_KEY_CUSTOMER_SERVICE_WECHAT_ID = "customer_service.wechat_id"
CONFIG_KEY_CUSTOMER_SERVICE_QR_CODE_URL = "customer_service.qr_code_url"
CONFIG_KEY_CUSTOMER_SERVICE_GUIDANCE_TEXT = "customer_service.guidance_text"
CONFIG_KEY_CUSTOMER_SERVICE_QR_GUIDANCE_TEXT = "customer_service.qr_guidance_text"
CONFIG_KEY_CUSTOMER_SERVICE_COPY_BUTTON_TEXT = "customer_service.copy_button_text"
CONFIG_KEY_CUSTOMER_SERVICE_UNCONFIGURED_TEXT = "customer_service.unconfigured_text"
CONFIG_KEY_COMPLIANCE_SAFE_MODE_ENABLED = "compliance.safe_mode_enabled"
CONFIG_KEY_COMPLIANCE_SAFE_MODULES = "compliance.safe_modules"
CONFIG_KEY_COMPLIANCE_HIDDEN_MODULES = "compliance.hidden_modules"
CONFIG_KEY_COMPLIANCE_HIDDEN_PAGES = "compliance.hidden_pages"
CONFIG_KEY_PLATFORM_RECHARGE_ENABLED = "platform.recharge_enabled"
CONFIG_KEY_AGENT_METAPHYSICS_SKILL_ENABLED = "agent.metaphysics_skill_enabled"
CONFIG_KEY_VOICE_MODE = "voice.mode"
CONFIG_KEY_VOICE_AUTOPLAY_DEFAULT_ENABLED = "voice.autoplay_default_enabled"
CONFIG_KEY_VOICE_PROVIDER = "voice.provider"
CONFIG_KEY_VOICE_DEFAULT_VOICE_KEY = "voice.default_voice_key"
CONFIG_KEY_VOICE_CACHE_ENABLED = "voice.cache_enabled"
CONFIG_KEY_VOICE_MAX_CHARS_PER_REQUEST = "voice.max_chars_per_request"
CONFIG_KEY_PROMOTION_NORMAL_THRESHOLD_CENTS = "promotion.normal_threshold_cents"
CONFIG_KEY_PROMOTION_SENIOR_THRESHOLD_CENTS = "promotion.senior_threshold_cents"
CONFIG_KEY_PROMOTION_NORMAL_COMMISSION_RATE = "promotion.normal_commission_rate"
CONFIG_KEY_PROMOTION_SENIOR_COMMISSION_RATE = "promotion.senior_commission_rate"
CONFIG_KEY_PROMOTION_MIN_WITHDRAW_CENTS = "promotion.min_withdraw_cents"
CONFIG_KEY_PROMOTION_ORDER_COMPLETION_DAYS = "promotion.order_completion_days"

CUSTOMER_SERVICE_COPY_DEFAULTS: dict[str, str] = {
    "default": "请添加客服微信，客服会协助你处理相关问题。",
    "recharge_help": "充值订单与手机号、微信 ID 绑定，可跨平台使用。如需协助，请添加客服。",
    "payment_issue": "如果已经扣款或支付状态异常，请添加客服协助核查订单。",
    "points_insufficient": "当前积分不足时，可添加客服协助确认充值或套餐配置。",
    "account_security": "账号密码相关问题需要人工核验，请添加客服协助处理。",
    "promotion_consulting": "推广合作申请、身份开通和规则咨询，可添加客服进一步确认。",
    "review_support": "评测后的后续支持、报告疑问和服务说明，可添加客服咨询。",
}
DEFAULT_CUSTOMER_SERVICE_QR_GUIDANCE_TEXT = "截图或长按保存二维码后，前往微信添加客服。"
DEFAULT_CUSTOMER_SERVICE_COPY_BUTTON_TEXT = "复制微信"
DEFAULT_CUSTOMER_SERVICE_UNCONFIGURED_TEXT = "请先在后台客服配置中填写客服微信号。"


def normalize_scope_type(scope_type: str) -> str:
    normalized_value = scope_type.strip().lower()
    if normalized_value not in {GLOBAL_SCOPE_TYPE, CHANNEL_SCOPE_TYPE}:
        raise ValueError("invalid_scope_type")
    return normalized_value


def normalize_scope_key(scope_key: str) -> str:
    normalized_value = scope_key.strip()
    if not normalized_value:
        raise ValueError("scope_key_required")
    return normalized_value


def normalize_config_key(config_key: str) -> str:
    normalized_value = config_key.strip()
    if not normalized_value:
        raise ValueError("config_key_required")
    return normalized_value


def normalize_channel_key(channel_key: str | None) -> str | None:
    if channel_key is None:
        return None
    normalized_value = channel_key.strip()
    return normalized_value or None


def build_scope_chain(channel_key: str | None = None) -> list[tuple[str, str]]:
    scope_chain = [(GLOBAL_SCOPE_TYPE, DEFAULT_SCOPE_KEY)]
    normalized_channel_key = normalize_channel_key(channel_key)
    if normalized_channel_key:
        scope_chain.append((CHANNEL_SCOPE_TYPE, normalized_channel_key))
    return scope_chain


def resolve_runtime_config_bundle(channel_key: str | None = None) -> dict[str, Any]:
    resolved_bundle: dict[str, Any] = {}
    for scope_type, scope_key in build_scope_chain(channel_key):
        for entry in list_runtime_config_entries(scope_type=scope_type, scope_key=scope_key):
            resolved_bundle[str(entry["config_key"])] = entry.get("value")
    return resolved_bundle


def get_runtime_initial_points() -> int:
    config_bundle = resolve_runtime_config_bundle()
    return _coerce_int(config_bundle.get(CONFIG_KEY_POINTS_INITIAL_GRANT), fallback=get_initial_points(), minimum=0)


def get_runtime_recharge_packages(channel_key: str | None = None) -> list[dict[str, Any]]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_recharge_package_list(config_bundle.get(CONFIG_KEY_RECHARGE_PACKAGES), fallback=get_recharge_packages())


def get_runtime_available_recharge_packages(channel_key: str | None = None) -> list[dict[str, Any]]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    if not _coerce_bool(config_bundle.get(CONFIG_KEY_PLATFORM_RECHARGE_ENABLED), fallback=True):
        return []
    return [item for item in get_runtime_recharge_packages(channel_key) if item.get("enabled", True)]


def get_runtime_phone_review_base_points_cost(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_PHONE_REVIEW_BASE_POINTS_COST), fallback=get_phone_review_base_points_cost(), minimum=0)


def get_runtime_phone_review_aspect_unlock_points_cost(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_PHONE_REVIEW_ASPECT_UNLOCK_POINTS_COST), fallback=50, minimum=0)


def get_runtime_phone_review_aspect_order(channel_key: str | None = None) -> list[str]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    configured_order = _coerce_string_list(config_bundle.get(CONFIG_KEY_PHONE_REVIEW_ASPECT_ORDER), fallback=DEFAULT_PHONE_REVIEW_ASPECT_ORDER)
    valid_keys = set(PUBLIC_ASPECT_ORDER)
    ordered_items = [item for item in configured_order if item in valid_keys]
    for item in PUBLIC_ASPECT_ORDER:
        if item not in ordered_items:
            ordered_items.append(item)
    return ordered_items


def get_runtime_phone_review_free_aspect_keys(channel_key: str | None = None) -> list[str]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    configured_keys = _coerce_string_list(config_bundle.get(CONFIG_KEY_PHONE_REVIEW_FREE_ASPECT_KEYS), fallback=[])
    valid_keys = set(PUBLIC_ASPECT_ORDER)
    return [item for item in configured_keys if item in valid_keys]


def get_runtime_agent_metaphysics_skill_enabled(channel_key: str | None = None) -> bool:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_bool(config_bundle.get(CONFIG_KEY_AGENT_METAPHYSICS_SKILL_ENABLED), fallback=True)


def get_runtime_phone_review_unlock_enforcement_enabled(channel_key: str | None = None) -> bool:
    return True


def get_runtime_four_pillars_base_points_cost(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_BASE_POINTS_COST), fallback=get_runtime_phone_review_base_points_cost(channel_key), minimum=0)


def get_runtime_four_pillars_aspect_unlock_points_cost(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_ASPECT_UNLOCK_POINTS_COST), fallback=get_runtime_phone_review_aspect_unlock_points_cost(channel_key), minimum=0)


def get_runtime_four_pillars_aspect_order(channel_key: str | None = None) -> list[str]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    configured_order = _coerce_string_list(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_ASPECT_ORDER), fallback=FOUR_PILLARS_ASPECT_ORDER)
    valid_keys = set(FOUR_PILLARS_ASPECT_ORDER)
    ordered_items = [item for item in configured_order if item in valid_keys]
    for item in FOUR_PILLARS_ASPECT_ORDER:
        if item not in ordered_items:
            ordered_items.append(item)
    return ordered_items


def get_runtime_four_pillars_free_aspect_keys(channel_key: str | None = None) -> list[str]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    configured_keys = _coerce_string_list(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_FREE_ASPECT_KEYS), fallback=[])
    valid_keys = set(FOUR_PILLARS_ASPECT_ORDER)
    return [item for item in configured_keys if item in valid_keys]


def get_runtime_four_pillars_unlock_enforcement_enabled(channel_key: str | None = None) -> bool:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_bool(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_UNLOCK_ENFORCEMENT_ENABLED), fallback=True)


def get_runtime_four_pillars_luck_cycle_points_cost(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_LUCK_CYCLE_POINTS_COST), fallback=50, minimum=0)


def get_runtime_four_pillars_luck_year_points_cost(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_LUCK_YEAR_POINTS_COST), fallback=20, minimum=0)


def get_runtime_four_pillars_luck_generation_enabled(channel_key: str | None = None) -> bool:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_bool(config_bundle.get(CONFIG_KEY_FOUR_PILLARS_LUCK_GENERATION_ENABLED), fallback=True)


def get_runtime_voice_mode(channel_key: str | None = None) -> str:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    value = _coerce_text(config_bundle.get(CONFIG_KEY_VOICE_MODE), fallback=get_voice_mode()).lower()
    return value if value in {"hybrid", "browser", "cloud"} else "hybrid"


def get_runtime_voice_autoplay_default_enabled(channel_key: str | None = None) -> bool:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_bool(config_bundle.get(CONFIG_KEY_VOICE_AUTOPLAY_DEFAULT_ENABLED), fallback=get_voice_autoplay_default_enabled())


def get_runtime_voice_provider(channel_key: str | None = None) -> str:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_text(config_bundle.get(CONFIG_KEY_VOICE_PROVIDER), fallback=get_voice_provider()).lower()


def get_runtime_voice_default_voice_key(channel_key: str | None = None) -> str:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_text(config_bundle.get(CONFIG_KEY_VOICE_DEFAULT_VOICE_KEY), fallback=get_voice_default_voice_key())


def get_runtime_voice_cache_enabled(channel_key: str | None = None) -> bool:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_bool(config_bundle.get(CONFIG_KEY_VOICE_CACHE_ENABLED), fallback=get_voice_cache_enabled())


def get_runtime_voice_max_chars_per_request(channel_key: str | None = None) -> int:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return _coerce_int(config_bundle.get(CONFIG_KEY_VOICE_MAX_CHARS_PER_REQUEST), fallback=get_voice_max_chars_per_request(), minimum=120)


def get_runtime_customer_service_config(channel_key: str | None = None) -> dict[str, Any]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    legacy_contact = _coerce_optional_text(
        config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_CONTACT_URL),
        fallback=get_customer_service_contact_url(),
    )
    guidance_text = _coerce_text(config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_GUIDANCE_TEXT), fallback=get_customer_service_guidance_text())
    copy_texts = {
        scene_key: _coerce_text(
            config_bundle.get(f"customer_service.copy.{scene_key}"),
            fallback=default_text if scene_key != "default" else guidance_text,
        )
        for scene_key, default_text in CUSTOMER_SERVICE_COPY_DEFAULTS.items()
    }
    if not copy_texts.get("default"):
        copy_texts["default"] = guidance_text or CUSTOMER_SERVICE_COPY_DEFAULTS["default"]
    return {
        "wechat_id": _coerce_optional_text(
            config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_WECHAT_ID),
            fallback=get_customer_service_wechat_id(),
        ),
        "contact_url": legacy_contact,
        "qr_code_url": _coerce_optional_text(config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_QR_CODE_URL), fallback=get_customer_service_qr_code_url()),
        "guidance_text": guidance_text,
        "qr_guidance_text": _coerce_text(config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_QR_GUIDANCE_TEXT), fallback=DEFAULT_CUSTOMER_SERVICE_QR_GUIDANCE_TEXT),
        "copy_button_text": _coerce_text(config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_COPY_BUTTON_TEXT), fallback=DEFAULT_CUSTOMER_SERVICE_COPY_BUTTON_TEXT),
        "unconfigured_text": _coerce_text(config_bundle.get(CONFIG_KEY_CUSTOMER_SERVICE_UNCONFIGURED_TEXT), fallback=DEFAULT_CUSTOMER_SERVICE_UNCONFIGURED_TEXT),
        "copy": copy_texts,
    }


def get_runtime_compliance_config(channel_key: str | None = None) -> dict[str, Any]:
    config_bundle = resolve_runtime_config_bundle(channel_key)
    return {
        "safe_mode_enabled": _coerce_bool(config_bundle.get(CONFIG_KEY_COMPLIANCE_SAFE_MODE_ENABLED), fallback=get_compliance_safe_mode_enabled()),
        "safe_modules": _coerce_string_list(config_bundle.get(CONFIG_KEY_COMPLIANCE_SAFE_MODULES), fallback=get_compliance_safe_modules()),
        "hidden_modules": _coerce_string_list(config_bundle.get(CONFIG_KEY_COMPLIANCE_HIDDEN_MODULES), fallback=get_compliance_hidden_modules()),
        "hidden_pages": _coerce_string_list(config_bundle.get(CONFIG_KEY_COMPLIANCE_HIDDEN_PAGES), fallback=get_compliance_hidden_pages()),
    }


def is_module_enabled(module_key: str, *, channel_key: str | None = None) -> bool:
    normalized_module_key = module_key.strip()
    if not normalized_module_key:
        return False
    compliance_config = get_runtime_compliance_config(channel_key)
    hidden_modules = {item.strip() for item in compliance_config["hidden_modules"] if item.strip()}
    if normalized_module_key in hidden_modules:
        return False
    if compliance_config["safe_mode_enabled"]:
        safe_modules = {item.strip() for item in compliance_config["safe_modules"] if item.strip()}
        return normalized_module_key in safe_modules
    return True


def resolve_public_runtime_config(channel_key: str | None = None) -> dict[str, Any]:
    normalized_channel_key = normalize_channel_key(channel_key)
    customer_service_config = get_runtime_customer_service_config(normalized_channel_key)
    compliance_config = get_runtime_compliance_config(normalized_channel_key)
    return {
        "channel": normalized_channel_key,
        "points": {
            "initial_grant": get_runtime_initial_points(),
        },
        "recharge": {
            "packages": get_runtime_available_recharge_packages(normalized_channel_key),
        },
        "customer_service": customer_service_config,
        "compliance": compliance_config,
        "modules": {
            "phone_review": {
                "enabled": is_module_enabled("phone_review", channel_key=normalized_channel_key),
                "base_points_cost": get_runtime_phone_review_base_points_cost(normalized_channel_key),
                "aspect_unlock_points_cost": get_runtime_phone_review_aspect_unlock_points_cost(normalized_channel_key),
                "free_aspect_keys": get_runtime_phone_review_free_aspect_keys(normalized_channel_key),
                "aspect_order": get_runtime_phone_review_aspect_order(normalized_channel_key),
                "unlock_enforcement_enabled": get_runtime_phone_review_unlock_enforcement_enabled(normalized_channel_key),
            },
            "four_pillars": {
                "enabled": is_module_enabled("four_pillars", channel_key=normalized_channel_key),
                "base_points_cost": get_runtime_four_pillars_base_points_cost(normalized_channel_key),
                "aspect_unlock_points_cost": get_runtime_four_pillars_aspect_unlock_points_cost(normalized_channel_key),
                "free_aspect_keys": get_runtime_four_pillars_free_aspect_keys(normalized_channel_key),
                "aspect_order": get_runtime_four_pillars_aspect_order(normalized_channel_key),
                "unlock_enforcement_enabled": get_runtime_four_pillars_unlock_enforcement_enabled(normalized_channel_key),
                "luck_cycle_points_cost": get_runtime_four_pillars_luck_cycle_points_cost(normalized_channel_key),
                "luck_year_points_cost": get_runtime_four_pillars_luck_year_points_cost(normalized_channel_key),
                "luck_generation_enabled": get_runtime_four_pillars_luck_generation_enabled(normalized_channel_key),
            },
            "agent": {
                "enabled": is_module_enabled("agent", channel_key=normalized_channel_key),
                "base_points_cost": None,
                "metaphysics_skill_enabled": get_runtime_agent_metaphysics_skill_enabled(normalized_channel_key),
            },
            "almanac": {
                "enabled": is_module_enabled("almanac", channel_key=normalized_channel_key),
                "base_points_cost": None,
            },
            "voice": {
                "enabled": is_module_enabled("voice", channel_key=normalized_channel_key),
                "mode": get_runtime_voice_mode(normalized_channel_key),
                "autoplay_default_enabled": get_runtime_voice_autoplay_default_enabled(normalized_channel_key),
                "provider": get_runtime_voice_provider(normalized_channel_key),
                "default_voice_key": get_runtime_voice_default_voice_key(normalized_channel_key),
                "cache_enabled": get_runtime_voice_cache_enabled(normalized_channel_key),
                "max_chars_per_request": get_runtime_voice_max_chars_per_request(normalized_channel_key),
            },
        },
    }


def _coerce_int(value: Any, *, fallback: int, minimum: int) -> int:
    try:
        if value is None:
            return fallback
        return max(minimum, int(value))
    except (TypeError, ValueError):
        return fallback


def _coerce_bool(value: Any, *, fallback: bool) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized_value = value.strip().lower()
        if normalized_value in {"1", "true", "yes", "on"}:
            return True
        if normalized_value in {"0", "false", "no", "off"}:
            return False
    return fallback


def _coerce_text(value: Any, *, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _coerce_optional_text(value: Any, *, fallback: str | None) -> str | None:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _coerce_string_list(value: Any, *, fallback: list[str]) -> list[str]:
    if value is None:
        return fallback
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return fallback


def _coerce_recharge_package_list(value: Any, *, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_items = value if isinstance(value, list) else fallback
    if not isinstance(raw_items, list):
        return []

    packages: list[dict[str, Any]] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            continue
        package_key = _coerce_text(item.get("package_key") or item.get("key") or item.get("id"), fallback="")
        if not package_key:
            continue
        title = _coerce_text(item.get("title") or item.get("name"), fallback=package_key)
        description = _coerce_optional_text(item.get("description"), fallback=None)
        price_cents = _coerce_int(item.get("price_cents", item.get("amount_cents")), fallback=0, minimum=0)
        points_amount = _coerce_int(item.get("points_amount", item.get("points")), fallback=0, minimum=0)
        bonus_points = _coerce_int(item.get("bonus_points"), fallback=0, minimum=0)
        sort_order = _coerce_int(item.get("sort_order"), fallback=index, minimum=0)
        enabled = _coerce_bool(item.get("enabled"), fallback=True)
        total_points = points_amount + bonus_points
        if price_cents <= 0 or total_points <= 0:
            continue
        packages.append({
            "package_key": package_key,
            "title": title,
            "description": description,
            "price_cents": price_cents,
            "points_amount": points_amount,
            "bonus_points": bonus_points,
            "total_points": total_points,
            "enabled": enabled,
            "sort_order": sort_order,
        })

    packages.sort(key=lambda item: (int(item.get("sort_order", 0)), int(item.get("price_cents", 0)), str(item.get("package_key", ""))))
    return packages
