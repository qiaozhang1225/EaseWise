from __future__ import annotations

import html
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, Cookie, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from product.backend.llm import load_env_file
from features.almanac.engine import build_almanac_for_date, build_today_almanac
from features.phone_qimen.scoring.total_score.engine import load_rules, score_phone
from features.phone_qimen.scoring.total_score.bundle import build_scoring_bundle

from .agent import build_agent_reply
from .auth import build_session_expiry, exchange_wechat_code, hash_access_token, issue_access_token, require_authenticated_user, require_internal_admin_access, require_registered_user, resolve_authenticated_user
from .config import APP_TITLE, APP_VERSION, allow_mock_wechat_login, get_cors_origins, get_database_path, get_public_base_url, get_wechat_oa_app_id
from .database import InsufficientPointsError, adjust_points, adjust_rebate_points, complete_review, complete_review_with_message, complete_usage_record, create_recharge_order, create_refund_request, create_review_aspect_unlock, create_review_with_charge, create_session, create_usage_record, delete_llm_api_key, ensure_schema, fail_review, fail_usage_record, get_dashboard_summary, get_internal_user, get_points_account, get_promotion_application, get_promotion_commission, get_promotion_rules, get_promotion_withdrawal, get_recharge_order, get_review, get_session_user_by_token_hash, get_usage_record, get_user, list_llm_api_keys, list_points_ledger, list_promotion_applications, list_promotion_commissions, list_promotion_withdrawals, list_recharge_orders, list_recent_recharge_orders_for_user, list_refund_requests_for_order, list_review_aspect_unlocks, list_reviews, list_runtime_config_entries, list_usage_records, list_users, mark_promotion_withdrawal_paid, merge_guest_user_into_user, refund_points, retry_promotion_withdrawal_payout, retry_refund_request, review_promotion_application, review_promotion_withdrawal, review_recharge_order, review_refund_request, update_review_generation_payload, update_review_progress, update_review_score_template, update_user_identity, update_user_profile, update_user_promoter_parent, update_user_status, upsert_guest_user, upsert_llm_api_key, upsert_runtime_config_entry, upsert_wechat_user
from .phone_review_view import PUBLIC_ASPECT_ORDER, build_phone_review_product_view
from .product_review import build_product_review_aspects_render, build_product_review_core_render
from .runtime_config import get_runtime_agent_metaphysics_skill_enabled, get_runtime_available_recharge_packages, get_runtime_guest_initial_points, get_runtime_initial_points, get_runtime_phone_review_aspect_order, get_runtime_phone_review_aspect_unlock_points_cost, get_runtime_phone_review_base_points_cost, get_runtime_phone_review_free_aspect_keys, get_runtime_phone_review_unlock_enforcement_enabled, is_module_enabled, normalize_channel_key, normalize_config_key, normalize_scope_key, normalize_scope_type, resolve_public_runtime_config
from .schemas import AdminReviewRequest, AgentReplyRequest, AgentReplyResponse, AlmanacResponse, AuthLoginResponse, ComplianceConfigResponse, CurrentUserResponse, CustomerServiceConfigResponse, DashboardResponse, DashboardMetricResponse, DashboardSectionResponse, GuestSessionRequest, GuestSessionResponse, InternalUserAdminSummaryResponse, InternalUserListResponse, InternalUserResponse, LlmApiKeyListResponse, LlmApiKeyResponse, LlmApiKeyUpsertRequest, ManualPointsAdjustRequest, ManualPointsAdjustResponse, ModuleRuntimeConfigResponse, PointsAccountResponse, PointsLedgerEntryResponse, PointsLedgerListResponse, PublicRuntimeConfigResponse, PromotionApplicationListResponse, PromotionApplicationResponse, PromotionCommissionListResponse, PromotionCommissionResponse, PromotionRulesResponse, PromotionRulesUpdateRequest, PromotionWithdrawalListResponse, PromotionWithdrawalPayoutRequest, PromotionWithdrawalResponse, RebatePointsAdjustRequest, RebatePointsAdjustResponse, RebatePointsAccountResponse, RefundCreateRequest, RefundRequestResponse, RefundRetryRequest, RechargeOrderCreateRequest, RechargeOrderListResponse, RechargeOrderResponse, RechargeOrderReviewRequest, RechargeOrderReviewResponse, RechargeOrderSummaryResponse, RechargePackageListResponse, RechargePackageResponse, ReviewAspectResponse, ReviewAspectUnlockListResponse, ReviewAspectUnlockRequest, ReviewAspectUnlockResponse, ReviewBoardResponse, ReviewCreateRequest, ReviewListResponse, ReviewPhoneSummaryResponse, ReviewRecordResponse, ReviewStabilityDetailResponse, ReviewSummaryResponse, RuntimeConfigEntryResponse, RuntimeConfigListResponse, RuntimeConfigSchemaItemResponse, RuntimeConfigSchemaResponse, RuntimeConfigUpsertRequest, RuntimeModulesConfigResponse, RuntimePointsConfigResponse, RuntimeRechargeConfigResponse, UsageRecordDetailResponse, UsageRecordListResponse, UsageRecordResponse, UserIdentityUpdateRequest, UserPromoterParentUpdateRequest, UserProfileUpdateRequest, UserResponse, UserStatusUpdateRequest, WeChatLoginRequest
from .wechat_h5 import STATE_COOKIE_NAME, build_oauth_state, build_wechat_oauth_authorize_url, exchange_h5_oauth_code, h5_oauth_is_configured, is_wechat_browser

