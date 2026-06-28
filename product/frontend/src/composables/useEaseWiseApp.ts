import { computed, reactive } from 'vue';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../config/pricing';
import { EASEWISE_STORAGE_KEYS } from '../constants/storage';
import {
  ApiError,
  createFourPillarsLuckCycleSummary,
  createFourPillarsLuckYearSummary,
  createFourPillarsReview,
  createPhoneReview,
  getCurrentUser,
  getFourPillarsReviewDetail,
  getFourPillarsLuckCycles,
  getPhoneAuthStatus,
  getPublicRuntimeConfig,
  getTodayAlmanac,
  getMyPoints,
  getPhoneReviewDetail,
  loginPhoneWithPassword,
  listFourPillarsReviews,
  listMyPointsLedger,
  listPhoneReviews,
  logoutCurrentUser,
  resolveApiAssetUrl,
  changeMyPassword,
  registerPhoneWithPassword,
  streamCreateFourPillarsReview,
  streamCreatePhoneReview,
  streamFourPillarsLuckCycleSummary,
  streamFourPillarsLuckYearSummary,
  streamFourPillarsReviewAspectUnlock,
  streamPhoneReviewAspectUnlock,
  type FourPillarsCoreStreamHandlers,
  type FourPillarsAspectStreamHandlers,
  type FourPillarsLuckStreamHandlers,
  type PhoneReviewCoreStreamHandlers,
  type PhoneReviewAspectStreamHandlers,
  uploadMyAvatar,
  updateMyProfile,
  unlockFourPillarsReviewAspect,
  unlockPhoneReviewAspect,
} from '../lib/api';
import type {
  AlmanacResponse,
  AuthLoginResponse,
  CurrentUserResponse,
  FourPillarsAspect,
  FourPillarsAspectStreamCompleteData,
  FourPillarsCoreStreamCompleteData,
  FourPillarsCreatePayload,
  FourPillarsLuckAnalysis,
  FourPillarsLuckRenderRecord,
  FourPillarsLuckStreamCompleteData,
  FourPillarsReviewRecord,
  FourPillarsReviewSummary,
  Gender,
  PhoneStatusResponse,
  PasswordChangeResponse,
  PhoneReviewAspectStreamCompleteData,
  PhoneReviewCoreStreamCompleteData,
  PointsAccountResponse,
  PointsLedgerEntryResponse,
  PublicRuntimeConfigResponse,
  ReviewAspect,
  ReviewRecord,
  ReviewSummary,
  UserResponse,
} from '../types/api';

type AppState = {
  initialized: boolean;
  booting: boolean;
  connectionError: string | null;
  accessToken: string | null;
  user: UserResponse | null;
  points: PointsAccountResponse | null;
  runtimeConfig: PublicRuntimeConfigResponse | null;
  almanac: AlmanacResponse | null;
  reviewHistory: ReviewSummary[];
  fourPillarsHistory: FourPillarsReviewSummary[];
  pointsLedger: PointsLedgerEntryResponse[];
  currentReview: ReviewRecord | null;
  currentFourPillarsReview: FourPillarsReviewRecord | null;
  authPromptVisible: boolean;
  authPromptReason: string | null;
  contactServiceModalVisible: boolean;
  contactServiceScene: CustomerServiceScene;
  contactServiceContext: string | null;
};

type CustomerServiceScene =
  | 'default'
  | 'recharge_help'
  | 'payment_issue'
  | 'points_insufficient'
  | 'account_security'
  | 'promotion_consulting'
  | 'review_support';

const CUSTOMER_SERVICE_SCENES = new Set<CustomerServiceScene>([
  'default',
  'recharge_help',
  'payment_issue',
  'points_insufficient',
  'account_security',
  'promotion_consulting',
  'review_support',
]);

const state = reactive<AppState>({
  initialized: false,
  booting: false,
  connectionError: null,
  accessToken: readStorage(EASEWISE_STORAGE_KEYS.accessToken),
  user: null,
  points: null,
  runtimeConfig: null,
  almanac: null,
  reviewHistory: [],
  fourPillarsHistory: [],
  pointsLedger: [],
  currentReview: null,
  currentFourPillarsReview: null,
  authPromptVisible: false,
  authPromptReason: null,
  contactServiceModalVisible: false,
  contactServiceScene: 'default',
  contactServiceContext: null,
});

let bootstrapPromise: Promise<void> | null = null;
let authPromptResolver: ((authenticated: boolean) => void) | null = null;

