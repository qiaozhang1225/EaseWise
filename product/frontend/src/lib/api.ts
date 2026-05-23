import type {
  AlmanacResponse,
  Gender,
  GuestSessionResponse,
  PointsAccountResponse,
  PointsLedgerListResponse,
  PublicRuntimeConfigResponse,
  ReviewAspectUnlockResponse,
  ReviewListResponse,
  ReviewRecord,
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
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${window.location.hostname}:8000`;
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