PHONE_PATTERN = re.compile(r"^\d{11}$")
TESTER_PAGE_PATH = Path(__file__).resolve().parent / "static" / "tester.html"
load_env_file()
RULES = load_rules()
PHONE_REVIEW_BASE_SCENE = "phone_review_base"
PHONE_REVIEW_BASE_REFUND_BIZ_TYPE = "phone_review_base_refund"
PHONE_REVIEW_ASPECT_UNLOCK_SCENE = "phone_review_aspect_unlock"
REVIEW_PREVIEW_ASPECT_THRESHOLD = 4
_RUNTIME_CONFIG_SCHEMA_ITEMS: list[dict[str, object]] = [
    {"config_key": "recharge.packages", "label": "充值套餐", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": True, "description": "充值金额与积分套餐列表"},
    {"config_key": "points.initial_grant", "label": "注册初始积分", "value_type": "int", "default_value": 100, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": False, "description": "注册用户默认发放积分"},
    {"config_key": "points.guest_initial_grant", "label": "游客初始积分", "value_type": "int", "default_value": 100, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": False, "description": "游客会话初始积分"},
    {"config_key": "customer_service.contact_url", "label": "客服联系方式", "value_type": "string", "default_value": None, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": False, "description": "客服跳转链接"},
    {"config_key": "customer_service.qr_code_url", "label": "客服二维码", "value_type": "string", "default_value": None, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": False, "description": "客服二维码图片地址"},
    {"config_key": "customer_service.guidance_text", "label": "客服说明文案", "value_type": "string", "default_value": "联系客服获取充值与服务支持", "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": False, "description": "前台客服说明"},
    {"config_key": "platform.recharge_enabled", "label": "充值总开关", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "系统配置", "high_risk": True, "description": "控制前台是否开放充值入口"},
    {"config_key": "compliance.safe_mode_enabled", "label": "渠道总开关", "value_type": "bool", "default_value": False, "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": True, "description": "控制玄学功能是否整体可用"},
    {"config_key": "compliance.safe_modules", "label": "合规白名单模块", "value_type": "json", "default_value": ["almanac", "five_elements"], "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": True, "description": "总开关开启时允许的模块"},
    {"config_key": "compliance.hidden_modules", "label": "隐藏模块列表", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": True, "description": "被隐藏的功能模块"},
    {"config_key": "compliance.hidden_pages", "label": "隐藏页面列表", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": True, "description": "被隐藏的页面"},
    {"config_key": "phone_review.base_points_cost", "label": "手机号评测基础消耗", "value_type": "int", "default_value": 100, "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": False, "description": "手机号评测基础积分消耗"},
    {"config_key": "phone_review.aspect_unlock_points_cost", "label": "维度解锁消耗", "value_type": "int", "default_value": 50, "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": False, "description": "单个维度解锁积分"},
    {"config_key": "phone_review.free_aspect_keys", "label": "免费维度列表", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": False, "description": "不消耗积分的维度"},
    {"config_key": "phone_review.aspect_order", "label": "维度顺序", "value_type": "json", "default_value": [], "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": False, "description": "手机号评测维度展示顺序"},
    {"config_key": "phone_review.unlock_enforcement_enabled", "label": "维度解锁限制", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": True, "description": "是否强制未解锁维度隐藏内容"},
    {"config_key": "agent.metaphysics_skill_enabled", "label": "智能体玄学技能开关", "value_type": "bool", "default_value": True, "scope_type": "global", "scope_key": "default", "group": "功能管理", "high_risk": True, "description": "仅控制智能体的玄学技能"},
    {"config_key": "promotion.normal_threshold_cents", "label": "普通大使门槛", "value_type": "int", "default_value": 39800, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "普通推广大使申请门槛"},
    {"config_key": "promotion.senior_threshold_cents", "label": "高级大使门槛", "value_type": "int", "default_value": 398000, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "高级推广大使申请门槛"},
    {"config_key": "promotion.normal_commission_rate", "label": "普通返佣比例", "value_type": "float", "default_value": 0.1, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "普通推广大使返佣比例"},
    {"config_key": "promotion.senior_commission_rate", "label": "高级返佣比例", "value_type": "float", "default_value": 0.2, "scope_type": "global", "scope_key": "default", "group": "推广合作", "high_risk": False, "description": "高级推广大使返佣比例"},
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
    return DashboardResponse(
        generated_at=str(dashboard["generated_at"]),
        revenue=dict(dashboard.get("revenue", {})),
        users=dict(dashboard.get("users", {})),
        orders=dict(dashboard.get("orders", {})),
        promotion=dict(dashboard.get("promotion", {})),
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
            for section in dashboard.get("sections", [])
        ],
    )


def create_guest_session(payload: GuestSessionRequest, request: Request) -> GuestSessionResponse:
    now_text = _utc_now()
    try:
        guest_session = upsert_guest_user(
            channel=payload.channel,
            guest_key=payload.guest_key,
            appid=payload.appid,
            openid=payload.openid,
            unionid=payload.unionid,
            initial_points=get_runtime_guest_initial_points(),
            now_text=now_text,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 409 if detail in {"guest_identity_conflict", "guest_identity_bound_to_registered_user"} else 422
        raise HTTPException(status_code=status_code, detail=detail) from exc

    access_token = issue_access_token()
    expires_at = build_session_expiry(now_text)
    create_session(
        user_id=str(guest_session["user"]["user_id"]),
        token_hash=hash_access_token(access_token),
        device_type=request.headers.get("X-Client-Platform"),
        client_version=request.headers.get("X-Client-Version"),
        ip=request.client.host if request.client else None,
        expires_at=expires_at,
        now_text=now_text,
    )
    return GuestSessionResponse(
        access_token=access_token,
        expires_at=expires_at,
        channel=str(guest_session["channel"]),
        guest_key=str(guest_session["guest_key"]),
        user=_build_user_response(guest_session["user"]),
        points=_build_points_response_from_user(guest_session["user"]),
    )


def login_with_wechat(payload: WeChatLoginRequest, request: Request) -> AuthLoginResponse:
    exchange = exchange_wechat_code(payload.code)
    now_text = _utc_now()
    guest_user: dict[str, object] | None = None
    if payload.guest_access_token:
        guest_user = get_session_user_by_token_hash(hash_access_token(payload.guest_access_token), now_text=now_text, ip=request.client.host if request.client else None)
        if guest_user is None:
            raise HTTPException(status_code=401, detail="invalid_guest_access_token")
        if str(guest_user.get("status") or "") != "guest":
            raise HTTPException(status_code=422, detail="guest_access_token_must_belong_to_guest_user")

    try:
        user = upsert_wechat_user(
            appid=exchange.appid,
            openid=exchange.openid,
            unionid=exchange.unionid,
            session_key=exchange.session_key,
            nickname=payload.nickname,
            avatar_url=payload.avatar_url,
            initial_points=0 if guest_user is not None else get_runtime_initial_points(),
            now_text=now_text,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 409 if detail == "wechat_identity_conflict" else 422
        raise HTTPException(status_code=status_code, detail=detail) from exc
    if guest_user is not None and str(guest_user["user_id"]) != str(user["user_id"]):
        merge_guest_user_into_user(guest_user_id=str(guest_user["user_id"]), target_user_id=str(user["user_id"]), now_text=now_text)
        refreshed_user = get_user(str(user["user_id"]))
        if refreshed_user is None:
            raise HTTPException(status_code=500, detail="guest_merge_refresh_failed")
        user = refreshed_user

    access_token = issue_access_token()
    expires_at = build_session_expiry(now_text)
    create_session(user_id=str(user["user_id"]), token_hash=hash_access_token(access_token), device_type=request.headers.get("X-Client-Platform"), client_version=request.headers.get("X-Client-Version"), ip=request.client.host if request.client else None, expires_at=expires_at, now_text=now_text)
    return AuthLoginResponse(access_token=access_token, expires_at=expires_at, user=_build_user_response(user), points=_build_points_response_from_user(user))


def get_me(current_user: dict[str, object] = Depends(require_authenticated_user)) -> CurrentUserResponse:
    return CurrentUserResponse(user=_build_user_response(current_user), points=_build_points_response_from_user(current_user))


def patch_me_profile(payload: UserProfileUpdateRequest, current_user: dict[str, object] = Depends(require_registered_user)) -> UserResponse:
    if payload.nickname is None and payload.avatar_url is None:
        raise HTTPException(status_code=422, detail="nickname_or_avatar_required")
    updated = update_user_profile(user_id=str(current_user["user_id"]), nickname=payload.nickname, avatar_url=payload.avatar_url, now_text=_utc_now())
    if updated is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    return _build_user_response(updated)


def get_my_points(current_user: dict[str, object] = Depends(require_authenticated_user)) -> PointsAccountResponse:
    points_account = get_points_account(str(current_user["user_id"]))
    if points_account is None:
        raise HTTPException(status_code=404, detail="points_account_not_found")
    return _build_points_account_response(points_account)


def get_my_points_ledger(limit: int = Query(default=20, ge=1, le=100), current_user: dict[str, object] = Depends(require_authenticated_user)) -> PointsLedgerListResponse:
    items = [_build_points_ledger_entry_response(item) for item in list_points_ledger(str(current_user["user_id"]), limit)]
    return PointsLedgerListResponse(items=items)


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
    return _build_recharge_order_response(_require_owned_recharge_order(order_id, current_user_id=str(current_user["user_id"])))


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
            agent=ModuleRuntimeConfigResponse(**payload["modules"]["agent"]),
            almanac=ModuleRuntimeConfigResponse(**payload["modules"]["almanac"]),
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


def get_internal_runtime_config_schema(_: None = Depends(require_internal_admin_access)) -> RuntimeConfigSchemaResponse:
    return RuntimeConfigSchemaResponse(items=[RuntimeConfigSchemaItemResponse(**item) for item in _RUNTIME_CONFIG_SCHEMA_ITEMS])


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
    return InternalUserListResponse(items=items, total=len(items), limit=limit, offset=offset)


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
    order_response = _build_recharge_order_response(order)
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


def get_internal_llm_api_keys(_: None = Depends(require_internal_admin_access)) -> LlmApiKeyListResponse:
    return LlmApiKeyListResponse(items=[LlmApiKeyResponse(**item) for item in list_llm_api_keys()])


def post_internal_llm_api_key(payload: LlmApiKeyUpsertRequest, _: None = Depends(require_internal_admin_access)) -> LlmApiKeyResponse:
    saved = upsert_llm_api_key(
        key_id=None,
        provider=payload.provider,
        model=payload.model,
        display_name=payload.display_name,
        masked_key=payload.masked_key,
        secret_ref=payload.secret_ref,
        enabled=payload.enabled,
        priority=payload.priority,
        remark=payload.remark,
        last_operator=payload.last_operator,
        now_text=_utc_now(),
    )
    return LlmApiKeyResponse(**saved)


def patch_internal_llm_api_key(key_id: str, payload: LlmApiKeyUpsertRequest, _: None = Depends(require_internal_admin_access)) -> LlmApiKeyResponse:
    saved = upsert_llm_api_key(
        key_id=key_id,
        provider=payload.provider,
        model=payload.model,
        display_name=payload.display_name,
        masked_key=payload.masked_key,
        secret_ref=payload.secret_ref,
        enabled=payload.enabled,
        priority=payload.priority,
        remark=payload.remark,
        last_operator=payload.last_operator,
        now_text=_utc_now(),
    )
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


def create_review_record(request: Request, background_tasks: BackgroundTasks, payload: ReviewCreateRequest, current_user: dict[str, object] | None = Depends(resolve_authenticated_user)) -> ReviewRecordResponse:
    _ensure_module_available(module_key="phone_review", request=request)
    normalized_phone = _normalize_phone(payload.phone)
    review_id = uuid4().hex
    created_at = _utc_now()
    user_id = str(current_user["user_id"]) if current_user else None
    channel_key = _resolve_request_channel(request)
    points_cost = get_runtime_phone_review_base_points_cost(channel_key) if user_id else 0
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
            request_payload_summary={"phone": normalized_phone, "gender": payload.gender, "include_markdown": payload.include_markdown} if user_id and points_cost > 0 else None,
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
    )
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=500, detail="review_persistence_failed")
    return _build_review_record_response(
        review,
        channel_key=channel_key,
        current_user_id=str(current_user["user_id"]) if current_user else None,
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
    current_user: dict[str, object] = Depends(require_authenticated_user),
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
    current_user: dict[str, object] = Depends(require_authenticated_user),
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



def _build_user_response(user: dict[str, object]) -> UserResponse:
    return UserResponse(user_id=str(user["user_id"]), status=str(user["status"]), nickname=user.get("nickname"), avatar_url=user.get("avatar_url"), profile_completed=bool(user["profile_completed"]), created_at=str(user["created_at"]), updated_at=str(user["updated_at"]), last_active_at=str(user["last_active_at"]))



def _build_internal_user_response(user: dict[str, object]) -> InternalUserResponse:
    return InternalUserResponse(
        user_id=str(user["user_id"]),
        status=str(user["status"]),
        identity_level=str(user.get("identity_level") or "normal_user"),
        primary_identity_type=str(user.get("primary_identity_type") or "session"),
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
        guest_channel=user.get("guest_channel"),
        guest_key=user.get("guest_key"),
        guest_appid=user.get("guest_appid"),
        guest_openid=user.get("guest_openid"),
        guest_unionid=user.get("guest_unionid"),
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
        complete_review(
            review_id=str(review["id"]),
            status=str(review.get("status") or "completed"),
            score_result=score_result,
            score_template=score_template,
            score_markdown=review.get("score_markdown") if isinstance(review.get("score_markdown"), str) else None,
            updated_at=_utc_now(),
        )

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



def _require_owned_review(review_id: str, *, current_user_id: str) -> dict[str, object]:
    review = get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review_not_found")
    review_user_id = str(review.get("user_id") or "")
    if not review_user_id or review_user_id != current_user_id:
        raise HTTPException(status_code=404, detail="review_not_found")
    if str(review.get("status")) != "completed" or not isinstance(review.get("score_template"), dict):
        raise HTTPException(status_code=409, detail="review_not_ready_for_unlock")
    return review



def _resolve_review_aspect_keys(review: dict[str, object], *, channel_key: str | None) -> list[str]:
    return get_runtime_phone_review_aspect_order(channel_key)



def _resolve_review_free_aspect_keys(available_aspect_keys: list[str], *, channel_key: str | None) -> list[str]:
    configured_keys = set(get_runtime_phone_review_free_aspect_keys(channel_key))
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



def _run_review_generation(*, review_id: str, phone: str, gender: str, include_markdown: bool, user_id: str | None = None, points_cost: int = 0) -> None:
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

        update_review_generation_payload(
            review_id=review_id,
            score_result=bundle["score_result"],
            score_template=bundle["score_template"],
            score_markdown=bundle.get("score_markdown"),
            progress_stage="rendering",
            progress_message="总评和长期使用建议已完成，专项内容正在预热",
            updated_at=_utc_now(),
        )
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


def _run_review_aspect_prefetch(*, review_id: str) -> None:
    review = get_review(review_id)
    if review is None or not isinstance(review.get("score_result"), dict) or not isinstance(review.get("score_template"), dict):
        return
    try:
        score_template = dict(review["score_template"])
        if not isinstance(score_template.get("product_aspects_render"), dict):
            score_template["product_aspects_render"] = {}
        update_review_score_template(review_id=review_id, score_template=score_template, updated_at=_utc_now())

        progressed_count = 0
        preview_completed = False

        def persist_aspect(aspect_key: str, rendered_aspect: dict[str, Any]) -> None:
            nonlocal progressed_count, preview_completed
            current_review = get_review(review_id)
            if current_review is None or not isinstance(current_review.get("score_template"), dict):
                return
            current_template = dict(current_review["score_template"])
            current_render = current_template.get("product_aspects_render") if isinstance(current_template.get("product_aspects_render"), dict) else {}
            next_render = dict(current_render)
            next_render[aspect_key] = rendered_aspect
            current_template["product_aspects_render"] = next_render
            current_template["product_view"] = build_phone_review_product_view(review["score_result"], current_template)
            current_template["product_view"]["rules_version"] = RULES.get("version")
            update_review_score_template(review_id=review_id, score_template=current_template, updated_at=_utc_now())
            progressed_count = len(next_render)

            if progressed_count >= REVIEW_PREVIEW_ASPECT_THRESHOLD and not preview_completed:
                complete_review_with_message(
                    review_id=review_id,
                    score_result=review["score_result"],
                    score_template=current_template,
                    score_markdown=review.get("score_markdown") if isinstance(review.get("score_markdown"), str) else None,
                    progress_message=f"前 {REVIEW_PREVIEW_ASPECT_THRESHOLD} 个专项已完成，剩余专项继续后台生成",
                    updated_at=_utc_now(),
                )
                preview_completed = True

        rendered_aspects = build_product_review_aspects_render(
            {
                "score_result": review["score_result"],
                "score_template": score_template,
            },
            on_result=persist_aspect,
        )
        score_template["product_aspects_render"] = rendered_aspects
        score_template["product_view"] = build_phone_review_product_view(review["score_result"], score_template)
        score_template["product_view"]["rules_version"] = RULES.get("version")
        if preview_completed or len(rendered_aspects) >= REVIEW_PREVIEW_ASPECT_THRESHOLD:
            complete_review_with_message(
                review_id=review_id,
                score_result=review["score_result"],
                score_template=score_template,
                score_markdown=review.get("score_markdown") if isinstance(review.get("score_markdown"), str) else None,
                progress_message="12 个专项已全部生成",
                updated_at=_utc_now(),
            )
        else:
            update_review_generation_payload(
                review_id=review_id,
                score_result=review["score_result"],
                score_template=score_template,
                score_markdown=review.get("score_markdown") if isinstance(review.get("score_markdown"), str) else None,
                progress_stage="finalizing",
                progress_message=f"专项内容已生成 {len(rendered_aspects)}/12，稍后可继续刷新查看",
                updated_at=_utc_now(),
            )
    except Exception:
        return



def _normalize_phone(phone: str) -> str:
    normalized_phone = "".join(character for character in phone if character.isdigit())
    if not PHONE_PATTERN.fullmatch(normalized_phone):
        raise HTTPException(status_code=422, detail="phone_must_be_11_digits")
    return normalized_phone



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