const isRegisteredUser = computed(() => Boolean(state.user && state.user.status === 'active' && state.accessToken));
const isGuestUser = computed(() => !isRegisteredUser.value);
const displayNickname = computed(() => {
  if (state.user?.nickname?.trim()) {
    return state.user.nickname.trim();
  }
  return state.user ? '易友' : '未登录用户';
});
const displayAvatarText = computed(() => displayNickname.value.slice(0, 1) || '易');
const reviewBasePointsCost = computed(
  () => state.runtimeConfig?.modules.phone_review.base_points_cost ?? DEFAULT_BASE_REVIEW_POINTS,
);
const aspectUnlockPointsCost = computed(
  () => state.runtimeConfig?.modules.phone_review.aspect_unlock_points_cost ?? DEFAULT_ASPECT_UNLOCK_POINTS,
);
const fourPillarsBasePointsCost = computed(
  () => state.runtimeConfig?.modules.four_pillars?.base_points_cost ?? DEFAULT_BASE_REVIEW_POINTS,
);
const fourPillarsAspectUnlockPointsCost = computed(
  () => state.runtimeConfig?.modules.four_pillars?.aspect_unlock_points_cost ?? DEFAULT_ASPECT_UNLOCK_POINTS,
);
const customerServiceCopy = computed(() => state.runtimeConfig?.customer_service.copy || {});
const customerServiceGuidance = computed(() => customerServiceCopyForScene('default'));
const customerServiceWechatId = computed(
  () => state.runtimeConfig?.customer_service.wechat_id || state.runtimeConfig?.customer_service.contact_url || '',
);
const customerServiceContact = computed(() => customerServiceWechatId.value || 'yirufanzhang888');
const customerServiceQrCodeUrl = computed(
  () => resolveApiAssetUrl(state.runtimeConfig?.customer_service.qr_code_url),
);
const customerServiceQrGuidanceText = computed(
  () => state.runtimeConfig?.customer_service.qr_guidance_text || '截图或长按保存二维码后，前往微信添加客服。',
);
const customerServiceCopyButtonText = computed(
  () => state.runtimeConfig?.customer_service.copy_button_text || '复制微信',
);
const customerServiceUnconfiguredText = computed(
  () => state.runtimeConfig?.customer_service.unconfigured_text || '请先在后台客服配置中填写客服微信号。',
);

function normalizeCustomerServiceScene(value: unknown): CustomerServiceScene {
  const scene = typeof value === 'string' ? value.trim() : '';
  return CUSTOMER_SERVICE_SCENES.has(scene as CustomerServiceScene) ? (scene as CustomerServiceScene) : 'default';
}

function customerServiceCopyForScene(scene: unknown = 'default'): string {
  const normalizedScene = normalizeCustomerServiceScene(scene);
  const copyMap = customerServiceCopy.value;
  return (
    copyMap[normalizedScene]?.trim()
    || copyMap.default?.trim()
    || state.runtimeConfig?.customer_service.guidance_text?.trim()
    || '请添加客服微信，客服会协助你处理相关问题。'
  );
}

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

function clearLegacyAuthStorage(): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.removeItem('easewise_guest_access_token');
  window.localStorage.removeItem('easewise_guest_key');
}

function persistAuthSession(session: AuthLoginResponse): void {
  state.accessToken = session.access_token;
  state.user = session.user;
  state.points = session.points;
  writeStorage(EASEWISE_STORAGE_KEYS.accessToken, session.access_token);
  clearLegacyAuthStorage();
  writeStorage(EASEWISE_STORAGE_KEYS.points, String(session.points.balance));
  writeStorage(EASEWISE_STORAGE_KEYS.userSnapshot, JSON.stringify(session.user));
}

