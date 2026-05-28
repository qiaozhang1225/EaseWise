import type {
  AlmanacResponse,
  DashboardResponse,
  Gender,
  GuestSessionResponse,
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
  ManualPointsAdjustResponse,
  RebatePointsAdjustResponse,
  RefundRequestResponse,
  RechargeOrderListResponse,
  RechargeOrderResponse,
  RechargeOrderReviewResponse,
  ReviewAspectUnlockResponse,
  ReviewListResponse,
  ReviewRecord,
  RuntimeConfigListResponse,
  RuntimeConfigEntryUpsertRequest,
  RuntimeConfigSchemaResponse,
  UsageRecordDetailResponse,
  UsageRecordListResponse,
  InternalUserResponse,
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

function resolveApiBaseUrl(): string {
  const configuredValue = import.meta.env.VITE_API_BASE_URL;
  if (configuredValue) {
    return configuredValue.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined') {
    const {hostname, origin, port, protocol} = window.location;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1';
    const isPrivateLan = /^(10|127|172\.(1[6-9]|2\d|3[01])|192\.168)\./.test(hostname);
    const isDevPort = port === '3000' || port === '5173';

    if (isDevPort || isLocalHost || isPrivateLan) {
      const resolvedProtocol = protocol === 'https:' ? 'https:' : 'http:';
      return `${resolvedProtocol}//${hostname}:8000`;
    }

    return origin.replace(/\/+$/, '');
  }

  return 'http://127.0.0.1:8000';
}

export function createGuestSession(guestKey?: string | null): Promise<GuestSessionResponse> {
  return requestJson<GuestSessionResponse>('/api/v1/guest/session', {
    method: 'POST',
    body: {
      channel: 'h5',
      guest_key: guestKey || undefined,
    },
  });
}

export function getPublicRuntimeConfig(): Promise<PublicRuntimeConfigResponse> {
  return requestJson<PublicRuntimeConfigResponse>('/api/v1/runtime-config/public?channel=h5');
}

export function getTodayAlmanac(): Promise<AlmanacResponse> {
  return requestJson<AlmanacResponse>('/api/v1/almanac/today');
}

export function getMyPoints(accessToken: string): Promise<PointsAccountResponse> {
  return requestJson<PointsAccountResponse>('/api/v1/me/points', {
    accessToken,
  });
}

export function listMyPointsLedger(accessToken: string, limit = 20): Promise<PointsLedgerListResponse> {
  return requestJson<PointsLedgerListResponse>(`/api/v1/me/points/ledger?limit=${limit}`, {
    accessToken,
  });
}

export function createPhoneReview(accessToken: string, payload: { phone: string; gender: Gender; include_markdown?: boolean }): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>('/api/v1/reviews', {
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
  return requestJson<ReviewListResponse>(`/api/v1/reviews?limit=${limit}`, {
    accessToken,
  });
}

export function getPhoneReviewDetail(accessToken: string, reviewId: string): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>(`/api/v1/reviews/${reviewId}`, {
    accessToken,
  });
}

export function unlockPhoneReviewAspect(accessToken: string, reviewId: string, aspectKey: string): Promise<ReviewAspectUnlockResponse> {
  return requestJson<ReviewAspectUnlockResponse>(`/api/v1/reviews/${reviewId}/aspect-unlocks`, {
    method: 'POST',
    accessToken,
    body: {
      aspect_key: aspectKey,
    },
  });
}

type QueryValue = string | number | boolean | null | undefined;

export function getInternalDashboard(adminToken: string, params: Record<string, QueryValue> = {}): Promise<DashboardResponse> {
  return requestJson<DashboardResponse>(`/api/v1/internal/dashboard${toQueryString(params)}`, {
    adminToken,
  });
}

export function listInternalLlmApiKeys(adminToken: string, params: Record<string, QueryValue> = {}): Promise<LlmApiKeyListResponse> {
  return requestJson<LlmApiKeyListResponse>(`/api/v1/internal/llm-api-keys${toQueryString(params)}`, {
    adminToken,
  });
}

export type InternalLlmApiKeyPayload = {
  provider: string;
  model: string;
  display_name: string;
  masked_key: string;
  secret_ref: string;
  enabled: boolean;
  priority: number;
  remark?: string | null;
  last_operator?: string | null;
};

export function createInternalLlmApiKey(adminToken: string, payload: InternalLlmApiKeyPayload): Promise<LlmApiKeyResponse> {
  return requestJson<LlmApiKeyResponse>('/api/v1/internal/llm-api-keys', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function updateInternalLlmApiKey(adminToken: string, keyId: string, payload: InternalLlmApiKeyPayload): Promise<LlmApiKeyResponse> {
  return requestJson<LlmApiKeyResponse>(`/api/v1/internal/llm-api-keys/${encodeURIComponent(keyId)}`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function deleteInternalLlmApiKey(adminToken: string, keyId: string): Promise<{status: string}> {
  return requestJson<{status: string}>(`/api/v1/internal/llm-api-keys/${encodeURIComponent(keyId)}`, {
    method: 'DELETE',
    adminToken,
  });
}

export function listInternalUsageRecords(adminToken: string, params: Record<string, QueryValue>): Promise<UsageRecordListResponse> {
  return requestJson<UsageRecordListResponse>(`/api/v1/internal/usage-records${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalUsageRecord(adminToken: string, usageRecordId: string): Promise<UsageRecordDetailResponse> {
  return requestJson<UsageRecordDetailResponse>(`/api/v1/internal/usage-records/${encodeURIComponent(usageRecordId)}`, {
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
  return requestJson<RechargeOrderListResponse>(`/api/v1/internal/recharge-orders${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalRechargeOrder(adminToken: string, orderId: string): Promise<RechargeOrderResponse> {
  return requestJson<RechargeOrderResponse>(`/api/v1/internal/recharge-orders/${encodeURIComponent(orderId)}`, {
    adminToken,
  });
}

export function reviewInternalRechargeOrder(adminToken: string, orderId: string, payload: {action: 'approve' | 'reject'; review_note?: string | null}): Promise<RechargeOrderReviewResponse> {
  return requestJson<RechargeOrderReviewResponse>(`/api/v1/internal/recharge-orders/${encodeURIComponent(orderId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function createInternalRechargeOrderRefund(adminToken: string, orderId: string, payload: {reason?: string | null; operator_note?: string | null}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/recharge-orders/${encodeURIComponent(orderId)}/refunds`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function reviewInternalRefund(adminToken: string, refundId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; operator_note?: string | null}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/refunds/${encodeURIComponent(refundId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function retryInternalRefund(adminToken: string, refundId: string, payload: {operator_note?: string | null} = {}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/refunds/${encodeURIComponent(refundId)}/retry`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalReviews(adminToken: string, params: Record<string, QueryValue> = {}): Promise<ReviewListResponse> {
  return requestJson<ReviewListResponse>(`/api/v1/internal/reviews${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalReview(adminToken: string, reviewId: string): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>(`/api/v1/internal/reviews/${encodeURIComponent(reviewId)}`, {
    adminToken,
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

export function getInternalRuntimeConfigSchema(adminToken: string): Promise<RuntimeConfigSchemaResponse> {
  return requestJson<RuntimeConfigSchemaResponse>('/api/v1/internal/runtime-config/schema', {
    adminToken,
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
