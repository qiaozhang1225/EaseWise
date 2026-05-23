import { computed, reactive } from 'vue';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../config/pricing';
import { EASEWISE_STORAGE_KEYS } from '../constants/storage';
import {
  ApiError,
  createGuestSession,
  createPhoneReview,
  getPublicRuntimeConfig,
  getTodayAlmanac,
  getMyPoints,
  getPhoneReviewDetail,
  listMyPointsLedger,
  listPhoneReviews,
  unlockPhoneReviewAspect,
} from '../lib/api';
import type {
  AlmanacResponse,
  Gender,
  GuestSessionResponse,
  PointsAccountResponse,
  PointsLedgerEntryResponse,
  PublicRuntimeConfigResponse,
  ReviewRecord,
  ReviewSummary,
  UserResponse,
} from '../types/api';

type AppState = {
  initialized: boolean;
  booting: boolean;
  connectionError: string | null;
  accessToken: string | null;
  guestKey: string | null;
  user: UserResponse | null;
  points: PointsAccountResponse | null;
  runtimeConfig: PublicRuntimeConfigResponse | null;
  almanac: AlmanacResponse | null;
  reviewHistory: ReviewSummary[];
  pointsLedger: PointsLedgerEntryResponse[];
  currentReview: ReviewRecord | null;
};

const state = reactive<AppState>({
  initialized: false,
  booting: false,
  connectionError: null,
  accessToken: readStorage(EASEWISE_STORAGE_KEYS.guestAccessToken),
  guestKey: readStorage(EASEWISE_STORAGE_KEYS.guestKey),
  user: null,
  points: null,
  runtimeConfig: null,
  almanac: null,
  reviewHistory: [],
  pointsLedger: [],
  currentReview: null,
});

let bootstrapPromise: Promise<void> | null = null;

const isGuestUser = computed(() => state.user?.status === 'guest');
const displayNickname = computed(() => {
  if (state.user?.nickname?.trim()) {
    return state.user.nickname.trim();
  }
  return isGuestUser.value ? '体验用户' : '易友';
});
const displayAvatarText = computed(() => displayNickname.value.slice(0, 1) || '易');
const accountLabel = computed(() => {
  if (!state.user) {
    return '本地数据连接中';
  }
  return isGuestUser.value ? '本地游客会话 · 当前设备可继续查看积分与评测记录' : '已登录用户';
});
const reviewBasePointsCost = computed(
  () => state.runtimeConfig?.modules.phone_review.base_points_cost ?? DEFAULT_BASE_REVIEW_POINTS,
);
const aspectUnlockPointsCost = computed(
  () => state.runtimeConfig?.modules.phone_review.aspect_unlock_points_cost ?? DEFAULT_ASPECT_UNLOCK_POINTS,
);
const customerServiceGuidance = computed(
  () => state.runtimeConfig?.customer_service.guidance_text || '联系客服获取充值与服务支持',
);
const customerServiceContact = computed(
  () => state.runtimeConfig?.customer_service.contact_url || 'yirufanzhang888',
);

function readStorage(key: string): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(key);
}

function writeStorage(key: string, value: string | null): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (value === null) {
    window.localStorage.removeItem(key);
    return;
  }
  window.localStorage.setItem(key, value);
}

function persistGuestSession(session: GuestSessionResponse): void {
  state.accessToken = session.access_token;
  state.guestKey = session.guest_key;
  state.user = session.user;
  state.points = session.points;
  writeStorage(EASEWISE_STORAGE_KEYS.guestAccessToken, session.access_token);
  writeStorage(EASEWISE_STORAGE_KEYS.guestKey, session.guest_key);
  writeStorage(EASEWISE_STORAGE_KEYS.points, String(session.points.balance));
}

function persistPoints(points: PointsAccountResponse | null): void {
  state.points = points;
  if (points) {
    writeStorage(EASEWISE_STORAGE_KEYS.points, String(points.balance));
  }
}

function persistCurrentReview(review: ReviewRecord | null): void {
  state.currentReview = review;
  if (review) {
    writeStorage(EASEWISE_STORAGE_KEYS.lastReviewId, review.id);
    writeStorage(
      EASEWISE_STORAGE_KEYS.lastPhoneReport,
      JSON.stringify({
        report_id: review.report_id,
        phone: review.phone_number,
        masked_phone: review.masked_phone,
        gender: review.gender,
        score: review.score,
        status: review.status,
        created_at: review.created_at,
      }),
    );
    return;
  }
  writeStorage(EASEWISE_STORAGE_KEYS.lastReviewId, null);
}

function clearConnectionError(): void {
  state.connectionError = null;
}

function setConnectionError(error: unknown): void {
  state.connectionError = humanizeError(error);
}

async function ensureGuestSession(): Promise<string> {
  try {
    const session = await createGuestSession(state.guestKey);
    persistGuestSession(session);
    clearConnectionError();
    return session.access_token;
  } catch (error) {
    if (state.guestKey) {
      state.guestKey = null;
      writeStorage(EASEWISE_STORAGE_KEYS.guestKey, null);
      const session = await createGuestSession();
      persistGuestSession(session);
      clearConnectionError();
      return session.access_token;
    }
    throw error;
  }
}

