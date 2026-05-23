from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Gender = Literal['male', 'female']
ReviewStatus = Literal['processing', 'completed', 'failed']
ReviewProgressStage = Literal['queued', 'scoring', 'rendering', 'finalizing', 'completed', 'failed']
AgentMessageRole = Literal['user', 'assistant']
RuntimeConfigScopeType = Literal['global', 'channel']
RechargeOrderStatus = Literal['pending', 'approved', 'rejected']
RechargeOrderReviewAction = Literal['approve', 'reject']


class ReviewCreateRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=32)
    gender: Gender
    include_markdown: bool = True


class ReviewTextBlockResponse(BaseModel):
    title: str
    content: str


class ReviewLabelValueResponse(BaseModel):
    label: str
    value: str


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


class ReviewBoardSummaryResponse(BaseModel):
    main_axis: str | None = None
    main_contradiction: str | None = None


class ReviewBoardResponse(BaseModel):
    center_basis: ReviewBoardCenterBasisResponse
    active_basis: ReviewBoardActiveBasisResponse | None = None
    grid_cells: list[ReviewBoardGridCellResponse] = Field(default_factory=list)
    relations: ReviewBoardRelationsResponse | None = None
    risks: ReviewBoardRisksResponse | None = None
    summary: ReviewBoardSummaryResponse | None = None


class ReviewAspectResponse(BaseModel):
    aspect_id: str
    title: str
    short_title: str | None = None
    score: int | None = None
    level: str | None = None
    level_text: str | None = None
    is_unlocked: bool = False
    unlock_points: int = 0
    core_judge: str | None = None
    explain: str | None = None
    signal: str | None = None
    suggestion: str | None = None


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
    summary: ReviewTextBlockResponse | None = None
    board: ReviewBoardResponse | None = None
    board_analysis: ReviewTextBlockResponse | None = None
    stability_judgement: ReviewLabelValueResponse | None = None
    long_term_advice: list[str] = Field(default_factory=list)
    aspects: list[ReviewAspectResponse] = Field(default_factory=list)
    aspect_unlock_points: int | None = None
    free_aspect_keys: list[str] = Field(default_factory=list)
    unlock_enforcement_enabled: bool | None = None
    score_result: dict[str, Any] | None = None
    score_template: dict[str, Any] | None = None
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
    guest_access_token: str | None = Field(default=None, max_length=512)


class GuestSessionRequest(BaseModel):
    channel: str = Field(default='h5', min_length=1, max_length=64)
    guest_key: str | None = Field(default=None, max_length=128)
    appid: str | None = Field(default=None, max_length=128)
    openid: str | None = Field(default=None, max_length=256)
    unionid: str | None = Field(default=None, max_length=256)


class GuestSessionResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_at: str
    channel: str
    guest_key: str
    user: 'UserResponse'
    points: 'PointsAccountResponse'


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    avatar_url: str | None = Field(default=None, max_length=1024)


class UserResponse(BaseModel):
    user_id: str
    status: str
    nickname: str | None = None
    avatar_url: str | None = None
    profile_completed: bool
    created_at: str
    updated_at: str
    last_active_at: str


class InternalUserResponse(BaseModel):
    user_id: str
    status: str
    nickname: str | None = None
    avatar_url: str | None = None
    profile_completed: bool
    points_balance: int
    frozen_balance: int
    created_at: str
    updated_at: str
    last_active_at: str
    openid: str | None = None
    unionid: str | None = None
    guest_channel: str | None = None
    guest_key: str | None = None
    guest_appid: str | None = None
    guest_openid: str | None = None
    guest_unionid: str | None = None


class InternalUserListResponse(BaseModel):
    items: list[InternalUserResponse]


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
    source: str = Field(default='customer_service_h5', min_length=1, max_length=64)
    external_order_id: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)
    proof_url: str | None = Field(default=None, max_length=1024)
    remark: str | None = Field(default=None, max_length=512)


class RechargeOrderResponse(BaseModel):
    order_id: str
    user_id: str
    user_status: str | None = None
    user_nickname: str | None = None
    channel: str | None = None
    status: RechargeOrderStatus
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
    granted_ledger_id: str | None = None
    created_at: str
    updated_at: str


class RechargeOrderListResponse(BaseModel):
    items: list[RechargeOrderResponse]


class RechargeOrderReviewRequest(BaseModel):
    action: RechargeOrderReviewAction
    review_note: str | None = Field(default=None, max_length=512)


class RechargeOrderReviewResponse(BaseModel):
    order: RechargeOrderResponse
    points: PointsAccountResponse
    ledger: PointsLedgerEntryResponse | None = None


class ManualPointsAdjustRequest(BaseModel):
    delta: int
    biz_type: str = Field(min_length=1, max_length=128)
    biz_id: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)
    remark: str | None = Field(default=None, max_length=512)


class ManualPointsAdjustResponse(BaseModel):
    user: InternalUserResponse
    points: PointsAccountResponse
    ledger: PointsLedgerEntryResponse


class UsageRecordResponse(BaseModel):
    usage_record_id: str
    user_id: str
    scene: str
    target_id: str | None = None
    points_cost: int
    status: str
    request_payload_summary: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    created_at: str
    updated_at: str


class UsageRecordListResponse(BaseModel):
    items: list[UsageRecordResponse]


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


class RuntimeConfigEntryResponse(BaseModel):
    entry_id: str
    scope_type: RuntimeConfigScopeType
    scope_key: str
    config_key: str
    value: Any
    updated_at: str


class RuntimeConfigEntryUpsertRequest(BaseModel):
    scope_type: RuntimeConfigScopeType
    scope_key: str = Field(min_length=1, max_length=128)
    config_key: str = Field(min_length=1, max_length=128)
    value: Any


class RuntimeConfigUpsertRequest(BaseModel):
    entries: list[RuntimeConfigEntryUpsertRequest] = Field(min_length=1)


class RuntimeConfigListResponse(BaseModel):
    items: list[RuntimeConfigEntryResponse]


class RuntimePointsConfigResponse(BaseModel):
    initial_grant: int
    guest_initial_grant: int


class RuntimeRechargeConfigResponse(BaseModel):
    packages: list[RechargePackageResponse]


class CustomerServiceConfigResponse(BaseModel):
    contact_url: str | None = None
    qr_code_url: str | None = None
    guidance_text: str


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


class RuntimeModulesConfigResponse(BaseModel):
    phone_review: ModuleRuntimeConfigResponse
    agent: ModuleRuntimeConfigResponse
    almanac: ModuleRuntimeConfigResponse


class PublicRuntimeConfigResponse(BaseModel):
    channel: str | None = None
    points: RuntimePointsConfigResponse
    recharge: RuntimeRechargeConfigResponse
    customer_service: CustomerServiceConfigResponse
    compliance: ComplianceConfigResponse
    modules: RuntimeModulesConfigResponse


GuestSessionResponse.model_rebuild()
