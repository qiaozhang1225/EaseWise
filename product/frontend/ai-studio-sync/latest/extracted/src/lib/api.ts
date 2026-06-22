import type {
  AlmanacResponse,
  AvatarUploadRequest,
  AuthLoginResponse,
  CurrentUserResponse,
  DashboardResponse,
  FourPillarsAspectUnlockResponse,
  FourPillarsCreatePayload,
  FourPillarsLuckCycleListResponse,
  FourPillarsLuckRenderRecord,
  FourPillarsReviewListResponse,
  FourPillarsReviewRecord,
  Gender,
  InternalFourPillarsReviewDetailResponse,
  InternalFourPillarsReviewListResponse,
  InternalFourPillarsSummaryResponse,
  InternalPhoneQimenReviewDetailResponse,
  InternalPhoneQimenReviewListResponse,
  InternalPhoneQimenSummaryResponse,
  PointsAccountResponse,
  PointsLedgerListResponse,
  PromotionApplicationListResponse,
  PromotionApplicationResponse,
  PromotionCommissionListResponse,
  PromotionCommissionResponse,
  PromotionRulesResponse,
  PromotionWithdrawalListResponse,
  PromotionWithdrawalResponse,
  PublicRuntimeConfigResponse,
  InternalUserAdminSummaryResponse,
  InternalUserListResponse,
  LlmApiKeyListResponse,
  LlmApiKeyResponse,
  LlmConcurrencyStatusResponse,
  ManualPointsAdjustResponse,
  PaymentTransactionResponse,
  PhonePasswordLoginRequest,
  PhonePasswordRegisterRequest,
  PhoneStatusRequest,
  PhoneStatusResponse,
  PasswordChangeRequest,
  PasswordChangeResponse,
  RebatePointsAdjustResponse,
  PointsClaimLinkListResponse,
  PointsClaimLinkResponse,
  PointsClaimRecordListResponse,
  PointsClaimSubmitResponse,
  PublicPointsClaimLinkResponse,
  RefundRequestResponse,
  RechargeOrderListResponse,
  RechargeOrderManualCompleteResponse,
  RechargeOrderPaymentStatusResponse,
  RechargeOrderResponse,
  RechargeOrderReviewResponse,
  RechargePackageListResponse,
  ReviewAspectUnlockResponse,
  ReviewListResponse,
  ReviewRecord,
  RuntimeConfigEntryResponse,
  RuntimeConfigListResponse,
  RuntimeConfigEntryUpsertRequest,
  RuntimeInitialPointsUpdateRequest,
  RuntimeInitialPointsUpdateResponse,
  RuntimeConfigSchemaResponse,
  UsageRecordDetailResponse,
  UsageRecordListResponse,
  InternalUserResponse,
  UserProfileUpdateRequest,
  VoiceNarrationRequest,
  VoiceNarrationResponse,
} from '../types/api';

const API_BASE_URL = resolveApiBaseUrl();

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;
  readonly payload: unknown;

  constructor(status: number, detail: string, payload: unknown) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.payload = payload;
  }
}

type RequestOptions = Omit<RequestInit, 'body'> & {
  body?: unknown;
  accessToken?: string | null;
  adminToken?: string | null;
};

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');
  headers.set('X-Client-Platform', 'h5');
  headers.set('X-Client-Channel', 'h5');
  headers.set('X-Client-Version', 'easewise-local-frontend');

  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json');
  }
  if (options.accessToken) {
    headers.set('Authorization', `Bearer ${options.accessToken}`);
  }
  if (options.adminToken) {
    headers.set('X-Internal-Admin-Token', options.adminToken);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  const rawText = await response.text();
  const payload = rawText ? tryParseJson(rawText) : null;

  if (!response.ok) {
    const detail = resolveApiErrorDetail(payload, response.statusText);
    throw new ApiError(response.status, detail, payload);
  }

  return payload as T;
}

function tryParseJson(rawText: string): unknown {
  try {
    return JSON.parse(rawText);
  } catch {
    return rawText;
  }
}

