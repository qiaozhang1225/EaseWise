import type {
  AlmanacResponse,
  AvatarUploadRequest,
  AuthLoginResponse,
  CurrentUserResponse,
  DashboardResponse,
  FourPillarsCoreStreamCompleteData,
  FourPillarsCoreStreamCreatedData,
  FourPillarsCoreStreamDeltaData,
  FourPillarsCoreStreamErrorData,
  FourPillarsCoreStreamFactsReadyData,
  FourPillarsCoreStreamSectionCompleteData,
  FourPillarsCoreStreamStatusData,
  FourPillarsAspectStreamCompleteData,
  FourPillarsAspectStreamDeltaData,
  FourPillarsAspectStreamErrorData,
  FourPillarsAspectStreamStatusData,
  FourPillarsAspectStreamUnlockData,
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
  PhoneReviewCoreStreamCompleteData,
  PhoneReviewCoreStreamCreatedData,
  PhoneReviewCoreStreamDeltaData,
  PhoneReviewCoreStreamErrorData,
  PhoneReviewCoreStreamFactsReadyData,
  PhoneReviewCoreStreamSectionCompleteData,
  PhoneReviewCoreStreamStatusData,
  PhoneReviewAspectStreamCompleteData,
  PhoneReviewAspectStreamDeltaData,
  PhoneReviewAspectStreamErrorData,
  PhoneReviewAspectStreamStatusData,
  PhoneReviewAspectStreamUnlockData,
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

export type PhoneReviewAspectStreamHandlers = {
  signal?: AbortSignal;
  onUnlock?: (data: PhoneReviewAspectStreamUnlockData) => void;
  onStatus?: (data: PhoneReviewAspectStreamStatusData) => void;
  onDelta?: (data: PhoneReviewAspectStreamDeltaData) => void;
  onComplete?: (data: PhoneReviewAspectStreamCompleteData) => void;
  onError?: (data: PhoneReviewAspectStreamErrorData) => void;
};

export type PhoneReviewCoreStreamHandlers = {
  signal?: AbortSignal;
  onCreated?: (data: PhoneReviewCoreStreamCreatedData) => void;
  onFactsReady?: (data: PhoneReviewCoreStreamFactsReadyData) => void;
  onCoreStatus?: (data: PhoneReviewCoreStreamStatusData) => void;
  onCoreDelta?: (data: PhoneReviewCoreStreamDeltaData) => void;
  onSectionComplete?: (data: PhoneReviewCoreStreamSectionCompleteData) => void;
  onComplete?: (data: PhoneReviewCoreStreamCompleteData) => void;
  onError?: (data: PhoneReviewCoreStreamErrorData) => void;
};

export type FourPillarsAspectStreamHandlers = {
  signal?: AbortSignal;
  onUnlock?: (data: FourPillarsAspectStreamUnlockData) => void;
  onStatus?: (data: FourPillarsAspectStreamStatusData) => void;
  onDelta?: (data: FourPillarsAspectStreamDeltaData) => void;
  onComplete?: (data: FourPillarsAspectStreamCompleteData) => void;
  onError?: (data: FourPillarsAspectStreamErrorData) => void;
};

export type FourPillarsCoreStreamHandlers = {
  signal?: AbortSignal;
  onCreated?: (data: FourPillarsCoreStreamCreatedData) => void;
  onFactsReady?: (data: FourPillarsCoreStreamFactsReadyData) => void;
  onCoreStatus?: (data: FourPillarsCoreStreamStatusData) => void;
  onCoreDelta?: (data: FourPillarsCoreStreamDeltaData) => void;
  onSectionComplete?: (data: FourPillarsCoreStreamSectionCompleteData) => void;
  onComplete?: (data: FourPillarsCoreStreamCompleteData) => void;
  onError?: (data: FourPillarsCoreStreamErrorData) => void;
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

  const controller = new AbortController();
  const { signal } = controller;

  let timer: any = null;
  const timeoutPromise = new Promise<never>((_, reject) => {
    timer = setTimeout(() => {
      controller.abort();
      reject(new ApiError(408, 'request_timeout', null));
    }, 8000);
  });

  if (options.signal) {
    if (options.signal.aborted) {
      clearTimeout(timer);
      throw options.signal.reason || new Error('Aborted');
    }
    options.signal.addEventListener('abort', () => {
      controller.abort();
    });
  }

  try {
    const fetchPromise = fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      signal,
    }).then(async (response) => {
      const rawText = await response.text();
      const payload = rawText ? tryParseJson(rawText) : null;

      if (!response.ok) {
        const detail = resolveApiErrorDetail(payload, response.statusText);
        throw new ApiError(response.status, detail, payload);
      }

      return payload as T;
    });

    const result = await Promise.race([fetchPromise, timeoutPromise]);
    return result;
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error.name === 'AbortError') {
      throw new ApiError(408, 'request_timeout', null);
    }
    throw error;
  } finally {
    if (timer) {
      clearTimeout(timer);
    }
  }
}