function persistCurrentUserSession(session: CurrentUserResponse): void {
  state.user = session.user;
  state.points = session.points;
  writeStorage(EASEWISE_STORAGE_KEYS.points, String(session.points.balance ?? 0));
  writeStorage(EASEWISE_STORAGE_KEYS.userSnapshot, JSON.stringify(session.user));
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

function mergeUnlockedAspectIntoReview(review: ReviewRecord, aspectKey: string, aspect: ReviewAspect | null | undefined): ReviewRecord {
  if (!aspect) {
    return review;
  }
  return {
    ...review,
    aspects: review.aspects.map((item) => {
      if (item.aspect_key !== aspectKey) {
        return item;
      }
      return {
        ...item,
        ...aspect,
        aspect_key: item.aspect_key,
        short_title: aspect.short_title ?? item.short_title,
        score: aspect.score ?? item.score,
        is_unlocked: true,
        unlock_points: item.unlock_points,
        elements_check: aspect.elements_check ?? item.elements_check,
      };
    }),
  };
}

function mergeUnlockedFourPillarsAspectIntoReview(
  review: FourPillarsReviewRecord,
  aspectKey: string,
  aspect: FourPillarsAspect | null | undefined,
): FourPillarsReviewRecord {
  if (!aspect) {
    return review;
  }
  return {
    ...review,
    aspects: review.aspects.map((item) => {
      if (item.aspect_key !== aspectKey) {
        return item;
      }
      return {
        ...item,
        ...aspect,
        aspect_key: item.aspect_key,
        short_title: aspect.short_title ?? item.short_title,
        is_unlocked: true,
        unlock_points: item.unlock_points,
        elements_check: aspect.elements_check ?? item.elements_check,
      };
    }),
  };
}

function persistCurrentFourPillarsReview(review: FourPillarsReviewRecord | null): void {
  state.currentFourPillarsReview = review;
  if (review) {
    writeStorage(EASEWISE_STORAGE_KEYS.lastFourPillarsReviewId, review.id);
    writeStorage(
      EASEWISE_STORAGE_KEYS.lastFourPillarsReport,
      JSON.stringify({
        report_id: review.report_id,
        gender: review.gender,
        birth_date: review.birth_date,
        birth_time: review.birth_time,
        timezone: review.timezone,
        status: review.status,
        created_at: review.created_at,
      }),
    );
    return;
  }
  writeStorage(EASEWISE_STORAGE_KEYS.lastFourPillarsReviewId, null);
}

function clearConnectionError(): void {
  state.connectionError = null;
}

function setConnectionError(error: unknown): void {
  state.connectionError = humanizeError(error);
}

function clearAuthPromptResolution(authenticated: boolean): void {
  if (authPromptResolver) {
    authPromptResolver(authenticated);
    authPromptResolver = null;
  }
}

function openAuthPrompt(reason: string | null = null): Promise<boolean> {
  state.authPromptVisible = true;
  state.authPromptReason = reason;
  return new Promise<boolean>((resolve) => {
    clearAuthPromptResolution(false);
    authPromptResolver = resolve;
  });
}

function closeAuthPrompt(authenticated: boolean): void {
  state.authPromptVisible = false;
  state.authPromptReason = null;
  clearAuthPromptResolution(authenticated);
}

function resetAuthState(): void {
  state.accessToken = null;
  state.user = null;
  state.points = null;
  state.reviewHistory = [];
  state.fourPillarsHistory = [];
  state.pointsLedger = [];
  state.currentReview = null;
  state.currentFourPillarsReview = null;
  writeStorage(EASEWISE_STORAGE_KEYS.accessToken, null);
  clearLegacyAuthStorage();
  writeStorage(EASEWISE_STORAGE_KEYS.points, null);
  writeStorage(EASEWISE_STORAGE_KEYS.userSnapshot, null);
}

async function withAuthRetry<T>(task: (accessToken: string) => Promise<T>): Promise<T> {
  if (!isRegisteredUser.value || !state.accessToken) {
    throw new ApiError(403, 'registered_user_required', null);
  }
  const accessToken = state.accessToken;
  try {
    return await task(accessToken);
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      resetAuthState();
    }
    throw error;
  }
}

async function refreshCurrentUser(): Promise<CurrentUserResponse | null> {
  if (!state.accessToken) {
    state.user = null;
    state.points = null;
    return null;
  }
  try {
    const session = await getCurrentUser(state.accessToken);
    persistCurrentUserSession(session);
    clearConnectionError();
    return session;
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      resetAuthState();
      return null;
    }
    setConnectionError(error);
    return null;
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
  if (!isRegisteredUser.value || !state.accessToken) {
    persistPoints(null);
    return null;
  }
  return withAuthRetry(async (accessToken) => {
    const points = await getMyPoints(accessToken);
    persistPoints(points);
    clearConnectionError();
    return points;
  });
}

async function refreshPointsLedger(limit = 20): Promise<PointsLedgerEntryResponse[]> {
  if (!isRegisteredUser.value || !state.accessToken) {
    state.pointsLedger = [];
    return [];
  }
  return withAuthRetry(async (accessToken) => {
    const response = await listMyPointsLedger(accessToken, limit);
    state.pointsLedger = response.items;
    clearConnectionError();
    return response.items;
  });
}