async function withAuthRetry<T>(task: (accessToken: string) => Promise<T>): Promise<T> {
  const accessToken = state.accessToken || await ensureGuestSession();
  try {
    return await task(accessToken);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      const nextToken = await ensureGuestSession();
      return task(nextToken);
    }
    throw error;
  }
}

async function refreshRuntimeConfig(): Promise<PublicRuntimeConfigResponse | null> {
  try {
    const config = await getPublicRuntimeConfig();
    state.runtimeConfig = config;
    clearConnectionError();
    return config;
  } catch (error) {
    setConnectionError(error);
    return null;
  }
}

async function refreshAlmanac(): Promise<AlmanacResponse | null> {
  try {
    const almanac = await getTodayAlmanac();
    state.almanac = almanac;
    clearConnectionError();
    return almanac;
  } catch (error) {
    setConnectionError(error);
    return null;
  }
}

async function refreshPoints(): Promise<PointsAccountResponse | null> {
  return withAuthRetry(async (accessToken) => {
    const points = await getMyPoints(accessToken);
    persistPoints(points);
    clearConnectionError();
    return points;
  });
}

async function refreshPointsLedger(limit = 20): Promise<PointsLedgerEntryResponse[]> {
  return withAuthRetry(async (accessToken) => {
    const response = await listMyPointsLedger(accessToken, limit);
    state.pointsLedger = response.items;
    clearConnectionError();
    return response.items;
  });
}

async function refreshReviewHistory(limit = 20): Promise<ReviewSummary[]> {
  return withAuthRetry(async (accessToken) => {
    const response = await listPhoneReviews(accessToken, limit);
    state.reviewHistory = response.items;
    clearConnectionError();
    return response.items;
  });
}

async function refreshCurrentReview(reviewId: string, { setAsCurrent = true }: { setAsCurrent?: boolean } = {}): Promise<ReviewRecord> {
  return withAuthRetry(async (accessToken) => {
    const review = await getPhoneReviewDetail(accessToken, reviewId);
    if (setAsCurrent) {
      persistCurrentReview(review);
    }
    clearConnectionError();
    return review;
  });
}

async function refreshAppData(): Promise<void> {
  state.booting = true;
  try {
    await ensureGuestSession();
    await Promise.allSettled([
      refreshRuntimeConfig(),
      refreshAlmanac(),
      refreshPoints(),
      refreshReviewHistory(),
      refreshPointsLedger(),
    ]);
  } finally {
    state.booting = false;
  }
}

async function bootstrapApp(): Promise<void> {
  if (bootstrapPromise) {
    return bootstrapPromise;
  }

  bootstrapPromise = (async () => {
    state.booting = true;

    const [runtimeResult, almanacResult, guestResult] = await Promise.allSettled([
      refreshRuntimeConfig(),
      refreshAlmanac(),
      ensureGuestSession(),
    ]);

    if (guestResult.status === 'fulfilled') {
      await Promise.allSettled([
        refreshPoints(),
        refreshReviewHistory(),
        refreshPointsLedger(),
      ]);

      const lastReviewId = readStorage(EASEWISE_STORAGE_KEYS.lastReviewId);
      if (lastReviewId) {
        await refreshCurrentReview(lastReviewId).catch(() => undefined);
      }
    } else if (runtimeResult.status === 'rejected') {
      setConnectionError(runtimeResult.reason);
    } else if (almanacResult.status === 'rejected') {
      setConnectionError(almanacResult.reason);
    } else {
      setConnectionError(guestResult.reason);
    }

    state.initialized = true;
    state.booting = false;
    bootstrapPromise = null;
  })();

  return bootstrapPromise;
}

async function submitPhoneReview(payload: { phone: string; gender: Gender; include_markdown?: boolean }): Promise<ReviewRecord> {
  return withAuthRetry(async (accessToken) => {
    const review = await createPhoneReview(accessToken, payload);
    persistCurrentReview(review);
    await Promise.allSettled([refreshPoints(), refreshReviewHistory(), refreshPointsLedger()]);
    clearConnectionError();
    return review;
  });
}

async function unlockAspect(reviewId: string, aspectKey: string): Promise<ReviewRecord> {
  return withAuthRetry(async (accessToken) => {
    const unlockResponse = await unlockPhoneReviewAspect(accessToken, reviewId, aspectKey);
    if (unlockResponse.points) {
      persistPoints(unlockResponse.points);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshReviewHistory()]);
    return refreshCurrentReview(reviewId);
  });
}

function humanizeError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.detail;
  }
  if (error instanceof Error && error.message.trim()) {
    return error.message.trim();
  }
  return '本地 API 暂时不可用';
}

export function useEaseWiseApp() {
  return {
    state,
    isGuestUser,
    displayNickname,
    displayAvatarText,
    accountLabel,
    reviewBasePointsCost,
    aspectUnlockPointsCost,
    customerServiceGuidance,
    customerServiceContact,
    bootstrapApp,
    refreshAppData,
    refreshRuntimeConfig,
    refreshAlmanac,
    refreshPoints,
    refreshPointsLedger,
    refreshReviewHistory,
    refreshCurrentReview,
    submitPhoneReview,
    unlockAspect,
    ensureGuestSession,
    humanizeError,
  };
}
