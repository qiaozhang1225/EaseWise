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