async function refreshReviewHistory(limit = 20): Promise<ReviewSummary[]> {
  if (!isRegisteredUser.value || !state.accessToken) {
    state.reviewHistory = [];
    return [];
  }
  return withAuthRetry(async (accessToken) => {
    const response = await listPhoneReviews(accessToken, limit);
    state.reviewHistory = response.items;
    clearConnectionError();
    return response.items;
  });
}

async function refreshFourPillarsHistory(limit = 20): Promise<FourPillarsReviewSummary[]> {
  if (!isRegisteredUser.value || !state.accessToken) {
    state.fourPillarsHistory = [];
    return [];
  }
  return withAuthRetry(async (accessToken) => {
    const response = await listFourPillarsReviews(accessToken, limit);
    state.fourPillarsHistory = response.items;
    clearConnectionError();
    return response.items;
  });
}

async function refreshCurrentReview(reviewId: string, { setAsCurrent = true }: { setAsCurrent?: boolean } = {}): Promise<ReviewRecord> {
  if (!isRegisteredUser.value || !state.accessToken) {
    throw new ApiError(403, 'registered_user_required', null);
  }
  return withAuthRetry(async (accessToken) => {
    const review = await getPhoneReviewDetail(accessToken, reviewId);
    if (setAsCurrent) {
      persistCurrentReview(review);
    }
    clearConnectionError();
    return review;
  });
}

async function refreshCurrentFourPillarsReview(reviewId: string, { setAsCurrent = true }: { setAsCurrent?: boolean } = {}): Promise<FourPillarsReviewRecord> {
  if (!isRegisteredUser.value || !state.accessToken) {
    throw new ApiError(403, 'registered_user_required', null);
  }
  return withAuthRetry(async (accessToken) => {
    const review = await getFourPillarsReviewDetail(accessToken, reviewId);
    if (setAsCurrent) {
      persistCurrentFourPillarsReview(review);
    }
    clearConnectionError();
    return review;
  });
}

async function refreshUserScopedData(): Promise<void> {
  if (!isRegisteredUser.value || !state.accessToken) {
    state.pointsLedger = [];
    state.reviewHistory = [];
    state.fourPillarsHistory = [];
    state.currentReview = null;
    state.currentFourPillarsReview = null;
    return;
  }
  await Promise.allSettled([
    refreshPoints(),
    refreshReviewHistory(),
    refreshFourPillarsHistory(),
    refreshPointsLedger(),
  ]);

  const lastReviewId = readStorage(EASEWISE_STORAGE_KEYS.lastReviewId);
  if (lastReviewId) {
    await refreshCurrentReview(lastReviewId).catch(() => undefined);
  }
  const lastFourPillarsReviewId = readStorage(EASEWISE_STORAGE_KEYS.lastFourPillarsReviewId);
  if (lastFourPillarsReviewId) {
    await refreshCurrentFourPillarsReview(lastFourPillarsReviewId).catch(() => undefined);
  }
}

async function refreshAppData(): Promise<void> {
  state.booting = true;
  try {
    if (state.accessToken) {
      await refreshCurrentUser();
    } else {
      resetAuthState();
    }
    await Promise.allSettled([
      refreshRuntimeConfig(),
      refreshAlmanac(),
    ]);
    await refreshUserScopedData();
  } finally {
    state.booting = false;
  }
}

async function bootstrapApp(): Promise<void> {
  if (state.initialized) {
    return;
  }

  if (bootstrapPromise) {
    return bootstrapPromise;
  }

  bootstrapPromise = (async () => {
    state.booting = true;

    try {
      const [runtimeResult, almanacResult] = await Promise.allSettled([
        refreshRuntimeConfig(),
        refreshAlmanac(),
      ]);

      if (state.accessToken) {
        await refreshCurrentUser();
      } else {
        resetAuthState();
      }

      await refreshUserScopedData();

      if (runtimeResult.status === 'rejected') {
        setConnectionError(runtimeResult.reason);
      } else if (almanacResult.status === 'rejected') {
        setConnectionError(almanacResult.reason);
      }
    } catch (error) {
      setConnectionError(error);
    } finally {
      state.initialized = true;
      state.booting = false;
      bootstrapPromise = null;
    }
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

async function submitPhoneReviewStream(
  payload: { phone: string; gender: Gender; include_markdown?: boolean },
  handlers: PhoneReviewCoreStreamHandlers = {},
): Promise<PhoneReviewCoreStreamCompleteData> {
  return withAuthRetry(async (accessToken) => {
    const result = await streamCreatePhoneReview(accessToken, payload, {
      ...handlers,
      onCreated: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        if (data.review) {
          persistCurrentReview(data.review);
        }
        handlers.onCreated?.(data);
      },
      onFactsReady: (data) => {
        if (data.review) {
          persistCurrentReview(data.review);
        }
        handlers.onFactsReady?.(data);
      },
      onComplete: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        if (data.review) {
          persistCurrentReview(data.review);
        }
        handlers.onComplete?.(data);
      },
    });
    if (result.points) {
      persistPoints(result.points);
    }
    if (result.review) {
      persistCurrentReview(result.review);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshReviewHistory()]);
    clearConnectionError();
    return result;
  });
}