type SseRequestOptions = {
  method?: string;
  body?: unknown;
  accessToken?: string | null;
  signal?: AbortSignal;
  onEvent: (eventName: string, payload: unknown) => void;
};

async function streamSse(path: string, options: SseRequestOptions): Promise<void> {
  const headers = new Headers();
  headers.set('Accept', 'text/event-stream');
  headers.set('X-Client-Platform', 'h5');
  headers.set('X-Client-Channel', 'h5');
  headers.set('X-Client-Version', 'easewise-local-frontend');
  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json');
  }
  if (options.accessToken) {
    headers.set('Authorization', `Bearer ${options.accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || 'GET',
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  if (!response.ok) {
    const rawText = await response.text();
    const payload = rawText ? tryParseJson(rawText) : null;
    throw new ApiError(response.status, resolveApiErrorDetail(payload, response.statusText), payload);
  }
  if (!response.body) {
    throw new ApiError(500, 'stream_body_missing', null);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  const processBlock = (block: string) => {
    const lines = block.split(/\r?\n/);
    let eventName = 'message';
    const dataLines: string[] = [];
    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim();
        continue;
      }
      if (line.startsWith('data:')) {
        dataLines.push(line.slice(5).trimStart());
      }
    }
    if (!dataLines.length) {
      return;
    }
    options.onEvent(eventName, tryParseJson(dataLines.join('\n')));
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    let separatorIndex = buffer.search(/\r?\n\r?\n/);
    while (separatorIndex >= 0) {
      const block = buffer.slice(0, separatorIndex);
      const separatorLength = buffer[separatorIndex] === '\r' ? 4 : 2;
      buffer = buffer.slice(separatorIndex + separatorLength);
      processBlock(block);
      separatorIndex = buffer.search(/\r?\n\r?\n/);
    }
  }

  buffer += decoder.decode();
  if (buffer.trim()) {
    processBlock(buffer.trim());
  }
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
  const configuredValue = String(import.meta.env.VITE_API_BASE_URL || '').trim();
  const normalized = configuredValue.replace(/\/+$/, '');

  if (!normalized || normalized === '/api') {
    return '';
  }

  return normalized;
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

export function getMockSummary(): Promise<any> {
  return requestJson<any>('/api/v1/mock/summary');
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

export function getTodayAlmanacInfo(): Promise<AlmanacResponse> {
  return requestJson<AlmanacResponse>('/api/v1/almanac/today');
}

export function getPhoneReviewList(accessToken: string): Promise<ReviewListResponse> {
  return requestJson<ReviewListResponse>('/api/v1/phone-review', {
    accessToken,
  });
}

export function getFourPillarsReviewList(accessToken: string): Promise<FourPillarsReviewListResponse> {
  return requestJson<FourPillarsReviewListResponse>('/api/v1/four-pillars-review', {
    accessToken,
  });
}

export function getFourPillarsReview(accessToken: string, id: string): Promise<FourPillarsReviewRecord> {
  return requestJson<FourPillarsReviewRecord>(`/api/v1/four-pillars-review/${id}`, {
    accessToken,
  });
}

export function getPhoneReview(accessToken: string, id: string): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>(`/api/v1/phone-review/${id}`, {
    accessToken,
  });
}

export function startPhoneReviewAspectUnlock(accessToken: string, reviewId: string, aspectKey: string): Promise<ReviewAspectUnlockResponse> {
  return requestJson<ReviewAspectUnlockResponse>(`/api/v1/phone-review/${reviewId}/unlock/${aspectKey}`, {
    method: 'POST',
    accessToken,
  });
}

export function startFourPillarsReviewAspectUnlock(accessToken: string, reviewId: string, aspectKey: string): Promise<FourPillarsAspectUnlockResponse> {
  return requestJson<FourPillarsAspectUnlockResponse>(`/api/v1/four-pillars-review/${reviewId}/unlock/${aspectKey}`, {
    method: 'POST',
    accessToken,
  });
}

export function generateFourPillarsLuckCycle(accessToken: string, reviewId: string, cycleKey: string): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars-review/${reviewId}/luck-cycle/${cycleKey}/render`, {
    method: 'POST',
    accessToken,
  });
}

