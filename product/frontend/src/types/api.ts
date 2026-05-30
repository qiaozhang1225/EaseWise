export type Gender = 'male' | 'female';
export type ReviewStatus = 'processing' | 'completed' | 'failed';
export type ReviewProgressStage = 'queued' | 'scoring' | 'rendering' | 'finalizing' | 'completed' | 'failed';

export interface ReviewPhoneSummary {
  title: string;
  risk: string;
  usage_guidance: string;
  elements_check: Record<string, string>;
}

export interface ReviewStabilityDetail {
  verdict: string;
  content: string;
  elements_check: Record<string, string>;
}

export interface ReviewBoardCenterBasis {
  trigger: string;
}

export interface ReviewBoardActiveBasis {
  palace: string;
  direction: string | null;
  god: string;
  star: string;
  door: string;
  heaven_stem: string;
  earth_stem: string;
}

export interface ReviewBoardGridCell {
  slot_id: string;
  palace_key: string;
  palace_name: string;
  direction: string | null;
  wuxing: string | null;
  is_active: boolean;
}

export interface ReviewBoardRelations {
  palace_door_relation: string | null;
  stem_pair_relation: string | null;
}

export interface ReviewBoardFourHarms {
  emptiness: string;
  door_pressure: string;
  tomb: string;
  punishment_hit: string;
}

export interface ReviewBoardRisks {
  four_harms: ReviewBoardFourHarms;
  pattern_flags: string[];
  risk_pairs: string[];
  structural_cap_reasons: string[];
}

export interface ReviewBoard {
  center_basis: ReviewBoardCenterBasis;
  active_basis: ReviewBoardActiveBasis | null;
  grid_cells: ReviewBoardGridCell[];
  relations: ReviewBoardRelations | null;
  risks: ReviewBoardRisks | null;
}

export interface ReviewAspect {
  aspect_key: string;
  title: string;
  short_title: string | null;
  score: number | null;
  is_unlocked: boolean;
  unlock_points: number;
  content: string | null;
  risk: string | null;
  elements_check: Record<string, string>;
}