async function submitFourPillarsReview(payload: FourPillarsCreatePayload): Promise<FourPillarsReviewRecord> {
  return withAuthRetry(async (accessToken) => {
    const review = await createFourPillarsReview(accessToken, payload);
    persistCurrentFourPillarsReview(review);
    await Promise.allSettled([refreshPoints(), refreshFourPillarsHistory(), refreshPointsLedger()]);
    clearConnectionError();
    return review;
  });
}

async function submitFourPillarsReviewStream(
  payload: FourPillarsCreatePayload,
  handlers: FourPillarsCoreStreamHandlers = {},
): Promise<FourPillarsCoreStreamCompleteData> {
  return withAuthRetry(async (accessToken) => {
    const result = await streamCreateFourPillarsReview(accessToken, payload, {
      ...handlers,
      onCreated: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        if (data.review) {
          persistCurrentFourPillarsReview(data.review);
        }
        handlers.onCreated?.(data);
      },
      onFactsReady: (data) => {
        if (data.review) {
          persistCurrentFourPillarsReview(data.review);
        }
        handlers.onFactsReady?.(data);
      },
      onComplete: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        if (data.review) {
          persistCurrentFourPillarsReview(data.review);
        }
        handlers.onComplete?.(data);
      },
    });
    if (result.points) {
      persistPoints(result.points);
    }
    if (result.review) {
      persistCurrentFourPillarsReview(result.review);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshFourPillarsHistory()]);
    clearConnectionError();
    return result;
  });
}

async function unlockAspect(reviewId: string, aspectKey: string): Promise<ReviewRecord> {
  return withAuthRetry(async (accessToken) => {
    const unlockResponse = await unlockPhoneReviewAspect(accessToken, reviewId, aspectKey);
    if (unlockResponse.points) {
      persistPoints(unlockResponse.points);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshReviewHistory()]);
    const review = await refreshCurrentReview(reviewId);
    return review;
  });
}

async function streamUnlockAspect(
  reviewId: string,
  aspectKey: string,
  handlers: PhoneReviewAspectStreamHandlers = {},
): Promise<PhoneReviewAspectStreamCompleteData> {
  return withAuthRetry(async (accessToken) => {
    const result = await streamPhoneReviewAspectUnlock(accessToken, reviewId, aspectKey, {
      ...handlers,
      onUnlock: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        handlers.onUnlock?.(data);
      },
      onComplete: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        const completedData = data.review
          ? { ...data, review: mergeUnlockedAspectIntoReview(data.review, aspectKey, data.aspect) }
          : data;
        if (completedData.review) {
          persistCurrentReview(completedData.review);
        }
        handlers.onComplete?.(completedData);
      },
    });
    const completedResult = result.review
      ? { ...result, review: mergeUnlockedAspectIntoReview(result.review, aspectKey, result.aspect) }
      : result;
    if (result.points) {
      persistPoints(result.points);
    }
    if (completedResult.review) {
      persistCurrentReview(completedResult.review);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshReviewHistory()]);
    clearConnectionError();
    return completedResult;
  });
}

async function unlockFourPillarsAspect(reviewId: string, aspectKey: string): Promise<FourPillarsReviewRecord> {
  return withAuthRetry(async (accessToken) => {
    const unlockResponse = await unlockFourPillarsReviewAspect(accessToken, reviewId, aspectKey);
    if (unlockResponse.points) {
      persistPoints(unlockResponse.points);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshFourPillarsHistory()]);
    const review = await refreshCurrentFourPillarsReview(reviewId);
    return review;
  });
}

