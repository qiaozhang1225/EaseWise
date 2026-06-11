from __future__ import annotations

import base64
import binascii
import html
import re
import secrets
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, Cookie, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from product.backend.llm import get_deepseek_governor_status, load_env_file
from features.almanac.engine import build_almanac_for_date, build_today_almanac
from features.four_pillars.engine import FOUR_PILLARS_ASPECT_ORDER, FOUR_PILLARS_ASPECTS, build_dayun_facts, build_four_pillars_review, build_liunian_facts
from features.four_pillars.rendering import (
    build_four_pillars_product_view,
    build_product_review_aspects_render as build_four_pillars_aspects_render,
    build_product_review_core_render as build_four_pillars_core_render,
    render_dayun_from_package as render_four_pillars_dayun,
    render_liunian_from_package as render_four_pillars_liunian,
)
from features.phone_qimen.scoring.total_score.engine import load_rules, score_phone
from features.phone_qimen.scoring.total_score.bundle import build_scoring_bundle

from .agent import build_agent_reply
from .auth import build_session_expiry, exchange_wechat_code, hash_access_token, hash_password, issue_access_token, require_authenticated_user, require_authenticated_user_with_token_hash, require_internal_admin_access, require_registered_user, resolve_authenticated_user, verify_password
from .config import APP_TITLE, APP_VERSION, allow_mock_wechat_login, get_cors_origins, get_database_path, get_public_base_url, get_uploads_dir, get_wechat_oa_app_id
from .database import InsufficientPointsError, adjust_points, adjust_rebate_points, claim_points_from_link, complete_recharge_order_manually, complete_review, complete_review_with_message, complete_usage_record, count_internal_phone_qimen_reviews, count_points_claim_links, count_points_claim_records, count_users, create_payment_transaction, create_phone_user, create_points_claim_link, create_recharge_order, create_refund_request, create_review_aspect_unlock, create_review_with_charge, create_session, create_usage_record, delete_llm_api_key, disable_points_claim_link, ensure_schema, fail_review, fail_usage_record, get_dashboard_summary, get_internal_phone_qimen_review, get_internal_phone_qimen_summary as get_internal_phone_qimen_summary_data, get_internal_user, get_latest_payment_transaction_for_order, get_llm_api_key, get_phone_identity_by_normalized_phone, get_points_account, get_points_claim_link, get_points_claim_link_by_code, get_primary_phone_identity_by_user_id, get_promotion_application, get_promotion_commission, get_promotion_rules, get_promotion_withdrawal, get_recharge_order, get_review, get_usage_record, get_user, get_user_current_week_points_claim, list_internal_phone_qimen_reviews, list_llm_api_keys, list_payment_transactions_for_order, list_points_claim_links, list_points_claim_records, list_points_ledger, list_promotion_applications, list_promotion_commissions, list_promotion_withdrawals, list_recharge_orders, list_recent_recharge_orders_for_user, list_refund_requests_for_order, list_review_aspect_unlocks, list_reviews, list_runtime_config_entries, list_usage_records, list_users, list_voice_usage_records_for_review, mark_phone_identity_login, mark_promotion_withdrawal_paid, record_points_claim_duplicate_link_visit, refund_points, revoke_session_by_token_hash, retry_promotion_withdrawal_payout, retry_refund_request, review_promotion_application, review_promotion_withdrawal, review_recharge_order, review_refund_request, settle_payment_transaction, update_initial_points_config, update_phone_identity_password, update_review_generation_payload, update_review_progress, update_review_score_template, update_usage_record_llm_metrics, update_user_identity, update_user_profile, update_user_promoter_parent, update_user_status, upsert_llm_api_key, upsert_runtime_config_entry, upsert_wechat_user
from .database import (
    complete_four_pillars_review_with_message,
    complete_four_pillars_luck_render,
    count_internal_four_pillars_reviews,
    create_four_pillars_aspect_unlock,
    create_four_pillars_luck_render_request,
    create_four_pillars_review_with_charge,
    fail_four_pillars_luck_render,
    fail_four_pillars_review,
    get_four_pillars_review,
    get_four_pillars_luck_render,
    get_four_pillars_luck_render_by_id,
    get_internal_four_pillars_review,
    get_internal_four_pillars_summary as get_internal_four_pillars_summary_data,
    list_four_pillars_aspect_unlocks,
    list_four_pillars_luck_renders,
    list_four_pillars_reviews,
    list_internal_four_pillars_reviews,
    update_four_pillars_review_generation_payload,
    update_four_pillars_review_progress,
    update_four_pillars_review_score_template,
)
from .phone_review_view import PUBLIC_ASPECT_ORDER, build_phone_review_product_view
from .payments import create_payment_request
from .product_review import build_product_review_aspects_render, build_product_review_core_render
from .runtime_config import get_runtime_agent_metaphysics_skill_enabled, get_runtime_available_recharge_packages, get_runtime_four_pillars_aspect_order, get_runtime_four_pillars_aspect_unlock_points_cost, get_runtime_four_pillars_base_points_cost, get_runtime_four_pillars_free_aspect_keys, get_runtime_four_pillars_luck_cycle_points_cost, get_runtime_four_pillars_luck_generation_enabled, get_runtime_four_pillars_luck_year_points_cost, get_runtime_four_pillars_unlock_enforcement_enabled, get_runtime_initial_points, get_runtime_phone_review_aspect_order, get_runtime_phone_review_aspect_unlock_points_cost, get_runtime_phone_review_base_points_cost, get_runtime_phone_review_free_aspect_keys, get_runtime_phone_review_unlock_enforcement_enabled, get_runtime_voice_cache_enabled, get_runtime_voice_default_voice_key, get_runtime_voice_max_chars_per_request, get_runtime_voice_provider, is_module_enabled, normalize_channel_key, normalize_config_key, normalize_scope_key, normalize_scope_type, resolve_public_runtime_config
from .schemas import AdminReviewRequest, AgentReplyRequest, AgentReplyResponse, AlmanacResponse, AuthLoginResponse, AvatarUploadRequest, ComplianceConfigResponse, CurrentUserResponse, CustomerServiceConfigResponse, CustomerServiceQrCodeUploadRequest, DashboardResponse, DashboardMetricResponse, DashboardSectionResponse, InternalPhoneQimenAspectUnlockRecordResponse, InternalPhoneQimenReviewDetailResponse, InternalPhoneQimenReviewItemResponse, InternalPhoneQimenReviewListResponse, InternalPhoneQimenSummaryResponse, InternalUserAdminSummaryResponse, InternalUserListResponse, InternalUserResponse, LlmApiKeyListResponse, LlmApiKeyResponse, LlmApiKeyUpsertRequest, LlmConcurrencyStatusResponse, ManualPointsAdjustRequest, ManualPointsAdjustResponse, ModuleRuntimeConfigResponse, PasswordChangeRequest, PasswordChangeResponse, PaymentNotifyResponse, PaymentTransactionCreateRequest, PaymentTransactionResponse, PhonePasswordLoginRequest, PhonePasswordRegisterRequest, PhoneStatusRequest, PhoneStatusResponse, PointsAccountResponse, PointsClaimLinkCreateRequest, PointsClaimLinkDisableRequest, PointsClaimLinkListResponse, PointsClaimLinkResponse, PointsClaimRecordListResponse, PointsClaimRecordResponse, PointsClaimSubmitResponse, PointsLedgerEntryResponse, PointsLedgerListResponse, PublicPointsClaimLinkResponse, PublicRuntimeConfigResponse, PromotionApplicationListResponse, PromotionApplicationResponse, PromotionCommissionListResponse, PromotionCommissionResponse, PromotionRulesResponse, PromotionRulesUpdateRequest, PromotionWithdrawalListResponse, PromotionWithdrawalPayoutRequest, PromotionWithdrawalResponse, RebatePointsAdjustRequest, RebatePointsAdjustResponse, RebatePointsAccountResponse, RefundCreateRequest, RefundRequestResponse, RefundRetryRequest, RechargeOrderCreateRequest, RechargeOrderListResponse, RechargeOrderManualCompleteRequest, RechargeOrderManualCompleteResponse, RechargeOrderPaymentStatusResponse, RechargeOrderResponse, RechargeOrderReviewRequest, RechargeOrderReviewResponse, RechargeOrderSummaryResponse, RechargePackageListResponse, RechargePackageResponse, ReviewAspectResponse, ReviewAspectUnlockListResponse, ReviewAspectUnlockRequest, ReviewAspectUnlockResponse, ReviewBoardResponse, ReviewCreateRequest, ReviewListResponse, ReviewPhoneSummaryResponse, ReviewRecordResponse, ReviewStabilityDetailResponse, ReviewSummaryResponse, RuntimeConfigEntryResponse, RuntimeConfigListResponse, RuntimeConfigSchemaItemResponse, RuntimeConfigSchemaResponse, RuntimeConfigUpsertRequest, RuntimeInitialPointsUpdateRequest, RuntimeInitialPointsUpdateResponse, RuntimeModulesConfigResponse, RuntimePointsConfigResponse, RuntimeRechargeConfigResponse, UsageRecordDetailResponse, UsageRecordListResponse, UsageRecordResponse, UserIdentityUpdateRequest, UserPromoterParentUpdateRequest, UserProfileUpdateRequest, UserResponse, UserStatusUpdateRequest, VoiceNarrationRequest, VoiceNarrationResponse, VoiceRuntimeConfigResponse, WeChatLoginRequest
from .schemas import (
    FourPillarsAspectUnlockListResponse,
    FourPillarsAspectUnlockResponse,
    FourPillarsAspectResponse,
    FourPillarsLuckCycleListResponse,
    FourPillarsLuckRenderRecordResponse,
    FourPillarsReviewCreateRequest,
    FourPillarsReviewListResponse,
    FourPillarsReviewRecordResponse,
    FourPillarsReviewSummaryResponse,
    FourPillarsSummaryResponse,
    InternalFourPillarsAspectUnlockRecordResponse,
    InternalFourPillarsReviewDetailResponse,
    InternalFourPillarsReviewItemResponse,
    InternalFourPillarsReviewListResponse,
    InternalFourPillarsSummaryResponse,
)
from .tts import VoiceProviderUnavailableError, VoiceSynthesisError, synthesize_voice_audio
from .wechat_h5 import STATE_COOKIE_NAME, build_oauth_state, build_wechat_oauth_authorize_url, exchange_h5_oauth_code, h5_oauth_is_configured, is_wechat_browser

