export type Gender = 'male' | 'female';
export type ReviewStatus = 'processing' | 'completed' | 'failed' | 'retryable';
export type ReviewProgressStage = 'queued' | 'scoring' | 'rendering' | 'finalizing' | 'completed' | 'failed';
export type VoiceNarrationScene = 'phone_summary' | 'phone_stability' | 'phone_aspect';
export type VoiceNarrationFormat = 'mp3';
export type VoiceMode = 'hybrid' | 'browser' | 'cloud';

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

export interface FourPillarsSummary {
  title: string;
  risk: string;
  usage_guidance: string;
  elements_check: Record<string, string>;
}

export type FourPillarsPillarKey = 'year' | 'month' | 'day' | 'hour';

export interface FourPillarsDisplayHiddenStem {
  stem: string;
  element: string;
  ten_god: string;
}

export interface FourPillarsShenShaDetail {
  name: string;
  category: string;
  basis: string;
  basis_value: string;
  target: string;
  target_value: string;
  rule: string;
  meaning: string;
}

export interface FourPillarsDisplayPillar {
  key: FourPillarsPillarKey;
  label: string;
  ganzhi: string;
  stem: string;
  branch: string;
  stem_element: string;
  branch_element: string;
  stem_ten_god: string;
  branch_ten_gods: string[];
  hidden_stems: FourPillarsDisplayHiddenStem[];
  na_yin: string;
  xun_kong: string;
  di_shi: string;
  self_sitting: string;
  shen_sha: string[];
  shen_sha_details?: FourPillarsShenShaDetail[];
}

export interface FourPillarsChartDisplay {
  profile: {
    gender_label: string;
    zodiac: string | null;
    solar_datetime_text: string;
    lunar_date: string;
    lunar_full_text: string | null;
    birth_place: string | null;
    timezone: string;
    solar_term_context: string | null;
  };
  pillars: Record<FourPillarsPillarKey, FourPillarsDisplayPillar>;
  element_status: Array<{
    element: '木' | '火' | '土' | '金' | '水';
    status: '旺' | '相' | '休' | '囚' | '死' | '';
  }>;
}