async function streamUnlockFourPillarsAspect(
  reviewId: string,
  aspectKey: string,
  handlers: FourPillarsAspectStreamHandlers = {},
): Promise<FourPillarsAspectStreamCompleteData> {
  return withAuthRetry(async (accessToken) => {
    const result = await streamFourPillarsReviewAspectUnlock(accessToken, reviewId, aspectKey, {
      ...handlers,
      onUnlock: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        handlers.onUnlock?.(data);
      },
      onComplete: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        const completedData = data.review
          ? { ...data, review: mergeUnlockedFourPillarsAspectIntoReview(data.review, aspectKey, data.aspect) }
          : data;
        if (completedData.review) {
          persistCurrentFourPillarsReview(completedData.review);
        }
        handlers.onComplete?.(completedData);
      },
    });
    const completedResult = result.review
      ? { ...result, review: mergeUnlockedFourPillarsAspectIntoReview(result.review, aspectKey, result.aspect) }
      : result;
    if (result.points) {
      persistPoints(result.points);
    }
    if (completedResult.review) {
      persistCurrentFourPillarsReview(completedResult.review);
    }
    await Promise.allSettled([refreshPointsLedger(), refreshFourPillarsHistory()]);
    clearConnectionError();
    return completedResult;
  });
}

async function refreshFourPillarsLuckAnalysis(reviewId: string): Promise<FourPillarsLuckAnalysis> {
  return withAuthRetry(async (accessToken) => {
    const response = await getFourPillarsLuckCycles(accessToken, reviewId);
    if (state.currentFourPillarsReview?.id === reviewId) {
      state.currentFourPillarsReview = {
        ...state.currentFourPillarsReview,
        luck_analysis: response.luck_analysis,
      };
      persistCurrentFourPillarsReview(state.currentFourPillarsReview);
    }
    clearConnectionError();
    return response.luck_analysis;
  });
}

async function generateFourPillarsLuckCycle(reviewId: string, cycleKey: string): Promise<FourPillarsLuckRenderRecord> {
  return withAuthRetry(async (accessToken) => {
    const render = await createFourPillarsLuckCycleSummary(accessToken, reviewId, cycleKey);
    await Promise.allSettled([refreshPoints(), refreshPointsLedger(), refreshFourPillarsLuckAnalysis(reviewId)]);
    clearConnectionError();
    return render;
  });
}

async function generateFourPillarsLuckYear(reviewId: string, cycleKey: string, year: number): Promise<FourPillarsLuckRenderRecord> {
  return withAuthRetry(async (accessToken) => {
    const render = await createFourPillarsLuckYearSummary(accessToken, reviewId, cycleKey, year);
    await Promise.allSettled([refreshPoints(), refreshPointsLedger(), refreshFourPillarsLuckAnalysis(reviewId)]);
    clearConnectionError();
    return render;
  });
}

function persistFourPillarsLuckAnalysis(reviewId: string, luckAnalysis: FourPillarsLuckAnalysis): void {
  if (state.currentFourPillarsReview?.id !== reviewId) {
    return;
  }
  persistCurrentFourPillarsReview({
    ...state.currentFourPillarsReview,
    luck_analysis: luckAnalysis,
  });
}

async function streamGenerateFourPillarsLuckCycle(
  reviewId: string,
  cycleKey: string,
  handlers: FourPillarsLuckStreamHandlers = {},
): Promise<FourPillarsLuckStreamCompleteData> {
  return withAuthRetry(async (accessToken) => {
    const result = await streamFourPillarsLuckCycleSummary(accessToken, reviewId, cycleKey, {
      ...handlers,
      onRender: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        handlers.onRender?.(data);
      },
      onComplete: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        persistFourPillarsLuckAnalysis(reviewId, data.luck_analysis);
        handlers.onComplete?.(data);
      },
    });
    if (result.points) {
      persistPoints(result.points);
    }
    persistFourPillarsLuckAnalysis(reviewId, result.luck_analysis);
    await Promise.allSettled([refreshPointsLedger(), refreshFourPillarsHistory()]);
    clearConnectionError();
    return result;
  });
}

