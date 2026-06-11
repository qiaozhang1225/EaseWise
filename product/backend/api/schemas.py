from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Gender = Literal['male', 'female']
ReviewStatus = Literal['processing', 'completed', 'failed', 'retryable']
ReviewProgressStage = Literal['queued', 'scoring', 'rendering', 'finalizing', 'completed', 'failed']
AgentMessageRole = Literal['user', 'assistant']
RuntimeConfigScopeType = Literal['global', 'channel']
InitialPointsApplyScope = Literal['future_users', 'all_users']
RechargeOrderStatus = Literal['pending', 'approved', 'rejected']
RechargeOrderReviewAction = Literal['approve', 'reject']
AdminRechargeOrderStatus = Literal['unpaid', 'paid', 'completed', 'refund_pending', 'refunded', 'closed']
PaymentTransactionStatus = Literal['pending', 'provider_unconfigured', 'paid', 'failed', 'cancelled']
AdminReviewAction = Literal['approve', 'reject']
VoiceNarrationScene = Literal['phone_summary', 'phone_stability', 'phone_aspect']
VoiceNarrationFormat = Literal['mp3']


class DashboardMetricResponse(BaseModel):
    label: str
    value: int | float
    display_value: str
    unit: str | None = None
    trend_value: int | float | None = None
    trend_label: str | None = None


class DashboardSectionResponse(BaseModel):
    title: str
    summary: str | None = None
    metrics: list[DashboardMetricResponse] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    generated_at: str
    revenue: dict[str, Any] = Field(default_factory=dict)
    users: dict[str, Any] = Field(default_factory=dict)
    orders: dict[str, Any] = Field(default_factory=dict)
    promotion: dict[str, Any] = Field(default_factory=dict)
    llm: dict[str, Any] = Field(default_factory=dict)
    sections: list[DashboardSectionResponse] = Field(default_factory=list)


class ReviewCreateRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=32)
    gender: Gender
    include_markdown: bool = True


class ReviewPhoneSummaryResponse(BaseModel):
    title: str = ""
    risk: str = ""
    usage_guidance: str = ""
    elements_check: dict[str, str] = Field(default_factory=dict)


class ReviewStabilityDetailResponse(BaseModel):
    verdict: str = ""
    content: str = ""
    elements_check: dict[str, str] = Field(default_factory=dict)


class ReviewBoardCenterBasisResponse(BaseModel):
    trigger: str


class ReviewBoardActiveBasisResponse(BaseModel):
    palace: str
    direction: str | None = None
    god: str
    star: str
    door: str
    heaven_stem: str
    earth_stem: str


class ReviewBoardGridCellResponse(BaseModel):
    slot_id: str
    palace_key: str
    palace_name: str
    direction: str | None = None
    wuxing: str | None = None
    is_active: bool


class ReviewBoardRelationsResponse(BaseModel):
    palace_door_relation: str | None = None
    stem_pair_relation: str | None = None


class ReviewBoardFourHarmsResponse(BaseModel):
    emptiness: str
    door_pressure: str
    tomb: str
    punishment_hit: str


class ReviewBoardRisksResponse(BaseModel):
    four_harms: ReviewBoardFourHarmsResponse
    pattern_flags: list[str] = Field(default_factory=list)
    risk_pairs: list[str] = Field(default_factory=list)
    structural_cap_reasons: list[str] = Field(default_factory=list)


class ReviewBoardResponse(BaseModel):
    center_basis: ReviewBoardCenterBasisResponse
    active_basis: ReviewBoardActiveBasisResponse | None = None
    grid_cells: list[ReviewBoardGridCellResponse] = Field(default_factory=list)
    relations: ReviewBoardRelationsResponse | None = None
    risks: ReviewBoardRisksResponse | None = None


class ReviewAspectResponse(BaseModel):
    aspect_key: str
    title: str
    short_title: str | None = None
    score: int | None = None
    is_unlocked: bool = False
    unlock_points: int = 0
    content: str | None = None
    risk: str | None = None
    elements_check: dict[str, str] = Field(default_factory=dict)


class ReviewRecordResponse(BaseModel):
    id: str
    report_id: str
    phone: str
    phone_number: str
    masked_phone: str
    gender: Gender
    status: ReviewStatus
    progress_stage: ReviewProgressStage | None = None
    progress_message: str | None = None
    score: int | None = None
    phone_summary: ReviewPhoneSummaryResponse | None = None
    board: ReviewBoardResponse | None = None
    stability_detail: ReviewStabilityDetailResponse | None = None
    aspects: list[ReviewAspectResponse] = Field(default_factory=list)
    aspect_unlock_points: int | None = None
    free_aspect_keys: list[str] = Field(default_factory=list)
    unlock_enforcement_enabled: bool | None = None
    score_markdown: str | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str