export interface FourPillarsAspect {
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

export interface FourPillarsLuckRenderRecord {
  id: string;
  render_id: string;
  review_id: string;
  user_id: string;
  render_type: 'dayun' | 'liunian';
  cycle_key: string;
  year: number | null;
  status: ReviewStatus;
  progress_message: string | null;
  facts: Record<string, unknown> | null;
  result: Record<string, unknown> | null;
  points_cost: number;
  error_message: string | null;
  retry_count: number;
  last_attempt_at: string | null;
  next_retry_available_at: string | null;
  is_retryable: boolean;
  created_at: string;
  updated_at: string;
}

export interface FourPillarsLuckYearItem {
  year: number;
  age: number | null;
  ganzhi: string;
  stem?: string | null;
  branch?: string | null;
  stem_ten_god?: string | null;
  stem_element?: string | null;
  branch_element?: string | null;
  di_shi?: string | null;
  shen_sha?: string[];
  shen_sha_details?: FourPillarsShenShaDetail[];
  is_current: boolean;
  render_status: 'not_generated' | ReviewStatus | string;
  render: FourPillarsLuckRenderRecord | null;
}

export interface FourPillarsLuckCycle {
  cycle_key: string;
  start_year: number;
  end_year: number;
  start_age: number | null;
  end_age: number | null;
  ganzhi: string | null;
  display_ganzhi: string | null;
  is_current: boolean;
  stem?: string | null;
  branch?: string | null;
  stem_ten_god?: string | null;
  stem_element?: string | null;
  branch_element?: string | null;
  di_shi?: string | null;
  shen_sha?: string[];
  shen_sha_details?: FourPillarsShenShaDetail[];
  render_status: 'not_generated' | ReviewStatus | string;
  render: FourPillarsLuckRenderRecord | null;
  year_items: FourPillarsLuckYearItem[];
}

export interface FourPillarsLuckAnalysis {
  enabled: boolean;
  cycle_points_cost: number;
  year_points_cost: number;
  current_cycle_key: string | null;
  cycles: FourPillarsLuckCycle[];
}

export interface FourPillarsLuckCycleListResponse {
  luck_analysis: FourPillarsLuckAnalysis;
}

export interface FourPillarsCreatePayload {
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone?: string | null;
  birth_place?: string | null;
  name?: string | null;
  include_markdown?: boolean;
}

export interface FourPillarsReviewRecord {
  id: string;
  report_id: string;
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birth_place: string | null;
  name: string | null;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  score: number | null;
  input_profile: Record<string, unknown>;
  chart: Record<string, unknown> | null;
  chart_display: FourPillarsChartDisplay | null;
  summary: FourPillarsSummary | null;
  deterministic_facts: Record<string, unknown>;
  aspects: FourPillarsAspect[];
  analysis_branches: Record<string, unknown>;
  luck_analysis: FourPillarsLuckAnalysis | null;
  aspect_unlock_points: number | null;
  free_aspect_keys: string[];
  unlock_enforcement_enabled: boolean | null;
  score_markdown: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface FourPillarsReviewSummary {
  id: string;
  report_id: string;
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birth_place: string | null;
  name: string | null;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  score: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface FourPillarsReviewListResponse {
  items: FourPillarsReviewSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface FourPillarsAspectUnlockResponse {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  points: PointsAccountResponse | null;
  aspect: FourPillarsAspect | null;
}

export interface FourPillarsAspectUnlockListResponse {
  items: FourPillarsAspectUnlockResponse[];
  available_aspect_keys: string[];
  free_aspect_keys: string[];
  unlocked_aspect_keys: string[];
  aspect_unlock_points_cost: number;
  unlock_enforcement_enabled: boolean;
  aspects: FourPillarsAspect[];
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
  llm: Record<string, unknown>;
  sections: DashboardSection[];
}

export interface UserResponse {
  user_id: string;
  uid: string | null;
  status: string;
  identity_level: string;
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

export interface PointsClaimLinkResponse {
  claim_link_id: string;
  claim_code: string;
  claim_url: string;
  title: string;
  points_amount: number;
  display_value_cents: number;
  status: string;
  effective_status: string;
  valid_from: string;
  expires_at: string;
  claimed_user_count: number;
  granted_points_total: number;
  duplicate_attempt_count: number;
  created_by: string | null;
  disabled_by: string | null;
  disabled_at: string | null;
  operator_note: string | null;
  created_at: string;
  updated_at: string;
}

export interface PointsClaimLinkListResponse {
  items: PointsClaimLinkResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PointsClaimRecordResponse {
  claim_record_id: string;
  claim_link_id: string;
  claim_code: string | null;
  claim_title: string | null;
  user_id: string;
  user_uid: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  week_key: string;
  week_starts_at: string;
  status: string;
  points_amount_snapshot: number;
  display_value_cents_snapshot: number;
  ledger_id: string | null;
  failure_reason: string | null;
  request_ip: string | null;
  user_agent: string | null;
  created_at: string;
  updated_at: string;
}

export interface PointsClaimRecordListResponse {
  items: PointsClaimRecordResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PublicPointsClaimLinkResponse {
  claim_code: string;
  title: string;
  points_amount: number;
  display_value_cents: number;
  status: string;
  effective_status: string;
  valid_from: string;
  expires_at: string;
  current_user_claim_status: string | null;
  current_user_claim_record: PointsClaimRecordResponse | null;
}

export interface PointsClaimSubmitResponse {
  claim_status: string;
  message: string;
  points: PointsAccountResponse | null;
  ledger: PointsLedgerEntryResponse | null;
  record: PointsClaimRecordResponse | null;
  already_claimed_record: PointsClaimRecordResponse | null;
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

export interface RechargePackageListResponse {
  items: RechargePackageResponse[];
}

export interface ModuleRuntimeConfigResponse {
  enabled: boolean;
  base_points_cost: number | null;
  aspect_unlock_points_cost?: number | null;
  free_aspect_keys?: string[] | null;
  aspect_order?: string[] | null;
  unlock_enforcement_enabled?: boolean | null;
  luck_cycle_points_cost?: number | null;
  luck_year_points_cost?: number | null;
  luck_generation_enabled?: boolean | null;
  metaphysics_skill_enabled?: boolean | null;
}

export interface VoiceRuntimeConfigResponse {
  enabled: boolean;
  mode: VoiceMode;
  autoplay_default_enabled: boolean;
  provider: string;
  default_voice_key: string;
  cache_enabled: boolean;
  max_chars_per_request: number;
}

export interface PublicRuntimeConfigResponse {
  channel: string | null;
  points: {
    initial_grant: number;
  };
  recharge: {
    packages: RechargePackageResponse[];
  };
  customer_service: {
    wechat_id: string | null;
    contact_url: string | null;
    qr_code_url: string | null;
    guidance_text: string;
    qr_guidance_text: string;
    copy_button_text: string;
    unconfigured_text: string;
    copy: Record<string, string>;
  };
  compliance: {
    safe_mode_enabled: boolean;
    safe_modules: string[];
    hidden_modules: string[];
    hidden_pages: string[];
  };
  modules: {
    phone_review: ModuleRuntimeConfigResponse;
    four_pillars: ModuleRuntimeConfigResponse;
    agent: ModuleRuntimeConfigResponse;
    almanac: ModuleRuntimeConfigResponse;
    voice: VoiceRuntimeConfigResponse;
  };
}

export interface PhoneStatusRequest {
  phone: string;
}

export type VoiceNarrationRequest =
  | { scene: 'phone_summary'; review_id: string; voice_key?: string | null }
  | { scene: 'phone_stability'; review_id: string; voice_key?: string | null }
  | { scene: 'phone_aspect'; review_id: string; aspect_key: string; voice_key?: string | null };

export interface VoiceNarrationResponse {
  narration_id: string;
  scene: VoiceNarrationScene;
  text_hash: string;
  audio_url: string;
  provider: string;
  voice_key: string;
  format: VoiceNarrationFormat;
  char_count: number;
  cached: boolean;
}

export interface PhoneStatusResponse {
  registered: boolean;
  normalized_phone: string;
  next_action: 'login' | 'register';
}

export interface PhonePasswordRegisterRequest {
  phone: string;
  password: string;
  confirm_password: string;
}

export interface PhonePasswordLoginRequest {
  phone: string;
  password: string;
}

export interface UserProfileUpdateRequest {
  nickname?: string | null;
  avatar_url?: string | null;
}

export interface AvatarUploadRequest {
  image_data_url: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface PasswordChangeResponse {
  status: string;
}

export interface AuthLoginResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: UserResponse;
  points: PointsAccountResponse;
}

export interface CurrentUserResponse {
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

export type PhoneReviewAspectStreamDeltaField = 'title' | 'risk' | 'content';

export interface PhoneReviewAspectStreamUnlockData {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  status: string;
  points: PointsAccountResponse | null;
}

export interface PhoneReviewAspectStreamStatusData {
  message: string;
}

export interface PhoneReviewAspectStreamDeltaData {
  field: PhoneReviewAspectStreamDeltaField;
  delta: string;
  text: string;
}

export interface PhoneReviewAspectStreamCompleteData {
  aspect: ReviewAspect | null;
  review: ReviewRecord;
  points: PointsAccountResponse | null;
}

export interface PhoneReviewAspectStreamErrorData {
  detail: string;
  message?: string;
  refunded?: boolean;
}

export interface InternalUserResponse {
  user_id: string;
  uid: string | null;
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
  payment_transactions: PaymentTransactionResponse[];
  latest_payment: PaymentTransactionResponse | null;
  granted_ledger_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaymentTransactionResponse {
  transaction_id: string;
  order_id: string;
  user_id: string;
  provider: string;
  payment_method: string;
  amount_cents: number;
  status: string;
  provider_transaction_id: string | null;
  prepay_id: string | null;
  idempotency_key: string | null;
  payment_params: Record<string, unknown>;
  client_message: string | null;
  failure_reason: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RechargeOrderPaymentStatusResponse {
  order: RechargeOrderResponse;
  latest_payment: PaymentTransactionResponse | null;
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

export interface RechargeOrderManualCompleteResponse {
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
  llm_key_id: string | null;
  llm_key_name: string | null;
  llm_model: string | null;
  llm_priority_class: string | null;
  llm_wait_ms: number | null;
  llm_duration_ms: number | null;
  llm_retry_count: number;
  llm_error_type: string | null;
  llm_error_message: string | null;
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

export interface InternalPhoneQimenSummaryResponse {
  generated_at: string;
  today_review_count: number;
  week_review_count: number;
  total_review_count: number;
  completed_review_count: number;
  failed_review_count: number;
  success_rate: number;
  average_generation_seconds: number | null;
  aspect_unlock_count: number;
  aspect_unlock_rate: number;
  review_points_cost: number;
  voice_request_count: number;
}

export interface InternalPhoneQimenReviewItemResponse {
  review_id: string;
  user_id: string | null;
  user_uid: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  phone: string;
  gender: Gender;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  error_message: string | null;
  channel: string | null;
  base_points_cost: number;
  unlock_count: number;
  voice_count: number;
  generation_duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface InternalPhoneQimenReviewListResponse {
  items: InternalPhoneQimenReviewItemResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternalPhoneQimenAspectUnlockRecordResponse {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  aspect_name: string;
  points_cost: number;
  usage_record_id: string | null;
  unlocked_at: string;
}

export interface InternalPhoneQimenReviewDetailResponse {
  review: InternalPhoneQimenReviewItemResponse;
  unlock_records: InternalPhoneQimenAspectUnlockRecordResponse[];
  voice_records: UsageRecordResponse[];
}

export interface InternalFourPillarsSummaryResponse extends InternalPhoneQimenSummaryResponse {}

export interface InternalFourPillarsReviewItemResponse {
  review_id: string;
  user_id: string | null;
  user_uid: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birth_place: string | null;
  name: string | null;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  error_message: string | null;
  channel: string | null;
  base_points_cost: number;
  unlock_count: number;
  voice_count: number;
  generation_duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface InternalFourPillarsReviewListResponse {
  items: InternalFourPillarsReviewItemResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternalFourPillarsAspectUnlockRecordResponse extends InternalPhoneQimenAspectUnlockRecordResponse {}

export interface InternalFourPillarsReviewDetailResponse {
  review: InternalFourPillarsReviewItemResponse;
  unlock_records: InternalFourPillarsAspectUnlockRecordResponse[];
  luck_render_records: FourPillarsLuckRenderRecord[];
}

export interface LlmApiKeyResponse {
  key_id: string;
  provider: string;
  model: string;
  display_name: string;
  masked_key: string;
  secret_ref: string;
  secret_configured: boolean;
  enabled: boolean;
  priority: number;
  max_concurrency: number;
  cooldown_seconds: number;
  current_inflight: number;
  available_slots: number;
  cooldown_until: string | null;
  last_rate_limited_at: string | null;
  last_error_message: string | null;
  last_used_at: string | null;
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

export interface LlmConcurrencyKeyResponse {
  key_id: string;
  display_name: string;
  provider: string;
  model: string;
  enabled: boolean;
  priority: number;
  max_concurrency: number;
  cooldown_seconds: number;
  current_inflight: number;
  available_slots: number;
  cooldown_until: string | null;
  last_rate_limited_at: string | null;
  last_error_message: string | null;
  last_used_at: string | null;
}

export interface LlmConcurrencyStatusResponse {
  backend: string;
  backend_available: boolean;
  backend_error: string | null;
  redis_configured: boolean;
  global_inflight: number;
  foreground_waiting: number;
  background_waiting: number;
  foreground_inflight: number;
  background_inflight: number;
  enabled_key_count: number;
  total_capacity: number;
  recent_429_count: number;
  recent_timeout_count: number;
  avg_wait_ms: number;
  avg_duration_ms: number;
  config: Record<string, unknown>;
  keys: LlmConcurrencyKeyResponse[];
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

export interface RuntimeInitialPointsUpdateRequest {
  initial_grant: number;
  apply_scope: 'future_users' | 'all_users';
  reason?: string | null;
}

export interface RuntimeInitialPointsUpdateResponse {
  previous_initial_grant: number;
  initial_grant: number;
  delta: number;
  apply_scope: 'future_users' | 'all_users';
  target_user_count: number;
  affected_user_count: number;
  adjusted_points_total: number;
  zeroed_user_count: number;
  operation_id: string;
  entry: RuntimeConfigEntryResponse;
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
  admin_group?: string | null;
  admin_section?: string | null;
  advanced?: boolean;
  sort_order?: number;
  input_options?: Array<{value: string; label: string}>;
  help_text?: string | null;
  admin_hidden?: boolean;
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