async function streamGenerateFourPillarsLuckYear(
  reviewId: string,
  cycleKey: string,
  year: number,
  handlers: FourPillarsLuckStreamHandlers = {},
): Promise<FourPillarsLuckStreamCompleteData> {
  return withAuthRetry(async (accessToken) => {
    const result = await streamFourPillarsLuckYearSummary(accessToken, reviewId, cycleKey, year, {
      ...handlers,
      onRender: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        handlers.onRender?.(data);
      },
      onComplete: (data) => {
        if (data.points) {
          persistPoints(data.points);
        }
        persistFourPillarsLuckAnalysis(reviewId, data.luck_analysis);
        handlers.onComplete?.(data);
      },
    });
    if (result.points) {
      persistPoints(result.points);
    }
    persistFourPillarsLuckAnalysis(reviewId, result.luck_analysis);
    await Promise.allSettled([refreshPointsLedger(), refreshFourPillarsHistory()]);
    clearConnectionError();
    return result;
  });
}

async function requestRegisteredUser(reason = 'default'): Promise<boolean> {
  if (!state.initialized) {
    await bootstrapApp().catch(() => undefined);
  }
  if (isRegisteredUser.value) {
    return true;
  }
  return openAuthPrompt(reason);
}

function cancelAuthRequest(): void {
  closeAuthPrompt(false);
}

async function checkPhoneAuthStatus(phone: string): Promise<PhoneStatusResponse> {
  return getPhoneAuthStatus({ phone });
}

async function acceptAuthSession(session: AuthLoginResponse): Promise<AuthLoginResponse> {
  persistAuthSession(session);
  clearConnectionError();
  await refreshUserScopedData();
  closeAuthPrompt(true);
  return session;
}

async function registerWithPhonePassword(phone: string, password: string, confirmPassword: string): Promise<AuthLoginResponse> {
  const session = await registerPhoneWithPassword({
    phone,
    password,
    confirm_password: confirmPassword,
  });
  return acceptAuthSession(session);
}

async function loginWithPhonePassword(phone: string, password: string): Promise<AuthLoginResponse> {
  const session = await loginPhoneWithPassword({
    phone,
    password,
  });
  return acceptAuthSession(session);
}

async function logout(): Promise<void> {
  const accessToken = state.accessToken;
  if (accessToken) {
    await logoutCurrentUser(accessToken).catch(() => undefined);
  }
  resetAuthState();
  await Promise.allSettled([
    refreshRuntimeConfig(),
    refreshAlmanac(),
  ]);
}

async function updateProfile(payload: { nickname?: string | null; avatar_url?: string | null }): Promise<UserResponse> {
  if (!isRegisteredUser.value || !state.accessToken) {
    throw new ApiError(403, 'registered_user_required', null);
  }
  const accessToken = state.accessToken;
  const user = await updateMyProfile(accessToken, payload);
  state.user = user;
  writeStorage(EASEWISE_STORAGE_KEYS.userSnapshot, JSON.stringify(user));
  const refreshed = await refreshCurrentUser().catch(() => null);
  if (refreshed) {
    return refreshed.user;
  }
  return user;
}

async function uploadAvatar(imageDataUrl: string): Promise<UserResponse> {
  if (!isRegisteredUser.value || !state.accessToken) {
    throw new ApiError(403, 'registered_user_required', null);
  }
  const accessToken = state.accessToken;
  const user = await uploadMyAvatar(accessToken, { image_data_url: imageDataUrl });
  state.user = user;
  writeStorage(EASEWISE_STORAGE_KEYS.userSnapshot, JSON.stringify(user));
  const refreshed = await refreshCurrentUser().catch(() => null);
  if (refreshed) {
    return refreshed.user;
  }
  return user;
}

async function changePassword(currentPassword: string, newPassword: string, confirmPassword: string): Promise<PasswordChangeResponse> {
  if (!isRegisteredUser.value || !state.accessToken) {
    throw new ApiError(403, 'registered_user_required', null);
  }
  return changeMyPassword(state.accessToken, {
    current_password: currentPassword,
    new_password: newPassword,
    confirm_password: confirmPassword,
  });
}

function openCustomerServiceModal(sceneOrReason?: unknown, context?: unknown): void {
  const normalizedScene = normalizeCustomerServiceScene(sceneOrReason);
  const trimmedText = typeof sceneOrReason === 'string' ? sceneOrReason.trim() : '';
  state.contactServiceScene = normalizedScene;
  state.contactServiceContext = normalizedScene === 'default' && trimmedText && !CUSTOMER_SERVICE_SCENES.has(trimmedText as CustomerServiceScene)
    ? trimmedText
    : (typeof context === 'string' ? context.trim() || null : null);
  state.contactServiceModalVisible = true;
}

function closeCustomerServiceModal(): void {
  state.contactServiceModalVisible = false;
  state.contactServiceScene = 'default';
  state.contactServiceContext = null;
}