export function generateFourPillarsLuckYear(accessToken: string, reviewId: string, year: number): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars-review/${reviewId}/luck-year/${year}/render`, {
    method: 'POST',
    accessToken,
  });
}

export function getFourPillarsLuckCycleList(accessToken: string, reviewId: string): Promise<FourPillarsLuckCycleListResponse> {
  return requestJson<FourPillarsLuckCycleListResponse>(`/api/v1/four-pillars-review/${reviewId}/luck-cycles`, {
    accessToken,
  });
}

export function getFourPillarsHistory(accessToken: string): Promise<FourPillarsReviewListResponse> {
  return requestJson<FourPillarsReviewListResponse>('/api/v1/four-pillars-review', {
    accessToken,
  });
}

export function createVoiceNarration(accessToken: string, payload: any): Promise<any> {
  return requestJson<any>('/api/v1/voice/narrations', {
    method: 'POST',
    accessToken,
    body: payload,
  });
}

export function callAgentChat(message: string, history?: { role: string; content: string }[]): Promise<{ reply: string }> {
  return requestJson<{ reply: string }>('/api/v1/agent/chat', {
    method: 'POST',
    body: { message, history },
  });
}

export async function submitPhoneReviewStream(
  accessToken: string | null,
  payload: { phone: string; gender: Gender; include_markdown?: boolean },
  handlers: PhoneReviewCoreStreamHandlers,
): Promise<void> {
  await streamSse('/api/v1/phone-review/stream', {
    method: 'POST',
    body: payload,
    accessToken,
    signal: handlers.signal,
    onEvent: (eventName, data) => {
      if (eventName === 'created' && handlers.onCreated) {
        handlers.onCreated(data as PhoneReviewCoreStreamCreatedData);
      } else if (eventName === 'facts_ready' && handlers.onFactsReady) {
        handlers.onFactsReady(data as PhoneReviewCoreStreamFactsReadyData);
      } else if (eventName === 'core_status' && handlers.onCoreStatus) {
        handlers.onCoreStatus(data as PhoneReviewCoreStreamStatusData);
      } else if (eventName === 'core_delta' && handlers.onCoreDelta) {
        handlers.onCoreDelta(data as PhoneReviewCoreStreamDeltaData);
      } else if (eventName === 'section_complete' && handlers.onSectionComplete) {
        handlers.onSectionComplete(data as PhoneReviewCoreStreamSectionCompleteData);
      } else if (eventName === 'complete' && handlers.onComplete) {
        handlers.onComplete(data as PhoneReviewCoreStreamCompleteData);
      } else if (eventName === 'error' && handlers.onError) {
        handlers.onError(data as PhoneReviewCoreStreamErrorData);
      }
    },
  });
}

export async function submitFourPillarsReviewStream(
  accessToken: string | null,
  payload: FourPillarsCreatePayload,
  handlers: FourPillarsCoreStreamHandlers,
): Promise<void> {
  await streamSse('/api/v1/four-pillars-review/stream', {
    method: 'POST',
    body: payload,
    accessToken,
    signal: handlers.signal,
    onEvent: (eventName, data) => {
      if (eventName === 'created' && handlers.onCreated) {
        handlers.onCreated(data as FourPillarsCoreStreamCreatedData);
      } else if (eventName === 'facts_ready' && handlers.onFactsReady) {
        handlers.onFactsReady(data as FourPillarsCoreStreamFactsReadyData);
      } else if (eventName === 'core_status' && handlers.onCoreStatus) {
        handlers.onCoreStatus(data as FourPillarsCoreStreamStatusData);
      } else if (eventName === 'core_delta' && handlers.onCoreDelta) {
        handlers.onCoreDelta(data as FourPillarsCoreStreamDeltaData);
      } else if (eventName === 'section_complete' && handlers.onSectionComplete) {
        handlers.onSectionComplete(data as FourPillarsCoreStreamSectionCompleteData);
      } else if (eventName === 'complete' && handlers.onComplete) {
        handlers.onComplete(data as FourPillarsCoreStreamCompleteData);
      } else if (eventName === 'error' && handlers.onError) {
        handlers.onError(data as FourPillarsCoreStreamErrorData);
      }
    },
  });
}

export async function streamUnlockAspect(
  accessToken: string | null,
  reviewId: string,
  aspectKey: string,
  handlers: PhoneReviewAspectStreamHandlers,
): Promise<PhoneReviewAspectStreamCompleteData> {
  let completePayload: PhoneReviewAspectStreamCompleteData | null = null;
  await streamSse(`/api/v1/phone-review/${encodeURIComponent(reviewId)}/aspect-unlocks/${encodeURIComponent(aspectKey)}/stream`, {
    method: 'POST',
    accessToken,
    signal: handlers.signal,
    onEvent: (eventName, data) => {
      if (eventName === 'unlock' && handlers.onUnlock) {
        handlers.onUnlock(data as PhoneReviewAspectStreamUnlockData);
      } else if (eventName === 'status' && handlers.onStatus) {
        handlers.onStatus(data as PhoneReviewAspectStreamStatusData);
      } else if (eventName === 'delta' && handlers.onDelta) {
        handlers.onDelta(data as PhoneReviewAspectStreamDeltaData);
      } else if (eventName === 'complete') {
        completePayload = data as PhoneReviewAspectStreamCompleteData;
        handlers.onComplete?.(completePayload);
      } else if (eventName === 'error' && handlers.onError) {
        const errorPayload = data as PhoneReviewAspectStreamErrorData;
        handlers.onError(errorPayload);
        const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
        throw new ApiError(status, errorPayload.detail || 'aspect_unlock_failed', errorPayload);
      }
    },
  });
  if (!completePayload) {
    throw new ApiError(409, 'aspect_unlock_incomplete', null);
  }
  return completePayload;
}

export async function streamUnlockFourPillarsAspect(
  accessToken: string | null,
  reviewId: string,
  aspectKey: string,
  handlers: FourPillarsAspectStreamHandlers,
): Promise<FourPillarsAspectStreamCompleteData> {
  let completePayload: FourPillarsAspectStreamCompleteData | null = null;
  await streamSse(`/api/v1/four-pillars-review/${encodeURIComponent(reviewId)}/aspect-unlocks/${encodeURIComponent(aspectKey)}/stream`, {
    method: 'POST',
    accessToken,
    signal: handlers.signal,
    onEvent: (eventName, data) => {
      if (eventName === 'unlock' && handlers.onUnlock) {
        handlers.onUnlock(data as FourPillarsAspectStreamUnlockData);
      } else if (eventName === 'status' && handlers.onStatus) {
        handlers.onStatus(data as FourPillarsAspectStreamStatusData);
      } else if (eventName === 'delta' && handlers.onDelta) {
        handlers.onDelta(data as FourPillarsAspectStreamDeltaData);
      } else if (eventName === 'complete') {
        completePayload = data as FourPillarsAspectStreamCompleteData;
        handlers.onComplete?.(completePayload);
      } else if (eventName === 'error' && handlers.onError) {
        const errorPayload = data as FourPillarsAspectStreamErrorData;
        handlers.onError(errorPayload);
        const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
        throw new ApiError(status, errorPayload.detail || 'aspect_unlock_failed', errorPayload);
      }
    },
  });
  if (!completePayload) {
    throw new ApiError(409, 'aspect_unlock_incomplete', null);
  }
  return completePayload;
}

export function listFourPillarsBirthLocations(): Promise<{ locations: any[]; default_location_id: string }> {
  return requestJson<{ locations: any[]; default_location_id: string }>('/api/v1/four-pillars-review/locations');
}

export function resolveFourPillarsInput(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  return requestJson<Record<string, unknown>>('/api/v1/four-pillars-review/input-resolve', {
    method: 'POST',
    body: payload,
  });
}