function resolveApiErrorDetail(payload: unknown, fallback: string): string {
  if (typeof payload === 'string' && payload.trim()) {
    return payload.trim();
  }
  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail.trim();
    }
  }
  return fallback || 'request_failed';
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export function resolveApiAssetUrl(assetUrl: string | null | undefined): string {
  const trimmedUrl = String(assetUrl || '').trim();
  if (!trimmedUrl) {
    return '';
  }
  if (/^(https?:|data:|blob:)/i.test(trimmedUrl)) {
    return trimmedUrl;
  }
  const normalizedPath = trimmedUrl.startsWith('/') ? trimmedUrl : `/${trimmedUrl}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

function resolveApiBaseUrl(): string {
  const configuredValue = (import.meta as any).env?.VITE_API_BASE_URL;
  if (configuredValue) {
    return configuredValue.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined') {
    return window.location.origin.replace(/\/+$/, '');
  }

  return 'http://127.0.0.1:8000';
}

export function getPhoneAuthStatus(payload: PhoneStatusRequest): Promise<PhoneStatusResponse> {
  return requestJson<PhoneStatusResponse>('/api/v1/auth/phone/status', {
    method: 'POST',
    body: payload,
  });
}

export function registerPhoneWithPassword(payload: PhonePasswordRegisterRequest): Promise<AuthLoginResponse> {
  return requestJson<AuthLoginResponse>('/api/v1/auth/phone/register', {
    method: 'POST',
    body: payload,
  });
}

export function loginPhoneWithPassword(payload: PhonePasswordLoginRequest): Promise<AuthLoginResponse> {
  return requestJson<AuthLoginResponse>('/api/v1/auth/phone/login', {
    method: 'POST',
    body: payload,
  });
}

export function logoutCurrentUser(accessToken: string): Promise<{status: string}> {
  return requestJson<{status: string}>('/api/v1/auth/logout', {
    method: 'POST',
    accessToken,
  });
}

export function getPublicRuntimeConfig(): Promise<PublicRuntimeConfigResponse> {
  return requestJson<PublicRuntimeConfigResponse>('/api/v1/runtime-config/public?channel=h5');
}

export function getTodayAlmanac(): Promise<AlmanacResponse> {
  return requestJson<AlmanacResponse>('/api/v1/almanac/today');
}

export function getMyPoints(accessToken: string): Promise<PointsAccountResponse> {
  return requestJson<PointsAccountResponse>('/api/v1/account/points', {
    accessToken,
  });
}

export function getCurrentUser(accessToken: string): Promise<CurrentUserResponse> {
  return requestJson<CurrentUserResponse>('/api/v1/account/me', {
    accessToken,
  });
}

export function updateMyProfile(accessToken: string, payload: UserProfileUpdateRequest): Promise<CurrentUserResponse['user']> {
  return requestJson<CurrentUserResponse['user']>('/api/v1/account/profile', {
    method: 'PATCH',
    accessToken,
    body: payload,
  });
}

export function uploadMyAvatar(accessToken: string, payload: AvatarUploadRequest): Promise<CurrentUserResponse['user']> {
  return requestJson<CurrentUserResponse['user']>('/api/v1/account/avatar', {
    method: 'POST',
    accessToken,
    body: payload,
  });
}

export function changeMyPassword(accessToken: string, payload: PasswordChangeRequest): Promise<PasswordChangeResponse> {
  return requestJson<PasswordChangeResponse>('/api/v1/account/password/change', {
    method: 'POST',
    accessToken,
    body: payload,
  });
}

export function listMyPointsLedger(accessToken: string, limit = 20): Promise<PointsLedgerListResponse> {
  return requestJson<PointsLedgerListResponse>(`/api/v1/account/points/ledger?limit=${limit}`, {
    accessToken,
  });
}

export function getPublicPointsClaimLink(claimCode: string, accessToken?: string | null): Promise<PublicPointsClaimLinkResponse> {
  return requestJson<PublicPointsClaimLinkResponse>(`/api/v1/points-claims/${encodeURIComponent(claimCode)}`, {
    accessToken,
  });
}

export function claimPublicPoints(accessToken: string, claimCode: string): Promise<PointsClaimSubmitResponse> {
  return requestJson<PointsClaimSubmitResponse>(`/api/v1/points-claims/${encodeURIComponent(claimCode)}/claim`, {
    method: 'POST',
    accessToken,
  });
}

export function listRechargePackages(accessToken: string): Promise<RechargePackageListResponse> {
  return requestJson<RechargePackageListResponse>('/api/v1/billing/recharge-packages', {
    accessToken,
  });
}

export type RechargeOrderCreatePayload = {
  package_key: string;
  source?: string;
  external_order_id?: string | null;
  idempotency_key?: string | null;
  proof_url?: string | null;
  remark?: string | null;
};

export function createRechargeOrder(accessToken: string, payload: RechargeOrderCreatePayload): Promise<RechargeOrderResponse> {
  return requestJson<RechargeOrderResponse>('/api/v1/billing/recharge-orders', {
    method: 'POST',
    accessToken,
    body: {
      source: 'h5_recharge_page',
      ...payload,
    },
  });
}

export function getRechargeOrder(accessToken: string, orderId: string): Promise<RechargeOrderResponse> {
  return requestJson<RechargeOrderResponse>(`/api/v1/billing/recharge-orders/${encodeURIComponent(orderId)}`, {
    accessToken,
  });
}

export function createRechargePayment(accessToken: string, orderId: string, payload: {provider?: string; payment_method?: string | null; idempotency_key?: string | null; return_url?: string | null; client_context?: Record<string, unknown> | null} = {}): Promise<PaymentTransactionResponse> {
  return requestJson<PaymentTransactionResponse>(`/api/v1/billing/recharge-orders/${encodeURIComponent(orderId)}/payments`, {
    method: 'POST',
    accessToken,
    body: {
      provider: 'wechat_h5',
      ...payload,
    },
  });
}

export function getRechargePaymentStatus(accessToken: string, orderId: string): Promise<RechargeOrderPaymentStatusResponse> {
  return requestJson<RechargeOrderPaymentStatusResponse>(`/api/v1/billing/recharge-orders/${encodeURIComponent(orderId)}/payment-status`, {
    accessToken,
  });
}

export function createPhoneReview(accessToken: string, payload: { phone: string; gender: Gender; include_markdown?: boolean }): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>('/api/v1/phone-qimen/reviews', {
    method: 'POST',
    accessToken,
    body: {
      phone: payload.phone,
      gender: payload.gender,
      include_markdown: payload.include_markdown ?? true,
    },
  });
}

export function listPhoneReviews(accessToken: string, limit = 20): Promise<ReviewListResponse> {
  return requestJson<ReviewListResponse>(`/api/v1/phone-qimen/reviews?limit=${limit}`, {
    accessToken,
  });
}

export function getPhoneReviewDetail(accessToken: string, reviewId: string): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>(`/api/v1/phone-qimen/reviews/${reviewId}`, {
    accessToken,
  });
}

export function unlockPhoneReviewAspect(accessToken: string, reviewId: string, aspectKey: string): Promise<ReviewAspectUnlockResponse> {
  return requestJson<ReviewAspectUnlockResponse>(`/api/v1/phone-qimen/reviews/${reviewId}/aspect-unlocks`, {
    method: 'POST',
    accessToken,
    body: {
      aspect_key: aspectKey,
    },
  });
}

export function createFourPillarsReview(accessToken: string, payload: FourPillarsCreatePayload): Promise<FourPillarsReviewRecord> {
  return requestJson<FourPillarsReviewRecord>('/api/v1/four-pillars/reviews', {
    method: 'POST',
    accessToken,
    body: {
      timezone: 'Asia/Shanghai',
      include_markdown: true,
      ...payload,
    },
  });
}

export function listFourPillarsReviews(accessToken: string, limit = 20): Promise<FourPillarsReviewListResponse> {
  return requestJson<FourPillarsReviewListResponse>(`/api/v1/four-pillars/reviews?limit=${limit}`, {
    accessToken,
  });
}

export function getFourPillarsReviewDetail(accessToken: string, reviewId: string): Promise<FourPillarsReviewRecord> {
  return requestJson<FourPillarsReviewRecord>(`/api/v1/four-pillars/reviews/${reviewId}`, {
    accessToken,
  });
}

export function unlockFourPillarsReviewAspect(accessToken: string, reviewId: string, aspectKey: string): Promise<FourPillarsAspectUnlockResponse> {
  return requestJson<FourPillarsAspectUnlockResponse>(`/api/v1/four-pillars/reviews/${reviewId}/aspect-unlocks`, {
    method: 'POST',
    accessToken,
    body: {
      aspect_key: aspectKey,
    },
  });
}

export function getFourPillarsLuckCycles(accessToken: string, reviewId: string): Promise<FourPillarsLuckCycleListResponse> {
  return requestJson<FourPillarsLuckCycleListResponse>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles`, {
    accessToken,
  });
}