function humanizeError(error: unknown): string {
  if (error instanceof ApiError) {
    const payloadMessage = error.payload && typeof error.payload === 'object' && 'message' in error.payload
      ? String((error.payload as { message?: unknown }).message || '').trim()
      : '';
    if (error.detail === 'llm_insufficient_balance' && payloadMessage) {
      return payloadMessage;
    }
    const messageMap: Record<string, string> = {
      invalid_phone_number: '请输入正确的中国大陆手机号码。',
      phone_already_registered: '该手机号已经注册，请直接登录。',
      phone_not_registered: '该手机号尚未注册。',
      password_too_weak: '密码强度不足，请使用 8-32 位且至少包含两类字符。',
      password_confirm_mismatch: '两次输入的密码不一致。',
      invalid_phone_or_password: '手机号或密码不正确。',
      invalid_current_password: '当前密码不正确，请重新输入。',
      phone_password_identity_not_found: '当前账号尚未绑定手机号密码，暂不支持修改密码。',
      new_password_same_as_old: '新密码不能与当前密码相同。',
      password_update_failed: '密码修改失败，请稍后重试。',
      registered_user_required: '请先登录或注册后再继续。',
      account_disabled: '账号已被禁用，请联系管理员处理。',
      insufficient_points: '当前积分不足，请充值后继续。',
      module_disabled: '当前功能暂未开放。',
      invalid_birth_datetime: '请输入有效的出生日期和出生时间。',
      invalid_timezone: '请输入有效的时区。',
      review_not_ready_for_unlock: '专项内容还在准备中，请稍后刷新后再试。',
      aspect_not_ready: '专项内容还在生成中，请稍后再试。',
      aspect_generation_failed: '专项内容生成失败，积分已按规则退回，请稍后重试。',
      llm_insufficient_balance: 'AI 服务额度不足，本次积分已退回，请联系管理员处理后再试。',
      aspect_generation_in_progress: '该专项正在生成中，请稍后再试。',
      aspect_generation_incomplete: '专项内容生成未完成，请稍后重试。',
      session_not_found: '当前登录态已失效，请重新登录。',
      claim_link_not_found: '领取链接不存在，请确认链接是否完整。',
      claim_link_expired: '领取链接已过期。',
      claim_link_disabled: '领取链接已停用。',
      claim_link_not_started: '领取链接尚未生效。',
      already_claimed_this_week: '本周已领取过免费积分',
      points_claim_duration_too_long: '领取链接有效期最多可配置 30 天。',
      expires_at_must_be_after_now: '过期时间必须晚于当前时间。',
      expires_at_must_be_after_valid_from: '过期时间必须晚于生效时间。',
    };
    return messageMap[error.detail] || error.detail;
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
    isRegisteredUser,
    displayNickname,
    displayAvatarText,
    reviewBasePointsCost,
    aspectUnlockPointsCost,
    fourPillarsBasePointsCost,
    fourPillarsAspectUnlockPointsCost,
    customerServiceGuidance,
    customerServiceContact,
    customerServiceWechatId,
    customerServiceQrCodeUrl,
    customerServiceQrGuidanceText,
    customerServiceCopyButtonText,
    customerServiceUnconfiguredText,
    customerServiceCopyForScene,
    bootstrapApp,
    refreshAppData,
    refreshRuntimeConfig,
    refreshAlmanac,
    refreshCurrentUser,
    refreshPoints,
    refreshPointsLedger,
    refreshReviewHistory,
    refreshFourPillarsHistory,
    refreshCurrentReview,
    refreshCurrentFourPillarsReview,
    refreshFourPillarsLuckAnalysis,
    submitPhoneReview,
    submitPhoneReviewStream,
    submitFourPillarsReview,
    submitFourPillarsReviewStream,
    unlockAspect,
    streamUnlockAspect,
    unlockFourPillarsAspect,
    streamUnlockFourPillarsAspect,
    generateFourPillarsLuckCycle,
    generateFourPillarsLuckYear,
    streamGenerateFourPillarsLuckCycle,
    streamGenerateFourPillarsLuckYear,
    requestRegisteredUser,
    cancelAuthRequest,
    checkPhoneAuthStatus,
    registerWithPhonePassword,
    loginWithPhonePassword,
    logout,
    updateProfile,
    uploadAvatar,
    changePassword,
    openCustomerServiceModal,
    closeCustomerServiceModal,
    humanizeError,
  };
}