class ReviewSummaryResponse(BaseModel):
    id: str
    report_id: str
    phone: str
    phone_number: str
    masked_phone: str
    gender: Gender
    status: ReviewStatus
    progress_stage: ReviewProgressStage | None = None
    progress_message: str | None = None
    score: int | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str


class ReviewListResponse(BaseModel):
    items: list[ReviewSummaryResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class FourPillarsReviewCreateRequest(BaseModel):
    gender: Gender
    birth_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    birth_time: str = Field(pattern=r'^\d{2}:\d{2}$')
    timezone: str | None = Field(default='Asia/Shanghai', max_length=64)
    birth_place: str | None = Field(default=None, max_length=128)
    name: str | None = Field(default=None, max_length=64)
    include_markdown: bool = True


class FourPillarsSummaryResponse(BaseModel):
    title: str = ""
    risk: str = ""
    usage_guidance: str = ""
    elements_check: dict[str, str] = Field(default_factory=dict)


class FourPillarsAspectResponse(BaseModel):
    aspect_key: str
    title: str
    short_title: str | None = None
    score: int | None = None
    is_unlocked: bool = False
    unlock_points: int = 0
    content: str | None = None
    risk: str | None = None
    elements_check: dict[str, str] = Field(default_factory=dict)


class FourPillarsLuckRenderRecordResponse(BaseModel):
    id: str
    render_id: str
    review_id: str
    user_id: str
    render_type: Literal['dayun', 'liunian']
    cycle_key: str
    year: int | None = None
    status: ReviewStatus
    progress_message: str | None = None
    facts: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    points_cost: int = 0
    error_message: str | None = None
    retry_count: int = 0
    last_attempt_at: str | None = None
    next_retry_available_at: str | None = None
    is_retryable: bool = False
    created_at: str
    updated_at: str


class FourPillarsLuckYearItemResponse(BaseModel):
    year: int
    age: int | None = None
    ganzhi: str
    stem: str | None = None
    branch: str | None = None
    stem_ten_god: str | None = None
    stem_element: str | None = None
    branch_element: str | None = None
    is_current: bool = False
    render_status: str = "not_generated"
    render: FourPillarsLuckRenderRecordResponse | None = None


class FourPillarsLuckCycleResponse(BaseModel):
    cycle_key: str
    start_year: int
    end_year: int
    start_age: int | None = None
    end_age: int | None = None
    ganzhi: str | None = None
    display_ganzhi: str | None = None
    is_current: bool = False
    stem: str | None = None
    branch: str | None = None
    stem_ten_god: str | None = None
    stem_element: str | None = None
    branch_element: str | None = None
    render_status: str = "not_generated"
    render: FourPillarsLuckRenderRecordResponse | None = None
    year_items: list[FourPillarsLuckYearItemResponse] = Field(default_factory=list)


class FourPillarsLuckAnalysisResponse(BaseModel):
    enabled: bool = True
    cycle_points_cost: int = 0
    year_points_cost: int = 0
    current_cycle_key: str | None = None
    cycles: list[FourPillarsLuckCycleResponse] = Field(default_factory=list)


class FourPillarsLuckCycleListResponse(BaseModel):
    luck_analysis: FourPillarsLuckAnalysisResponse


class FourPillarsReviewRecordResponse(BaseModel):
    id: str
    report_id: str
    gender: Gender
    birth_date: str
    birth_time: str
    timezone: str
    birth_place: str | None = None
    name: str | None = None
    status: ReviewStatus
    progress_stage: ReviewProgressStage | None = None
    progress_message: str | None = None
    score: int | None = None
    input_profile: dict[str, Any] = Field(default_factory=dict)
    chart: dict[str, Any] | None = None
    chart_display: dict[str, Any] | None = None
    summary: FourPillarsSummaryResponse | None = None
    deterministic_facts: dict[str, Any] = Field(default_factory=dict)
    aspects: list[FourPillarsAspectResponse] = Field(default_factory=list)
    analysis_branches: dict[str, Any] = Field(default_factory=dict)
    luck_analysis: FourPillarsLuckAnalysisResponse | None = None
    aspect_unlock_points: int | None = None
    free_aspect_keys: list[str] = Field(default_factory=list)
    unlock_enforcement_enabled: bool | None = None
    score_markdown: str | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str


class FourPillarsReviewSummaryResponse(BaseModel):
    id: str
    report_id: str
    gender: Gender
    birth_date: str
    birth_time: str
    timezone: str
    birth_place: str | None = None
    name: str | None = None
    status: ReviewStatus
    progress_stage: ReviewProgressStage | None = None
    progress_message: str | None = None
    score: int | None = None
    error_message: str | None = None
    created_at: str
    updated_at: str


class FourPillarsReviewListResponse(BaseModel):
    items: list[FourPillarsReviewSummaryResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class AlmanacResponse(BaseModel):
    solar_date: str
    display_date: str
    weekday_label: str
    lunar_date: str
    lunar_full_text: str
    ganzhi_year: str
    ganzhi_month: str
    ganzhi_day: str
    zodiac_year: str
    zodiac_month: str
    zodiac_day: str
    yi: list[str]
    ji: list[str]
    yi_summary: str
    ji_summary: str
    solar_term: str | None = None
    festivals: list[str]
    pengzu_gan: str
    pengzu_zhi: str
    pengzu_summary: str
    chong: str
    sha: str
    zhi_xing: str
    tian_shen: str
    tian_shen_luck: str
    ji_shen: list[str]
    xiong_sha: list[str]


class WeChatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=256)
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=1024)