export function createFourPillarsLuckCycleSummary(accessToken: string, reviewId: string, cycleKey: string): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/summary`, {
    method: 'POST',
    accessToken,
  });
}

export function getFourPillarsLuckCycleSummary(accessToken: string, reviewId: string, cycleKey: string): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/summary`, {
    accessToken,
  });
}

export function createFourPillarsLuckYearSummary(accessToken: string, reviewId: string, cycleKey: string, year: number): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/years/${encodeURIComponent(String(year))}`, {
    method: 'POST',
    accessToken,
  });
}

export function getFourPillarsLuckYearSummary(accessToken: string, reviewId: string, cycleKey: string, year: number): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/years/${encodeURIComponent(String(year))}`, {
    accessToken,
  });
}

export function createVoiceNarration(accessToken: string, payload: VoiceNarrationRequest): Promise<VoiceNarrationResponse> {
  return requestJson<VoiceNarrationResponse>('/api/v1/voice/narrations', {
    method: 'POST',
    accessToken,
    body: payload,
  });
}

type QueryValue = string | number | boolean | null | undefined;

export function getInternalDashboard(adminToken: string, params: Record<string, QueryValue> = {}): Promise<DashboardResponse> {
  return requestJson<DashboardResponse>(`/api/v1/internal/dashboard${toQueryString(params)}`, {
    adminToken,
  });
}