PHONE_PATTERN = re.compile(r"^\d{11}$")
MAINLAND_MOBILE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
TESTER_PAGE_PATH = Path(__file__).resolve().parent / "static" / "tester.html"
AVATAR_DATA_URL_PATTERN = re.compile(r"^data:image/(?P<kind>png|jpe?g|webp);base64,(?P<data>.+)$", re.DOTALL)
MAX_AVATAR_UPLOAD_BYTES = 1_500_000
load_env_file()
RULES = load_rules()
PHONE_REVIEW_BASE_SCENE = "phone_review_base"
PHONE_REVIEW_BASE_REFUND_BIZ_TYPE = "phone_review_base_refund"
PHONE_REVIEW_ASPECT_UNLOCK_SCENE = "phone_review_aspect_unlock"
FOUR_PILLARS_REVIEW_BASE_SCENE = "four_pillars_review_base"
FOUR_PILLARS_REVIEW_BASE_REFUND_BIZ_TYPE = "four_pillars_review_base_refund"
FOUR_PILLARS_ASPECT_UNLOCK_SCENE = "four_pillars_aspect_unlock"
FOUR_PILLARS_LUCK_CYCLE_RENDER_SCENE = "four_pillars_luck_cycle_render"
FOUR_PILLARS_LUCK_YEAR_RENDER_SCENE = "four_pillars_luck_year_render"
FOUR_PILLARS_LUCK_RENDER_REFUND_BIZ_TYPE = "four_pillars_luck_render_refund"
VOICE_TTS_SCENE = "voice_tts"
REVIEW_PREVIEW_ASPECT_THRESHOLD = 4
PHONE_QIMEN_ASPECT_LABELS = {
    "career": "事业",
    "wealth": "财富",
    "love": "感情",
    "health": "健康",
    "acad": "学业",
    "fortune": "运势",
    "investment": "投资",
    "travel": "出行",
    "social": "社交",
    "family": "家庭",
    "personality": "性格",
    "fengshui": "风水",
}
FOUR_PILLARS_ASPECT_LABELS = {item["aspect_key"]: item["title"] for item in FOUR_PILLARS_ASPECTS}
_RUNTIME_CONFIG_SCHEMA_ITEMS: list[dict[str, object]] = [
    {"config_key": "recharge.packages", "label": "充值套餐", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": True, "description": "充值金额与积分套餐列表"},
    {"config_key": "points.initial_grant", "label": "注册初始积分", "value_type": "int", "default_value": 10000, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": False, "description": "注册用户默认发放积分"},
    {"config_key": "customer_service.wechat_id", "label": "客服微信号", "value_type": "string", "default_value": None, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 10, "high_risk": False, "description": "前台联系客服弹窗复制的客服微信号"},
    {"config_key": "customer_service.contact_url", "label": "旧客服联系方式", "value_type": "string", "default_value": None, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 20, "advanced": True, "admin_hidden": True, "high_risk": False, "description": "历史兼容字段，仅作为客服微信号 fallback"},
    {"config_key": "customer_service.qr_code_url", "label": "客服二维码", "value_type": "string", "default_value": None, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 30, "admin_hidden": True, "high_risk": False, "description": "客服二维码图片地址"},
    {"config_key": "customer_service.guidance_text", "label": "旧客服说明文案", "value_type": "string", "default_value": "联系客服获取充值与服务支持", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 40, "advanced": True, "admin_hidden": True, "high_risk": False, "description": "历史兼容字段，仅作为默认客服说明 fallback"},
    {"config_key": "customer_service.qr_guidance_text", "label": "二维码提示文案", "value_type": "string", "default_value": "截图或长按保存二维码后，前往微信添加客服。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 50, "high_risk": False, "description": "客服二维码下方的操作提示"},
    {"config_key": "customer_service.copy_button_text", "label": "复制按钮文案", "value_type": "string", "default_value": "复制微信", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 60, "high_risk": False, "description": "客服微信号复制按钮文案"},
    {"config_key": "customer_service.unconfigured_text", "label": "未配置提示", "value_type": "string", "default_value": "请先在后台客服配置中填写客服微信号。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 70, "high_risk": False, "description": "客服微信号为空时展示的提示"},
    {"config_key": "customer_service.copy.default", "label": "默认客服文案", "value_type": "string", "default_value": "请添加客服微信，客服会协助你处理相关问题。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 100, "high_risk": False, "description": "未指定业务场景时的客服弹窗说明"},
    {"config_key": "customer_service.copy.recharge_help", "label": "充值协助文案", "value_type": "string", "default_value": "充值订单与手机号、微信 ID 绑定，可跨平台使用。如需协助，请添加客服。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 110, "high_risk": False, "description": "充值身份协助、充值页底部客服入口文案"},
    {"config_key": "customer_service.copy.payment_issue", "label": "支付异常文案", "value_type": "string", "default_value": "如果已经扣款或支付状态异常，请添加客服协助核查订单。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 120, "high_risk": False, "description": "支付处理中、支付异常、扣款疑问入口文案"},
    {"config_key": "customer_service.copy.points_insufficient", "label": "积分不足文案", "value_type": "string", "default_value": "当前积分不足时，可添加客服协助确认充值或套餐配置。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 130, "high_risk": False, "description": "评测积分不足、专项解锁积分不足入口文案"},
    {"config_key": "customer_service.copy.account_security", "label": "账号安全文案", "value_type": "string", "default_value": "账号密码相关问题需要人工核验，请添加客服协助处理。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 140, "high_risk": False, "description": "忘记密码、修改密码人工核验入口文案"},
    {"config_key": "customer_service.copy.promotion_consulting", "label": "推广咨询文案", "value_type": "string", "default_value": "推广合作申请、身份开通和规则咨询，可添加客服进一步确认。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 150, "high_risk": False, "description": "推广合作咨询入口文案"},
    {"config_key": "customer_service.copy.review_support", "label": "评测后续支持文案", "value_type": "string", "default_value": "评测后的后续支持、报告疑问和服务说明，可添加客服咨询。", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "客服配置", "sort_order": 160, "high_risk": False, "description": "评测结果页后续支持入口文案"},
    {"config_key": "platform.recharge_enabled", "label": "充值总开关", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": True, "description": "控制前台是否开放充值入口"},
    {"config_key": "compliance.safe_mode_enabled", "label": "安全模式", "value_type": "bool", "default_value": False, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "安全与合规", "sort_order": 10, "high_risk": True, "description": "开启后仅允许安全模式允许功能继续可用"},
    {"config_key": "compliance.safe_modules", "label": "安全模式允许功能", "value_type": "json", "default_value": ["almanac", "five_elements"], "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "安全与合规", "sort_order": 20, "high_risk": True, "description": "安全模式开启时仍允许访问的功能", "input_options": [{"value": "phone_review", "label": "手机号评测"}, {"value": "four_pillars", "label": "四柱八字"}, {"value": "voice", "label": "语音播报"}, {"value": "almanac", "label": "黄历"}, {"value": "agent", "label": "智能体"}, {"value": "five_elements", "label": "五行查询"}]},
    {"config_key": "compliance.hidden_modules", "label": "强制隐藏功能", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "安全与合规", "sort_order": 30, "high_risk": True, "description": "无论安全模式是否开启，都强制隐藏的功能", "input_options": [{"value": "phone_review", "label": "手机号评测"}, {"value": "four_pillars", "label": "四柱八字"}, {"value": "voice", "label": "语音播报"}, {"value": "almanac", "label": "黄历"}, {"value": "agent", "label": "智能体"}, {"value": "five_elements", "label": "五行查询"}]},
    {"config_key": "compliance.hidden_pages", "label": "隐藏页面列表", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "安全与合规", "high_risk": True, "description": "被隐藏的页面", "admin_hidden": True},
    {"config_key": "llm.concurrency.backend", "label": "LLM 并发 backend", "value_type": "string", "default_value": "memory", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "DeepSeek 并发治理", "sort_order": 10, "high_risk": True, "description": "memory 适合单进程；redis 适合多进程或多服务器", "input_options": [{"value": "memory", "label": "memory"}, {"value": "redis", "label": "redis"}]},
    {"config_key": "llm.deepseek.default_key_max_concurrency", "label": "默认单 Key 并发", "value_type": "int", "default_value": 450, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "DeepSeek 并发治理", "sort_order": 20, "high_risk": True, "description": "DeepSeek 默认 500 并发额度，建议保留余量使用 450"},
    {"config_key": "llm.deepseek.default_cooldown_seconds", "label": "429 冷却秒数", "value_type": "int", "default_value": 60, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "DeepSeek 并发治理", "sort_order": 30, "high_risk": False, "description": "某个 Key 被 429 后暂停使用的时间"},
    {"config_key": "llm.deepseek.foreground_priority_enabled", "label": "前台优先", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "DeepSeek 并发治理", "sort_order": 40, "high_risk": False, "description": "前台用户等待请求优先获取释放的令牌"},
    {"config_key": "llm.deepseek.background_prefetch_enabled", "label": "后台预热", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "DeepSeek 并发治理", "sort_order": 50, "high_risk": False, "description": "允许手机号和四柱专项等后台预热请求"},
    {"config_key": "llm.deepseek.background_max_concurrency_ratio", "label": "后台预热占比", "value_type": "float", "default_value": 0.3, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "DeepSeek 并发治理", "sort_order": 60, "high_risk": True, "description": "后台预热最多占用总并发的比例，最高 0.8"},
    {"config_key": "phone_review.base_points_cost", "label": "基础评测消耗", "value_type": "int", "default_value": 100, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "数字奇门手机号评测", "sort_order": 10, "high_risk": False, "description": "手机号评测基础积分消耗"},
    {"config_key": "phone_review.aspect_unlock_points_cost", "label": "专项解锁消耗", "value_type": "int", "default_value": 50, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "数字奇门手机号评测", "sort_order": 20, "high_risk": False, "description": "单个专项解锁积分"},
    {"config_key": "phone_review.free_aspect_keys", "label": "免费专项", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "数字奇门手机号评测", "sort_order": 30, "high_risk": False, "description": "不消耗积分的专项"},
    {"config_key": "phone_review.aspect_order", "label": "专项顺序", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "数字奇门手机号评测", "sort_order": 40, "high_risk": False, "description": "手机号评测专项展示顺序"},
    {"config_key": "phone_review.unlock_enforcement_enabled", "label": "未解锁内容隐藏", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "数字奇门手机号评测", "sort_order": 50, "high_risk": True, "description": "是否强制未解锁专项隐藏内容", "admin_hidden": True},
    {"config_key": "four_pillars.base_points_cost", "label": "基础评测消耗", "value_type": "int", "default_value": 100, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 10, "high_risk": False, "description": "四柱八字基础评测积分消耗"},
    {"config_key": "four_pillars.aspect_unlock_points_cost", "label": "专项解锁消耗", "value_type": "int", "default_value": 50, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 20, "high_risk": False, "description": "四柱八字单个专项解锁积分"},
    {"config_key": "four_pillars.free_aspect_keys", "label": "免费专项", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 30, "high_risk": False, "description": "四柱八字不消耗积分的专项", "input_options": [{"value": item["aspect_key"], "label": item["title"]} for item in FOUR_PILLARS_ASPECTS]},
    {"config_key": "four_pillars.aspect_order", "label": "专项顺序", "value_type": "json", "default_value": FOUR_PILLARS_ASPECT_ORDER, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 40, "high_risk": False, "description": "四柱八字专项展示顺序", "input_options": [{"value": item["aspect_key"], "label": item["title"]} for item in FOUR_PILLARS_ASPECTS]},
    {"config_key": "four_pillars.unlock_enforcement_enabled", "label": "未解锁内容隐藏", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 50, "high_risk": True, "description": "是否强制未解锁专项隐藏内容", "admin_hidden": True},
    {"config_key": "four_pillars.luck_cycle_points_cost", "label": "大运综评消耗", "value_type": "int", "default_value": 50, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 60, "high_risk": False, "description": "单个大运综评生成积分消耗"},
    {"config_key": "four_pillars.luck_year_points_cost", "label": "流年单年消耗", "value_type": "int", "default_value": 20, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 70, "high_risk": False, "description": "单个流年年份生成积分消耗"},
    {"config_key": "four_pillars.luck_generation_enabled", "label": "流年大运生成开关", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "功能管理", "admin_group": "功能管理", "admin_section": "四柱八字评测", "sort_order": 80, "high_risk": True, "description": "是否允许前台按需生成大运综评和流年单年内容"},
    {"config_key": "agent.metaphysics_skill_enabled", "label": "智能体玄学技能开关", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "智能体", "high_risk": True, "description": "仅控制智能体的玄学技能", "admin_hidden": True},
    {"config_key": "voice.mode", "label": "语音播报模式", "value_type": "string", "default_value": "hybrid", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "语音播报", "sort_order": 10, "advanced": True, "high_risk": False, "description": "hybrid / browser / cloud"},
    {"config_key": "voice.autoplay_default_enabled", "label": "语音默认自动播报", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "语音播报", "sort_order": 20, "high_risk": False, "description": "控制前台新用户是否默认自动播报"},
    {"config_key": "voice.provider", "label": "语音合成供应商", "value_type": "string", "default_value": "aliyun", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "语音播报", "sort_order": 30, "advanced": True, "high_risk": False, "description": "当前支持 aliyun / bailian，检测到百炼 API Key 时优先走百炼语音"},
    {"config_key": "voice.default_voice_key", "label": "默认音色", "value_type": "string", "default_value": "zhiyan_emo", "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "语音播报", "sort_order": 40, "high_risk": False, "description": "云 TTS 默认 voice key，知燕多情感对应 zhiyan_emo"},
    {"config_key": "voice.cache_enabled", "label": "语音缓存", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "语音播报", "sort_order": 50, "advanced": True, "high_risk": False, "description": "同文案同音色复用已生成音频"},
    {"config_key": "voice.max_chars_per_request", "label": "单次播报最大字数", "value_type": "int", "default_value": 1800, "scope_type": "global", "scope_key": "default", "group": "系统配置", "admin_group": "系统配置", "admin_section": "语音播报", "sort_order": 60, "advanced": True, "high_risk": False, "description": "超过后服务端会拒绝生成语音"},
    {"config_key": "promotion.normal_threshold_cents", "label": "推广大使门槛", "value_type": "int", "default_value": 39800, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "推广大使申请门槛"},
    {"config_key": "promotion.senior_threshold_cents", "label": "VIP 推广大使门槛", "value_type": "int", "default_value": 398000, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "VIP 推广大使申请门槛"},
    {"config_key": "promotion.normal_commission_rate", "label": "推广大使返佣比例", "value_type": "float", "default_value": 0.1, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "推广大使返佣比例"},
    {"config_key": "promotion.senior_commission_rate", "label": "VIP 返佣比例", "value_type": "float", "default_value": 0.2, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "VIP 推广大使返佣比例"},
    {"config_key": "promotion.min_withdraw_cents", "label": "最低提现门槛", "value_type": "int", "default_value": 3000, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "最低提现金额"},
    {"config_key": "promotion.order_completion_days", "label": "订单完成判定天数", "value_type": "int", "default_value": 7, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": True, "description": "充值订单完成判定天数"},
]



def startup() -> None:
    ensure_schema()


def index() -> FileResponse:
    return FileResponse(TESTER_PAGE_PATH)


def h5_wechat_openid_test(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    mock_openid: str | None = None,
    oauth_state: str | None = Cookie(default=None, alias=STATE_COOKIE_NAME),
):
    if allow_mock_wechat_login() and mock_openid:
        return HTMLResponse(_render_h5_openid_page(title="H5 微信 OpenID 测试页", status="mock_success", body=f"当前为 mock 模式，展示的不是微信真实 OpenID。<br><br><code>{html.escape(mock_openid)}</code>", footnote="要验证真实 H5 微信 OpenID，必须使用微信公众号网页授权，并且在微信内打开。"))

    if code:
        if not state or not oauth_state or state != oauth_state:
            return HTMLResponse(_render_h5_openid_page(title="H5 微信 OpenID 测试页", status="invalid_state", body="回调 state 校验失败，已拒绝本次 H5 OpenID 提取。请重新打开页面重试。", footnote="这是为了避免错误回调或重复回调。"), status_code=400)
        try:
            result = exchange_h5_oauth_code(code)
        except HTTPException as exc:
            return HTMLResponse(_render_h5_openid_page(title="H5 微信 OpenID 测试页", status="oauth_exchange_failed", body=f"微信网页授权换取 OpenID 失败：<br><br><code>{html.escape(str(exc.detail))}</code>", footnote="请检查公众号 AppID / Secret、网页授权域名，以及当前页面是否在微信内打开。"), status_code=exc.status_code)
        response = HTMLResponse(_render_h5_openid_page(title="H5 微信 OpenID 测试页", status="oauth_success", body=f"已成功获取 H5 网页授权 OpenID：<br><br><code>{html.escape(result.openid)}</code>", footnote="注意：这里拿到的是微信公众号 H5 OpenID，不是小程序 OpenID。二者按 AppID 维度区分。"))
        response.delete_cookie(STATE_COOKIE_NAME)
        return response

    if not h5_oauth_is_configured():
        return HTMLResponse(_render_h5_openid_page(title="H5 微信 OpenID 测试页", status="not_configured", body=(
            "当前服务还没有配置 H5 微信网页授权所需参数，所以这个页面现在无法自动获取真实微信 OpenID。<br><br>"
            "需要补齐：<br>"
            "1. 公众号 `AppID`<br>"
            "2. 公众号 `AppSecret`<br>"
            "3. `EASEWISE_PUBLIC_BASE_URL`，并使用可访问的正式域名，而不是裸 IP<br>"
            "4. 微信后台配置 `网页授权域名`"
        ), footnote="如果你要验证小程序 OpenID，请走小程序 `wx.login -> code2Session`，不要用纯 H5 页面代替。"))

    if not is_wechat_browser(request.headers.get("user-agent")):
        return HTMLResponse(_render_h5_openid_page(title="H5 微信 OpenID 测试页", status="not_in_wechat", body="当前页面不是在微信内打开，所以无法触发微信公众号网页授权拿 OpenID。", footnote="请把页面链接发到微信里，从微信客户端内打开后再测试。"))

    state_token = build_oauth_state()
    response = RedirectResponse(build_wechat_oauth_authorize_url(state_token), status_code=302)
    response.set_cookie(STATE_COOKIE_NAME, state_token, max_age=600, httponly=True, samesite="Lax")
    return response


def health() -> dict[str, str]:
    return {"status": "ok", "database": str(get_database_path())}


def get_internal_dashboard(
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    channel: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> DashboardResponse:
    dashboard = get_dashboard_summary(date_from=date_from, date_to=date_to, channel=channel)
    llm_status = get_deepseek_governor_status()
    dashboard_sections = list(dashboard.get("sections", []))
    dashboard_sections.append(_build_llm_dashboard_section(llm_status))
    return DashboardResponse(
        generated_at=str(dashboard["generated_at"]),
        revenue=dict(dashboard.get("revenue", {})),
        users=dict(dashboard.get("users", {})),
        orders=dict(dashboard.get("orders", {})),
        promotion=dict(dashboard.get("promotion", {})),
        llm=dict(llm_status),
        sections=[
            DashboardSectionResponse(
                title=str(section["title"]),
                summary=section.get("summary"),
                metrics=[
                    DashboardMetricResponse(
                        label=str(metric["label"]),
                        value=metric["value"],
                        display_value=str(metric["display_value"]),
                        unit=metric.get("unit"),
                        trend_value=metric.get("trend_value"),
                        trend_label=metric.get("trend_label"),
                    )
                    for metric in section.get("metrics", [])
                ],
            )
            for section in dashboard_sections
        ],
    )


def _build_llm_dashboard_section(llm_status: dict[str, Any]) -> dict[str, Any]:
    total_capacity = int(llm_status.get("total_capacity") or 0)
    global_inflight = int(llm_status.get("global_inflight") or 0)
    return {
        "title": "LLM 运行",
        "summary": "DeepSeek key 池、前后台等待和近 1 小时限流状态",
        "metrics": [
            {
                "label": "DeepSeek 并发",
                "value": global_inflight,
                "display_value": f"{global_inflight} / {total_capacity}",
                "unit": "请求",
            },
            {"label": "前台等待", "value": int(llm_status.get("foreground_waiting") or 0), "display_value": str(llm_status.get("foreground_waiting") or 0), "unit": "个"},
            {"label": "后台等待", "value": int(llm_status.get("background_waiting") or 0), "display_value": str(llm_status.get("background_waiting") or 0), "unit": "个"},
            {"label": "启用 Key", "value": int(llm_status.get("enabled_key_count") or 0), "display_value": str(llm_status.get("enabled_key_count") or 0), "unit": "个"},
            {"label": "近1小时429", "value": int(llm_status.get("recent_429_count") or 0), "display_value": str(llm_status.get("recent_429_count") or 0), "unit": "次"},
            {"label": "近1小时超时", "value": int(llm_status.get("recent_timeout_count") or 0), "display_value": str(llm_status.get("recent_timeout_count") or 0), "unit": "次"},
            {"label": "平均等待", "value": int(llm_status.get("avg_wait_ms") or 0), "display_value": f"{int(llm_status.get('avg_wait_ms') or 0)} ms", "unit": None},
            {"label": "平均响应", "value": int(llm_status.get("avg_duration_ms") or 0), "display_value": f"{int(llm_status.get('avg_duration_ms') or 0)} ms", "unit": None},
            {"label": "Backend", "value": 1 if str(llm_status.get("backend") or "memory") == "redis" else 0, "display_value": str(llm_status.get("backend") or "memory"), "unit": None},
        ],
    }


def login_with_wechat(payload: WeChatLoginRequest, request: Request) -> AuthLoginResponse:
    exchange = exchange_wechat_code(payload.code)
    now_text = _utc_now()

    try:
        user = upsert_wechat_user(
            appid=exchange.appid,
            openid=exchange.openid,
            unionid=exchange.unionid,
            session_key=exchange.session_key,
            nickname=payload.nickname,
            avatar_url=payload.avatar_url,
            initial_points=get_runtime_initial_points(),
            now_text=now_text,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 409 if detail == "wechat_identity_conflict" else 422
        raise HTTPException(status_code=status_code, detail=detail) from exc

    access_token = issue_access_token()
    expires_at = build_session_expiry(now_text)
    create_session(user_id=str(user["user_id"]), token_hash=hash_access_token(access_token), device_type=request.headers.get("X-Client-Platform"), client_version=request.headers.get("X-Client-Version"), ip=request.client.host if request.client else None, expires_at=expires_at, now_text=now_text)
    return AuthLoginResponse(access_token=access_token, expires_at=expires_at, user=_build_user_response(user), points=_build_points_response_from_user(user))


def get_phone_registration_status(payload: PhoneStatusRequest) -> PhoneStatusResponse:
    normalized_phone = _normalize_mainland_mobile(payload.phone)
    identity = get_phone_identity_by_normalized_phone(normalized_phone=normalized_phone)
    registered = identity is not None and bool(identity.get("password_hash"))
    return PhoneStatusResponse(
        registered=registered,
        normalized_phone=normalized_phone,
        next_action="login" if registered else "register",
    )


def register_with_phone_password(payload: PhonePasswordRegisterRequest, request: Request) -> AuthLoginResponse:
    normalized_phone = _normalize_mainland_mobile(payload.phone)
    _validate_phone_password_pair(payload.password, payload.confirm_password)
    now_text = _utc_now()
    try:
        user = create_phone_user(
            normalized_phone=normalized_phone,
            password_hash=hash_password(payload.password),
            initial_points=get_runtime_initial_points(),
            registered_channel=f"phone:{_resolve_request_channel(request) or 'h5'}",
            now_text=now_text,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 409 if detail == "phone_already_registered" else 422
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return _issue_auth_login_response(user, request=request, now_text=now_text)


def login_with_phone_password(payload: PhonePasswordLoginRequest, request: Request) -> AuthLoginResponse:
    normalized_phone = _normalize_mainland_mobile(payload.phone)
    identity = get_phone_identity_by_normalized_phone(normalized_phone=normalized_phone)
    if identity is None or not verify_password(payload.password, str(identity.get("password_hash") or "")):
        raise HTTPException(status_code=401, detail="invalid_phone_or_password")

    now_text = _utc_now()
    user = mark_phone_identity_login(identity_id=str(identity["identity_id"]), now_text=now_text)
    if user is None:
        raise HTTPException(status_code=404, detail="phone_not_registered")
    return _issue_auth_login_response(user, request=request, now_text=now_text)


def get_me(current_user: dict[str, object] = Depends(require_authenticated_user)) -> CurrentUserResponse:
    return CurrentUserResponse(user=_build_user_response(current_user), points=_build_points_response_from_user(current_user))


def patch_me_profile(payload: UserProfileUpdateRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> UserResponse:
    if payload.nickname is None and payload.avatar_url is None:
        raise HTTPException(status_code=422, detail="nickname_or_avatar_required")
    updated = update_user_profile(user_id=str(current_user["user_id"]), nickname=payload.nickname, avatar_url=payload.avatar_url, now_text=_utc_now())
    if updated is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_user_response(updated)


def upload_my_avatar(payload: AvatarUploadRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> UserResponse:
    image_bytes, extension = _decode_avatar_data_url(payload.image_data_url)
    user_id = str(current_user["user_id"])
    avatar_upload_dir = _get_avatar_upload_dir()
    avatar_upload_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{user_id}-{uuid4().hex}.{extension}"
    file_path = avatar_upload_dir / file_name
    file_path.write_bytes(image_bytes)
    avatar_url = f"/api/v1/static/uploads/avatars/{file_name}"
    updated = update_user_profile(user_id=user_id, nickname=None, avatar_url=avatar_url, now_text=_utc_now())
    if updated is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_user_response(updated)


def _get_avatar_upload_dir() -> Path:
    return get_uploads_dir() / "avatars"


def _get_customer_service_qr_upload_dir() -> Path:
    return get_uploads_dir() / "customer-service"


def change_my_password(payload: PasswordChangeRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> PasswordChangeResponse:
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=422, detail="password_confirm_mismatch")

    _validate_phone_password_pair(payload.new_password, payload.confirm_password)

    identity = get_primary_phone_identity_by_user_id(str(current_user["user_id"]))
    if identity is None or not identity.get("password_hash"):
        raise HTTPException(status_code=422, detail="phone_password_identity_not_found")
    if not verify_password(payload.current_password, str(identity.get("password_hash") or "")):
        raise HTTPException(status_code=401, detail="invalid_current_password")
    if payload.new_password == payload.current_password:
        raise HTTPException(status_code=422, detail="new_password_same_as_old")

    updated = update_phone_identity_password(
        identity_id=str(identity["identity_id"]),
        password_hash=hash_password(payload.new_password.strip()),
        now_text=_utc_now(),
    )
    if not updated:
        raise HTTPException(status_code=500, detail="password_update_failed")
    return PasswordChangeResponse(status="ok")


def logout_user(auth_result: tuple[dict[str, object], str] = Depends(require_authenticated_user_with_token_hash)) -> dict[str, str]:
    _, token_hash = auth_result
    revoked = revoke_session_by_token_hash(token_hash, now_text=_utc_now())
    if not revoked:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {"status": "ok"}


def get_my_points(current_user: dict[str, object] = Depends(require_authenticated_user)) -> PointsAccountResponse:
    points_account = get_points_account(str(current_user["user_id"]))
    if points_account is None:
        raise HTTPException(status_code=404, detail="points_account_not_found")
    return _build_points_account_response(points_account)


def get_my_points_ledger(limit: int = Query(default=20, ge=1, le=100), current_user: dict[str, object] = Depends(require_authenticated_user)) -> PointsLedgerListResponse:
    items = [_build_points_ledger_entry_response(item) for item in list_points_ledger(str(current_user["user_id"]), limit)]
    return PointsLedgerListResponse(items=items)


def get_public_points_claim_link(
    claim_code: str,
    request: Request,
    current_user: dict[str, object] | None = Depends(resolve_authenticated_user),
) -> PublicPointsClaimLinkResponse:
    now_text = _utc_now()
    link = get_points_claim_link_by_code(claim_code)
    if link is None:
        raise HTTPException(status_code=404, detail="claim_link_not_found")
    current_record = None
    current_status = None
    if current_user is not None:
        duplicate_visit = record_points_claim_duplicate_link_visit(
            claim_code=claim_code,
            user_id=str(current_user["user_id"]),
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            now_text=now_text,
        )
        if duplicate_visit is not None:
            current_status = "already_claimed_this_week"
            current_record = duplicate_visit.get("already_claimed_record")
        else:
            current_record = get_user_current_week_points_claim(str(current_user["user_id"]), now_text=now_text)
    return _build_public_points_claim_link_response(link, now_text=now_text, current_status=current_status, current_record=current_record)


def post_public_points_claim(
    claim_code: str,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> PointsClaimSubmitResponse:
    now_text = _utc_now()
    try:
        result = claim_points_from_link(
            claim_code=claim_code,
            user_id=str(current_user["user_id"]),
            request_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            now_text=now_text,
        )
    except RuntimeError as exc:
        detail = str(exc)
        if detail == "claim_link_not_found":
            raise HTTPException(status_code=404, detail=detail) from exc
        raise HTTPException(status_code=500, detail="claim_points_failed") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    claim_status = str(result["claim_status"])
    if claim_status in {"expired", "disabled", "not_started"}:
        raise HTTPException(status_code=409, detail=f"claim_link_{claim_status}")

    points_account = get_points_account(str(current_user["user_id"]))
    return PointsClaimSubmitResponse(
        claim_status=claim_status,
        message=_points_claim_status_message(claim_status),
        points=_build_points_account_response(points_account) if points_account is not None else None,
        ledger=_build_points_ledger_entry_response(result["ledger"]) if result.get("ledger") is not None else None,
        record=_build_points_claim_record_response(result["record"]) if result.get("record") is not None else None,
        already_claimed_record=_build_points_claim_record_response(result["already_claimed_record"]) if result.get("already_claimed_record") is not None else None,
    )


def get_recharge_packages(request: Request, _: dict[str, object] = Depends(require_registered_user)) -> RechargePackageListResponse:
    items = [_build_recharge_package_response(item) for item in get_runtime_available_recharge_packages(_resolve_request_channel(request))]
    return RechargePackageListResponse(items=items)


def create_recharge_order_record(request: Request, payload: RechargeOrderCreateRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> RechargeOrderResponse:
    channel_key = _resolve_request_channel(request)
    package = _find_available_recharge_package(package_key=payload.package_key, channel_key=channel_key)
    if package is None:
        raise HTTPException(status_code=404, detail="recharge_package_not_found")
    try:
        order = create_recharge_order(
            order_id=uuid4().hex,
            user_id=str(current_user["user_id"]),
            channel=channel_key,
            package_key=str(package["package_key"]),
            package_title=str(package["title"]),
            amount_cents=int(package["price_cents"]),
            points_amount=int(package["points_amount"]),
            bonus_points=int(package["bonus_points"]),
            source=payload.source,
            external_order_id=payload.external_order_id,
            idempotency_key=payload.idempotency_key,
            proof_url=payload.proof_url,
            remark=payload.remark,
            created_at=_utc_now(),
        )
    except ValueError as exc:
        if str(exc) == "recharge_order_external_order_conflict":
            raise HTTPException(status_code=409, detail="recharge_order_external_order_conflict") from exc
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _build_recharge_order_response(order)


def get_my_recharge_orders(
    limit: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None, max_length=32),
    current_user: dict[str, object] = Depends(require_registered_user),
) -> RechargeOrderListResponse:
    items = [
        _build_recharge_order_response(item)
        for item in list_recharge_orders(limit=limit, user_id=str(current_user["user_id"]), status=status)
    ]
    return RechargeOrderListResponse(items=items)


def get_my_recharge_order_detail(order_id: str, current_user: dict[str, object] = Depends(require_registered_user)) -> RechargeOrderResponse:
    order = _require_owned_recharge_order(order_id, current_user_id=str(current_user["user_id"]))
    return _build_recharge_order_response_with_payments(order)


def create_recharge_order_payment(order_id: str, payload: PaymentTransactionCreateRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> PaymentTransactionResponse:
    order = _require_owned_recharge_order(order_id, current_user_id=str(current_user["user_id"]))
    if str(order.get("status") or "") != "unpaid":
        raise HTTPException(status_code=409, detail="recharge_order_not_payable")

    payment_result = create_payment_request(
        provider=payload.provider,
        payment_method=payload.payment_method,
        order=order,
        return_url=payload.return_url,
        client_context=payload.client_context,
    )
    transaction = create_payment_transaction(
        transaction_id=uuid4().hex,
        order_id=order_id,
        user_id=str(current_user["user_id"]),
        provider=payment_result.provider,
        payment_method=payment_result.payment_method,
        amount_cents=int(order["amount_cents"]),
        status=payment_result.status,
        provider_transaction_id=payment_result.provider_transaction_id,
        prepay_id=payment_result.prepay_id,
        idempotency_key=payload.idempotency_key,
        payment_params=payment_result.payment_params,
        failure_reason=payment_result.failure_reason,
        now_text=_utc_now(),
    )
    return _build_payment_transaction_response(transaction, client_message=payment_result.client_message)


def get_recharge_order_payment_status(order_id: str, current_user: dict[str, object] = Depends(require_registered_user)) -> RechargeOrderPaymentStatusResponse:
    order = _require_owned_recharge_order(order_id, current_user_id=str(current_user["user_id"]))
    latest_payment = get_latest_payment_transaction_for_order(order_id)
    return RechargeOrderPaymentStatusResponse(
        order=_build_recharge_order_response_with_payments(order, payment_limit=5),
        latest_payment=_build_payment_transaction_response(latest_payment) if latest_payment is not None else None,
    )


async def post_payment_notify(provider: str, request: Request) -> PaymentNotifyResponse:
    normalized_provider = provider.strip().lower()
    if normalized_provider != "mock":
        return PaymentNotifyResponse(status="payment_notify_not_configured")
    if not allow_mock_wechat_login():
        raise HTTPException(status_code=403, detail="mock_payment_disabled")

    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="invalid_payment_notify_payload")
    transaction_id = str(payload.get("transaction_id") or "").strip()
    if not transaction_id:
        raise HTTPException(status_code=422, detail="transaction_id_required")

    try:
        transaction, order, ledger = settle_payment_transaction(
            transaction_id=transaction_id,
            provider_transaction_id=str(payload.get("provider_transaction_id") or "").strip() or None,
            notify_payload=payload,
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        detail = str(exc)
        status_code = 404 if detail in {"payment_transaction_not_found", "recharge_order_not_found"} else 500
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return PaymentNotifyResponse(
        status="settled",
        transaction=_build_payment_transaction_response(transaction),
        order=_build_recharge_order_response(order),
        ledger=_build_points_ledger_entry_response(ledger),
    )


def get_today_almanac(request: Request, current_user: dict[str, object] | None = Depends(resolve_authenticated_user)) -> AlmanacResponse:
    payload = build_today_almanac().to_dict()
    if current_user is not None:
        _record_zero_cost_usage(
            user_id=str(current_user["user_id"]),
            scene="almanac_query",
            channel=_resolve_request_channel(request),
            target_id=str(payload.get("solar_date") or "today"),
            request_payload_summary={"date": payload.get("solar_date"), "source": "today"},
            result_summary={"status": "completed", "display_date": payload.get("display_date")},
        )
    return AlmanacResponse(**payload)


def get_almanac_by_date(request: Request, date_text: str, current_user: dict[str, object] | None = Depends(resolve_authenticated_user)) -> AlmanacResponse:
    try:
        target_date = date.fromisoformat(date_text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="date_must_be_yyyy_mm_dd") from exc
    payload = build_almanac_for_date(target_date).to_dict()
    if current_user is not None:
        _record_zero_cost_usage(
            user_id=str(current_user["user_id"]),
            scene="almanac_query",
            channel=_resolve_request_channel(request),
            target_id=str(payload.get("solar_date") or date_text),
            request_payload_summary={"date": date_text, "source": "query"},
            result_summary={"status": "completed", "display_date": payload.get("display_date")},
        )
    return AlmanacResponse(**payload)


def get_public_runtime_config(channel: str | None = Query(default=None, max_length=128)) -> PublicRuntimeConfigResponse:
    payload = resolve_public_runtime_config(channel)
    return PublicRuntimeConfigResponse(
        channel=payload["channel"],
        points=RuntimePointsConfigResponse(**payload["points"]),
        recharge=RuntimeRechargeConfigResponse(packages=[_build_recharge_package_response(item) for item in payload["recharge"]["packages"]]),
        customer_service=CustomerServiceConfigResponse(**payload["customer_service"]),
        compliance=ComplianceConfigResponse(**payload["compliance"]),
        modules=RuntimeModulesConfigResponse(
            phone_review=ModuleRuntimeConfigResponse(**payload["modules"]["phone_review"]),
            four_pillars=ModuleRuntimeConfigResponse(**payload["modules"]["four_pillars"]),
            agent=ModuleRuntimeConfigResponse(**payload["modules"]["agent"]),
            almanac=ModuleRuntimeConfigResponse(**payload["modules"]["almanac"]),
            voice=VoiceRuntimeConfigResponse(**payload["modules"]["voice"]),
        ),
    )


def get_internal_runtime_config(
    scope_type: str | None = Query(default=None, max_length=32),
    scope_key: str | None = Query(default=None, max_length=128),
    _: None = Depends(require_internal_admin_access),
) -> RuntimeConfigListResponse:
    try:
        normalized_scope_type = normalize_scope_type(scope_type) if scope_type else None
        normalized_scope_key = normalize_scope_key(scope_key) if scope_key else None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    items = [RuntimeConfigEntryResponse(**item) for item in list_runtime_config_entries(scope_type=normalized_scope_type, scope_key=normalized_scope_key)]
    return RuntimeConfigListResponse(items=items)


def put_internal_runtime_config(payload: RuntimeConfigUpsertRequest, _: None = Depends(require_internal_admin_access)) -> RuntimeConfigListResponse:
    updated_at = _utc_now()
    items: list[RuntimeConfigEntryResponse] = []
    for entry in payload.entries:
        try:
            saved_entry = upsert_runtime_config_entry(
                scope_type=normalize_scope_type(entry.scope_type),
                scope_key=normalize_scope_key(entry.scope_key),
                config_key=normalize_config_key(entry.config_key),
                value=entry.value,
                updated_at=updated_at,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        items.append(RuntimeConfigEntryResponse(**saved_entry))
    return RuntimeConfigListResponse(items=items)


def post_internal_initial_points_config(payload: RuntimeInitialPointsUpdateRequest, _: None = Depends(require_internal_admin_access)) -> RuntimeInitialPointsUpdateResponse:
    try:
        result = update_initial_points_config(
            old_initial_grant=get_runtime_initial_points(),
            new_initial_grant=payload.initial_grant,
            apply_scope=payload.apply_scope,
            reason=payload.reason,
            updated_at=_utc_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RuntimeInitialPointsUpdateResponse(
        previous_initial_grant=int(result["previous_initial_grant"]),
        initial_grant=int(result["initial_grant"]),
        delta=int(result["delta"]),
        apply_scope=result["apply_scope"],
        target_user_count=int(result["target_user_count"]),
        affected_user_count=int(result["affected_user_count"]),
        adjusted_points_total=int(result["adjusted_points_total"]),
        zeroed_user_count=int(result["zeroed_user_count"]),
        operation_id=str(result["operation_id"]),
        entry=RuntimeConfigEntryResponse(**result["entry"]),
    )


def get_internal_runtime_config_schema(_: None = Depends(require_internal_admin_access)) -> RuntimeConfigSchemaResponse:
    return RuntimeConfigSchemaResponse(items=[RuntimeConfigSchemaItemResponse(**item) for item in _RUNTIME_CONFIG_SCHEMA_ITEMS])


def post_internal_customer_service_qr_code(
    payload: CustomerServiceQrCodeUploadRequest,
    _: None = Depends(require_internal_admin_access),
) -> RuntimeConfigEntryResponse:
    image_bytes, extension = _decode_customer_service_qr_data_url(payload.image_data_url)
    qr_upload_dir = _get_customer_service_qr_upload_dir()
    qr_upload_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"qr-{uuid4().hex}.{extension}"
    file_path = qr_upload_dir / file_name
    file_path.write_bytes(image_bytes)

    qr_code_url = f"/api/v1/static/uploads/customer-service/{file_name}"
    saved_entry = upsert_runtime_config_entry(
        scope_type="global",
        scope_key="default",
        config_key="customer_service.qr_code_url",
        value=qr_code_url,
        updated_at=_utc_now(),
    )
    return RuntimeConfigEntryResponse(**saved_entry)


def delete_internal_customer_service_qr_code(_: None = Depends(require_internal_admin_access)) -> RuntimeConfigEntryResponse:
    current_qr_code_url = None
    for entry in list_runtime_config_entries(scope_type="global", scope_key="default"):
        if entry.get("config_key") == "customer_service.qr_code_url":
            current_qr_code_url = entry.get("value")
            break
    _delete_local_customer_service_qr_code(current_qr_code_url)
    saved_entry = upsert_runtime_config_entry(
        scope_type="global",
        scope_key="default",
        config_key="customer_service.qr_code_url",
        value=None,
        updated_at=_utc_now(),
    )
    return RuntimeConfigEntryResponse(**saved_entry)


def get_internal_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    keyword: str | None = Query(default=None, max_length=128),
    query: str | None = Query(default=None, max_length=128),
    status: str | None = Query(default=None, max_length=64),
    identity_level: str | None = Query(default=None, max_length=64),
    channel: str | None = Query(default=None, max_length=64),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> InternalUserListResponse:
    total = count_users(
        keyword=keyword or query,
        status=status,
        identity_level=identity_level,
        channel=channel,
        date_from=date_from,
        date_to=date_to,
    )
    items = [
        _build_internal_user_response(item)
        for item in list_users(
            limit=limit,
            offset=offset,
            keyword=keyword or query,
            status=status,
            identity_level=identity_level,
            channel=channel,
            date_from=date_from,
            date_to=date_to,
        )
    ]
    return InternalUserListResponse(items=items, total=total, limit=limit, offset=offset)


def get_internal_user_detail(user_id: str, _: None = Depends(require_internal_admin_access)) -> InternalUserResponse:
    user = get_internal_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_internal_user_response(user)


def get_internal_user_admin_summary(user_id: str, _: None = Depends(require_internal_admin_access)) -> InternalUserAdminSummaryResponse:
    user = get_internal_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    recent_orders = list_recent_recharge_orders_for_user(user_id=user_id, limit=5)
    recent_amount = sum(int(item.get("amount_cents", 0) or 0) for item in recent_orders)
    return InternalUserAdminSummaryResponse(
        user=_build_internal_user_response(user),
        recent_orders=[_build_recharge_order_summary_response(item) for item in recent_orders],
        recent_order_count=len(recent_orders),
        recent_recharge_amount_cents=recent_amount,
        latest_order_status=str(recent_orders[0]["status"]) if recent_orders else None,
        total_recharge_amount_cents=recent_amount,
        total_withdraw_amount_cents=0,
        promoter_parent_user_id=str(user.get("promoter_parent_user_id")) if user.get("promoter_parent_user_id") else None,
        identity_level=str(user.get("identity_level") or "normal_user"),
    )


def get_internal_user_points_ledger(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    _: None = Depends(require_internal_admin_access),
) -> PointsLedgerListResponse:
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    items = [_build_points_ledger_entry_response(item) for item in list_points_ledger(user_id, limit)]
    return PointsLedgerListResponse(items=items)


def post_internal_user_points_adjust(
    user_id: str,
    payload: ManualPointsAdjustRequest,
    _: None = Depends(require_internal_admin_access),
) -> ManualPointsAdjustResponse:
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    if payload.delta == 0:
        raise HTTPException(status_code=422, detail="delta_must_not_be_zero")
    try:
        ledger = adjust_points(
            user_id=user_id,
            delta=payload.delta,
            biz_type=payload.biz_type,
            biz_id=payload.biz_id,
            idempotency_key=payload.idempotency_key,
            remark=payload.remark,
            now_text=_utc_now(),
        )
    except InsufficientPointsError as exc:
        raise HTTPException(status_code=402, detail="insufficient_points") from exc
    if ledger is None:
        raise HTTPException(status_code=500, detail="points_adjust_failed")
    refreshed_user = get_internal_user(user_id)
    points_account = get_points_account(user_id)
    if refreshed_user is None or points_account is None:
        raise HTTPException(status_code=500, detail="points_adjust_failed")
    return ManualPointsAdjustResponse(
        user=_build_internal_user_response(refreshed_user),
        points=_build_points_account_response(points_account),
        ledger=_build_points_ledger_entry_response(ledger),
    )


def post_internal_user_rebate_points_adjust(
    user_id: str,
    payload: RebatePointsAdjustRequest,
    _: None = Depends(require_internal_admin_access),
) -> RebatePointsAdjustResponse:
    user = get_internal_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    try:
        rebate_points = adjust_rebate_points(
            user_id=user_id,
            delta=payload.delta,
            reason=payload.reason,
            operator_note=payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    refreshed_user = get_internal_user(user_id) or user
    return RebatePointsAdjustResponse(
        user=_build_internal_user_response(refreshed_user),
        rebate_points=RebatePointsAccountResponse(
            user_id=str(rebate_points["user_id"]),
            balance=int(rebate_points["balance"]),
            frozen_balance=int(rebate_points["frozen_balance"]),
            created_at=str(rebate_points["created_at"]) if rebate_points.get("created_at") else None,
            updated_at=str(rebate_points["updated_at"]) if rebate_points.get("updated_at") else None,
        ),
    )


def get_internal_points_claim_links(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None, max_length=32),
    keyword: str | None = Query(default=None, max_length=128),
    _: None = Depends(require_internal_admin_access),
) -> PointsClaimLinkListResponse:
    now_text = _utc_now()
    items = [
        _build_points_claim_link_response(item, now_text=now_text)
        for item in list_points_claim_links(limit=limit, offset=offset, status=status, keyword=keyword, now_text=now_text)
    ]
    total = count_points_claim_links(status=status, keyword=keyword, now_text=now_text)
    return PointsClaimLinkListResponse(items=items, total=total, limit=limit, offset=offset)


def post_internal_points_claim_link(
    payload: PointsClaimLinkCreateRequest,
    _: None = Depends(require_internal_admin_access),
) -> PointsClaimLinkResponse:
    now_dt = datetime.now(timezone.utc).replace(microsecond=0)
    now_text = now_dt.isoformat()
    try:
        expires_at = _resolve_points_claim_expires_at(payload, now_dt)
        link = create_points_claim_link(
            link_id=uuid4().hex,
            claim_code=secrets.token_urlsafe(24),
            title=payload.title,
            points_amount=payload.points_amount,
            display_value_cents=payload.display_value_cents,
            valid_from=now_text,
            expires_at=expires_at,
            created_by="internal_admin",
            operator_note=payload.operator_note,
            now_text=now_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _build_points_claim_link_response(link, now_text=now_text)


def get_internal_points_claim_link_detail(
    claim_link_id: str,
    _: None = Depends(require_internal_admin_access),
) -> PointsClaimLinkResponse:
    link = get_points_claim_link(claim_link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="claim_link_not_found")
    return _build_points_claim_link_response(link, now_text=_utc_now())


def post_internal_points_claim_link_disable(
    claim_link_id: str,
    payload: PointsClaimLinkDisableRequest,
    _: None = Depends(require_internal_admin_access),
) -> PointsClaimLinkResponse:
    now_text = _utc_now()
    link = disable_points_claim_link(
        link_id=claim_link_id,
        disabled_by="internal_admin",
        operator_note=payload.operator_note,
        now_text=now_text,
    )
    if link is None:
        raise HTTPException(status_code=404, detail="claim_link_not_found")
    return _build_points_claim_link_response(link, now_text=now_text)


def get_internal_points_claim_records(
    claim_link_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None, max_length=32),
    user_id: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> PointsClaimRecordListResponse:
    link = get_points_claim_link(claim_link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="claim_link_not_found")
    records = list_points_claim_records(link_id=claim_link_id, user_id=user_id, status=status, limit=limit, offset=offset)
    total = count_points_claim_records(link_id=claim_link_id, user_id=user_id, status=status)
    return PointsClaimRecordListResponse(
        items=[_build_points_claim_record_response(item) for item in records],
        total=total,
        limit=limit,
        offset=offset,
    )


def patch_internal_user_status(
    user_id: str,
    payload: UserStatusUpdateRequest,
    _: None = Depends(require_internal_admin_access),
) -> InternalUserResponse:
    try:
        updated = update_user_status(
            user_id=user_id,
            status=payload.status,
            reason=payload.reason,
            operator_note=payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_internal_user_response(updated)


def patch_internal_user_identity(
    user_id: str,
    payload: UserIdentityUpdateRequest,
    _: None = Depends(require_internal_admin_access),
) -> InternalUserResponse:
    try:
        updated = update_user_identity(
            user_id=user_id,
            identity_level=payload.identity_level,
            reason=payload.reason,
            operator_note=payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_internal_user_response(updated)


def patch_internal_user_promoter_parent(
    user_id: str,
    payload: UserPromoterParentUpdateRequest,
    _: None = Depends(require_internal_admin_access),
) -> InternalUserResponse:
    try:
        updated = update_user_promoter_parent(
            user_id=user_id,
            promoter_parent_user_id=payload.promoter_parent_user_id,
            reason=payload.reason,
            operator_note=payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_internal_user_response(updated)


def get_internal_usage_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = Query(default=None, max_length=64),
    feature_key: str | None = Query(default=None, max_length=128),
    scene: str | None = Query(default=None, max_length=128),
    status: str | None = Query(default=None, max_length=32),
    keyword: str | None = Query(default=None, max_length=128),
    channel: str | None = Query(default=None, max_length=64),
    target_id: str | None = Query(default=None, max_length=64),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    include_hidden: bool = Query(default=False),
    _: None = Depends(require_internal_admin_access),
) -> UsageRecordListResponse:
    items = [
        _build_usage_record_response(item)
        for item in list_usage_records(limit=limit, offset=offset, user_id=user_id, feature_key=feature_key, scene=scene, status=status, keyword=keyword, channel=channel, target_id=target_id, date_from=date_from, date_to=date_to)
    ]
    return UsageRecordListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_internal_usage_record_detail(usage_record_id: str, _: None = Depends(require_internal_admin_access)) -> UsageRecordDetailResponse:
    record = get_usage_record(usage_record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="usage_record_not_found")
    user = get_internal_user(str(record["user_id"]))
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return UsageRecordDetailResponse(
        record=_build_usage_record_response(record),
        user=_build_internal_user_response(user),
        recent_orders=[_build_recharge_order_summary_response(item) for item in list_recent_recharge_orders_for_user(user_id=str(record["user_id"]), limit=5)],
    )


def get_internal_recharge_orders(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = Query(default=None, max_length=64),
    status: str | None = Query(default=None, max_length=32),
    source: str | None = Query(default=None, max_length=64),
    channel: str | None = Query(default=None, max_length=64),
    keyword: str | None = Query(default=None, max_length=128),
    amount_min: int | None = Query(default=None, ge=0),
    amount_max: int | None = Query(default=None, ge=0),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> RechargeOrderListResponse:
    items = [
        _build_recharge_order_response(item)
        for item in list_recharge_orders(limit=limit, offset=offset, user_id=user_id, status=status, source=source, channel=channel, keyword=keyword, amount_min=amount_min, amount_max=amount_max, date_from=date_from, date_to=date_to)
    ]
    return RechargeOrderListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_internal_recharge_order_detail(order_id: str, _: None = Depends(require_internal_admin_access)) -> RechargeOrderResponse:
    order = get_recharge_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="recharge_order_not_found")
    order_response = _build_recharge_order_response_with_payments(order)
    order_response.refund_requests = [RefundRequestResponse(**item) for item in list_refund_requests_for_order(order_id)]
    order_response.commission_records = [PromotionCommissionResponse(**item) for item in list_promotion_commissions(limit=20, order_id=order_id)]
    return order_response


def post_internal_recharge_order_review(
    order_id: str,
    payload: RechargeOrderReviewRequest,
    _: None = Depends(require_internal_admin_access),
) -> RechargeOrderReviewResponse:
    try:
        order, ledger = review_recharge_order(
            order_id=order_id,
            action=payload.action,
            review_note=payload.review_note,
            reviewed_by="internal_admin",
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        if str(exc) == "recharge_order_not_found":
            raise HTTPException(status_code=404, detail="recharge_order_not_found") from exc
        raise HTTPException(status_code=500, detail="recharge_order_review_failed") from exc
    except ValueError as exc:
        if str(exc) == "recharge_order_already_reviewed":
            raise HTTPException(status_code=409, detail="recharge_order_already_reviewed") from exc
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    points_account = get_points_account(str(order["user_id"]))
    if points_account is None:
        raise HTTPException(status_code=500, detail="recharge_order_review_failed")

    return RechargeOrderReviewResponse(
        order=_build_recharge_order_response(order),
        points=_build_points_account_response(points_account),
        ledger=_build_points_ledger_entry_response(ledger) if ledger is not None else None,
    )


def post_internal_recharge_order_manual_complete(
    order_id: str,
    payload: RechargeOrderManualCompleteRequest,
    _: None = Depends(require_internal_admin_access),
) -> RechargeOrderManualCompleteResponse:
    try:
        order, ledger = complete_recharge_order_manually(
            order_id=order_id,
            payment_method=payload.payment_method,
            payment_reference=payload.payment_reference,
            operator_note=payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        if str(exc) == "recharge_order_not_found":
            raise HTTPException(status_code=404, detail="recharge_order_not_found") from exc
        raise HTTPException(status_code=500, detail="recharge_order_manual_complete_failed") from exc
    except ValueError as exc:
        if str(exc) in {"recharge_order_already_completed", "recharge_order_not_manual_completable"}:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    points_account = get_points_account(str(order["user_id"]))
    if points_account is None:
        raise HTTPException(status_code=500, detail="recharge_order_manual_complete_failed")

    return RechargeOrderManualCompleteResponse(
        order=_build_recharge_order_response(order),
        points=_build_points_account_response(points_account),
        ledger=_build_points_ledger_entry_response(ledger),
    )


def post_internal_recharge_order_refund(
    order_id: str,
    payload: RefundCreateRequest,
    _: None = Depends(require_internal_admin_access),
) -> RefundRequestResponse:
    try:
        refund = create_refund_request(order_id=order_id, reason=payload.reason, operator_note=payload.operator_note, operator="internal_admin", now_text=_utc_now())
    except RuntimeError as exc:
        if str(exc) == "recharge_order_not_found":
            raise HTTPException(status_code=404, detail="recharge_order_not_found") from exc
        raise HTTPException(status_code=500, detail="refund_request_create_failed") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RefundRequestResponse(**refund)


def post_internal_refund_review(
    refund_id: str,
    payload: AdminReviewRequest,
    _: None = Depends(require_internal_admin_access),
) -> RefundRequestResponse:
    try:
        refund = review_refund_request(
            refund_id=refund_id,
            action=payload.action,
            reject_reason=payload.reject_reason or payload.reason,
            operator_note=payload.operator_note or payload.review_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        if str(exc) == "refund_request_not_found":
            raise HTTPException(status_code=404, detail="refund_request_not_found") from exc
        raise HTTPException(status_code=500, detail="refund_request_review_failed") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RefundRequestResponse(**refund)


def post_internal_refund_retry(
    refund_id: str,
    payload: RefundRetryRequest,
    _: None = Depends(require_internal_admin_access),
) -> RefundRequestResponse:
    try:
        refund = retry_refund_request(refund_id=refund_id, operator_note=payload.operator_note, operator="internal_admin", now_text=_utc_now())
    except RuntimeError as exc:
        if str(exc) == "refund_request_not_found":
            raise HTTPException(status_code=404, detail="refund_request_not_found") from exc
        raise HTTPException(status_code=500, detail="refund_request_retry_failed") from exc
    return RefundRequestResponse(**refund)


def get_internal_phone_qimen_summary(_: None = Depends(require_internal_admin_access)) -> InternalPhoneQimenSummaryResponse:
    return InternalPhoneQimenSummaryResponse(**get_internal_phone_qimen_summary_data())


def get_internal_phone_qimen_reviews(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    keyword: str | None = Query(default=None, max_length=128),
    status: str | None = Query(default=None, max_length=32),
    gender: str | None = Query(default=None, max_length=16),
    channel: str | None = Query(default=None, max_length=64),
    user_id: str | None = Query(default=None, max_length=64),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> InternalPhoneQimenReviewListResponse:
    items = [
        InternalPhoneQimenReviewItemResponse(**item)
        for item in list_internal_phone_qimen_reviews(
            limit=limit,
            offset=offset,
            keyword=keyword,
            status=status,
            gender=gender,
            channel=channel,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
    ]
    total = count_internal_phone_qimen_reviews(
        keyword=keyword,
        status=status,
        gender=gender,
        channel=channel,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    return InternalPhoneQimenReviewListResponse(items=items, total=total, limit=limit, offset=offset)


def get_internal_phone_qimen_review_detail(review_id: str, _: None = Depends(require_internal_admin_access)) -> InternalPhoneQimenReviewDetailResponse:
    review = get_internal_phone_qimen_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    user_id = str(review.get("user_id") or "")
    unlock_records = [
        _build_internal_phone_qimen_unlock_response(item)
        for item in (list_review_aspect_unlocks(review_id=review_id, user_id=user_id) if user_id else [])
    ]
    voice_records = [_build_usage_record_response(item) for item in list_voice_usage_records_for_review(review_id)]
    return InternalPhoneQimenReviewDetailResponse(
        review=InternalPhoneQimenReviewItemResponse(**review),
        unlock_records=unlock_records,
        voice_records=voice_records,
    )


def get_internal_four_pillars_summary(_: None = Depends(require_internal_admin_access)) -> InternalFourPillarsSummaryResponse:
    return InternalFourPillarsSummaryResponse(**get_internal_four_pillars_summary_data())


def get_internal_four_pillars_reviews(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    keyword: str | None = Query(default=None, max_length=128),
    status: str | None = Query(default=None, max_length=32),
    gender: str | None = Query(default=None, max_length=16),
    channel: str | None = Query(default=None, max_length=64),
    user_id: str | None = Query(default=None, max_length=64),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> InternalFourPillarsReviewListResponse:
    items = [
        InternalFourPillarsReviewItemResponse(**item)
        for item in list_internal_four_pillars_reviews(
            limit=limit,
            offset=offset,
            keyword=keyword,
            status=status,
            gender=gender,
            channel=channel,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
    ]
    total = count_internal_four_pillars_reviews(
        keyword=keyword,
        status=status,
        gender=gender,
        channel=channel,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    return InternalFourPillarsReviewListResponse(items=items, total=total, limit=limit, offset=offset)


def get_internal_four_pillars_review_detail(review_id: str, _: None = Depends(require_internal_admin_access)) -> InternalFourPillarsReviewDetailResponse:
    review = get_internal_four_pillars_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    user_id = str(review.get("user_id") or "")
    unlock_records = [
        _build_internal_four_pillars_unlock_response(item)
        for item in (list_four_pillars_aspect_unlocks(review_id=review_id, user_id=user_id) if user_id else [])
    ]
    luck_render_records = [
        _build_four_pillars_luck_render_response(item)
        for item in list_four_pillars_luck_renders(review_id=review_id, user_id=user_id or None)
    ]
    return InternalFourPillarsReviewDetailResponse(
        review=InternalFourPillarsReviewItemResponse(**review),
        unlock_records=unlock_records,
        luck_render_records=luck_render_records,
    )


def get_internal_reviews(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    keyword: str | None = Query(default=None, max_length=128),
    status: str | None = Query(default=None, max_length=32),
    channel: str | None = Query(default=None, max_length=64),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> ReviewListResponse:
    items = [_build_review_summary_response(item) for item in list_reviews(limit=limit, offset=offset, status=status, keyword=keyword, channel=channel, date_from=date_from, date_to=date_to)]
    return ReviewListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_internal_review_detail(review_id: str, _: None = Depends(require_internal_admin_access)) -> ReviewRecordResponse:
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    return _build_review_record_response(review)


def _normalize_service_key_text(value: str | None, *, required: bool = True) -> str | None:
    normalized_value = (value or "").strip()
    if required and not normalized_value:
        raise HTTPException(status_code=422, detail="service_key_field_required")
    return normalized_value or None


def _mask_secret_value(secret_value: str) -> str:
    normalized_secret = secret_value.strip()
    if len(normalized_secret) <= 8:
        return f"****{normalized_secret[-4:]}"
    prefix = normalized_secret[:3] if normalized_secret.startswith("sk-") else normalized_secret[:4]
    return f"{prefix}****{normalized_secret[-4:]}"


def _build_secret_ref(*, provider: str, model: str, key_id: str) -> str:
    normalized_model = re.sub(r"[^a-zA-Z0-9_.:-]+", "-", model.strip()).strip("-").lower() or "default"
    return f"admin:{provider}:{normalized_model}:{key_id}"


def _save_internal_service_key(*, payload: LlmApiKeyUpsertRequest, key_id: str | None) -> dict[str, object]:
    existing_key = get_llm_api_key(key_id) if key_id else None
    if key_id and existing_key is None:
        raise HTTPException(status_code=404, detail="llm_api_key_not_found")

    normalized_provider = str(_normalize_service_key_text(payload.provider)).lower()
    normalized_model = str(_normalize_service_key_text(payload.model))
    normalized_display_name = str(_normalize_service_key_text(payload.display_name))
    normalized_key_id = key_id or uuid4().hex
    normalized_secret_value = _normalize_service_key_text(payload.secret_value, required=False)
    if key_id is None and not normalized_secret_value:
        raise HTTPException(status_code=422, detail="secret_value_required")

    existing_masked_key = str(existing_key.get("masked_key") or "") if existing_key else ""
    masked_key = (
        _mask_secret_value(normalized_secret_value)
        if normalized_secret_value
        else existing_masked_key or str(payload.masked_key or "****")
    )
    secret_ref = (
        str(payload.secret_ref or "").strip()
        or (str(existing_key.get("secret_ref")) if existing_key else "")
        or _build_secret_ref(provider=normalized_provider, model=normalized_model, key_id=normalized_key_id)
    )

    try:
        return upsert_llm_api_key(
            key_id=normalized_key_id,
            provider=normalized_provider,
            model=normalized_model,
            display_name=normalized_display_name,
            masked_key=masked_key,
            secret_ref=secret_ref,
            secret_value=normalized_secret_value,
            enabled=payload.enabled,
            priority=payload.priority,
            max_concurrency=payload.max_concurrency,
            cooldown_seconds=payload.cooldown_seconds,
            remark=payload.remark,
            last_operator=payload.last_operator,
            now_text=_utc_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def get_internal_llm_api_keys(_: None = Depends(require_internal_admin_access)) -> LlmApiKeyListResponse:
    runtime_map = {
        str(item.get("key_id")): item
        for item in get_deepseek_governor_status().get("keys", [])
        if item.get("key_id")
    }
    merged_items: list[dict[str, Any]] = []
    for item in list_llm_api_keys():
        runtime = runtime_map.get(str(item.get("key_id"))) or {}
        next_item = dict(item)
        for key in ("current_inflight", "available_slots", "cooldown_until", "last_rate_limited_at", "last_error_message", "last_used_at"):
            if runtime.get(key) is not None:
                next_item[key] = runtime.get(key)
        merged_items.append(next_item)
    items = [LlmApiKeyResponse(**item) for item in merged_items]
    return LlmApiKeyListResponse(items=items, total=len(items))


def get_internal_llm_concurrency(_: None = Depends(require_internal_admin_access)) -> LlmConcurrencyStatusResponse:
    return LlmConcurrencyStatusResponse(**get_deepseek_governor_status())


def post_internal_llm_api_key(payload: LlmApiKeyUpsertRequest, _: None = Depends(require_internal_admin_access)) -> LlmApiKeyResponse:
    saved = _save_internal_service_key(payload=payload, key_id=None)
    return LlmApiKeyResponse(**saved)


def patch_internal_llm_api_key(key_id: str, payload: LlmApiKeyUpsertRequest, _: None = Depends(require_internal_admin_access)) -> LlmApiKeyResponse:
    saved = _save_internal_service_key(payload=payload, key_id=key_id)
    return LlmApiKeyResponse(**saved)


def delete_internal_llm_api_key(key_id: str, _: None = Depends(require_internal_admin_access)) -> dict[str, str]:
    delete_llm_api_key(key_id)
    return {"status": "ok"}


def get_internal_promotion_applications(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None, max_length=32),
    user_id: str | None = Query(default=None, max_length=64),
    keyword: str | None = Query(default=None, max_length=128),
    _: None = Depends(require_internal_admin_access),
) -> PromotionApplicationListResponse:
    items = [PromotionApplicationResponse(**item) for item in list_promotion_applications(limit=limit, status=status, user_id=user_id, keyword=keyword)]
    return PromotionApplicationListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_internal_promotion_application_detail(application_id: str, _: None = Depends(require_internal_admin_access)) -> PromotionApplicationResponse:
    application = get_promotion_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="promotion_application_not_found")
    return PromotionApplicationResponse(**application)


def post_internal_promotion_application_review(
    application_id: str,
    payload: AdminReviewRequest,
    _: None = Depends(require_internal_admin_access),
) -> PromotionApplicationResponse:
    try:
        application = review_promotion_application(
            application_id=application_id,
            action=payload.action,
            reject_reason=payload.reject_reason or payload.reason,
            review_note=payload.review_note or payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        if str(exc) == "promotion_application_not_found":
            raise HTTPException(status_code=404, detail="promotion_application_not_found") from exc
        raise HTTPException(status_code=500, detail="promotion_application_review_failed") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PromotionApplicationResponse(**application)


def get_internal_promotion_commissions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = Query(default=None, max_length=64),
    promoter_user_id: str | None = Query(default=None, max_length=64),
    order_id: str | None = Query(default=None, max_length=64),
    status: str | None = Query(default=None, max_length=32),
    date_from: str | None = Query(default=None, max_length=64),
    date_to: str | None = Query(default=None, max_length=64),
    _: None = Depends(require_internal_admin_access),
) -> PromotionCommissionListResponse:
    items = [PromotionCommissionResponse(**item) for item in list_promotion_commissions(limit=limit, user_id=user_id, promoter_user_id=promoter_user_id, order_id=order_id, status=status, date_from=date_from, date_to=date_to)]
    return PromotionCommissionListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_internal_promotion_commission_detail(commission_id: str, _: None = Depends(require_internal_admin_access)) -> PromotionCommissionResponse:
    commission = get_promotion_commission(commission_id)
    if commission is None:
        raise HTTPException(status_code=404, detail="promotion_commission_not_found")
    return PromotionCommissionResponse(**commission)


def get_internal_promotion_withdrawals(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str | None = Query(default=None, max_length=64),
    status: str | None = Query(default=None, max_length=32),
    keyword: str | None = Query(default=None, max_length=128),
    _: None = Depends(require_internal_admin_access),
) -> PromotionWithdrawalListResponse:
    items = [PromotionWithdrawalResponse(**item) for item in list_promotion_withdrawals(limit=limit, user_id=user_id, status=status, keyword=keyword)]
    return PromotionWithdrawalListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_internal_promotion_withdrawal_detail(withdrawal_id: str, _: None = Depends(require_internal_admin_access)) -> PromotionWithdrawalResponse:
    withdrawal = get_promotion_withdrawal(withdrawal_id)
    if withdrawal is None:
        raise HTTPException(status_code=404, detail="promotion_withdrawal_not_found")
    return PromotionWithdrawalResponse(**withdrawal)


def post_internal_promotion_withdrawal_review(
    withdrawal_id: str,
    payload: AdminReviewRequest,
    _: None = Depends(require_internal_admin_access),
) -> PromotionWithdrawalResponse:
    try:
        withdrawal = review_promotion_withdrawal(
            withdrawal_id=withdrawal_id,
            action=payload.action,
            reject_reason=payload.reject_reason or payload.reason,
            review_note=payload.review_note or payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        if str(exc) == "promotion_withdrawal_not_found":
            raise HTTPException(status_code=404, detail="promotion_withdrawal_not_found") from exc
        raise HTTPException(status_code=500, detail="promotion_withdrawal_review_failed") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PromotionWithdrawalResponse(**withdrawal)


def post_internal_promotion_withdrawal_retry_payout(
    withdrawal_id: str,
    payload: PromotionWithdrawalPayoutRequest,
    _: None = Depends(require_internal_admin_access),
) -> PromotionWithdrawalResponse:
    try:
        withdrawal = retry_promotion_withdrawal_payout(withdrawal_id=withdrawal_id, operator_note=payload.operator_note, operator="internal_admin", now_text=_utc_now())
    except RuntimeError as exc:
        if str(exc) == "promotion_withdrawal_not_found":
            raise HTTPException(status_code=404, detail="promotion_withdrawal_not_found") from exc
        raise HTTPException(status_code=500, detail="promotion_withdrawal_retry_failed") from exc
    return PromotionWithdrawalResponse(**withdrawal)


def post_internal_promotion_withdrawal_mark_paid(
    withdrawal_id: str,
    payload: PromotionWithdrawalPayoutRequest,
    _: None = Depends(require_internal_admin_access),
) -> PromotionWithdrawalResponse:
    try:
        withdrawal = mark_promotion_withdrawal_paid(
            withdrawal_id=withdrawal_id,
            payout_method=payload.payout_method,
            payout_proof=payload.payout_proof,
            operator_note=payload.operator_note,
            operator="internal_admin",
            now_text=_utc_now(),
        )
    except RuntimeError as exc:
        if str(exc) == "promotion_withdrawal_not_found":
            raise HTTPException(status_code=404, detail="promotion_withdrawal_not_found") from exc
        raise HTTPException(status_code=500, detail="promotion_withdrawal_mark_paid_failed") from exc
    return PromotionWithdrawalResponse(**withdrawal)


def get_internal_promotion_rules(_: None = Depends(require_internal_admin_access)) -> PromotionRulesResponse:
    return PromotionRulesResponse(**get_promotion_rules())


def put_internal_promotion_rules(payload: PromotionRulesUpdateRequest, _: None = Depends(require_internal_admin_access)) -> PromotionRulesResponse:
    updated_at = _utc_now()
    updates = {
        "promotion.normal_threshold_cents": payload.normal_threshold_cents,
        "promotion.senior_threshold_cents": payload.senior_threshold_cents,
        "promotion.normal_commission_rate": payload.normal_commission_rate,
        "promotion.senior_commission_rate": payload.senior_commission_rate,
        "promotion.min_withdraw_cents": payload.min_withdraw_cents,
        "promotion.order_completion_days": payload.order_completion_days,
    }
    for config_key, value in updates.items():
        if value is not None:
            upsert_runtime_config_entry(scope_type="global", scope_key="default", config_key=config_key, value=value, updated_at=updated_at)
    return PromotionRulesResponse(**get_promotion_rules())


def create_agent_reply(request: Request, payload: AgentReplyRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> AgentReplyResponse:
    _ensure_module_available(module_key="agent", request=request)
    reply_payload = build_agent_reply(message=payload.message, history=[item.model_dump() for item in payload.history], user_id=str(current_user["user_id"]))
    _record_zero_cost_usage(
        user_id=str(current_user["user_id"]),
        scene="agent_reply",
        channel=_resolve_request_channel(request),
        target_id=None,
        request_payload_summary={"message": payload.message[:120], "history_count": len(payload.history), "scene": payload.scene},
        result_summary={"status": "completed", "reply_mode": reply_payload.get("meta", {}).get("reply_mode"), "model_name": reply_payload.get("meta", {}).get("model_name")},
    )
    return AgentReplyResponse(**reply_payload)


def create_review_record(request: Request, background_tasks: BackgroundTasks, payload: ReviewCreateRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> ReviewRecordResponse:
    _ensure_module_available(module_key="phone_review", request=request)
    normalized_phone = _normalize_phone(payload.phone)
    review_id = uuid4().hex
    created_at = _utc_now()
    user_id = str(current_user["user_id"])
    channel_key = _resolve_request_channel(request)
    points_cost = get_runtime_phone_review_base_points_cost(channel_key)
    try:
        create_review_with_charge(
            review_id=review_id,
            user_id=user_id,
            phone=normalized_phone,
            gender=payload.gender,
            status="processing",
            created_at=created_at,
            progress_stage="queued",
            progress_message="评测任务已创建，等待开始",
            points_cost=points_cost,
            usage_scene=PHONE_REVIEW_BASE_SCENE,
            request_payload_summary={"phone": normalized_phone, "gender": payload.gender, "include_markdown": payload.include_markdown},
            channel=channel_key,
        )
    except InsufficientPointsError as exc:
        raise HTTPException(status_code=402, detail="insufficient_points") from exc
    background_tasks.add_task(
        _run_review_generation,
        review_id=review_id,
        phone=normalized_phone,
        gender=payload.gender,
        include_markdown=payload.include_markdown,
        user_id=user_id,
        points_cost=points_cost,
        channel_key=channel_key,
    )
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=500, detail="review_persistence_failed")
    return _build_review_record_response(
        review,
        channel_key=channel_key,
        current_user_id=str(current_user["user_id"]),
    )


def list_review_records(limit: int = Query(default=20, ge=1, le=100), current_user: dict[str, object] = Depends(require_authenticated_user)) -> ReviewListResponse:
    items = [_build_review_summary_response(item) for item in list_reviews(limit, user_id=str(current_user["user_id"]))]
    return ReviewListResponse(items=items)


def get_review_record(request: Request, review_id: str, current_user: dict[str, object] | None = Depends(resolve_authenticated_user)) -> ReviewRecordResponse:
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    review_user_id = str(review.get("user_id") or "")
    current_user_id = str(current_user["user_id"]) if current_user else ""
    if review_user_id and review_user_id != current_user_id:
        raise HTTPException(status_code=404, detail="review_not_found")
    return _build_review_record_response(review, channel_key=_resolve_request_channel(request), current_user_id=current_user_id or None)


def get_review_aspect_unlock_status(
    review_id: str,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> ReviewAspectUnlockListResponse:
    _ensure_module_available(module_key="phone_review", request=request)
    channel_key = _resolve_request_channel(request)
    review = _require_owned_review(review_id, current_user_id=str(current_user["user_id"]))
    available_aspect_keys = _resolve_review_aspect_keys(review, channel_key=channel_key)
    unlocked_items = [
        _build_review_aspect_unlock_response(item)
        for item in list_review_aspect_unlocks(review_id=review_id, user_id=str(current_user["user_id"]))
    ]
    unlocked_key_set = {item.aspect_key for item in unlocked_items}
    public_view = _resolve_review_public_view(review, current_user_id=str(current_user["user_id"]), channel_key=channel_key)
    return ReviewAspectUnlockListResponse(
        items=unlocked_items,
        available_aspect_keys=available_aspect_keys,
        free_aspect_keys=_resolve_review_free_aspect_keys(available_aspect_keys, channel_key=channel_key),
        unlocked_aspect_keys=[item for item in available_aspect_keys if item in unlocked_key_set],
        aspect_unlock_points_cost=get_runtime_phone_review_aspect_unlock_points_cost(channel_key),
        unlock_enforcement_enabled=get_runtime_phone_review_unlock_enforcement_enabled(channel_key),
        aspects=_build_review_aspect_models(public_view),
    )


def create_review_aspect_unlock_record(
    review_id: str,
    payload: ReviewAspectUnlockRequest,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> ReviewAspectUnlockResponse:
    _ensure_module_available(module_key="phone_review", request=request)
    current_user_id = str(current_user["user_id"])
    review = _require_owned_review(review_id, current_user_id=current_user_id)
    channel_key = _resolve_request_channel(request)
    available_aspect_keys = _resolve_review_aspect_keys(review, channel_key=channel_key)
    normalized_aspect_key = payload.aspect_key.strip().lower()
    if normalized_aspect_key not in available_aspect_keys:
        raise HTTPException(status_code=422, detail="invalid_aspect_key")
    if not _review_aspect_detail_ready(review, normalized_aspect_key):
        raise HTTPException(status_code=409, detail="aspect_not_ready")
    points_cost = get_runtime_phone_review_aspect_unlock_points_cost(channel_key)
    try:
        unlock = create_review_aspect_unlock(
            review_id=review_id,
            user_id=current_user_id,
            aspect_key=normalized_aspect_key,
            points_cost=points_cost,
            usage_scene=PHONE_REVIEW_ASPECT_UNLOCK_SCENE,
            request_payload_summary={"aspect_key": normalized_aspect_key, "phone": review["phone"]},
            now_text=_utc_now(),
            channel=channel_key,
        )
    except InsufficientPointsError as exc:
        raise HTTPException(status_code=402, detail="insufficient_points") from exc
    public_view = _resolve_review_public_view(review, current_user_id=current_user_id, channel_key=channel_key)
    aspect_map = {item.aspect_key: item for item in _build_review_aspect_models(public_view)}
    points_account = get_points_account(current_user_id)
    return _build_review_aspect_unlock_response(
        unlock,
        points=_build_points_account_response(points_account) if points_account is not None else None,
        aspect=aspect_map.get(normalized_aspect_key),
    )


def create_four_pillars_review_record(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: FourPillarsReviewCreateRequest,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsReviewRecordResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    input_profile = _normalize_four_pillars_input_profile(payload)
    review_id = uuid4().hex
    created_at = _utc_now()
    user_id = str(current_user["user_id"])
    channel_key = _resolve_request_channel(request)
    points_cost = get_runtime_four_pillars_base_points_cost(channel_key)
    try:
        create_four_pillars_review_with_charge(
            review_id=review_id,
            user_id=user_id,
            gender=input_profile["gender"],
            birth_date=input_profile["birth_date"],
            birth_time=input_profile["birth_time"],
            timezone_name=input_profile["timezone"],
            birth_place=input_profile.get("birth_place"),
            name=input_profile.get("name"),
            status="processing",
            created_at=created_at,
            progress_stage="queued",
            progress_message="四柱评测任务已创建，等待开始",
            points_cost=points_cost,
            usage_scene=FOUR_PILLARS_REVIEW_BASE_SCENE,
            request_payload_summary={
                "gender": input_profile["gender"],
                "birth_date": input_profile["birth_date"],
                "birth_time": input_profile["birth_time"],
                "timezone": input_profile["timezone"],
                "birth_place": input_profile.get("birth_place"),
                "name": input_profile.get("name"),
                "include_markdown": payload.include_markdown,
            },
            channel=channel_key,
        )
    except InsufficientPointsError as exc:
        raise HTTPException(status_code=402, detail="insufficient_points") from exc
    background_tasks.add_task(
        _run_four_pillars_review_generation,
        review_id=review_id,
        input_profile=input_profile,
        include_markdown=payload.include_markdown,
        user_id=user_id,
        points_cost=points_cost,
        channel_key=channel_key,
    )
    review = get_four_pillars_review(review_id)
    if review is None:
        raise HTTPException(status_code=500, detail="review_persistence_failed")
    return _build_four_pillars_review_record_response(
        review,
        channel_key=channel_key,
        current_user_id=user_id,
    )


def list_four_pillars_review_records(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict[str, object] = Depends(require_authenticated_user),
) -> FourPillarsReviewListResponse:
    items = [
        _build_four_pillars_review_summary_response(item)
        for item in list_four_pillars_reviews(limit=limit, offset=offset, user_id=str(current_user["user_id"]))
    ]
    return FourPillarsReviewListResponse(items=items, total=len(items), limit=limit, offset=offset)


def get_four_pillars_review_record(
    request: Request,
    review_id: str,
    current_user: dict[str, object] | None = Depends(resolve_authenticated_user),
) -> FourPillarsReviewRecordResponse:
    review = get_four_pillars_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    review_user_id = str(review.get("user_id") or "")
    current_user_id = str(current_user["user_id"]) if current_user else ""
    if review_user_id and review_user_id != current_user_id:
        raise HTTPException(status_code=404, detail="review_not_found")
    return _build_four_pillars_review_record_response(review, channel_key=_resolve_request_channel(request), current_user_id=current_user_id or None)


def get_four_pillars_review_aspect_unlock_status(
    review_id: str,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsAspectUnlockListResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    channel_key = _resolve_request_channel(request)
    review = _require_owned_four_pillars_review(review_id, current_user_id=str(current_user["user_id"]))
    available_aspect_keys = _resolve_four_pillars_aspect_keys(review, channel_key=channel_key)
    unlocked_items = [
        _build_four_pillars_aspect_unlock_response(item)
        for item in list_four_pillars_aspect_unlocks(review_id=review_id, user_id=str(current_user["user_id"]))
    ]
    unlocked_key_set = {item.aspect_key for item in unlocked_items}
    public_view = _resolve_four_pillars_public_view(review, current_user_id=str(current_user["user_id"]), channel_key=channel_key)
    return FourPillarsAspectUnlockListResponse(
        items=unlocked_items,
        available_aspect_keys=available_aspect_keys,
        free_aspect_keys=_resolve_four_pillars_free_aspect_keys(available_aspect_keys, channel_key=channel_key),
        unlocked_aspect_keys=[item for item in available_aspect_keys if item in unlocked_key_set],
        aspect_unlock_points_cost=get_runtime_four_pillars_aspect_unlock_points_cost(channel_key),
        unlock_enforcement_enabled=get_runtime_four_pillars_unlock_enforcement_enabled(channel_key),
        aspects=_build_four_pillars_aspect_models(public_view),
    )


def create_four_pillars_review_aspect_unlock_record(
    review_id: str,
    payload: ReviewAspectUnlockRequest,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsAspectUnlockResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    current_user_id = str(current_user["user_id"])
    review = _require_owned_four_pillars_review(review_id, current_user_id=current_user_id)
    channel_key = _resolve_request_channel(request)
    available_aspect_keys = _resolve_four_pillars_aspect_keys(review, channel_key=channel_key)
    normalized_aspect_key = payload.aspect_key.strip().lower()
    if normalized_aspect_key not in available_aspect_keys:
        raise HTTPException(status_code=422, detail="invalid_aspect_key")
    if not _four_pillars_aspect_detail_ready(review, normalized_aspect_key):
        raise HTTPException(status_code=409, detail="aspect_not_ready")
    free_aspect_keys = _resolve_four_pillars_free_aspect_keys(available_aspect_keys, channel_key=channel_key)
    points_cost = 0 if normalized_aspect_key in free_aspect_keys else get_runtime_four_pillars_aspect_unlock_points_cost(channel_key)
    try:
        unlock = create_four_pillars_aspect_unlock(
            review_id=review_id,
            user_id=current_user_id,
            aspect_key=normalized_aspect_key,
            points_cost=points_cost,
            usage_scene=FOUR_PILLARS_ASPECT_UNLOCK_SCENE,
            request_payload_summary={"aspect_key": normalized_aspect_key, "birth_date": review["birth_date"], "birth_time": review["birth_time"]},
            now_text=_utc_now(),
            channel=channel_key,
        )
    except InsufficientPointsError as exc:
        raise HTTPException(status_code=402, detail="insufficient_points") from exc
    public_view = _resolve_four_pillars_public_view(review, current_user_id=current_user_id, channel_key=channel_key)
    aspect_map = {item.aspect_key: item for item in _build_four_pillars_aspect_models(public_view)}
    points_account = get_points_account(current_user_id)
    return _build_four_pillars_aspect_unlock_response(
        unlock,
        points=_build_points_account_response(points_account) if points_account is not None else None,
        aspect=aspect_map.get(normalized_aspect_key),
    )


def get_four_pillars_luck_cycles(
    review_id: str,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsLuckCycleListResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    current_user_id = str(current_user["user_id"])
    review = _require_owned_four_pillars_review(review_id, current_user_id=current_user_id)
    public_view = _resolve_four_pillars_public_view(review, current_user_id=current_user_id, channel_key=_resolve_request_channel(request))
    return FourPillarsLuckCycleListResponse(
        luck_analysis=_build_four_pillars_luck_analysis_payload(
            review,
            public_view=public_view,
            current_user_id=current_user_id,
            channel_key=_resolve_request_channel(request),
        )
    )


def create_four_pillars_luck_cycle_summary(
    review_id: str,
    cycle_key: str,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsLuckRenderRecordResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    return _create_four_pillars_luck_render(
        review_id=review_id,
        render_type="dayun",
        cycle_key=cycle_key,
        year=None,
        request=request,
        background_tasks=background_tasks,
        current_user_id=str(current_user["user_id"]),
    )


def get_four_pillars_luck_cycle_summary(
    review_id: str,
    cycle_key: str,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsLuckRenderRecordResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    render = get_four_pillars_luck_render(
        review_id=review_id,
        user_id=str(current_user["user_id"]),
        render_type="dayun",
        cycle_key=cycle_key,
        year=None,
    )
    if render is None:
        raise HTTPException(status_code=404, detail="luck_render_not_found")
    return _build_four_pillars_luck_render_response(render)


def create_four_pillars_luck_year_summary(
    review_id: str,
    cycle_key: str,
    year: int,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsLuckRenderRecordResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    return _create_four_pillars_luck_render(
        review_id=review_id,
        render_type="liunian",
        cycle_key=cycle_key,
        year=year,
        request=request,
        background_tasks=background_tasks,
        current_user_id=str(current_user["user_id"]),
    )


def get_four_pillars_luck_year_summary(
    review_id: str,
    cycle_key: str,
    year: int,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> FourPillarsLuckRenderRecordResponse:
    _ensure_module_available(module_key="four_pillars", request=request)
    render = get_four_pillars_luck_render(
        review_id=review_id,
        user_id=str(current_user["user_id"]),
        render_type="liunian",
        cycle_key=cycle_key,
        year=year,
    )
    if render is None:
        raise HTTPException(status_code=404, detail="luck_render_not_found")
    return _build_four_pillars_luck_render_response(render)


def create_voice_narration(
    payload: VoiceNarrationRequest,
    request: Request,
    current_user: dict[str, object] = Depends(require_registered_user),
) -> VoiceNarrationResponse:
    _ensure_module_available(module_key="voice", request=request)
    current_user_id = str(current_user["user_id"])
    channel_key = _resolve_request_channel(request)
    review = _require_owned_review(
        payload.review_id,
        current_user_id=current_user_id,
        not_ready_detail="review_not_ready_for_voice",
    )
    public_view = _resolve_review_voice_public_view(review, current_user_id=current_user_id, channel_key=channel_key)
    if not public_view:
        raise HTTPException(status_code=409, detail="review_not_ready_for_voice")

    narration_text = _build_voice_narration_text(payload, public_view)
    max_chars = get_runtime_voice_max_chars_per_request(channel_key)
    if len(narration_text) > max_chars:
        raise HTTPException(status_code=422, detail="voice_text_too_long")

    provider = get_runtime_voice_provider(channel_key)
    voice_key = str(payload.voice_key or get_runtime_voice_default_voice_key(channel_key)).strip() or get_runtime_voice_default_voice_key(channel_key)
    try:
        audio_result = synthesize_voice_audio(
            text=narration_text,
            scene=payload.scene,
            provider=provider,
            voice_key=voice_key,
            cache_enabled=get_runtime_voice_cache_enabled(channel_key),
        )
    except VoiceProviderUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc) or "voice_provider_unavailable") from exc
    except VoiceSynthesisError as exc:
        raise HTTPException(status_code=502, detail=str(exc) or "voice_synthesis_failed") from exc

    target_id = _resolve_voice_target_id(payload)
    _record_zero_cost_usage(
        user_id=current_user_id,
        scene=VOICE_TTS_SCENE,
        channel=channel_key,
        target_id=target_id,
        request_payload_summary={"scene": payload.scene, "review_id": payload.review_id, "aspect_key": payload.aspect_key},
        result_summary={
            "status": "completed",
            "provider": audio_result.provider,
            "voice_key": audio_result.voice_key,
            "text_hash": audio_result.text_hash,
            "char_count": audio_result.char_count,
            "cached": audio_result.cached,
        },
    )
    return VoiceNarrationResponse(
        narration_id=uuid4().hex,
        scene=payload.scene,
        text_hash=audio_result.text_hash,
        audio_url=audio_result.audio_url,
        provider=audio_result.provider,
        voice_key=audio_result.voice_key,
        format="mp3",
        char_count=audio_result.char_count,
        cached=audio_result.cached,
    )


def get_user_debug(user_id: str) -> UserResponse:
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_user_response(user)



def _build_review_record_response(
    review: dict[str, object],
    *,
    channel_key: str | None = None,
    current_user_id: str | None = None,
) -> ReviewRecordResponse:
    public_view = _resolve_review_public_view(review, current_user_id=current_user_id, channel_key=channel_key)
    return ReviewRecordResponse(
        id=str(review["id"]),
        report_id=str(review["id"]),
        phone=str(review["phone"]),
        phone_number=str(review["phone"]),
        masked_phone=_mask_phone(str(review["phone"])),
        gender=str(review["gender"]),
        status=str(review["status"]),
        progress_stage=review.get("progress_stage"),
        progress_message=review.get("progress_message"),
        score=_coerce_review_score(review, public_view),
        phone_summary=_build_review_phone_summary(public_view.get("phone_summary") if public_view else None),
        board=_build_review_board_response(public_view.get("board") if public_view else None),
        stability_detail=_build_review_stability_detail(public_view.get("stability_detail") if public_view else None),
        aspects=_build_review_aspect_models(public_view),
        aspect_unlock_points=int(public_view.get("aspect_unlock_points")) if public_view and public_view.get("aspect_unlock_points") is not None else None,
        free_aspect_keys=list(public_view.get("free_aspect_keys") or []) if public_view else [],
        unlock_enforcement_enabled=bool(public_view.get("unlock_enforcement_enabled")) if public_view and public_view.get("unlock_enforcement_enabled") is not None else None,
        score_markdown=review.get("score_markdown"),
        error_message=review.get("error_message"),
        created_at=str(review["created_at"]),
        updated_at=str(review["updated_at"]),
    )


def _build_review_summary_response(review: dict[str, object]) -> ReviewSummaryResponse:
    return ReviewSummaryResponse(
        id=str(review["id"]),
        report_id=str(review["id"]),
        phone=str(review["phone"]),
        phone_number=str(review["phone"]),
        masked_phone=_mask_phone(str(review["phone"])),
        gender=str(review["gender"]),
        status=str(review["status"]),
        progress_stage=review.get("progress_stage"),
        progress_message=review.get("progress_message"),
        score=_coerce_review_score(review),
        error_message=review.get("error_message"),
        created_at=str(review["created_at"]),
        updated_at=str(review["updated_at"]),
    )


def _build_four_pillars_review_record_response(
    review: dict[str, object],
    *,
    channel_key: str | None = None,
    current_user_id: str | None = None,
) -> FourPillarsReviewRecordResponse:
    public_view = _resolve_four_pillars_public_view(review, current_user_id=current_user_id, channel_key=channel_key)
    input_profile = _resolve_four_pillars_input_profile_from_review(review, public_view)
    return FourPillarsReviewRecordResponse(
        id=str(review["id"]),
        report_id=str(review["id"]),
        gender=str(review["gender"]),
        birth_date=str(review["birth_date"]),
        birth_time=str(review["birth_time"]),
        timezone=str(review["timezone"]),
        birth_place=review.get("birth_place"),
        name=review.get("name"),
        status=str(review["status"]),
        progress_stage=review.get("progress_stage"),
        progress_message=review.get("progress_message"),
        score=_coerce_four_pillars_score(review, public_view),
        input_profile=input_profile,
        chart=public_view.get("chart") if public_view else _resolve_four_pillars_template_dict(review, "chart"),
        chart_display=public_view.get("chart_display") if public_view and isinstance(public_view.get("chart_display"), dict) else None,
        summary=_build_four_pillars_summary_response(public_view.get("summary") if public_view else None),
        deterministic_facts=public_view.get("deterministic_facts") if public_view else (_resolve_four_pillars_template_dict(review, "deterministic_facts") or {}),
        aspects=_build_four_pillars_aspect_models(public_view),
        analysis_branches=public_view.get("analysis_branches") if public_view and isinstance(public_view.get("analysis_branches"), dict) else {},
        luck_analysis=_build_four_pillars_luck_analysis_payload(
            review,
            public_view=public_view,
            current_user_id=current_user_id,
            channel_key=channel_key,
        ),
        aspect_unlock_points=int(public_view.get("aspect_unlock_points")) if public_view and public_view.get("aspect_unlock_points") is not None else None,
        free_aspect_keys=list(public_view.get("free_aspect_keys") or []) if public_view else [],
        unlock_enforcement_enabled=bool(public_view.get("unlock_enforcement_enabled")) if public_view and public_view.get("unlock_enforcement_enabled") is not None else None,
        score_markdown=review.get("score_markdown"),
        error_message=review.get("error_message"),
        created_at=str(review["created_at"]),
        updated_at=str(review["updated_at"]),
    )


def _build_four_pillars_review_summary_response(review: dict[str, object]) -> FourPillarsReviewSummaryResponse:
    return FourPillarsReviewSummaryResponse(
        id=str(review["id"]),
        report_id=str(review["id"]),
        gender=str(review["gender"]),
        birth_date=str(review["birth_date"]),
        birth_time=str(review["birth_time"]),
        timezone=str(review["timezone"]),
        birth_place=review.get("birth_place"),
        name=review.get("name"),
        status=str(review["status"]),
        progress_stage=review.get("progress_stage"),
        progress_message=review.get("progress_message"),
        score=_coerce_four_pillars_score(review),
        error_message=review.get("error_message"),
        created_at=str(review["created_at"]),
        updated_at=str(review["updated_at"]),
    )


def _build_four_pillars_summary_response(payload: Any) -> FourPillarsSummaryResponse | None:
    if not isinstance(payload, dict):
        return None
    title = str(payload.get("title") or "").strip()
    risk = str(payload.get("risk") or "").strip()
    usage_guidance = str(payload.get("usage_guidance") or "").strip()
    elements_check = _string_dict(payload.get("elements_check"))
    if not title and not risk and not usage_guidance and not elements_check:
        return None
    return FourPillarsSummaryResponse(
        title=title,
        risk=risk,
        usage_guidance=usage_guidance,
        elements_check=elements_check,
    )


def _build_four_pillars_aspect_models(public_view: dict[str, Any] | None) -> list[FourPillarsAspectResponse]:
    if not isinstance(public_view, dict):
        return []
    items = public_view.get("aspects")
    if not isinstance(items, list):
        return []
    return [FourPillarsAspectResponse(**item) for item in items if isinstance(item, dict)]


def _build_four_pillars_aspect_unlock_response(
    item: dict[str, object],
    *,
    points: PointsAccountResponse | None = None,
    aspect: FourPillarsAspectResponse | None = None,
) -> FourPillarsAspectUnlockResponse:
    return FourPillarsAspectUnlockResponse(
        unlock_id=str(item["unlock_id"]),
        review_id=str(item["review_id"]),
        user_id=str(item["user_id"]),
        aspect_key=str(item["aspect_key"]),
        points_cost=int(item["points_cost"]),
        usage_record_id=str(item["usage_record_id"]),
        unlocked_at=str(item["unlocked_at"]),
        points=points,
        aspect=aspect,
    )


def _build_four_pillars_luck_render_response(item: dict[str, Any]) -> FourPillarsLuckRenderRecordResponse:
    return FourPillarsLuckRenderRecordResponse(**item)


def _build_four_pillars_luck_analysis_payload(
    review: dict[str, object],
    *,
    public_view: dict[str, Any] | None,
    current_user_id: str | None,
    channel_key: str | None,
) -> dict[str, Any]:
    luck_source = public_view.get("luck_analysis") if isinstance(public_view, dict) else None
    cycles = []
    current_cycle_key = None
    if isinstance(luck_source, dict):
        cycles = [dict(item) for item in luck_source.get("cycles", []) if isinstance(item, dict)]
        current_cycle_key = luck_source.get("current_cycle_key")
    else:
        score_template = review.get("score_template")
        facts = score_template.get("deterministic_facts") if isinstance(score_template, dict) else None
        luck_cycles = facts.get("luck_cycles") if isinstance(facts, dict) and isinstance(facts.get("luck_cycles"), dict) else {}
        cycles = [dict(item) for item in luck_cycles.get("cycles", []) if isinstance(item, dict)]
        current_cycle_key = luck_cycles.get("current_cycle_key")

    render_map: dict[tuple[str, str, int], dict[str, Any]] = {}
    if current_user_id:
        for render in list_four_pillars_luck_renders(review_id=str(review["id"]), user_id=current_user_id):
            render_map[(str(render["render_type"]), str(render["cycle_key"]), int(render.get("year") or 0))] = render

    response_cycles: list[dict[str, Any]] = []
    for cycle in cycles:
        cycle_key = str(cycle.get("cycle_key") or "")
        cycle_render = render_map.get(("dayun", cycle_key, 0))
        next_cycle = {
            key: cycle.get(key)
            for key in (
                "cycle_key",
                "start_year",
                "end_year",
                "start_age",
                "end_age",
                "ganzhi",
                "display_ganzhi",
                "is_current",
                "stem",
                "branch",
                "stem_ten_god",
                "stem_element",
                "branch_element",
            )
        }
        next_cycle["render_status"] = str(cycle_render.get("status") if cycle_render else "not_generated")
        next_cycle["render"] = _build_four_pillars_luck_render_response(cycle_render).model_dump() if cycle_render else None
        year_items = []
        for year_item in cycle.get("year_items", []):
            if not isinstance(year_item, dict):
                continue
            year_value = int(year_item.get("year") or 0)
            year_render = render_map.get(("liunian", cycle_key, year_value))
            next_year = dict(year_item)
            next_year["render_status"] = str(year_render.get("status") if year_render else "not_generated")
            next_year["render"] = _build_four_pillars_luck_render_response(year_render).model_dump() if year_render else None
            year_items.append(next_year)
        next_cycle["year_items"] = year_items
        response_cycles.append(next_cycle)

    return {
        "enabled": get_runtime_four_pillars_luck_generation_enabled(channel_key),
        "cycle_points_cost": get_runtime_four_pillars_luck_cycle_points_cost(channel_key),
        "year_points_cost": get_runtime_four_pillars_luck_year_points_cost(channel_key),
        "current_cycle_key": current_cycle_key,
        "cycles": response_cycles,
    }


def _build_internal_four_pillars_unlock_response(item: dict[str, object]) -> InternalFourPillarsAspectUnlockRecordResponse:
    aspect_key = str(item["aspect_key"])
    return InternalFourPillarsAspectUnlockRecordResponse(
        unlock_id=str(item["unlock_id"]),
        review_id=str(item["review_id"]),
        user_id=str(item["user_id"]),
        aspect_key=aspect_key,
        aspect_name=FOUR_PILLARS_ASPECT_LABELS.get(aspect_key, aspect_key),
        points_cost=int(item["points_cost"]),
        usage_record_id=str(item["usage_record_id"]) if item.get("usage_record_id") else None,
        unlocked_at=str(item["unlocked_at"]),
    )


def _resolve_four_pillars_input_profile_from_review(review: dict[str, object], public_view: dict[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(public_view, dict) and isinstance(public_view.get("input_profile"), dict):
        return dict(public_view["input_profile"])
    score_template = review.get("score_template")
    if isinstance(score_template, dict) and isinstance(score_template.get("input_profile"), dict):
        return dict(score_template["input_profile"])
    return {
        "gender": review.get("gender"),
        "birth_date": review.get("birth_date"),
        "birth_time": review.get("birth_time"),
        "timezone": review.get("timezone"),
        "birth_place": review.get("birth_place"),
        "name": review.get("name"),
    }


def _resolve_four_pillars_template_dict(review: dict[str, object], key: str) -> dict[str, Any] | None:
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return None
    value = score_template.get(key)
    return dict(value) if isinstance(value, dict) else None



def _build_user_response(user: dict[str, object]) -> UserResponse:
    return UserResponse(user_id=str(user["user_id"]), uid=str(user["uid"]) if user.get("uid") else None, status=str(user["status"]), identity_level=str(user.get("identity_level") or "normal_user"), nickname=user.get("nickname"), avatar_url=user.get("avatar_url"), profile_completed=bool(user["profile_completed"]), created_at=str(user["created_at"]), updated_at=str(user["updated_at"]), last_active_at=str(user["last_active_at"]))



def _build_internal_user_response(user: dict[str, object]) -> InternalUserResponse:
    return InternalUserResponse(
        user_id=str(user["user_id"]),
        uid=str(user["uid"]) if user.get("uid") else None,
        status=str(user["status"]),
        identity_level=str(user.get("identity_level") or "normal_user"),
        primary_identity_type=str(user.get("primary_identity_type") or "unknown"),
        registered_channel=str(user["registered_channel"]) if user.get("registered_channel") else None,
        promoter_parent_user_id=str(user["promoter_parent_user_id"]) if user.get("promoter_parent_user_id") else None,
        nickname=user.get("nickname"),
        avatar_url=user.get("avatar_url"),
        profile_completed=bool(user["profile_completed"]),
        points_balance=int(user.get("points_balance", 0) or 0),
        frozen_balance=int(user.get("frozen_balance", 0) or 0),
        withdrawable_balance_cents=int(user.get("withdrawable_balance_cents", 0) or 0),
        frozen_commission_cents=int(user.get("frozen_commission_cents", 0) or 0),
        withdrawn_amount_cents=int(user.get("withdrawn_amount_cents", 0) or 0),
        rebate_points_balance=int(user.get("rebate_points_balance", 0) or 0),
        rebate_frozen_balance=int(user.get("rebate_frozen_balance", 0) or 0),
        primary_phone=str(user["primary_phone"]) if user.get("primary_phone") else None,
        phone_verified_at=str(user["phone_verified_at"]) if user.get("phone_verified_at") else None,
        primary_unionid=str(user["primary_unionid"]) if user.get("primary_unionid") else None,
        first_login_at=str(user.get("first_login_at") or user["created_at"]),
        registered_at=str(user.get("registered_at") or user["created_at"]),
        created_at=str(user["created_at"]),
        updated_at=str(user["updated_at"]),
        last_active_at=str(user["last_active_at"]),
        openid=user.get("openid"),
        unionid=user.get("unionid"),
    )


def _build_recharge_order_summary_response(item: dict[str, object]) -> RechargeOrderSummaryResponse:
    return RechargeOrderSummaryResponse(
        order_id=str(item["order_id"]),
        package_title=str(item["package_title"]),
        amount_cents=int(item["amount_cents"]),
        status=str(item["status"]),
        created_at=str(item["created_at"]),
        reviewed_at=str(item["reviewed_at"]) if item.get("reviewed_at") else None,
        reviewed_by=str(item["reviewed_by"]) if item.get("reviewed_by") else None,
        paid_at=str(item["paid_at"]) if item.get("paid_at") else None,
        completed_at=str(item["completed_at"]) if item.get("completed_at") else None,
    )



def _build_points_account_response(points_account: dict[str, object]) -> PointsAccountResponse:
    return PointsAccountResponse(
        balance=int(points_account["balance"]),
        frozen_balance=int(points_account["frozen_balance"]),
        created_at=str(points_account["created_at"]) if points_account.get("created_at") else None,
        updated_at=str(points_account["updated_at"]) if points_account.get("updated_at") else None,
    )



def _build_points_response_from_user(user: dict[str, object]) -> PointsAccountResponse:
    return PointsAccountResponse(balance=int(user.get("points_balance", 0) or 0), frozen_balance=int(user.get("frozen_balance", 0) or 0), created_at=None, updated_at=None)



def _build_points_ledger_entry_response(item: dict[str, object]) -> PointsLedgerEntryResponse:
    return PointsLedgerEntryResponse(
        ledger_id=str(item["ledger_id"]),
        change_type=str(item["change_type"]),
        delta=int(item["delta"]),
        balance_after=int(item["balance_after"]),
        biz_type=str(item["biz_type"]),
        biz_id=item.get("biz_id"),
        idempotency_key=item.get("idempotency_key"),
        remark=item.get("remark"),
        created_at=str(item["created_at"]),
    )


def _build_points_claim_link_response(item: dict[str, object], *, now_text: str | None = None) -> PointsClaimLinkResponse:
    resolved_now = now_text or _utc_now()
    return PointsClaimLinkResponse(
        claim_link_id=str(item["claim_link_id"]),
        claim_code=str(item["claim_code"]),
        claim_url=_build_points_claim_url(str(item["claim_code"])),
        title=str(item["title"]),
        points_amount=int(item["points_amount"]),
        display_value_cents=int(item["display_value_cents"]),
        status=str(item["status"]),
        effective_status=_resolve_points_claim_effective_status(item, now_text=resolved_now),
        valid_from=str(item["valid_from"]),
        expires_at=str(item["expires_at"]),
        claimed_user_count=int(item.get("claimed_user_count", 0) or 0),
        granted_points_total=int(item.get("granted_points_total", 0) or 0),
        duplicate_attempt_count=int(item.get("duplicate_attempt_count", 0) or 0),
        created_by=str(item["created_by"]) if item.get("created_by") else None,
        disabled_by=str(item["disabled_by"]) if item.get("disabled_by") else None,
        disabled_at=str(item["disabled_at"]) if item.get("disabled_at") else None,
        operator_note=str(item["operator_note"]) if item.get("operator_note") else None,
        created_at=str(item["created_at"]),
        updated_at=str(item["updated_at"]),
    )


def _build_points_claim_record_response(item: dict[str, object]) -> PointsClaimRecordResponse:
    return PointsClaimRecordResponse(
        claim_record_id=str(item["claim_record_id"]),
        claim_link_id=str(item["claim_link_id"]),
        claim_code=str(item["claim_code"]) if item.get("claim_code") else None,
        claim_title=str(item["claim_title"]) if item.get("claim_title") else None,
        user_id=str(item["user_id"]),
        user_uid=str(item["user_uid"]) if item.get("user_uid") else None,
        user_nickname=str(item["user_nickname"]) if item.get("user_nickname") else None,
        user_phone=str(item["user_phone"]) if item.get("user_phone") else None,
        week_key=str(item["week_key"]),
        week_starts_at=str(item["week_starts_at"]),
        status=str(item["status"]),
        points_amount_snapshot=int(item["points_amount_snapshot"]),
        display_value_cents_snapshot=int(item.get("display_value_cents_snapshot", 0) or 0),
        ledger_id=str(item["ledger_id"]) if item.get("ledger_id") else None,
        failure_reason=str(item["failure_reason"]) if item.get("failure_reason") else None,
        request_ip=str(item["request_ip"]) if item.get("request_ip") else None,
        user_agent=str(item["user_agent"]) if item.get("user_agent") else None,
        created_at=str(item["created_at"]),
        updated_at=str(item["updated_at"]),
    )


def _build_public_points_claim_link_response(
    item: dict[str, object],
    *,
    now_text: str,
    current_status: str | None,
    current_record: dict[str, object] | None,
) -> PublicPointsClaimLinkResponse:
    return PublicPointsClaimLinkResponse(
        claim_code=str(item["claim_code"]),
        title=str(item["title"]),
        points_amount=int(item["points_amount"]),
        display_value_cents=int(item["display_value_cents"]),
        status=str(item["status"]),
        effective_status=_resolve_points_claim_effective_status(item, now_text=now_text),
        valid_from=str(item["valid_from"]),
        expires_at=str(item["expires_at"]),
        current_user_claim_status=current_status,
        current_user_claim_record=_build_points_claim_record_response(current_record) if current_record is not None else None,
    )


def _build_recharge_package_response(item: dict[str, object]) -> RechargePackageResponse:
    return RechargePackageResponse(
        package_key=str(item["package_key"]),
        title=str(item["title"]),
        description=item.get("description"),
        price_cents=int(item["price_cents"]),
        points_amount=int(item["points_amount"]),
        bonus_points=int(item["bonus_points"]),
        total_points=int(item["total_points"]),
        enabled=bool(item.get("enabled", True)),
        sort_order=int(item.get("sort_order", 0) or 0),
    )



def _build_recharge_order_response(item: dict[str, object]) -> RechargeOrderResponse:
    return RechargeOrderResponse(
        order_id=str(item["order_id"]),
        user_id=str(item["user_id"]),
        user_status=str(item["user_status"]) if item.get("user_status") else None,
        user_nickname=item.get("user_nickname"),
        channel=str(item["channel"]) if item.get("channel") else None,
        status=str(item["status"]),
        raw_status=str(item["raw_status"]) if item.get("raw_status") else None,
        package_key=str(item["package_key"]),
        package_title=str(item["package_title"]),
        amount_cents=int(item["amount_cents"]),
        points_amount=int(item["points_amount"]),
        bonus_points=int(item["bonus_points"]),
        total_points=int(item["total_points"]),
        source=str(item["source"]),
        external_order_id=str(item["external_order_id"]) if item.get("external_order_id") else None,
        proof_url=str(item["proof_url"]) if item.get("proof_url") else None,
        remark=item.get("remark"),
        review_note=item.get("review_note"),
        reviewed_by=str(item["reviewed_by"]) if item.get("reviewed_by") else None,
        reviewed_at=str(item["reviewed_at"]) if item.get("reviewed_at") else None,
        paid_at=str(item["paid_at"]) if item.get("paid_at") else None,
        completed_at=str(item["completed_at"]) if item.get("completed_at") else None,
        closed_at=str(item["closed_at"]) if item.get("closed_at") else None,
        granted_ledger_id=str(item["granted_ledger_id"]) if item.get("granted_ledger_id") else None,
        created_at=str(item["created_at"]),
        updated_at=str(item["updated_at"]),
    )


def _build_recharge_order_response_with_payments(item: dict[str, object], *, payment_limit: int = 20) -> RechargeOrderResponse:
    response = _build_recharge_order_response(item)
    payments = list_payment_transactions_for_order(str(item["order_id"]), limit=payment_limit)
    response.payment_transactions = [_build_payment_transaction_response(payment) for payment in payments]
    response.latest_payment = response.payment_transactions[0] if response.payment_transactions else None
    return response


def _build_payment_transaction_response(item: dict[str, object] | None, *, client_message: str | None = None) -> PaymentTransactionResponse:
    if item is None:
        raise ValueError("payment_transaction_required")
    return PaymentTransactionResponse(
        transaction_id=str(item["transaction_id"]),
        order_id=str(item["order_id"]),
        user_id=str(item["user_id"]),
        provider=str(item["provider"]),
        payment_method=str(item["payment_method"]),
        amount_cents=int(item["amount_cents"]),
        status=str(item["status"]),
        provider_transaction_id=str(item["provider_transaction_id"]) if item.get("provider_transaction_id") else None,
        prepay_id=str(item["prepay_id"]) if item.get("prepay_id") else None,
        idempotency_key=str(item["idempotency_key"]) if item.get("idempotency_key") else None,
        payment_params=dict(item.get("payment_params") or {}),
        client_message=client_message,
        failure_reason=str(item["failure_reason"]) if item.get("failure_reason") else None,
        paid_at=str(item["paid_at"]) if item.get("paid_at") else None,
        created_at=str(item["created_at"]),
        updated_at=str(item["updated_at"]),
    )



def _build_usage_record_response(item: dict[str, object]) -> UsageRecordResponse:
    return UsageRecordResponse(
        usage_record_id=str(item["usage_record_id"]),
        user_id=str(item["user_id"]),
        scene=str(item["scene"]),
        feature_key=str(item["feature_key"]),
        feature_name=item.get("feature_name"),
        channel=str(item["channel"]) if item.get("channel") else None,
        target_id=str(item["target_id"]) if item.get("target_id") else None,
        points_cost=int(item["points_cost"]),
        normal_points_cost=int(item.get("normal_points_cost", item["points_cost"]) or 0),
        rebate_points_cost=int(item.get("rebate_points_cost", 0) or 0),
        status=str(item["status"]),
        user_status=str(item["user_status"]) if item.get("user_status") else None,
        user_nickname=item.get("user_nickname"),
        user_phone=_extract_user_phone_from_usage_record(item),
        user_avatar_url=item.get("user_avatar_url"),
        request_payload_summary=item.get("request_payload_summary"),
        result_summary=item.get("result_summary"),
        created_at=str(item["created_at"]),
        updated_at=str(item["updated_at"]),
    )


def _extract_user_phone_from_usage_record(item: dict[str, object]) -> str | None:
    for summary_key in ("request_payload_summary", "result_summary"):
        summary = item.get(summary_key)
        if not isinstance(summary, dict):
            continue
        for phone_key in ("phone", "phone_number", "mobile", "mobile_phone"):
            raw_value = summary.get(phone_key)
            if raw_value is None:
                continue
            normalized = "".join(character for character in str(raw_value) if character.isdigit())
            if len(normalized) >= 7:
                return _mask_phone(normalized)
    return None



def _build_review_aspect_unlock_response(
    item: dict[str, object],
    *,
    points: PointsAccountResponse | None = None,
    aspect: ReviewAspectResponse | None = None,
) -> ReviewAspectUnlockResponse:
    return ReviewAspectUnlockResponse(
        unlock_id=str(item["unlock_id"]),
        review_id=str(item["review_id"]),
        user_id=str(item["user_id"]),
        aspect_key=str(item["aspect_key"]),
        points_cost=int(item["points_cost"]),
        usage_record_id=str(item["usage_record_id"]),
        unlocked_at=str(item["unlocked_at"]),
        points=points,
        aspect=aspect,
    )


def _build_internal_phone_qimen_unlock_response(item: dict[str, object]) -> InternalPhoneQimenAspectUnlockRecordResponse:
    aspect_key = str(item["aspect_key"])
    return InternalPhoneQimenAspectUnlockRecordResponse(
        unlock_id=str(item["unlock_id"]),
        review_id=str(item["review_id"]),
        user_id=str(item["user_id"]),
        aspect_key=aspect_key,
        aspect_name=PHONE_QIMEN_ASPECT_LABELS.get(aspect_key, aspect_key),
        points_cost=int(item["points_cost"]),
        usage_record_id=str(item["usage_record_id"]) if item.get("usage_record_id") else None,
        unlocked_at=str(item["unlocked_at"]),
    )


def _build_voice_narration_text(payload: VoiceNarrationRequest, public_view: dict[str, Any]) -> str:
    if payload.scene == "phone_summary":
        phone_summary = _build_review_phone_summary(public_view.get("phone_summary"))
        if phone_summary is None:
            raise HTTPException(status_code=409, detail="phone_summary_not_ready")
        parts = [
            "综合评述",
            phone_summary.title,
            "风险提醒",
            phone_summary.risk,
            "使用建议",
            phone_summary.usage_guidance,
        ]
        return _join_voice_parts(parts)

    if payload.scene == "phone_stability":
        stability_detail = _build_review_stability_detail(public_view.get("stability_detail"))
        if stability_detail is None:
            raise HTTPException(status_code=409, detail="stability_detail_not_ready")
        parts = [
            "长期使用建议",
            stability_detail.verdict,
            stability_detail.content,
        ]
        return _join_voice_parts(parts)

    if payload.scene == "phone_aspect":
        aspect_key = str(payload.aspect_key or "").strip().lower()
        if not aspect_key:
            raise HTTPException(status_code=422, detail="aspect_key_required")
        aspect = _find_public_view_aspect(public_view, aspect_key)
        if aspect is None:
            raise HTTPException(status_code=422, detail="invalid_aspect_key")
        if not aspect.is_unlocked:
            raise HTTPException(status_code=403, detail="aspect_not_unlocked")
        if not str(aspect.content or "").strip():
            raise HTTPException(status_code=409, detail="aspect_not_ready")
        aspect_title = aspect.short_title or aspect.title
        parts = [
            f"{aspect_title}专项",
            aspect.title,
        ]
        if str(aspect.risk or "").strip():
            parts.extend(["风险提示", aspect.risk or ""])
        parts.append(aspect.content or "")
        return _join_voice_parts(parts)

    raise HTTPException(status_code=422, detail="invalid_voice_scene")


def _resolve_voice_target_id(payload: VoiceNarrationRequest) -> str:
    if payload.scene == "phone_aspect":
        return f"{payload.review_id}:{payload.aspect_key}"
    if payload.scene == "phone_stability":
        return f"{payload.review_id}:stability"
    return payload.review_id


def _find_public_view_aspect(public_view: dict[str, Any], aspect_key: str) -> ReviewAspectResponse | None:
    for aspect in _build_review_aspect_models(public_view):
        if aspect.aspect_key == aspect_key:
            return aspect
    return None


def _join_voice_parts(parts: list[str | None]) -> str:
    cleaned_parts = []
    for part in parts:
        text = str(part or "").strip()
        if text and text not in {"title", "risk", "usage guidance"}:
            cleaned_parts.append(text.strip(" 。"))
    narration_text = "。".join(cleaned_parts).strip(" 。")
    if not narration_text:
        raise HTTPException(status_code=409, detail="voice_text_empty")
    return f"{narration_text}。"


def _resolve_four_pillars_public_view(
    review: dict[str, object],
    *,
    current_user_id: str | None,
    channel_key: str | None,
) -> dict[str, Any] | None:
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return None

    base_view = score_template.get("product_view")
    if (
        not isinstance(base_view, dict)
        or _four_pillars_product_view_needs_refresh(base_view)
        or _four_pillars_product_view_missing_cached_aspects(base_view, score_template)
    ):
        package = _build_four_pillars_package_from_review(review, score_template=score_template)
        if package is None:
            return None
        product_render = score_template.get("product_render") if isinstance(score_template.get("product_render"), dict) else {}
        summary = product_render.get("summary") if isinstance(product_render.get("summary"), dict) else {}
        if not (
            str(summary.get("title") or "").strip()
            and str(summary.get("risk") or "").strip()
            and str(summary.get("usage_guidance") or "").strip()
        ):
            score_template["product_render"] = build_four_pillars_core_render(package)
            package["score_template"] = score_template
        base_view = build_four_pillars_product_view(package)
        score_template["product_view"] = base_view
        now_text = _utc_now()
        score_result = package["score_result"]
        if str(review.get("status")) == "completed":
            update_four_pillars_review_score_template(review_id=str(review["id"]), score_template=score_template, updated_at=now_text)
        else:
            complete_four_pillars_review_with_message(
                review_id=str(review["id"]),
                score_result=score_result,
                score_template=score_template,
                score_markdown=review.get("score_markdown") if isinstance(review.get("score_markdown"), str) else None,
                progress_message="四柱总评已完成，专项内容正在后台生成",
                updated_at=now_text,
            )
            review["status"] = "completed"
            review["progress_stage"] = "completed"
            review["progress_message"] = "四柱总评已完成，专项内容正在后台生成"
        review["score_template"] = score_template
        review["updated_at"] = now_text

    return _apply_four_pillars_public_view_access(base_view, review, current_user_id=current_user_id, channel_key=channel_key)


def _apply_four_pillars_public_view_access(
    base_view: dict[str, Any],
    review: dict[str, object],
    *,
    current_user_id: str | None,
    channel_key: str | None,
) -> dict[str, Any]:
    public_view = dict(base_view)
    aspects = [dict(item) for item in public_view.get("aspects", []) if isinstance(item, dict)]
    configured_order = get_runtime_four_pillars_aspect_order(channel_key)
    valid_aspect_keys = set(FOUR_PILLARS_ASPECT_ORDER)
    available_aspect_keys = [
        str(item.get("aspect_key") or "").strip()
        for item in aspects
        if str(item.get("aspect_key") or "").strip() in valid_aspect_keys
    ]
    ordered_aspect_keys = [item for item in configured_order if item in available_aspect_keys]
    for item in available_aspect_keys:
        if item not in ordered_aspect_keys:
            ordered_aspect_keys.append(item)

    aspect_map = {str(item.get("aspect_key")): item for item in aspects}
    free_aspect_keys = _resolve_four_pillars_free_aspect_keys(ordered_aspect_keys, channel_key=channel_key)
    unlock_enforcement_enabled = get_runtime_four_pillars_unlock_enforcement_enabled(channel_key)
    unlocked_key_set = set(ordered_aspect_keys if not unlock_enforcement_enabled else free_aspect_keys)
    review_user_id = str(review.get("user_id") or "")

    if current_user_id and review_user_id and current_user_id == review_user_id:
        unlocked_items = list_four_pillars_aspect_unlocks(review_id=str(review["id"]), user_id=current_user_id)
        unlocked_key_set.update(str(item["aspect_key"]) for item in unlocked_items)

    ordered_aspects: list[dict[str, Any]] = []
    unlock_points_cost = get_runtime_four_pillars_aspect_unlock_points_cost(channel_key)
    for aspect_key in ordered_aspect_keys:
        aspect = dict(aspect_map[aspect_key])
        is_unlocked = aspect_key in unlocked_key_set
        aspect["is_unlocked"] = is_unlocked
        aspect["unlock_points"] = 0 if aspect_key in free_aspect_keys else unlock_points_cost
        if unlock_enforcement_enabled and not is_unlocked:
            aspect["content"] = None
            aspect["risk"] = None
            aspect["elements_check"] = {}
        ordered_aspects.append(aspect)

    public_view["aspects"] = ordered_aspects
    public_view["aspect_order"] = ordered_aspect_keys
    public_view["free_aspect_keys"] = free_aspect_keys
    public_view["aspect_unlock_points"] = unlock_points_cost
    public_view["unlock_enforcement_enabled"] = unlock_enforcement_enabled
    return public_view


def _four_pillars_product_view_needs_refresh(payload: dict[str, Any]) -> bool:
    if not isinstance(payload.get("input_profile"), dict):
        return True
    if not isinstance(payload.get("chart"), dict):
        return True
    if not isinstance(payload.get("chart_display"), dict):
        return True
    if not isinstance(payload.get("deterministic_facts"), dict):
        return True
    if not isinstance(payload.get("summary"), dict):
        return True
    aspects = payload.get("aspects")
    if not isinstance(aspects, list):
        return True
    seen_keys: set[str] = set()
    for item in aspects:
        if not isinstance(item, dict):
            return True
        aspect_key = str(item.get("aspect_key") or "").strip()
        if not aspect_key:
            return True
        seen_keys.add(aspect_key)
        if item.get("score") is None:
            return True
        if not isinstance(item.get("elements_check"), dict):
            return True
    return not set(FOUR_PILLARS_ASPECT_ORDER).issubset(seen_keys)


def _four_pillars_product_view_missing_cached_aspects(payload: dict[str, Any], score_template: dict[str, Any]) -> bool:
    product_aspects_render = score_template.get("product_aspects_render")
    if not isinstance(product_aspects_render, dict) or not product_aspects_render:
        return False

    public_aspects = payload.get("aspects")
    if not isinstance(public_aspects, list):
        return True
    public_aspect_map = {
        str(item.get("aspect_key") or "").strip(): item
        for item in public_aspects
        if isinstance(item, dict)
    }
    for aspect_key in FOUR_PILLARS_ASPECT_ORDER:
        cached_aspect = product_aspects_render.get(aspect_key)
        if not isinstance(cached_aspect, dict):
            continue
        public_aspect = public_aspect_map.get(aspect_key)
        if not isinstance(public_aspect, dict):
            return True
        if _rendered_aspect_field_changed(cached_aspect, public_aspect, "title"):
            return True
        if _rendered_aspect_field_changed(cached_aspect, public_aspect, "content"):
            return True
        if _rendered_aspect_field_changed(cached_aspect, public_aspect, "risk"):
            return True
        if cached_aspect.get("score") is not None and public_aspect.get("score") != cached_aspect.get("score"):
            return True
    return False


def _build_four_pillars_package_from_review(
    review: dict[str, object],
    *,
    score_template: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    resolved_template = score_template if isinstance(score_template, dict) else review.get("score_template")
    score_result = review.get("score_result")
    if not isinstance(resolved_template, dict) or not isinstance(score_result, dict):
        return None
    chart = resolved_template.get("chart")
    deterministic_facts = resolved_template.get("deterministic_facts")
    input_profile = resolved_template.get("input_profile")
    if not isinstance(chart, dict) or not isinstance(deterministic_facts, dict) or not isinstance(input_profile, dict):
        return None
    return {
        "input_profile": input_profile,
        "chart": chart,
        "deterministic_facts": deterministic_facts,
        "score_result": score_result,
        "score_template": resolved_template,
    }


def _resolve_review_voice_public_view(
    review: dict[str, object],
    *,
    current_user_id: str | None,
    channel_key: str | None,
) -> dict[str, Any] | None:
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return None

    score_result = review.get("score_result")
    if isinstance(score_result, dict):
        base_view = build_phone_review_product_view(score_result, score_template)
        base_view["rules_version"] = RULES.get("version")
    else:
        stored_view = score_template.get("product_view")
        if not isinstance(stored_view, dict):
            return None
        base_view = dict(stored_view)

    return _apply_review_public_view_access(base_view, review, current_user_id=current_user_id, channel_key=channel_key)


def _resolve_review_public_view(
    review: dict[str, object],
    *,
    current_user_id: str | None,
    channel_key: str | None,
) -> dict[str, Any] | None:
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return None

    base_view = score_template.get("product_view")
    if (
        not isinstance(base_view, dict)
        or _review_product_view_needs_refresh(base_view)
        or _review_product_view_missing_cached_aspects(base_view, score_template)
    ):
        score_result = review.get("score_result")
        if not isinstance(score_result, dict):
            return None
        product_render = score_template.get("product_render") if isinstance(score_template.get("product_render"), dict) else {}
        rendered_sections = product_render.get("sections") if isinstance(product_render.get("sections"), dict) else {}
        stability_section = rendered_sections.get("stability") if isinstance(rendered_sections.get("stability"), dict) else {}
        phone_summary = product_render.get("phone_summary") if isinstance(product_render.get("phone_summary"), dict) else {}
        needs_render_refresh = not (
            str(phone_summary.get("title") or "").strip()
            and str(phone_summary.get("risk") or "").strip()
            and str(phone_summary.get("usage_guidance") or "").strip()
            and str(stability_section.get("verdict") or "").strip()
            and str(stability_section.get("content") or "").strip()
        )
        if needs_render_refresh:
            refreshed_package = {
                "score_result": score_result,
                "score_template": dict(score_template),
            }
            refreshed_package["score_template"]["product_render"] = build_product_review_core_render(refreshed_package)
            score_template = refreshed_package["score_template"]
        base_view = build_phone_review_product_view(score_result, score_template)
        base_view["rules_version"] = RULES.get("version")
        score_template["product_view"] = base_view
        now_text = _utc_now()
        complete_review(
            review_id=str(review["id"]),
            status="completed",
            score_result=score_result,
            score_template=score_template,
            score_markdown=review.get("score_markdown") if isinstance(review.get("score_markdown"), str) else None,
            updated_at=now_text,
        )
        review["status"] = "completed"
        review["progress_stage"] = "completed"
        review["progress_message"] = "评测结果已生成"
        review["score_template"] = score_template
        review["updated_at"] = now_text

    return _apply_review_public_view_access(base_view, review, current_user_id=current_user_id, channel_key=channel_key)


def _apply_review_public_view_access(
    base_view: dict[str, Any],
    review: dict[str, object],
    *,
    current_user_id: str | None,
    channel_key: str | None,
) -> dict[str, Any]:
    public_view = dict(base_view)
    aspects = [dict(item) for item in public_view.get("aspects", []) if isinstance(item, dict)]
    configured_order = get_runtime_phone_review_aspect_order(channel_key)
    available_aspect_keys = [
        str(item.get("aspect_key") or item.get("aspect_id") or "").strip()
        for item in aspects
        if str(item.get("aspect_key") or item.get("aspect_id") or "").strip()
    ]
    ordered_aspect_keys = [item for item in configured_order if item in available_aspect_keys]
    for item in available_aspect_keys:
        if item not in ordered_aspect_keys:
            ordered_aspect_keys.append(item)

    aspect_map = {str(item.get("aspect_key") or item.get("aspect_id")): item for item in aspects}
    free_aspect_keys = _resolve_review_free_aspect_keys(ordered_aspect_keys, channel_key=channel_key)
    unlock_enforcement_enabled = get_runtime_phone_review_unlock_enforcement_enabled(channel_key)
    unlocked_key_set = set(ordered_aspect_keys if not unlock_enforcement_enabled else free_aspect_keys)
    review_user_id = str(review.get("user_id") or "")

    if current_user_id and review_user_id and current_user_id == review_user_id:
        unlocked_items = list_review_aspect_unlocks(review_id=str(review["id"]), user_id=current_user_id)
        unlocked_key_set.update(str(item["aspect_key"]) for item in unlocked_items)

    ordered_aspects: list[dict[str, Any]] = []
    unlock_points_cost = get_runtime_phone_review_aspect_unlock_points_cost(channel_key)
    for aspect_key in ordered_aspect_keys:
        aspect = dict(aspect_map[aspect_key])
        is_unlocked = aspect_key in unlocked_key_set
        aspect["is_unlocked"] = is_unlocked
        aspect["unlock_points"] = 0 if aspect_key in free_aspect_keys else unlock_points_cost
        if unlock_enforcement_enabled and not is_unlocked:
            aspect["content"] = None
            aspect["risk"] = None
            aspect["elements_check"] = {}
        ordered_aspects.append(aspect)

    public_view["aspects"] = ordered_aspects
    public_view["aspect_order"] = ordered_aspect_keys
    public_view["free_aspect_keys"] = free_aspect_keys
    public_view["aspect_unlock_points"] = unlock_points_cost
    public_view["unlock_enforcement_enabled"] = unlock_enforcement_enabled
    return public_view


def _build_review_phone_summary(payload: Any) -> ReviewPhoneSummaryResponse | None:
    if not isinstance(payload, dict):
        return None
    title = str(payload.get("title") or "").strip()
    risk = str(payload.get("risk") or "").strip()
    usage_guidance = str(payload.get("usage_guidance") or "").strip()
    elements_check = _string_dict(payload.get("elements_check"))
    if not title and not risk and not usage_guidance and not elements_check:
        return None
    return ReviewPhoneSummaryResponse(
        title=title,
        risk=risk,
        usage_guidance=usage_guidance,
        elements_check=elements_check,
    )


def _build_review_stability_detail(payload: Any) -> ReviewStabilityDetailResponse | None:
    if not isinstance(payload, dict):
        return None
    verdict = str(payload.get("verdict") or "").strip()
    content = str(payload.get("content") or "").strip()
    elements_check = _string_dict(payload.get("elements_check"))
    if not verdict and not content and not elements_check:
        return None
    return ReviewStabilityDetailResponse(
        verdict=verdict,
        content=content,
        elements_check=elements_check,
    )


def _string_dict(payload: Any) -> dict[str, str]:
    if not isinstance(payload, dict):
        return {}
    return {
        str(key): str(value).strip()
        for key, value in payload.items()
        if str(key).strip() and str(value).strip()
    }


def _build_review_board_response(payload: Any) -> ReviewBoardResponse | None:
    if not isinstance(payload, dict):
        return None
    if not isinstance(payload.get("grid_cells"), list):
        return None
    try:
        return ReviewBoardResponse(**payload)
    except Exception:
        return None


def _review_product_view_needs_refresh(payload: dict[str, Any]) -> bool:
    if payload.get("rules_version") != RULES.get("version"):
        return True
    if any(
        field in payload
        for field in ("summary", "board_analysis", "overall_detail", "stability_judgement", "elements_check", "long_term_advice")
    ):
        return True
    if not isinstance(payload.get("phone_summary"), dict):
        return True
    phone_summary = payload.get("phone_summary")
    if not isinstance(phone_summary.get("elements_check"), dict):
        return True
    if not isinstance(payload.get("stability_detail"), dict):
        return True
    board = payload.get("board")
    if not isinstance(board, dict):
        return True
    if not isinstance(board.get("grid_cells"), list):
        if isinstance(board.get("cells"), list):
            return True
        return True
    aspects = payload.get("aspects")
    if isinstance(aspects, list):
        seen_keys: set[str] = set()
        for item in aspects:
            if not isinstance(item, dict):
                return True
            aspect_key = str(item.get("aspect_key") or item.get("aspect_id") or "").strip()
            if not aspect_key:
                return True
            seen_keys.add(aspect_key)
            if item.get("score") is None:
                return True
            if not isinstance(item.get("elements_check"), dict):
                return True
            if any(field in item for field in ("level", "level_text", "core_judge", "explain", "signal", "suggestion")):
                return True
        if not set(PUBLIC_ASPECT_ORDER).issubset(seen_keys):
            return True
        return False
    if isinstance(board.get("cells"), list):
        return True
    return True


def _review_product_view_missing_cached_aspects(payload: dict[str, Any], score_template: dict[str, Any]) -> bool:
    product_aspects_render = score_template.get("product_aspects_render")
    if not isinstance(product_aspects_render, dict) or not product_aspects_render:
        return False

    public_aspects = payload.get("aspects")
    if not isinstance(public_aspects, list):
        return True
    public_aspect_map = {
        str(item.get("aspect_key") or item.get("aspect_id") or "").strip(): item
        for item in public_aspects
        if isinstance(item, dict)
    }

    for aspect_key in PUBLIC_ASPECT_ORDER:
        cached_aspect = product_aspects_render.get(aspect_key)
        if not isinstance(cached_aspect, dict):
            continue
        public_aspect = public_aspect_map.get(aspect_key)
        if not isinstance(public_aspect, dict):
            return True
        if _rendered_aspect_field_changed(cached_aspect, public_aspect, "title"):
            return True
        if _rendered_aspect_field_changed(cached_aspect, public_aspect, "content"):
            return True
        if _rendered_aspect_field_changed(cached_aspect, public_aspect, "risk"):
            return True
        cached_elements = cached_aspect.get("elements_check")
        if isinstance(cached_elements, dict) and cached_elements and public_aspect.get("elements_check") != cached_elements:
            return True
        if cached_aspect.get("score") is not None and public_aspect.get("score") != cached_aspect.get("score"):
            return True

    return False


def _rendered_aspect_field_changed(rendered: dict[str, Any], public: dict[str, Any], field: str) -> bool:
    rendered_value = str(rendered.get(field) or "").strip()
    if not rendered_value:
        return False
    return str(public.get(field) or "").strip() != rendered_value


def _build_review_aspect_models(public_view: dict[str, Any] | None) -> list[ReviewAspectResponse]:
    if not isinstance(public_view, dict):
        return []
    items = public_view.get("aspects")
    if not isinstance(items, list):
        return []
    return [ReviewAspectResponse(**item) for item in items if isinstance(item, dict)]


def _coerce_review_score(review: dict[str, object], public_view: dict[str, Any] | None = None) -> int | None:
    if isinstance(public_view, dict) and public_view.get("score") is not None:
        return int(public_view["score"])
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return None
    score_summary = score_template.get("score_summary")
    if not isinstance(score_summary, dict) or score_summary.get("final_score") is None:
        return None
    return int(score_summary["final_score"])



def _require_owned_recharge_order(order_id: str, *, current_user_id: str) -> dict[str, object]:
    order = get_recharge_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="recharge_order_not_found")
    if str(order.get("user_id") or "") != current_user_id:
        raise HTTPException(status_code=404, detail="recharge_order_not_found")
    return order



def _find_available_recharge_package(*, package_key: str, channel_key: str | None) -> dict[str, object] | None:
    normalized_package_key = package_key.strip()
    if not normalized_package_key:
        return None
    for item in get_runtime_available_recharge_packages(channel_key):
        if str(item.get("package_key") or "") == normalized_package_key:
            return item
    return None


def _resolve_points_claim_expires_at(payload: PointsClaimLinkCreateRequest, now_dt: datetime) -> str:
    if payload.expires_at:
        raw_text = payload.expires_at.strip()
        expires_at = _parse_iso_datetime(raw_text)
    else:
        expires_at = now_dt + timedelta(hours=int(payload.expires_in_hours or 24))
    if expires_at <= now_dt:
        raise ValueError("expires_at_must_be_after_now")
    if expires_at - now_dt > timedelta(days=30):
        raise ValueError("points_claim_duration_too_long")
    return expires_at.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_points_claim_effective_status(item: dict[str, object], *, now_text: str) -> str:
    status = str(item.get("status") or "").strip().lower()
    if status == "disabled":
        return "disabled"
    now_dt = _parse_iso_datetime(now_text)
    valid_from = _parse_iso_datetime(str(item["valid_from"]))
    expires_at = _parse_iso_datetime(str(item["expires_at"]))
    if now_dt < valid_from:
        return "not_started"
    if now_dt >= expires_at:
        return "expired"
    return status or "active"


def _build_points_claim_url(claim_code: str) -> str:
    path = f"/points-claim/{claim_code}"
    base_url = get_public_base_url()
    return f"{base_url}{path}" if base_url else path


def _points_claim_status_message(claim_status: str) -> str:
    message_map = {
        "granted": "积分已到账",
        "already_claimed_this_week": "本周已领取过免费积分",
    }
    return message_map.get(claim_status, claim_status)


def _parse_iso_datetime(value: str) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _normalize_four_pillars_input_profile(payload: FourPillarsReviewCreateRequest) -> dict[str, Any]:
    timezone_name = str(payload.timezone or "Asia/Shanghai").strip() or "Asia/Shanghai"
    try:
        ZoneInfo(timezone_name)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="invalid_timezone") from exc
    try:
        datetime.fromisoformat(f"{payload.birth_date}T{payload.birth_time}:00")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="invalid_birth_datetime") from exc
    return {
        "gender": payload.gender,
        "birth_date": payload.birth_date,
        "birth_time": payload.birth_time,
        "timezone": timezone_name,
        "birth_place": _normalize_optional_profile_text(payload.birth_place),
        "name": _normalize_optional_profile_text(payload.name),
    }


def _normalize_optional_profile_text(value: str | None) -> str | None:
    text = str(value or "").strip()
    return text or None



def _require_owned_review(review_id: str, *, current_user_id: str, not_ready_detail: str = "review_not_ready_for_unlock") -> dict[str, object]:
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    review_user_id = str(review.get("user_id") or "")
    if not review_user_id or review_user_id != current_user_id:
        raise HTTPException(status_code=404, detail="review_not_found")
    if str(review.get("status")) != "completed" or not isinstance(review.get("score_template"), dict):
        raise HTTPException(status_code=409, detail=not_ready_detail)
    return review



def _require_owned_four_pillars_review(review_id: str, *, current_user_id: str, not_ready_detail: str = "review_not_ready_for_unlock") -> dict[str, object]:
    review = get_four_pillars_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    review_user_id = str(review.get("user_id") or "")
    if not review_user_id or review_user_id != current_user_id:
        raise HTTPException(status_code=404, detail="review_not_found")
    if str(review.get("status")) != "completed" or not isinstance(review.get("score_template"), dict):
        raise HTTPException(status_code=409, detail=not_ready_detail)
    return review


def _create_four_pillars_luck_render(
    *,
    review_id: str,
    render_type: str,
    cycle_key: str,
    year: int | None,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user_id: str,
) -> FourPillarsLuckRenderRecordResponse:
    channel_key = _resolve_request_channel(request)
    if not get_runtime_four_pillars_luck_generation_enabled(channel_key):
        raise HTTPException(status_code=403, detail="luck_generation_disabled")
    review = _require_owned_four_pillars_review(review_id, current_user_id=current_user_id, not_ready_detail="review_not_ready_for_luck")
    existing_render = get_four_pillars_luck_render(
        review_id=review_id,
        user_id=current_user_id,
        render_type=render_type,
        cycle_key=cycle_key,
        year=year,
    )
    if existing_render is not None and existing_render.get("status") in {"processing", "completed"}:
        return _build_four_pillars_luck_render_response(existing_render)
    package = _build_four_pillars_package_from_review(review)
    if package is None:
        raise HTTPException(status_code=409, detail="review_not_ready_for_luck")
    try:
        facts = build_dayun_facts(package, cycle_key) if render_type == "dayun" else build_liunian_facts(package, cycle_key, int(year or 0))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    points_cost = (
        get_runtime_four_pillars_luck_cycle_points_cost(channel_key)
        if render_type == "dayun"
        else get_runtime_four_pillars_luck_year_points_cost(channel_key)
    )
    usage_scene = FOUR_PILLARS_LUCK_CYCLE_RENDER_SCENE if render_type == "dayun" else FOUR_PILLARS_LUCK_YEAR_RENDER_SCENE
    try:
        render = create_four_pillars_luck_render_request(
            review_id=review_id,
            user_id=current_user_id,
            render_type=render_type,
            cycle_key=cycle_key,
            year=year,
            points_cost=points_cost,
            usage_scene=usage_scene,
            request_payload_summary={"review_id": review_id, "render_type": render_type, "cycle_key": cycle_key, "year": year},
            facts=facts,
            now_text=_utc_now(),
            channel=channel_key,
        )
    except InsufficientPointsError as exc:
        raise HTTPException(status_code=402, detail="insufficient_points") from exc
    if render["status"] == "processing" and not render.get("result"):
        background_tasks.add_task(_run_four_pillars_luck_render_generation, render_id=str(render["id"]))
    return _build_four_pillars_luck_render_response(render)


def _resolve_review_aspect_keys(review: dict[str, object], *, channel_key: str | None) -> list[str]:
    return get_runtime_phone_review_aspect_order(channel_key)



def _resolve_four_pillars_aspect_keys(review: dict[str, object], *, channel_key: str | None) -> list[str]:
    return get_runtime_four_pillars_aspect_order(channel_key)


def _resolve_review_free_aspect_keys(available_aspect_keys: list[str], *, channel_key: str | None) -> list[str]:
    configured_keys = set(get_runtime_phone_review_free_aspect_keys(channel_key))
    return [item for item in available_aspect_keys if item in configured_keys]


def _resolve_four_pillars_free_aspect_keys(available_aspect_keys: list[str], *, channel_key: str | None) -> list[str]:
    configured_keys = set(get_runtime_four_pillars_free_aspect_keys(channel_key))
    return [item for item in available_aspect_keys if item in configured_keys]


def _review_aspect_detail_ready(review: dict[str, object], aspect_key: str) -> bool:
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return False
    product_aspects_render = score_template.get("product_aspects_render")
    if isinstance(product_aspects_render, dict):
        aspect = product_aspects_render.get(aspect_key)
        if isinstance(aspect, dict) and str(aspect.get("content") or "").strip() and str(aspect.get("risk") or "").strip():
            return True

    product_view = score_template.get("product_view")
    aspects = product_view.get("aspects") if isinstance(product_view, dict) else None
    if isinstance(aspects, list):
        for item in aspects:
            if not isinstance(item, dict):
                continue
            item_key = str(item.get("aspect_key") or item.get("aspect_id") or "").strip()
            if item_key == aspect_key and str(item.get("content") or "").strip() and str(item.get("risk") or "").strip():
                return True
    return False


def _four_pillars_aspect_detail_ready(review: dict[str, object], aspect_key: str) -> bool:
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return False
    product_aspects_render = score_template.get("product_aspects_render")
    if isinstance(product_aspects_render, dict):
        aspect = product_aspects_render.get(aspect_key)
        if isinstance(aspect, dict) and str(aspect.get("content") or "").strip() and str(aspect.get("risk") or "").strip():
            return True

    product_view = score_template.get("product_view")
    aspects = product_view.get("aspects") if isinstance(product_view, dict) else None
    if isinstance(aspects, list):
        for item in aspects:
            if not isinstance(item, dict):
                continue
            item_key = str(item.get("aspect_key") or "").strip()
            if item_key == aspect_key and str(item.get("content") or "").strip() and str(item.get("risk") or "").strip():
                return True
    return False


def _coerce_four_pillars_score(review: dict[str, object], public_view: dict[str, Any] | None = None) -> int | None:
    if isinstance(public_view, dict) and public_view.get("score") is not None:
        return int(public_view["score"])
    score_template = review.get("score_template")
    if not isinstance(score_template, dict):
        return None
    score_summary = score_template.get("score_summary")
    if not isinstance(score_summary, dict) or score_summary.get("final_score") is None:
        return None
    return int(score_summary["final_score"])



def _run_review_generation(*, review_id: str, phone: str, gender: str, include_markdown: bool, user_id: str | None = None, points_cost: int = 0, channel_key: str | None = None) -> None:
    aspect_prefetch_started = False
    try:
        update_review_progress(review_id=review_id, progress_stage="scoring", progress_message="正在计算基础盘面", updated_at=_utc_now())
        result = score_phone(phone, gender, RULES)

        bundle = build_scoring_bundle(result, include_markdown=include_markdown)
        bundle["score_template"]["product_view"] = build_phone_review_product_view(bundle["score_result"], bundle["score_template"])
        bundle["score_template"]["product_view"]["rules_version"] = RULES.get("version")
        update_review_generation_payload(
            review_id=review_id,
            score_result=bundle["score_result"],
            score_template=bundle["score_template"],
            score_markdown=bundle.get("score_markdown"),
            progress_stage="scoring",
            progress_message="基础盘面已完成，智能体正在同步生成总评和专项内容",
            updated_at=_utc_now(),
        )
        _start_review_aspect_prefetch(review_id=review_id)
        aspect_prefetch_started = True

        update_review_progress(review_id=review_id, progress_stage="scoring", progress_message="基础评分已完成，正在生成总评", updated_at=_utc_now())
        bundle["score_template"]["product_render"] = build_product_review_core_render(bundle)
        if isinstance(bundle["score_template"]["product_render"].get("phone_summary"), dict):
            bundle["score_template"]["phone_summary"] = bundle["score_template"]["product_render"]["phone_summary"]
        current_review = get_review(review_id)
        if current_review is not None and isinstance(current_review.get("score_template"), dict):
            current_template = current_review["score_template"]
            current_aspects = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
            if current_aspects:
                bundle["score_template"]["product_aspects_render"] = dict(current_aspects)
        bundle["score_template"]["product_view"] = build_phone_review_product_view(bundle["score_result"], bundle["score_template"])
        bundle["score_template"]["product_view"]["rules_version"] = RULES.get("version")

        complete_review_with_message(
            review_id=review_id,
            score_result=bundle["score_result"],
            score_template=bundle["score_template"],
            score_markdown=bundle.get("score_markdown"),
            progress_message="总评和长期使用建议已完成，专项内容正在后台生成",
            updated_at=_utc_now(),
        )
        _start_review_voice_preheat(review_id=review_id, channel_key=channel_key)
    except Exception as exc:
        fail_review(review_id=review_id, error_message=str(exc), updated_at=_utc_now())
        if user_id and points_cost > 0:
            refund_points(
                user_id=user_id,
                points_amount=points_cost,
                biz_type=PHONE_REVIEW_BASE_REFUND_BIZ_TYPE,
                biz_id=review_id,
                idempotency_key=f"review:refund:{review_id}",
                remark="phone_review_base_refund",
                now_text=_utc_now(),
            )
            fail_usage_record(usage_record_id=review_id, result_summary={"status": "failed", "error_message": str(exc)}, updated_at=_utc_now())
        return

    if user_id and points_cost > 0:
        complete_usage_record(usage_record_id=review_id, result_summary={"status": "completed"}, updated_at=_utc_now())

    if not aspect_prefetch_started:
        _start_review_aspect_prefetch(review_id=review_id)


def _start_review_aspect_prefetch(*, review_id: str) -> None:
    thread = threading.Thread(target=_run_review_aspect_prefetch, kwargs={"review_id": review_id}, daemon=True)
    thread.start()


def _start_review_voice_preheat(*, review_id: str, channel_key: str | None) -> None:
    thread = threading.Thread(target=_run_review_voice_preheat, kwargs={"review_id": review_id, "channel_key": channel_key}, daemon=True)
    thread.start()


def _run_review_voice_preheat(*, review_id: str, channel_key: str | None) -> None:
    if not is_module_enabled("voice", channel_key=channel_key):
        return
    review = get_review(review_id)
    if review is None:
        return
    review_user_id = str(review.get("user_id") or "") or None
    public_view = _resolve_review_voice_public_view(review, current_user_id=review_user_id, channel_key=channel_key)
    if not public_view:
        return

    provider = get_runtime_voice_provider(channel_key)
    voice_key = get_runtime_voice_default_voice_key(channel_key)
    cache_enabled = get_runtime_voice_cache_enabled(channel_key)
    max_chars = get_runtime_voice_max_chars_per_request(channel_key)
    for scene in ("phone_summary", "phone_stability"):
        try:
            payload = VoiceNarrationRequest(scene=scene, review_id=review_id, voice_key=voice_key)
            narration_text = _build_voice_narration_text(payload, public_view)
            if len(narration_text) > max_chars:
                continue
            synthesize_voice_audio(
                text=narration_text,
                scene=scene,
                provider=provider,
                voice_key=voice_key,
                cache_enabled=cache_enabled,
            )
        except (HTTPException, VoiceProviderUnavailableError, VoiceSynthesisError):
            continue
        except Exception:
            continue


def _run_review_aspect_prefetch(*, review_id: str) -> None:
    review = get_review(review_id)
    if review is None or not isinstance(review.get("score_result"), dict) or not isinstance(review.get("score_template"), dict):
        return
    try:
        score_template = dict(review["score_template"])
        if not isinstance(score_template.get("product_aspects_render"), dict):
            score_template["product_aspects_render"] = {}

        def persist_aspect(aspect_key: str, rendered_aspect: dict[str, Any]) -> None:
            current_review = get_review(review_id)
            if current_review is None or not isinstance(current_review.get("score_template"), dict):
                return
            current_score_result = current_review.get("score_result")
            if not isinstance(current_score_result, dict):
                current_score_result = review["score_result"]
            current_template = dict(current_review["score_template"])
            current_render = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
            next_render = dict(current_render)
            next_render[aspect_key] = rendered_aspect
            current_template["product_aspects_render"] = next_render
            current_template["product_view"] = build_phone_review_product_view(current_score_result, current_template)
            current_template["product_view"]["rules_version"] = RULES.get("version")
            update_review_score_template(review_id=review_id, score_template=current_template, updated_at=_utc_now())

        rendered_aspects = build_product_review_aspects_render(
            {
                "score_result": review["score_result"],
                "score_template": score_template,
            },
            on_result=persist_aspect,
        )
        current_review = get_review(review_id)
        if current_review is None or not isinstance(current_review.get("score_template"), dict):
            return
        current_score_result = current_review.get("score_result")
        if not isinstance(current_score_result, dict):
            current_score_result = review["score_result"]
        current_template = dict(current_review["score_template"])
        current_render = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
        next_render = dict(current_render)
        next_render.update(rendered_aspects)
        current_template["product_aspects_render"] = next_render
        current_template["product_view"] = build_phone_review_product_view(current_score_result, current_template)
        current_template["product_view"]["rules_version"] = RULES.get("version")
        update_review_score_template(review_id=review_id, score_template=current_template, updated_at=_utc_now())
    except Exception:
        return


def _run_four_pillars_review_generation(
    *,
    review_id: str,
    input_profile: dict[str, Any],
    include_markdown: bool,
    user_id: str | None = None,
    points_cost: int = 0,
    channel_key: str | None = None,
) -> None:
    aspect_prefetch_started = False
    try:
        update_four_pillars_review_progress(review_id=review_id, progress_stage="scoring", progress_message="正在排出四柱命盘和确定性事实", updated_at=_utc_now())
        bundle = build_four_pillars_review(input_profile, include_markdown=include_markdown)
        bundle["score_template"]["product_view"] = build_four_pillars_product_view(bundle)
        update_four_pillars_review_generation_payload(
            review_id=review_id,
            score_result=bundle["score_result"],
            score_template=bundle["score_template"],
            score_markdown=bundle.get("score_markdown"),
            progress_stage="scoring",
            progress_message="四柱事实包已完成，智能体正在同步生成总评和专项内容",
            updated_at=_utc_now(),
        )
        _start_four_pillars_aspect_prefetch(review_id=review_id)
        aspect_prefetch_started = True

        update_four_pillars_review_progress(review_id=review_id, progress_stage="rendering", progress_message="基础排盘已完成，正在生成四柱总评", updated_at=_utc_now())
        bundle["score_template"]["product_render"] = build_four_pillars_core_render(bundle)
        current_review = get_four_pillars_review(review_id)
        if current_review is not None and isinstance(current_review.get("score_template"), dict):
            current_template = current_review["score_template"]
            current_aspects = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
            if current_aspects:
                bundle["score_template"]["product_aspects_render"] = dict(current_aspects)
        bundle["score_template"]["product_view"] = build_four_pillars_product_view(bundle)

        complete_four_pillars_review_with_message(
            review_id=review_id,
            score_result=bundle["score_result"],
            score_template=bundle["score_template"],
            score_markdown=bundle.get("score_markdown"),
            progress_message="四柱总评已完成，专项内容正在后台生成",
            updated_at=_utc_now(),
        )
    except Exception as exc:
        fail_four_pillars_review(review_id=review_id, error_message=str(exc), updated_at=_utc_now())
        if user_id and points_cost > 0:
            refund_points(
                user_id=user_id,
                points_amount=points_cost,
                biz_type=FOUR_PILLARS_REVIEW_BASE_REFUND_BIZ_TYPE,
                biz_id=review_id,
                idempotency_key=f"four_pillars:refund:{review_id}",
                remark="four_pillars_review_base_refund",
                now_text=_utc_now(),
            )
            fail_usage_record(usage_record_id=review_id, result_summary={"status": "failed", "error_message": str(exc)}, updated_at=_utc_now())
        return

    if user_id and points_cost > 0:
        complete_usage_record(usage_record_id=review_id, result_summary={"status": "completed"}, updated_at=_utc_now())

    if not aspect_prefetch_started:
        _start_four_pillars_aspect_prefetch(review_id=review_id)


def _start_four_pillars_aspect_prefetch(*, review_id: str) -> None:
    thread = threading.Thread(target=_run_four_pillars_aspect_prefetch, kwargs={"review_id": review_id}, daemon=True)
    thread.start()


def _run_four_pillars_aspect_prefetch(*, review_id: str) -> None:
    review = get_four_pillars_review(review_id)
    if review is None or not isinstance(review.get("score_result"), dict) or not isinstance(review.get("score_template"), dict):
        return
    try:
        score_template = dict(review["score_template"])
        if not isinstance(score_template.get("product_aspects_render"), dict):
            score_template["product_aspects_render"] = {}

        def persist_aspect(aspect_key: str, rendered_aspect: dict[str, Any]) -> None:
            current_review = get_four_pillars_review(review_id)
            if current_review is None or not isinstance(current_review.get("score_template"), dict):
                return
            current_score_result = current_review.get("score_result")
            if not isinstance(current_score_result, dict):
                current_score_result = review["score_result"]
            current_template = dict(current_review["score_template"])
            current_render = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
            next_render = dict(current_render)
            next_render[aspect_key] = rendered_aspect
            current_template["product_aspects_render"] = next_render
            package = _build_four_pillars_package_from_review(
                {**current_review, "score_result": current_score_result},
                score_template=current_template,
            )
            if package is None:
                return
            current_template["product_view"] = build_four_pillars_product_view(package)
            update_four_pillars_review_score_template(review_id=review_id, score_template=current_template, updated_at=_utc_now())

        package = _build_four_pillars_package_from_review(review, score_template=score_template)
        if package is None:
            return
        rendered_aspects = build_four_pillars_aspects_render(package, on_result=persist_aspect)
        current_review = get_four_pillars_review(review_id)
        if current_review is None or not isinstance(current_review.get("score_template"), dict):
            return
        current_score_result = current_review.get("score_result")
        if not isinstance(current_score_result, dict):
            current_score_result = review["score_result"]
        current_template = dict(current_review["score_template"])
        current_render = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
        next_render = dict(current_render)
        next_render.update(rendered_aspects)
        current_template["product_aspects_render"] = next_render
        package = _build_four_pillars_package_from_review(
            {**current_review, "score_result": current_score_result},
            score_template=current_template,
        )
        if package is None:
            return
        current_template["product_view"] = build_four_pillars_product_view(package)
        update_four_pillars_review_score_template(review_id=review_id, score_template=current_template, updated_at=_utc_now())
    except Exception:
        return


def _run_four_pillars_luck_render_generation(*, render_id: str) -> None:
    render = get_four_pillars_luck_render_by_id(render_id)
    if render is None or render.get("status") != "processing":
        return
    review = get_four_pillars_review(str(render["review_id"]))
    if review is None:
        fail_four_pillars_luck_render(render_id=render_id, error_message="review_not_found", updated_at=_utc_now())
        return
    package = _build_four_pillars_package_from_review(review)
    if package is None:
        _fail_four_pillars_luck_render_with_refund(render, "review_not_ready_for_luck")
        return
    try:
        if render["render_type"] == "dayun":
            result = render_four_pillars_dayun(package, cycle_key=str(render["cycle_key"]))
        else:
            result = render_four_pillars_liunian(package, cycle_key=str(render["cycle_key"]), year=int(render.get("year") or 0))
        llm_meta = result.pop("_llm_meta", None) if isinstance(result, dict) else None
        complete_four_pillars_luck_render(render_id=render_id, result=result, progress_message="生成完成", updated_at=_utc_now())
        if render.get("usage_record_id"):
            if isinstance(llm_meta, dict):
                update_usage_record_llm_metrics(
                    usage_record_id=str(render["usage_record_id"]),
                    llm_key_id=str(llm_meta.get("llm_key_id") or "") or None,
                    llm_key_name=str(llm_meta.get("llm_key_name") or "") or None,
                    llm_model=str(llm_meta.get("model") or "") or None,
                    llm_priority_class=str(llm_meta.get("priority_class") or "") or None,
                    llm_wait_ms=int(llm_meta.get("wait_ms") or 0),
                    llm_duration_ms=int(llm_meta.get("duration_ms") or 0),
                    llm_retry_count=int(llm_meta.get("retry_count") or 0),
                    updated_at=_utc_now(),
                )
            complete_usage_record(
                usage_record_id=str(render["usage_record_id"]),
                result_summary={"status": "completed", "render_type": render["render_type"], "cycle_key": render["cycle_key"], "year": render.get("year")},
                updated_at=_utc_now(),
            )
    except Exception as exc:
        _fail_four_pillars_luck_render_with_refund(render, str(exc))


def _fail_four_pillars_luck_render_with_refund(render: dict[str, Any], error_message: str) -> None:
    now_text = _utc_now()
    render_id = str(render["id"])
    fail_four_pillars_luck_render(render_id=render_id, error_message=error_message, updated_at=now_text)
    usage_record_id = str(render.get("usage_record_id") or "")
    if usage_record_id:
        fail_usage_record(
            usage_record_id=usage_record_id,
            result_summary={"status": "failed", "error_message": error_message, "render_type": render.get("render_type"), "cycle_key": render.get("cycle_key"), "year": render.get("year")},
            updated_at=now_text,
        )
    points_cost = int(render.get("points_cost") or 0)
    user_id = str(render.get("user_id") or "")
    if user_id and points_cost > 0:
        refund_points(
            user_id=user_id,
            points_amount=points_cost,
            biz_type=FOUR_PILLARS_LUCK_RENDER_REFUND_BIZ_TYPE,
            biz_id=render_id,
            idempotency_key=f"four_pillars:luck:refund:{render_id}:{usage_record_id or 'no_usage'}",
            remark="four_pillars_luck_render_refund",
            now_text=now_text,
        )



def _decode_avatar_data_url(image_data_url: str) -> tuple[bytes, str]:
    return _decode_image_data_url(
        image_data_url,
        invalid_data_detail="invalid_avatar_data",
        empty_file_detail="empty_avatar_file",
        too_large_detail="avatar_file_too_large",
        invalid_image_detail="invalid_avatar_image",
    )


def _decode_customer_service_qr_data_url(image_data_url: str) -> tuple[bytes, str]:
    return _decode_image_data_url(
        image_data_url,
        invalid_data_detail="invalid_customer_service_qr_data",
        empty_file_detail="empty_customer_service_qr_file",
        too_large_detail="customer_service_qr_file_too_large",
        invalid_image_detail="invalid_customer_service_qr_image",
    )


def _decode_image_data_url(
    image_data_url: str,
    *,
    invalid_data_detail: str,
    empty_file_detail: str,
    too_large_detail: str,
    invalid_image_detail: str,
) -> tuple[bytes, str]:
    match = AVATAR_DATA_URL_PATTERN.match(image_data_url.strip())
    if match is None:
        raise HTTPException(status_code=422, detail=invalid_data_detail)

    kind = match.group("kind").lower()
    extension = "jpg" if kind in {"jpg", "jpeg"} else kind
    try:
        image_bytes = base64.b64decode(match.group("data"), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail=invalid_data_detail) from exc

    if not image_bytes:
        raise HTTPException(status_code=422, detail=empty_file_detail)
    if len(image_bytes) > MAX_AVATAR_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=too_large_detail)
    if not _avatar_file_signature_matches(extension, image_bytes):
        raise HTTPException(status_code=422, detail=invalid_image_detail)

    return image_bytes, extension


def _delete_local_customer_service_qr_code(qr_code_url: object) -> None:
    if not isinstance(qr_code_url, str):
        return
    local_prefix = "/api/v1/static/uploads/customer-service/"
    if not qr_code_url.startswith(local_prefix):
        return
    file_name = qr_code_url.removeprefix(local_prefix).strip()
    if not file_name or "/" in file_name or "\\" in file_name:
        return
    try:
        (_get_customer_service_qr_upload_dir() / file_name).unlink(missing_ok=True)
    except OSError:
        return


def _avatar_file_signature_matches(extension: str, image_bytes: bytes) -> bool:
    if extension == "png":
        return image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == "jpg":
        return image_bytes.startswith(b"\xff\xd8")
    if extension == "webp":
        return len(image_bytes) >= 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP"
    return False


def _normalize_phone(phone: str) -> str:
    normalized_phone = "".join(character for character in phone if character.isdigit())
    if not PHONE_PATTERN.fullmatch(normalized_phone):
        raise HTTPException(status_code=422, detail="phone_must_be_11_digits")
    return normalized_phone


def _normalize_mainland_mobile(phone: str) -> str:
    normalized_phone = "".join(character for character in phone if character.isdigit())
    if len(normalized_phone) == 13 and normalized_phone.startswith("86"):
        normalized_phone = normalized_phone[2:]
    if not MAINLAND_MOBILE_PATTERN.fullmatch(normalized_phone):
        raise HTTPException(status_code=422, detail="invalid_phone_number")
    return normalized_phone


def _issue_auth_login_response(user: dict[str, object], *, request: Request, now_text: str) -> AuthLoginResponse:
    access_token = issue_access_token()
    expires_at = build_session_expiry(now_text)
    create_session(
        user_id=str(user["user_id"]),
        token_hash=hash_access_token(access_token),
        device_type=request.headers.get("X-Client-Platform"),
        client_version=request.headers.get("X-Client-Version"),
        ip=request.client.host if request.client else None,
        expires_at=expires_at,
        now_text=now_text,
    )
    return AuthLoginResponse(
        access_token=access_token,
        expires_at=expires_at,
        user=_build_user_response(user),
        points=_build_points_response_from_user(user),
    )


def _validate_phone_password_pair(password: str, confirm_password: str) -> None:
    if password != confirm_password:
        raise HTTPException(status_code=422, detail="password_confirm_mismatch")
    if password != password.strip():
        raise HTTPException(status_code=422, detail="password_too_weak")
    normalized_password = password.strip()
    if len(normalized_password) < 8 or len(normalized_password) > 32:
        raise HTTPException(status_code=422, detail="password_too_weak")
    if len(set(normalized_password)) <= 1:
        raise HTTPException(status_code=422, detail="password_too_weak")
    category_count = sum(
        [
            any(character.isdigit() for character in normalized_password),
            any(character.isalpha() for character in normalized_password),
            any(not character.isalnum() for character in normalized_password),
        ]
    )
    if category_count < 2:
        raise HTTPException(status_code=422, detail="password_too_weak")



def _mask_phone(phone: str) -> str:
    if len(phone) < 7:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def _resolve_request_channel(request: Request) -> str | None:
    candidate_values = [request.headers.get("X-Client-Channel"), request.headers.get("X-Client-Platform")]
    for candidate_value in candidate_values:
        normalized_value = normalize_channel_key(candidate_value)
        if normalized_value:
            return normalized_value
    return None


def _ensure_module_available(*, module_key: str, request: Request) -> None:
    if is_module_enabled(module_key, channel_key=_resolve_request_channel(request)):
        return
    raise HTTPException(status_code=403, detail="module_disabled")


def _record_zero_cost_usage(*, user_id: str, scene: str, channel: str | None, target_id: str | None, request_payload_summary: dict[str, object] | None, result_summary: dict[str, object] | None) -> None:
    usage_record_id = uuid4().hex
    try:
        existing = get_usage_record(usage_record_id)
        if existing is not None:
            return
        create_usage_record(
            usage_record_id=usage_record_id,
            user_id=user_id,
            scene=scene,
            channel=channel,
            target_id=target_id,
            points_cost=0,
            status="completed",
            request_payload_summary=request_payload_summary,
            result_summary=result_summary,
            created_at=_utc_now(),
        )
    except Exception:
        return


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()



def _render_h5_openid_page(*, title: str, status: str, body: str, footnote: str) -> str:
    public_base_url = get_public_base_url() or "(未配置)"
    oa_appid = get_wechat_oa_app_id() or "(未配置)"
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #f4f7fb; color: #1f2937; }}
    .wrap {{ max-width: 760px; margin: 0 auto; padding: 24px; }}
    .card {{ background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08); }}
    .status {{ display: inline-block; padding: 6px 12px; border-radius: 999px; background: #eff6ff; color: #1d4ed8; font-size: 13px; margin-bottom: 12px; }}
    .main {{ line-height: 1.8; font-size: 16px; }}
    .tip {{ margin-top: 18px; font-size: 14px; color: #6b7280; line-height: 1.8; }}
    code {{ background: #111827; color: #f9fafb; padding: 2px 6px; border-radius: 6px; word-break: break-all; }}
    a {{ color: #2563eb; }}
    ul {{ padding-left: 20px; }}
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <div class='status'>{html.escape(status)}</div>
      <h1>{html.escape(title)}</h1>
      <div class='main'>{body}</div>
      <div class='tip'>
        <strong>说明</strong><br>
        {html.escape(footnote)}
        <br><br>
        <strong>当前服务配置</strong>
        <ul>
          <li>公众号 AppID：<code>{html.escape(oa_appid)}</code></li>
          <li>公网基础地址：<code>{html.escape(public_base_url)}</code></li>
        </ul>
        <strong>测试链接</strong><br>
        mock 演示：<a href='/h5/wechat-openid-test?mock_openid=demo-h5-openid-123'>/h5/wechat-openid-test?mock_openid=demo-h5-openid-123</a>
      </div>
    </div>
  </div>
</body>
</html>"""