class PhoneStatusRequest(BaseModel):
    phone: str = Field(min_length=1, max_length=32)


class PhoneStatusResponse(BaseModel):
    registered: bool
    normalized_phone: str
    next_action: Literal['login', 'register']


class PhonePasswordRegisterRequest(BaseModel):
    phone: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)


class PhonePasswordLoginRequest(BaseModel):
    phone: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=128)


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=1024)


class AvatarUploadRequest(BaseModel):
    image_data_url: str = Field(min_length=1, max_length=2_000_000)


class CustomerServiceQrCodeUploadRequest(BaseModel):
    image_data_url: str = Field(min_length=1, max_length=2_100_000)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)


class PasswordChangeResponse(BaseModel):
    status: str = 'ok'


class UserResponse(BaseModel):
    user_id: str
    uid: str | None = None
    status: str
    identity_level: str = 'normal_user'
    nickname: str | None = None
    avatar_url: str | None = None
    profile_completed: bool
    created_at: str
    updated_at: str
    last_active_at: str


class InternalUserResponse(BaseModel):
    user_id: str
    uid: str | None = None
    status: str
    identity_level: str = 'normal_user'
    primary_identity_type: str = 'unknown'
    registered_channel: str | None = None
    promoter_parent_user_id: str | None = None
    nickname: str | None = None
    avatar_url: str | None = None
    profile_completed: bool
    points_balance: int
    frozen_balance: int
    withdrawable_balance_cents: int = 0
    frozen_commission_cents: int = 0
    withdrawn_amount_cents: int = 0
    rebate_points_balance: int = 0
    rebate_frozen_balance: int = 0
    primary_phone: str | None = None
    phone_verified_at: str | None = None
    primary_unionid: str | None = None
    first_login_at: str
    registered_at: str
    created_at: str
    updated_at: str
    last_active_at: str
    openid: str | None = None
    unionid: str | None = None