export function listInternalLlmApiKeys(adminToken: string, params: Record<string, QueryValue> = {}): Promise<LlmApiKeyListResponse> {
  return requestJson<LlmApiKeyListResponse>(`/api/v1/internal/llm/api-keys${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalLlmConcurrency(adminToken: string): Promise<LlmConcurrencyStatusResponse> {
  return requestJson<LlmConcurrencyStatusResponse>('/api/v1/internal/llm/concurrency', {
    adminToken,
  });
}

export type InternalLlmApiKeyPayload = {
  provider: string;
  model: string;
  display_name: string;
  masked_key?: string | null;
  secret_ref?: string | null;
  secret_value?: string | null;
  enabled: boolean;
  priority: number;
  max_concurrency?: number;
  cooldown_seconds?: number;
  remark?: string | null;
  last_operator?: string | null;
};

export function createInternalLlmApiKey(adminToken: string, payload: InternalLlmApiKeyPayload): Promise<LlmApiKeyResponse> {
  return requestJson<LlmApiKeyResponse>('/api/v1/internal/llm/api-keys', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function updateInternalLlmApiKey(adminToken: string, keyId: string, payload: InternalLlmApiKeyPayload): Promise<LlmApiKeyResponse> {
  return requestJson<LlmApiKeyResponse>(`/api/v1/internal/llm/api-keys/${encodeURIComponent(keyId)}`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function deleteInternalLlmApiKey(adminToken: string, keyId: string): Promise<{status: string}> {
  return requestJson<{status: string}>(`/api/v1/internal/llm/api-keys/${encodeURIComponent(keyId)}`, {
    method: 'DELETE',
    adminToken,
  });
}

export function listInternalUsageRecords(adminToken: string, params: Record<string, QueryValue>): Promise<UsageRecordListResponse> {
  return requestJson<UsageRecordListResponse>(`/api/v1/internal/platform/usage-records${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalUsageRecord(adminToken: string, usageRecordId: string): Promise<UsageRecordDetailResponse> {
  return requestJson<UsageRecordDetailResponse>(`/api/v1/internal/platform/usage-records/${encodeURIComponent(usageRecordId)}`, {
    adminToken,
  });
}

export function getInternalPhoneQimenSummary(adminToken: string): Promise<InternalPhoneQimenSummaryResponse> {
  return requestJson<InternalPhoneQimenSummaryResponse>('/api/v1/internal/phone-qimen/summary', {
    adminToken,
  });
}

export function listInternalPhoneQimenReviews(adminToken: string, params: Record<string, QueryValue> = {}): Promise<InternalPhoneQimenReviewListResponse> {
  return requestJson<InternalPhoneQimenReviewListResponse>(`/api/v1/internal/phone-qimen/reviews${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPhoneQimenReview(adminToken: string, reviewId: string): Promise<InternalPhoneQimenReviewDetailResponse> {
  return requestJson<InternalPhoneQimenReviewDetailResponse>(`/api/v1/internal/phone-qimen/reviews/${encodeURIComponent(reviewId)}`, {
    adminToken,
  });
}

export function getInternalFourPillarsSummary(adminToken: string): Promise<InternalFourPillarsSummaryResponse> {
  return requestJson<InternalFourPillarsSummaryResponse>('/api/v1/internal/four-pillars/summary', {
    adminToken,
  });
}

export function listInternalFourPillarsReviews(adminToken: string, params: Record<string, QueryValue> = {}): Promise<InternalFourPillarsReviewListResponse> {
  return requestJson<InternalFourPillarsReviewListResponse>(`/api/v1/internal/four-pillars/reviews${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalFourPillarsReview(adminToken: string, reviewId: string): Promise<InternalFourPillarsReviewDetailResponse> {
  return requestJson<InternalFourPillarsReviewDetailResponse>(`/api/v1/internal/four-pillars/reviews/${encodeURIComponent(reviewId)}`, {
    adminToken,
  });
}

export function listInternalUsers(adminToken: string, queryOrParams?: string | Record<string, QueryValue>): Promise<InternalUserListResponse> {
  const params = typeof queryOrParams === 'string' ? {query: queryOrParams} : (queryOrParams || {});
  return requestJson<InternalUserListResponse>(`/api/v1/internal/users${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalUserAdminSummary(adminToken: string, userId: string): Promise<InternalUserAdminSummaryResponse> {
  return requestJson<InternalUserAdminSummaryResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/admin-summary`, {
    adminToken,
  });
}

export function listInternalRechargeOrders(adminToken: string, params: Record<string, QueryValue>): Promise<RechargeOrderListResponse> {
  return requestJson<RechargeOrderListResponse>(`/api/v1/internal/billing/recharge-orders${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalRechargeOrder(adminToken: string, orderId: string): Promise<RechargeOrderResponse> {
  return requestJson<RechargeOrderResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}`, {
    adminToken,
  });
}

export function reviewInternalRechargeOrder(adminToken: string, orderId: string, payload: {action: 'approve' | 'reject'; review_note?: string | null}): Promise<RechargeOrderReviewResponse> {
  return requestJson<RechargeOrderReviewResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function manualCompleteInternalRechargeOrder(adminToken: string, orderId: string, payload: {payment_method?: string | null; payment_reference?: string | null; operator_note?: string | null}): Promise<RechargeOrderManualCompleteResponse> {
  return requestJson<RechargeOrderManualCompleteResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}/manual-complete`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function createInternalRechargeOrderRefund(adminToken: string, orderId: string, payload: {reason?: string | null; operator_note?: string | null}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}/refunds`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function reviewInternalRefund(adminToken: string, refundId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; operator_note?: string | null}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/billing/refunds/${encodeURIComponent(refundId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function retryInternalRefund(adminToken: string, refundId: string, payload: {operator_note?: string | null} = {}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/billing/refunds/${encodeURIComponent(refundId)}/retry`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function adjustInternalUserPoints(adminToken: string, userId: string, payload: {delta: number; biz_type?: string | null; biz_id?: string | null; idempotency_key?: string | null; remark?: string | null; reason?: string | null; operator_note?: string | null}): Promise<ManualPointsAdjustResponse> {
  return requestJson<ManualPointsAdjustResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/points/adjust`, {
    method: 'POST',
    adminToken,
    body: {
      biz_type: 'admin_manual_adjust',
      ...payload,
    },
  });
}

export function adjustInternalUserRebatePoints(adminToken: string, userId: string, payload: {delta: number; reason?: string | null; operator_note?: string | null}): Promise<RebatePointsAdjustResponse> {
  return requestJson<RebatePointsAdjustResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/rebate-points/adjust`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalPointsClaimLinks(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PointsClaimLinkListResponse> {
  return requestJson<PointsClaimLinkListResponse>(`/api/v1/internal/points-claims${toQueryString(params)}`, {
    adminToken,
  });
}

export function createInternalPointsClaimLink(adminToken: string, payload: {title: string; points_amount: number; display_value_cents: number; expires_in_hours?: number | null; expires_at?: string | null; operator_note?: string | null}): Promise<PointsClaimLinkResponse> {
  return requestJson<PointsClaimLinkResponse>('/api/v1/internal/points-claims', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function getInternalPointsClaimLink(adminToken: string, claimLinkId: string): Promise<PointsClaimLinkResponse> {
  return requestJson<PointsClaimLinkResponse>(`/api/v1/internal/points-claims/${encodeURIComponent(claimLinkId)}`, {
    adminToken,
  });
}

export function disableInternalPointsClaimLink(adminToken: string, claimLinkId: string, payload: {operator_note?: string | null} = {}): Promise<PointsClaimLinkResponse> {
  return requestJson<PointsClaimLinkResponse>(`/api/v1/internal/points-claims/${encodeURIComponent(claimLinkId)}/disable`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalPointsClaimRecords(adminToken: string, claimLinkId: string, params: Record<string, QueryValue> = {}): Promise<PointsClaimRecordListResponse> {
  return requestJson<PointsClaimRecordListResponse>(`/api/v1/internal/points-claims/${encodeURIComponent(claimLinkId)}/records${toQueryString(params)}`, {
    adminToken,
  });
}

export function updateInternalUserStatus(adminToken: string, userId: string, payload: {status: string; reason?: string | null; operator_note?: string | null}): Promise<InternalUserResponse> {
  return requestJson<InternalUserResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/status`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function updateInternalUserIdentity(adminToken: string, userId: string, payload: {identity_level: string; reason?: string | null; operator_note?: string | null}): Promise<InternalUserResponse> {
  return requestJson<InternalUserResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/identity`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function updateInternalUserPromoterParent(adminToken: string, userId: string, payload: {promoter_parent_user_id?: string | null; reason?: string | null; operator_note?: string | null}): Promise<InternalUserResponse> {
  return requestJson<InternalUserResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/promoter-parent`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function listInternalPromotionApplications(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PromotionApplicationListResponse> {
  return requestJson<PromotionApplicationListResponse>(`/api/v1/internal/promotion/applications${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPromotionApplication(adminToken: string, applicationId: string): Promise<PromotionApplicationResponse> {
  return requestJson<PromotionApplicationResponse>(`/api/v1/internal/promotion/applications/${encodeURIComponent(applicationId)}`, {
    adminToken,
  });
}

export function reviewInternalPromotionApplication(adminToken: string, applicationId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; review_note?: string | null; operator_note?: string | null}): Promise<PromotionApplicationResponse> {
  return requestJson<PromotionApplicationResponse>(`/api/v1/internal/promotion/applications/${encodeURIComponent(applicationId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalPromotionCommissions(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PromotionCommissionListResponse> {
  return requestJson<PromotionCommissionListResponse>(`/api/v1/internal/promotion/commissions${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPromotionCommission(adminToken: string, commissionId: string): Promise<PromotionCommissionResponse> {
  return requestJson<PromotionCommissionResponse>(`/api/v1/internal/promotion/commissions/${encodeURIComponent(commissionId)}`, {
    adminToken,
  });
}

export function listInternalPromotionWithdrawals(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PromotionWithdrawalListResponse> {
  return requestJson<PromotionWithdrawalListResponse>(`/api/v1/internal/promotion/withdrawals${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPromotionWithdrawal(adminToken: string, withdrawalId: string): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}`, {
    adminToken,
  });
}

export function reviewInternalPromotionWithdrawal(adminToken: string, withdrawalId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; review_note?: string | null; operator_note?: string | null}): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function retryInternalPromotionWithdrawalPayout(adminToken: string, withdrawalId: string, payload: {operator_note?: string | null} = {}): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}/retry-payout`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function markInternalPromotionWithdrawalPaid(adminToken: string, withdrawalId: string, payload: {payout_method?: string | null; payout_proof?: string | null; operator_note?: string | null}): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}/mark-paid`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function getInternalPromotionRules(adminToken: string): Promise<PromotionRulesResponse> {
  return requestJson<PromotionRulesResponse>('/api/v1/internal/promotion/rules', {
    adminToken,
  });
}

export function updateInternalPromotionRules(adminToken: string, payload: Partial<PromotionRulesResponse>): Promise<PromotionRulesResponse> {
  return requestJson<PromotionRulesResponse>('/api/v1/internal/promotion/rules', {
    method: 'PUT',
    adminToken,
    body: payload,
  });
}

export function listInternalRuntimeConfig(adminToken: string, params: Record<string, QueryValue> = {}): Promise<RuntimeConfigListResponse> {
  return requestJson<RuntimeConfigListResponse>(`/api/v1/internal/runtime-config${toQueryString(params)}`, {
    adminToken,
  });
}

export function updateInternalRuntimeConfig(adminToken: string, entries: RuntimeConfigEntryUpsertRequest[]): Promise<RuntimeConfigListResponse> {
  return requestJson<RuntimeConfigListResponse>('/api/v1/internal/runtime-config', {
    method: 'PUT',
    adminToken,
    body: {
      entries,
    },
  });
}

export function updateInternalInitialPointsConfig(adminToken: string, payload: RuntimeInitialPointsUpdateRequest): Promise<RuntimeInitialPointsUpdateResponse> {
  return requestJson<RuntimeInitialPointsUpdateResponse>('/api/v1/internal/runtime-config/initial-points', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function getInternalRuntimeConfigSchema(adminToken: string): Promise<RuntimeConfigSchemaResponse> {
  return requestJson<RuntimeConfigSchemaResponse>('/api/v1/internal/runtime-config/schema', {
    adminToken,
  });
}

export function uploadInternalCustomerServiceQrCode(adminToken: string, payload: {image_data_url: string}): Promise<RuntimeConfigEntryResponse> {
  return requestJson<RuntimeConfigEntryResponse>('/api/v1/internal/customer-service/qr-code', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function deleteInternalCustomerServiceQrCode(adminToken: string): Promise<RuntimeConfigEntryResponse> {
  return requestJson<RuntimeConfigEntryResponse>('/api/v1/internal/customer-service/qr-code', {
    method: 'DELETE',
    adminToken,
  });
}

export function sendChatToAgent(message: string, history: Array<{role: string; content: string}>): Promise<{reply: string}> {
  return requestJson<{reply: string}>('/api/v1/agent/chat', {
    method: 'POST',
    body: { message, history }
  });
}

function toQueryString(params: Record<string, QueryValue>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) {
      continue;
    }
    const normalizedValue = String(value).trim();
    if (normalizedValue) {
      searchParams.set(key, normalizedValue);
    }
  }
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}