export interface ReviewRecord {
  id: string;
  report_id: string;
  phone: string;
  phone_number: string;
  masked_phone: string;
  gender: Gender;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  score: number | null;
  phone_summary?: ReviewPhoneSummary | null;
  board: ReviewBoard | null;
  stability_detail?: ReviewStabilityDetail | null;
  aspects: ReviewAspect[];
  aspect_unlock_points: number | null;
  free_aspect_keys: string[];
  unlock_enforcement_enabled: boolean | null;
  score_markdown: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewSummary {
  id: string;
  report_id: string;
  phone: string;
  phone_number: string;
  masked_phone: string;
  gender: Gender;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  score: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewListResponse {
  items: ReviewSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface AlmanacResponse {
  solar_date: string;
  display_date: string;
  weekday_label: string;
  lunar_date: string;
  lunar_full_text: string;
  ganzhi_year: string;
  ganzhi_month: string;
  ganzhi_day: string;
  zodiac_year: string;
  zodiac_month: string;
  zodiac_day: string;
  yi: string[];
  ji: string[];
  yi_summary: string;
  ji_summary: string;
  solar_term: string | null;
  festivals: string[];
  pengzu_gan: string;
  pengzu_zhi: string;
  pengzu_summary: string;
  chong: string;
  sha: string;
  zhi_xing: string;
  tian_shen: string;
  tian_shen_luck: string;
  ji_shen: string[];
  xiong_sha: string[];
}

export interface DashboardMetric {
  label: string;
  value: number;
  display_value: string;
  unit: string | null;
  trend_value: number | null;
  trend_label: string | null;
}

export interface DashboardSection {
  title: string;
  summary: string | null;
  metrics: DashboardMetric[];
}

export interface DashboardResponse {
  generated_at: string;
  revenue: Record<string, unknown>;
  users: Record<string, unknown>;
  orders: Record<string, unknown>;
  promotion: Record<string, unknown>;
  sections: DashboardSection[];
}

export interface UserResponse {
  user_id: string;
  status: string;
  nickname: string | null;
  avatar_url: string | null;
  profile_completed: boolean;
  created_at: string;
  updated_at: string;
  last_active_at: string;
}

export interface PointsAccountResponse {
  balance: number;
  frozen_balance: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface PointsLedgerEntryResponse {
  ledger_id: string;
  change_type: string;
  delta: number;
  balance_after: number;
  biz_type: string;
  biz_id: string | null;
  idempotency_key: string | null;
  remark: string | null;
  created_at: string;
}

export interface PointsLedgerListResponse {
  items: PointsLedgerEntryResponse[];
}

export interface RechargePackageResponse {
  package_key: string;
  title: string;
  description: string | null;
  price_cents: number;
  points_amount: number;
  bonus_points: number;
  total_points: number;
  enabled: boolean;
  sort_order: number;
}

export interface ModuleRuntimeConfigResponse {
  enabled: boolean;
  base_points_cost: number | null;
  aspect_unlock_points_cost?: number | null;
  free_aspect_keys?: string[] | null;
  aspect_order?: string[] | null;
  unlock_enforcement_enabled?: boolean | null;
  metaphysics_skill_enabled?: boolean | null;
}

export interface PublicRuntimeConfigResponse {
  channel: string | null;
  points: {
    initial_grant: number;
    guest_initial_grant: number;
  };
  recharge: {
    packages: RechargePackageResponse[];
  };
  customer_service: {
    contact_url: string | null;
    qr_code_url: string | null;
    guidance_text: string;
  };
  compliance: {
    safe_mode_enabled: boolean;
    safe_modules: string[];
    hidden_modules: string[];
    hidden_pages: string[];
  };
  modules: {
    phone_review: ModuleRuntimeConfigResponse;
    agent: ModuleRuntimeConfigResponse;
    almanac: ModuleRuntimeConfigResponse;
  };
}

export interface GuestSessionResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  channel: string;
  guest_key: string;
  user: UserResponse;
  points: PointsAccountResponse;
}

export interface ReviewAspectUnlockResponse {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  points: PointsAccountResponse | null;
  aspect: ReviewAspect | null;
}

export interface InternalUserResponse {
  user_id: string;
  status: string;
  identity_level: string;
  primary_identity_type: string;
  registered_channel: string | null;
  promoter_parent_user_id: string | null;
  nickname: string | null;
  avatar_url: string | null;
  profile_completed: boolean;
  points_balance: number;
  frozen_balance: number;
  withdrawable_balance_cents: number;
  frozen_commission_cents: number;
  withdrawn_amount_cents: number;
  rebate_points_balance: number;
  rebate_frozen_balance: number;
  primary_phone: string | null;
  phone_verified_at: string | null;
  primary_unionid: string | null;
  first_login_at: string;
  registered_at: string;
  created_at: string;
  updated_at: string;
  last_active_at: string;
  openid: string | null;
  unionid: string | null;
  guest_channel: string | null;
  guest_key: string | null;
  guest_appid: string | null;
  guest_openid: string | null;
  guest_unionid: string | null;
}

export interface InternalUserListResponse {
  items: InternalUserResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface RefundRequestResponse {
  refund_id: string;
  order_id: string;
  user_id: string;
  status: string;
  reason: string | null;
  operator_note: string | null;
  reject_reason: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  retry_count: number;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromotionCommissionResponse {
  commission_id: string;
  promoter_user_id: string;
  promoter_nickname: string | null;
  invited_user_id: string | null;
  invited_user_nickname: string | null;
  order_id: string | null;
  order_amount_cents: number;
  commission_rate: number;
  commission_amount_cents: number;
  commission_points: number;
  commission_type: string;
  status: string;
  remark: string | null;
  created_at: string;
  updated_at: string;
  settled_at: string | null;
  revoked_at: string | null;
}

export interface RechargeOrderResponse {
  order_id: string;
  user_id: string;
  user_status: string | null;
  user_nickname: string | null;
  channel: string | null;
  status: string;
  raw_status: string | null;
  package_key: string;
  package_title: string;
  amount_cents: number;
  points_amount: number;
  bonus_points: number;
  total_points: number;
  source: string;
  external_order_id: string | null;
  proof_url: string | null;
  remark: string | null;
  review_note: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  paid_at: string | null;
  completed_at: string | null;
  closed_at: string | null;
  refund_requests: RefundRequestResponse[];
  commission_records: PromotionCommissionResponse[];
  granted_ledger_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface RechargeOrderListResponse {
  items: RechargeOrderResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface RechargeOrderReviewResponse {
  order: RechargeOrderResponse;
  points: PointsAccountResponse;
  ledger: PointsLedgerEntryResponse | null;
}

export interface RechargeOrderSummaryResponse {
  order_id: string;
  package_title: string;
  amount_cents: number;
  status: string;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  paid_at: string | null;
  completed_at: string | null;
}

export interface UsageRecordResponse {
  usage_record_id: string;
  user_id: string;
  scene: string;
  feature_key: string;
  feature_name: string | null;
  channel: string | null;
  target_id: string | null;
  points_cost: number;
  normal_points_cost: number;
  rebate_points_cost: number;
  status: string;
  user_status: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  user_avatar_url: string | null;
  request_payload_summary: Record<string, unknown> | null;
  result_summary: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface UsageRecordListResponse {
  items: UsageRecordResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternalUserAdminSummaryResponse {
  user: InternalUserResponse;
  recent_orders: RechargeOrderSummaryResponse[];
  recent_order_count: number;
  recent_recharge_amount_cents: number;
  latest_order_status: string | null;
  total_recharge_amount_cents: number;
  total_withdraw_amount_cents: number;
  promoter_parent_user_id: string | null;
  identity_level: string;
}

export interface UsageRecordDetailResponse {
  record: UsageRecordResponse;
  user: InternalUserResponse;
  recent_orders: RechargeOrderSummaryResponse[];
}

export interface LlmApiKeyResponse {
  key_id: string;
  provider: string;
  model: string;
  display_name: string;
  masked_key: string;
  secret_ref: string;
  enabled: boolean;
  priority: number;
  remark: string | null;
  last_operator: string | null;
  created_at: string;
  updated_at: string;
}

export interface LlmApiKeyListResponse {
  items: LlmApiKeyResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface RuntimeConfigEntryResponse {
  entry_id: string;
  scope_type: 'global' | 'channel';
  scope_key: string;
  config_key: string;
  value: unknown;
  updated_at: string;
}

export interface RuntimeConfigListResponse {
  items: RuntimeConfigEntryResponse[];
}

export interface RuntimeConfigEntryUpsertRequest {
  scope_type: 'global' | 'channel';
  scope_key: string;
  config_key: string;
  value: unknown;
}

export interface RuntimeConfigSchemaItemResponse {
  config_key: string;
  label: string;
  value_type: string;
  default_value: unknown;
  scope_type: 'global' | 'channel';
  scope_key: string;
  group: string;
  high_risk: boolean;
  description: string | null;
}

export interface RuntimeConfigSchemaResponse {
  items: RuntimeConfigSchemaItemResponse[];
}

export interface RebatePointsAccountResponse {
  user_id: string;
  balance: number;
  frozen_balance: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface ManualPointsAdjustResponse {
  user: InternalUserResponse;
  points: PointsAccountResponse;
  ledger: PointsLedgerEntryResponse;
}

export interface RebatePointsAdjustResponse {
  user: InternalUserResponse;
  rebate_points: RebatePointsAccountResponse;
}

export interface PromotionApplicationResponse {
  application_id: string;
  user_id: string;
  user_nickname: string | null;
  current_identity_level: string | null;
  requested_level: string;
  status: string;
  applicant_name: string | null;
  applicant_phone: string | null;
  reject_reason: string | null;
  review_note: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromotionApplicationListResponse {
  items: PromotionApplicationResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromotionCommissionListResponse {
  items: PromotionCommissionResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromotionWithdrawalResponse {
  withdrawal_id: string;
  user_id: string;
  user_nickname: string | null;
  identity_level: string | null;
  status: string;
  withdrawable_balance_snapshot_cents: number;
  frozen_commission_snapshot_cents: number;
  points_used: number;
  amount_cents: number;
  rebate_points_balance_snapshot: number;
  cash_rate_snapshot: number;
  reject_reason: string | null;
  review_note: string | null;
  payout_method: string | null;
  payout_proof: string | null;
  payout_failure_reason: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromotionWithdrawalListResponse {
  items: PromotionWithdrawalResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromotionRulesResponse {
  normal_threshold_cents: number;
  senior_threshold_cents: number;
  normal_commission_rate: number;
  senior_commission_rate: number;
  min_withdraw_cents: number;
  order_completion_days: number;
}