class InternalUserListResponse(BaseModel):
    items: list[InternalUserResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class RechargeOrderSummaryResponse(BaseModel):
    order_id: str
    package_title: str
    amount_cents: int
    status: str
    created_at: str
    reviewed_at: str | None = None
    reviewed_by: str | None = None
    paid_at: str | None = None
    completed_at: str | None = None


class RefundRequestResponse(BaseModel):
    refund_id: str
    order_id: str
    user_id: str
    status: str
    reason: str | None = None
    operator_note: str | None = None
    reject_reason: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    retry_count: int = 0
    failure_reason: str | None = None
    created_at: str
    updated_at: str


class PromotionCommissionResponse(BaseModel):
    commission_id: str
    promoter_user_id: str
    promoter_nickname: str | None = None
    invited_user_id: str | None = None
    invited_user_nickname: str | None = None
    order_id: str | None = None
    order_amount_cents: int
    commission_rate: float
    commission_amount_cents: int = 0
    commission_points: int
    commission_type: str
    status: str
    remark: str | None = None
    created_at: str
    updated_at: str
    settled_at: str | None = None
    revoked_at: str | None = None


class PointsAccountResponse(BaseModel):
    balance: int
    frozen_balance: int
    created_at: str | None = None
    updated_at: str | None = None


class PointsLedgerEntryResponse(BaseModel):
    ledger_id: str
    change_type: str
    delta: int
    balance_after: int
    biz_type: str
    biz_id: str | None = None
    idempotency_key: str | None = None
    remark: str | None = None
    created_at: str


class PointsLedgerListResponse(BaseModel):
    items: list[PointsLedgerEntryResponse]


class PointsClaimLinkCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    points_amount: int = Field(gt=0)
    display_value_cents: int = Field(default=0, ge=0)
    expires_in_hours: int | None = Field(default=None, gt=0, le=24 * 30)
    expires_at: str | None = Field(default=None, max_length=64)
    operator_note: str | None = Field(default=None, max_length=512)


class PointsClaimLinkDisableRequest(BaseModel):
    operator_note: str | None = Field(default=None, max_length=512)


class PointsClaimLinkResponse(BaseModel):
    claim_link_id: str
    claim_code: str
    claim_url: str
    title: str
    points_amount: int
    display_value_cents: int
    status: str
    effective_status: str
    valid_from: str
    expires_at: str
    claimed_user_count: int = 0
    granted_points_total: int = 0
    duplicate_attempt_count: int = 0
    created_by: str | None = None
    disabled_by: str | None = None
    disabled_at: str | None = None
    operator_note: str | None = None
    created_at: str
    updated_at: str


class PointsClaimLinkListResponse(BaseModel):
    items: list[PointsClaimLinkResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class PointsClaimRecordResponse(BaseModel):
    claim_record_id: str
    claim_link_id: str
    claim_code: str | None = None
    claim_title: str | None = None
    user_id: str
    user_uid: str | None = None
    user_nickname: str | None = None
    user_phone: str | None = None
    week_key: str
    week_starts_at: str
    status: str
    points_amount_snapshot: int
    display_value_cents_snapshot: int = 0
    ledger_id: str | None = None
    failure_reason: str | None = None
    request_ip: str | None = None
    user_agent: str | None = None
    created_at: str
    updated_at: str


class PointsClaimRecordListResponse(BaseModel):
    items: list[PointsClaimRecordResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class PublicPointsClaimLinkResponse(BaseModel):
    claim_code: str
    title: str
    points_amount: int
    display_value_cents: int
    status: str
    effective_status: str
    valid_from: str
    expires_at: str
    current_user_claim_status: str | None = None
    current_user_claim_record: PointsClaimRecordResponse | None = None


class PointsClaimSubmitResponse(BaseModel):
    claim_status: str
    message: str
    points: PointsAccountResponse | None = None
    ledger: PointsLedgerEntryResponse | None = None
    record: PointsClaimRecordResponse | None = None
    already_claimed_record: PointsClaimRecordResponse | None = None


class RechargePackageResponse(BaseModel):
    package_key: str
    title: str
    description: str | None = None
    price_cents: int
    points_amount: int
    bonus_points: int
    total_points: int
    enabled: bool
    sort_order: int


class RechargePackageListResponse(BaseModel):
    items: list[RechargePackageResponse]


class RechargeOrderCreateRequest(BaseModel):
    package_key: str = Field(min_length=1, max_length=128)
    source: str = Field(default='h5_recharge_page', min_length=1, max_length=64)
    external_order_id: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)
    proof_url: str | None = Field(default=None, max_length=1024)
    remark: str | None = Field(default=None, max_length=512)


class PaymentTransactionResponse(BaseModel):
    transaction_id: str
    order_id: str
    user_id: str
    provider: str
    payment_method: str
    amount_cents: int
    status: PaymentTransactionStatus | str
    provider_transaction_id: str | None = None
    prepay_id: str | None = None
    idempotency_key: str | None = None
    payment_params: dict[str, Any] = Field(default_factory=dict)
    client_message: str | None = None
    failure_reason: str | None = None
    paid_at: str | None = None
    created_at: str
    updated_at: str


class PaymentTransactionCreateRequest(BaseModel):
    provider: str = Field(default='wechat_h5', min_length=1, max_length=64)
    payment_method: str | None = Field(default=None, max_length=64)
    idempotency_key: str | None = Field(default=None, max_length=128)
    return_url: str | None = Field(default=None, max_length=1024)
    client_context: dict[str, Any] | None = None


class RechargeOrderResponse(BaseModel):
    order_id: str
    user_id: str
    user_status: str | None = None
    user_nickname: str | None = None
    channel: str | None = None
    status: AdminRechargeOrderStatus | RechargeOrderStatus
    raw_status: str | None = None
    package_key: str
    package_title: str
    amount_cents: int
    points_amount: int
    bonus_points: int
    total_points: int
    source: str
    external_order_id: str | None = None
    proof_url: str | None = None
    remark: str | None = None
    review_note: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    paid_at: str | None = None
    completed_at: str | None = None
    closed_at: str | None = None
    refund_requests: list[RefundRequestResponse] = Field(default_factory=list)
    commission_records: list[PromotionCommissionResponse] = Field(default_factory=list)
    payment_transactions: list[PaymentTransactionResponse] = Field(default_factory=list)
    latest_payment: PaymentTransactionResponse | None = None
    granted_ledger_id: str | None = None
    created_at: str
    updated_at: str


class PaymentNotifyResponse(BaseModel):
    status: str
    transaction: PaymentTransactionResponse | None = None
    order: RechargeOrderResponse | None = None
    ledger: PointsLedgerEntryResponse | None = None


class RechargeOrderPaymentStatusResponse(BaseModel):
    order: RechargeOrderResponse
    latest_payment: PaymentTransactionResponse | None = None


class RechargeOrderListResponse(BaseModel):
    items: list[RechargeOrderResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class RechargeOrderReviewRequest(BaseModel):
    action: RechargeOrderReviewAction
    review_note: str | None = Field(default=None, max_length=512)


class RechargeOrderReviewResponse(BaseModel):
    order: RechargeOrderResponse
    points: PointsAccountResponse
    ledger: PointsLedgerEntryResponse | None = None


class RechargeOrderManualCompleteRequest(BaseModel):
    payment_method: str | None = Field(default=None, max_length=64)
    payment_reference: str | None = Field(default=None, max_length=128)
    operator_note: str | None = Field(default=None, max_length=512)


class RechargeOrderManualCompleteResponse(BaseModel):
    order: RechargeOrderResponse
    points: PointsAccountResponse
    ledger: PointsLedgerEntryResponse | None = None


class ManualPointsAdjustRequest(BaseModel):
    delta: int
    biz_type: str = Field(min_length=1, max_length=128)
    biz_id: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)
    remark: str | None = Field(default=None, max_length=512)
    reason: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class ManualPointsAdjustResponse(BaseModel):
    user: InternalUserResponse
    points: PointsAccountResponse
    ledger: PointsLedgerEntryResponse


class RebatePointsAccountResponse(BaseModel):
    user_id: str
    balance: int
    frozen_balance: int
    created_at: str | None = None
    updated_at: str | None = None


class RebatePointsAdjustRequest(BaseModel):
    delta: int
    reason: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class RebatePointsAdjustResponse(BaseModel):
    user: InternalUserResponse
    rebate_points: RebatePointsAccountResponse


class UserStatusUpdateRequest(BaseModel):
    status: str = Field(min_length=1, max_length=64)
    reason: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class UserIdentityUpdateRequest(BaseModel):
    identity_level: str = Field(min_length=1, max_length=64)
    reason: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class UserPromoterParentUpdateRequest(BaseModel):
    promoter_parent_user_id: str | None = Field(default=None, max_length=64)
    reason: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class UsageRecordResponse(BaseModel):
    usage_record_id: str
    user_id: str
    scene: str
    feature_key: str
    feature_name: str | None = None
    channel: str | None = None
    target_id: str | None = None
    points_cost: int
    normal_points_cost: int
    rebate_points_cost: int
    status: str
    user_status: str | None = None
    user_nickname: str | None = None
    user_phone: str | None = None
    user_avatar_url: str | None = None
    request_payload_summary: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    llm_key_id: str | None = None
    llm_key_name: str | None = None
    llm_model: str | None = None
    llm_priority_class: str | None = None
    llm_wait_ms: int | None = None
    llm_duration_ms: int | None = None
    llm_retry_count: int = 0
    llm_error_type: str | None = None
    llm_error_message: str | None = None
    created_at: str
    updated_at: str


class UsageRecordListResponse(BaseModel):
    items: list[UsageRecordResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class InternalUserAdminSummaryResponse(BaseModel):
    user: InternalUserResponse
    recent_orders: list[RechargeOrderSummaryResponse] = Field(default_factory=list)
    recent_order_count: int = 0
    recent_recharge_amount_cents: int = 0
    latest_order_status: str | None = None
    total_recharge_amount_cents: int = 0
    total_withdraw_amount_cents: int = 0
    promoter_parent_user_id: str | None = None
    identity_level: str = 'normal_user'


class UsageRecordDetailResponse(BaseModel):
    record: UsageRecordResponse
    user: InternalUserResponse
    recent_orders: list[RechargeOrderSummaryResponse] = Field(default_factory=list)


class InternalPhoneQimenSummaryResponse(BaseModel):
    generated_at: str
    today_review_count: int = 0
    week_review_count: int = 0
    total_review_count: int = 0
    completed_review_count: int = 0
    failed_review_count: int = 0
    success_rate: float = 0
    average_generation_seconds: float | None = None
    aspect_unlock_count: int = 0
    aspect_unlock_rate: float = 0
    review_points_cost: int = 0
    voice_request_count: int = 0


class InternalPhoneQimenReviewItemResponse(BaseModel):
    review_id: str
    user_id: str | None = None
    user_uid: str | None = None
    user_nickname: str | None = None
    user_phone: str | None = None
    phone: str
    gender: Gender
    status: ReviewStatus
    progress_stage: ReviewProgressStage | None = None
    progress_message: str | None = None
    error_message: str | None = None
    channel: str | None = None
    base_points_cost: int = 0
    unlock_count: int = 0
    voice_count: int = 0
    generation_duration_seconds: int | None = None
    created_at: str
    updated_at: str


class InternalPhoneQimenReviewListResponse(BaseModel):
    items: list[InternalPhoneQimenReviewItemResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class InternalPhoneQimenAspectUnlockRecordResponse(BaseModel):
    unlock_id: str
    review_id: str
    user_id: str
    aspect_key: str
    aspect_name: str
    points_cost: int
    usage_record_id: str | None = None
    unlocked_at: str


class InternalPhoneQimenReviewDetailResponse(BaseModel):
    review: InternalPhoneQimenReviewItemResponse
    unlock_records: list[InternalPhoneQimenAspectUnlockRecordResponse] = Field(default_factory=list)
    voice_records: list[UsageRecordResponse] = Field(default_factory=list)


class InternalFourPillarsSummaryResponse(InternalPhoneQimenSummaryResponse):
    pass


class InternalFourPillarsReviewItemResponse(BaseModel):
    review_id: str
    user_id: str | None = None
    user_uid: str | None = None
    user_nickname: str | None = None
    user_phone: str | None = None
    gender: Gender
    birth_date: str
    birth_time: str
    timezone: str
    birth_place: str | None = None
    name: str | None = None
    status: ReviewStatus
    progress_stage: ReviewProgressStage | None = None
    progress_message: str | None = None
    error_message: str | None = None
    channel: str | None = None
    base_points_cost: int = 0
    unlock_count: int = 0
    voice_count: int = 0
    generation_duration_seconds: int | None = None
    created_at: str
    updated_at: str


class InternalFourPillarsReviewListResponse(BaseModel):
    items: list[InternalFourPillarsReviewItemResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class InternalFourPillarsAspectUnlockRecordResponse(InternalPhoneQimenAspectUnlockRecordResponse):
    pass


class InternalFourPillarsReviewDetailResponse(BaseModel):
    review: InternalFourPillarsReviewItemResponse
    unlock_records: list[InternalFourPillarsAspectUnlockRecordResponse] = Field(default_factory=list)
    luck_render_records: list[FourPillarsLuckRenderRecordResponse] = Field(default_factory=list)


class AdminReviewRequest(BaseModel):
    action: AdminReviewAction
    reject_reason: str | None = Field(default=None, max_length=512)
    reason: str | None = Field(default=None, max_length=512)
    review_note: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class RefundCreateRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class RefundRetryRequest(BaseModel):
    operator_note: str | None = Field(default=None, max_length=512)


class PromotionApplicationResponse(BaseModel):
    application_id: str
    user_id: str
    user_nickname: str | None = None
    current_identity_level: str | None = None
    requested_level: str
    status: str
    applicant_name: str | None = None
    applicant_phone: str | None = None
    reject_reason: str | None = None
    review_note: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    created_at: str
    updated_at: str


class PromotionApplicationListResponse(BaseModel):
    items: list[PromotionApplicationResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class PromotionCommissionListResponse(BaseModel):
    items: list[PromotionCommissionResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class PromotionWithdrawalResponse(BaseModel):
    withdrawal_id: str
    user_id: str
    user_nickname: str | None = None
    identity_level: str | None = None
    status: str
    withdrawable_balance_snapshot_cents: int = 0
    frozen_commission_snapshot_cents: int = 0
    points_used: int
    amount_cents: int
    rebate_points_balance_snapshot: int
    cash_rate_snapshot: float
    reject_reason: str | None = None
    review_note: str | None = None
    payout_method: str | None = None
    payout_proof: str | None = None
    payout_failure_reason: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    paid_at: str | None = None
    created_at: str
    updated_at: str


class PromotionWithdrawalListResponse(BaseModel):
    items: list[PromotionWithdrawalResponse]
    total: int = 0
    limit: int = 20
    offset: int = 0


class PromotionWithdrawalPayoutRequest(BaseModel):
    payout_method: str | None = Field(default=None, max_length=128)
    payout_proof: str | None = Field(default=None, max_length=512)
    operator_note: str | None = Field(default=None, max_length=512)


class PromotionRulesResponse(BaseModel):
    normal_threshold_cents: int
    senior_threshold_cents: int
    normal_commission_rate: float
    senior_commission_rate: float
    min_withdraw_cents: int
    order_completion_days: int


class PromotionRulesUpdateRequest(BaseModel):
    normal_threshold_cents: int | None = None
    senior_threshold_cents: int | None = None
    normal_commission_rate: float | None = None
    senior_commission_rate: float | None = None
    min_withdraw_cents: int | None = None
    order_completion_days: int | None = None


class LlmApiKeyResponse(BaseModel):
    key_id: str
    provider: str
    model: str
    display_name: str
    masked_key: str
    secret_ref: str
    secret_configured: bool = False
    enabled: bool
    priority: int
    max_concurrency: int = 450
    cooldown_seconds: int = 60
    current_inflight: int = 0
    available_slots: int = 0
    cooldown_until: str | None = None
    last_rate_limited_at: str | None = None
    last_error_message: str | None = None
    last_used_at: str | None = None
    remark: str | None = None
    last_operator: str | None = None
    created_at: str
    updated_at: str


class LlmApiKeyListResponse(BaseModel):
    items: list[LlmApiKeyResponse]
    total: int = 0
    limit: int = 100
    offset: int = 0


class LlmApiKeyUpsertRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=128)
    masked_key: str | None = Field(default=None, max_length=256)
    secret_ref: str | None = Field(default=None, max_length=256)
    secret_value: str | None = Field(default=None, max_length=4096)
    enabled: bool = False
    priority: int = 100
    max_concurrency: int = Field(default=450, ge=1, le=5000)
    cooldown_seconds: int = Field(default=60, ge=1, le=3600)
    remark: str | None = Field(default=None, max_length=512)
    last_operator: str | None = Field(default=None, max_length=128)


class LlmConcurrencyKeyResponse(BaseModel):
    key_id: str
    display_name: str
    provider: str
    model: str
    enabled: bool = True
    priority: int = 100
    max_concurrency: int = 450
    cooldown_seconds: int = 60
    current_inflight: int = 0
    available_slots: int = 0
    cooldown_until: str | None = None
    last_rate_limited_at: str | None = None
    last_error_message: str | None = None
    last_used_at: str | None = None


class LlmConcurrencyStatusResponse(BaseModel):
    backend: str
    backend_available: bool = True
    backend_error: str | None = None
    redis_configured: bool = False
    global_inflight: int = 0
    foreground_waiting: int = 0
    background_waiting: int = 0
    foreground_inflight: int = 0
    background_inflight: int = 0
    enabled_key_count: int = 0
    total_capacity: int = 0
    recent_429_count: int = 0
    recent_timeout_count: int = 0
    avg_wait_ms: int = 0
    avg_duration_ms: int = 0
    config: dict[str, Any] = Field(default_factory=dict)
    keys: list[LlmConcurrencyKeyResponse] = Field(default_factory=list)


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_at: str
    user: UserResponse
    points: PointsAccountResponse


class CurrentUserResponse(BaseModel):
    user: UserResponse
    points: PointsAccountResponse


class AgentHistoryMessage(BaseModel):
    role: AgentMessageRole
    text: str = Field(min_length=1, max_length=2000)


class AgentReplyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[AgentHistoryMessage] = Field(default_factory=list)
    scene: str | None = Field(default='h5', max_length=64)


class AgentReplyMetaResponse(BaseModel):
    reply_mode: Literal['llm', 'fallback']
    used_llm: bool
    model_name: str


class AgentReplyResponse(BaseModel):
    reply: str
    suggestions: list[str]
    context_tags: list[str]
    generated_at: str
    meta: AgentReplyMetaResponse


class ReviewAspectUnlockRequest(BaseModel):
    aspect_key: str = Field(min_length=1, max_length=64)


class ReviewAspectUnlockResponse(BaseModel):
    unlock_id: str
    review_id: str
    user_id: str
    aspect_key: str
    points_cost: int
    usage_record_id: str
    unlocked_at: str
    points: PointsAccountResponse | None = None
    aspect: ReviewAspectResponse | None = None


class ReviewAspectUnlockListResponse(BaseModel):
    items: list[ReviewAspectUnlockResponse]
    available_aspect_keys: list[str]
    free_aspect_keys: list[str]
    unlocked_aspect_keys: list[str]
    aspect_unlock_points_cost: int
    unlock_enforcement_enabled: bool
    aspects: list[ReviewAspectResponse] = Field(default_factory=list)


class FourPillarsAspectUnlockResponse(BaseModel):
    unlock_id: str
    review_id: str
    user_id: str
    aspect_key: str
    points_cost: int
    usage_record_id: str
    unlocked_at: str
    points: PointsAccountResponse | None = None
    aspect: FourPillarsAspectResponse | None = None


class FourPillarsAspectUnlockListResponse(BaseModel):
    items: list[FourPillarsAspectUnlockResponse]
    available_aspect_keys: list[str]
    free_aspect_keys: list[str]
    unlocked_aspect_keys: list[str]
    aspect_unlock_points_cost: int
    unlock_enforcement_enabled: bool
    aspects: list[FourPillarsAspectResponse] = Field(default_factory=list)


class VoiceNarrationRequest(BaseModel):
    scene: VoiceNarrationScene
    review_id: str = Field(min_length=1, max_length=64)
    aspect_key: str | None = Field(default=None, min_length=1, max_length=64)
    voice_key: str | None = Field(default=None, max_length=64)


class VoiceNarrationResponse(BaseModel):
    narration_id: str
    scene: VoiceNarrationScene
    text_hash: str
    audio_url: str
    provider: str
    voice_key: str
    format: VoiceNarrationFormat
    char_count: int
    cached: bool


class RuntimeConfigEntryResponse(BaseModel):
    entry_id: str
    scope_type: RuntimeConfigScopeType
    scope_key: str
    config_key: str
    value: Any
    updated_at: str


class RuntimeInitialPointsUpdateRequest(BaseModel):
    initial_grant: int = Field(ge=0)
    apply_scope: InitialPointsApplyScope = 'future_users'
    reason: str | None = Field(default=None, max_length=512)


class RuntimeInitialPointsUpdateResponse(BaseModel):
    previous_initial_grant: int
    initial_grant: int
    delta: int
    apply_scope: InitialPointsApplyScope
    target_user_count: int = 0
    affected_user_count: int = 0
    adjusted_points_total: int = 0
    zeroed_user_count: int = 0
    operation_id: str
    entry: RuntimeConfigEntryResponse


class RuntimeConfigEntryUpsertRequest(BaseModel):
    scope_type: RuntimeConfigScopeType
    scope_key: str = Field(min_length=1, max_length=128)
    config_key: str = Field(min_length=1, max_length=128)
    value: Any


class RuntimeConfigUpsertRequest(BaseModel):
    entries: list[RuntimeConfigEntryUpsertRequest] = Field(min_length=1)


class RuntimeConfigListResponse(BaseModel):
    items: list[RuntimeConfigEntryResponse]


class RuntimeConfigSchemaItemResponse(BaseModel):
    config_key: str
    label: str
    value_type: str
    default_value: Any = None
    scope_type: RuntimeConfigScopeType = 'global'
    scope_key: str = 'default'
    group: str
    high_risk: bool = False
    description: str | None = None
    admin_group: str | None = None
    admin_section: str | None = None
    advanced: bool = False
    sort_order: int = 100
    input_options: list[dict[str, Any]] | None = None
    help_text: str | None = None
    admin_hidden: bool = False


class RuntimeConfigSchemaResponse(BaseModel):
    items: list[RuntimeConfigSchemaItemResponse]


class RuntimePointsConfigResponse(BaseModel):
    initial_grant: int


class RuntimeRechargeConfigResponse(BaseModel):
    packages: list[RechargePackageResponse]


class CustomerServiceConfigResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    wechat_id: str | None = None
    contact_url: str | None = None
    qr_code_url: str | None = None
    guidance_text: str
    qr_guidance_text: str
    copy_button_text: str
    unconfigured_text: str
    copy_texts: dict[str, str] = Field(default_factory=dict, alias='copy')


class ComplianceConfigResponse(BaseModel):
    safe_mode_enabled: bool
    safe_modules: list[str]
    hidden_modules: list[str]
    hidden_pages: list[str]


class ModuleRuntimeConfigResponse(BaseModel):
    enabled: bool
    base_points_cost: int | None = None
    aspect_unlock_points_cost: int | None = None
    free_aspect_keys: list[str] | None = None
    aspect_order: list[str] | None = None
    unlock_enforcement_enabled: bool | None = None
    luck_cycle_points_cost: int | None = None
    luck_year_points_cost: int | None = None
    luck_generation_enabled: bool | None = None
    metaphysics_skill_enabled: bool | None = None


class VoiceRuntimeConfigResponse(BaseModel):
    enabled: bool
    mode: Literal['hybrid', 'browser', 'cloud']
    autoplay_default_enabled: bool
    provider: str
    default_voice_key: str
    cache_enabled: bool
    max_chars_per_request: int


class RuntimeModulesConfigResponse(BaseModel):
    phone_review: ModuleRuntimeConfigResponse
    four_pillars: ModuleRuntimeConfigResponse
    agent: ModuleRuntimeConfigResponse
    almanac: ModuleRuntimeConfigResponse
    voice: VoiceRuntimeConfigResponse


class PublicRuntimeConfigResponse(BaseModel):
    channel: str | None = None
    points: RuntimePointsConfigResponse
    recharge: RuntimeRechargeConfigResponse
    customer_service: CustomerServiceConfigResponse
    compliance: ComplianceConfigResponse
    modules: RuntimeModulesConfigResponse


PaymentNotifyResponse.model_rebuild()
RechargeOrderPaymentStatusResponse.model_rebuild()
