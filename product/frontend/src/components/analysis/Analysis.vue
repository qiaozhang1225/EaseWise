<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch, type Component } from 'vue';
import {
  Shield,
  TrendingUp,
  Heart,
  HeartPulse,
  BookOpen,
  Users,
  Compass,
  ArrowLeft,
  Star,
  Clock,
  Check,
  Copy,
  AlertCircle,
  Sparkles,
  Lightbulb,
  CheckCircle2,
  MessageSquare,
  Plus,
  Lock,
  Download,
} from 'lucide-vue-next';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../../config/pricing';
import { EASEWISE_STORAGE_KEYS } from '../../constants/storage';
import { ApiError } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { Gender, ReviewAspect, ReviewProgressStage, ReviewRecord } from '../../types/api';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string): void;
}>();

type AppViewState = 'input' | 'waiting' | 'result' | 'error_state';
type ErrorType =
  | 'none'
  | 'phone_format'
  | 'insufficient_points'
  | 'unlock_points_insufficient'
  | 'request_failed'
  | 'review_timeout'
  | 'review_failed';

type DisplayAspect = ReviewAspect & {
  icon: Component;
  tint: string;
  textTint: string;
};

type BoardSinglePalaceDisplay = {
  palace: string;
  palaceName: string;
  palaceShort: string;
  direction: string;
  deity: string;
  star: string;
  door: string;
  heavenStem: string;
  earthStem: string;
  trigger: string;
  wuxing: string | null;
};

type BoardRelationCard = {
  label: string;
  labelTop: string;
  labelBottom: string;
  value: string;
  valueClass: string;
};

type BoardHarmBadge = {
  label: string;
  value: string;
  compactValue: string;
  toneClass: string;
};

const {
  state,
  bootstrapApp,
  submitPhoneReview,
  refreshCurrentReview,
  unlockAspect,
  reviewBasePointsCost,
  aspectUnlockPointsCost,
  customerServiceContact,
  customerServiceGuidance,
  humanizeError,
} = useEaseWiseApp();

const appState = ref<AppViewState>('input');
const phoneNumber = ref('');
const gender = ref<Gender>('male');
const activeAspect = ref(-1);
const errorType = ref<ErrorType>('none');
const errorDetail = ref('');
const toast = ref<string | null>(null);
const copied = ref(false);
const exportingImage = ref(false);
const currentProgressStage = ref<ReviewProgressStage | null>(null);
const currentProgressMessage = ref('');
const waitingVisualPhase = ref(0);
const waitingPoemIndex = ref(0);
const waitingProgressValue = ref(0);
const pendingCompletedReview = ref<ReviewRecord | null>(null);
const pendingCompletedReviewShouldToast = ref(false);
const showReviewConfirmDialog = ref(false);
const aspectSectionRef = ref<HTMLElement | null>(null);
const skipReviewConfirmHint = ref(true);
const skipFutureReviewConfirm = ref(
  readStoredFlag(EASEWISE_STORAGE_KEYS.reviewConfirmSkipPrompt, EASEWISE_STORAGE_KEYS.legacyReviewConfirmSkipPrompt),
);
const pollingReviewId = ref<string | null>(null);
const unlockingAspectKey = ref<string | null>(null);
const unlockWaitingAspectKey = ref<string | null>(null);
const unlockWaitingAttempt = ref(0);
let disposed = false;
let pollingPromise: Promise<ReviewRecord> | null = null;
let lastCompletedReviewId: string | null = null;
let waitingVisualTimers: ReturnType<typeof setTimeout>[] = [];
let waitingPoemTimer: ReturnType<typeof setInterval> | null = null;
let waitingProgressTimer: ReturnType<typeof setInterval> | null = null;
let waitingStartedAt = 0;

const ASPECT_UNLOCK_RETRY_LIMIT = 45;
const ASPECT_UNLOCK_RETRY_DELAY_MS = 2000;
const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const REVIEW_TIMEOUT_MESSAGE = '评测时间比预期更长，请稍后在“我的”页面查看结果。';
const WAITING_PHASE_DURATION_MS = 4000;
const WAITING_POEM_INTERVAL_MS = 2000;
const WAITING_PROGRESS_START_PERCENT = 6;
const WAITING_PROGRESS_HOLD_PERCENT = 96;

const waitingSteps = [
  {
    title: '基础盘面生成中',
    desc: '智能体正在完成基础评分和盘面定位',
  },
  {
    title: '宫门关系识别中',
    desc: '智能体正在梳理宫位、九星八门与天地关系',
  },
  {
    title: '风险结构扫描中',
    desc: '智能体正在检查四害、特殊组合和结构封顶',
  },
  {
    title: '综合评分评价中',
    desc: '智能体正在根据奇门遁甲规则综合评价',
  },
  {
    title: '总评建议生成中',
    desc: '智能体正在通过大模型生成总评和长期使用建议',
  },
  {
    title: '专项内容预热中',
    desc: '智能体正在准备十二项专题评测',
  },
];

const waitingPoemLines = [
  '轩辕黄帝战蚩尤',
  '逐鹿经年苦未休',
  '偶梦天神授符诀',
  '登坛致祭谨虔修',
  '因命风后演成文',
  '遁甲奇门从此始',
];

const WAITING_FINAL_PHASE_INDEX = waitingSteps.length - 1;
const WAITING_LINEAR_PROGRESS_MS = WAITING_PHASE_DURATION_MS * WAITING_FINAL_PHASE_INDEX;

const aspectUiMap: Record<string, { icon: Component; tint: string; textTint: string }> = {
  career: { icon: Shield, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  wealth: { icon: TrendingUp, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  love: { icon: Heart, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  health: { icon: HeartPulse, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  acad: { icon: BookOpen, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  fortune: { icon: Star, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  investment: { icon: TrendingUp, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  travel: { icon: Compass, tint: 'bg-red-50 text-red-600', textTint: 'text-red-600' },
  social: { icon: Users, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  family: { icon: Heart, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  personality: { icon: Sparkles, tint: 'bg-brand-paper text-brand-secondary', textTint: 'text-brand-secondary' },
  fengshui: { icon: Compass, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
};

const currentReview = computed(() => state.currentReview);
const userPoints = computed(() => state.points?.balance ?? 0);
const effectiveBaseReviewPoints = computed(() => reviewBasePointsCost.value ?? DEFAULT_BASE_REVIEW_POINTS);
const effectiveAspectUnlockPoints = computed(
  () => currentReview.value?.aspect_unlock_points ?? aspectUnlockPointsCost.value ?? DEFAULT_ASPECT_UNLOCK_POINTS,
);
const waitingPhase = computed(() => waitingVisualPhase.value);
const waitingProgressMessage = computed(() => currentProgressMessage.value || waitingSteps[waitingPhase.value]?.desc || '正在准备本次评测内容，请稍候。');
const waitingMessage = computed(
  () => {
    const step = waitingSteps[waitingPhase.value];
    if (waitingPhase.value < WAITING_FINAL_PHASE_INDEX) {
      return step?.desc || '正在准备本次评测内容，请稍候。';
    }
    return waitingProgressMessage.value || step?.desc || '正在准备本次评测内容，请稍候。';
  },
);
const waitingPoemLine = computed(() => waitingPoemLines[waitingPoemIndex.value] || waitingPoemLines[0]);
const waitingProgressPercent = computed(() => waitingProgressValue.value);
const waitingProgressPercentText = computed(() => Math.round(waitingProgressPercent.value));
const activeBoardGridCell = computed(() => {
  const board = currentReview.value?.board;
  return board?.grid_cells.find((cell) => cell.is_active) ?? null;
});
const reviewAspects = computed<DisplayAspect[]>(() =>
  (currentReview.value?.aspects ?? []).map((aspect) => ({
    ...aspect,
    ...(aspectUiMap[aspect.aspect_key] || {
      icon: Sparkles,
      tint: 'bg-brand-paper text-brand-secondary',
      textTint: 'text-brand-secondary',
    }),
  })),
);
const selectedAspect = computed(() => reviewAspects.value[activeAspect.value] || null);
const selectedAspectUnlockPending = computed(() => selectedAspect.value ? isAspectUnlockPending(selectedAspect.value) : false);
const selectedAspectWaitingForGeneration = computed(
  () => Boolean(selectedAspect.value && unlockWaitingAspectKey.value === selectedAspect.value.aspect_key),
);
const unlockWaitingAspect = computed(() =>
  reviewAspects.value.find((aspect) => aspect.aspect_key === unlockWaitingAspectKey.value) || null,
);
const unlockWaitingAspectTitle = computed(
  () => unlockWaitingAspect.value?.short_title || unlockWaitingAspect.value?.title || selectedAspect.value?.short_title || selectedAspect.value?.title || '专项内容',
);
const unlockProcessingTitle = computed(
  () => selectedAspect.value?.short_title || selectedAspect.value?.title || unlockWaitingAspectTitle.value,
);
const unlockWaitingMessage = computed(() => {
  if (!selectedAspectWaitingForGeneration.value) {
    return '正在读取已经预热的专项结果，完成后会立即展示。';
  }
  if (unlockWaitingAttempt.value <= 1) {
    return '这部分内容正在后台整理，完成后会自动解锁展示。';
  }
  return `专项内容仍在生成中，系统正在自动等待第 ${unlockWaitingAttempt.value} 次确认。`;
});
const unlockProcessingHeading = computed(
  () => selectedAspectWaitingForGeneration.value ? `正在生成「${unlockWaitingAspectTitle.value}」` : `正在解锁「${unlockProcessingTitle.value}」`,
);
const reviewPhoneDisplay = computed(() => currentReview.value?.phone_number || phoneNumber.value);
const reviewGenderDisplay = computed(() => (currentReview.value?.gender || gender.value) === 'male' ? '男' : '女');
const reviewScore = computed(() => currentReview.value?.score ?? 0);
const phoneSummary = computed(() => currentReview.value?.phone_summary ?? null);
const stabilityDetail = computed(() => currentReview.value?.stability_detail ?? null);
const phoneSummaryTitle = computed(() => cleanDisplayText(phoneSummary.value?.title) || '系统会根据盘面结果生成总评。');
const phoneSummaryRisk = computed(() => cleanDisplayText(phoneSummary.value?.risk) || '系统会根据盘面结果生成风险提醒。');
const phoneSummaryUsageGuidance = computed(
  () => cleanDisplayText(phoneSummary.value?.usage_guidance) || '系统会根据盘面结果生成使用建议。',
);
const stabilityLabel = computed(
  () => cleanDisplayText(stabilityDetail.value?.verdict) || resolveFallbackStabilityLabel(),
);
const stabilityValue = computed(
  () => cleanDisplayText(stabilityDetail.value?.content) || '系统会根据盘面结果生成长期使用建议。',
);
const singlePalaceData = computed<BoardSinglePalaceDisplay>(() => {
  const board = currentReview.value?.board;
  const activeBasis = board?.active_basis;
  const activeCell = activeBoardGridCell.value;
  const palace = activeBasis?.palace || activeCell?.palace_key || '待';
  return {
    palace,
    palaceName: activeCell?.palace_name || (palace ? `${palace}宫` : '待生成'),
    palaceShort: palace.slice(0, 1) || '宫',
    direction: activeBasis?.direction || activeCell?.direction || '待生成',
    deity: activeBasis?.god || '待生成',
    star: activeBasis?.star || '待生成',
    door: activeBasis?.door || '待生成',
    heavenStem: activeBasis?.heaven_stem || '-',
    earthStem: activeBasis?.earth_stem || '-',
    trigger: board?.center_basis?.trigger || '待',
    wuxing: activeCell?.wuxing || null,
  };
});
const boardRelationCards = computed<BoardRelationCard[]>(() => {
  const relations = currentReview.value?.board?.relations;
  return [
    {
      label: '宫门关系',
      labelTop: '宫门',
      labelBottom: '关系',
      value: relations?.palace_door_relation || '待生成',
      valueClass: (relations?.palace_door_relation || '').includes('克') ? 'text-red-600' : 'text-brand-ink-strong',
    },
    {
      label: '天地关系',
      labelTop: '天地',
      labelBottom: '关系',
      value: compactStemRelationValue(relations?.stem_pair_relation || '待生成'),
      valueClass: (relations?.stem_pair_relation || '').includes('克') ? 'text-amber-700' : 'text-brand-gold-fixed',
    },
  ];
});
const boardHarmBadges = computed<BoardHarmBadge[]>(() => {
  const harms = currentReview.value?.board?.risks?.four_harms;
  return [
    { label: '空亡', value: harms?.emptiness || '待生成' },
    { label: '门迫', value: harms?.door_pressure || '待生成' },
    { label: '入墓', value: harms?.tomb || '待生成' },
    { label: '击刑', value: harms?.punishment_hit || '待生成' },
  ].map((item) => ({
    ...item,
    compactValue: compactHarmValue(item.value),
    toneClass: resolveHarmToneClass(item.value),
  }));
});
const boardPatternFlags = computed(() => currentReview.value?.board?.risks?.pattern_flags ?? []);
const boardStructuralCaps = computed(() => currentReview.value?.board?.risks?.structural_cap_reasons ?? []);
const boardSpecialCombos = computed(() => {
  if (boardPatternFlags.value.length) {
    return boardPatternFlags.value;
  }
  const riskPairs = currentReview.value?.board?.risks?.risk_pairs ?? [];
  return riskPairs.map((pair) => `${pair} 风险数字对`);
});
const boardStructureCapText = computed(() => {
  if (boardStructuralCaps.value.length) {
    return boardStructuralCaps.value.join('；');
  }
  return '当前未见明显结构封顶限制';
});
const boardStructureCapTags = computed(() => {
  if (boardStructuralCaps.value.length) {
    return boardStructuralCaps.value;
  }
  return [boardStructureCapText.value];
});
const prefetchedAspectCount = computed(() =>
  reviewAspects.value.filter((aspect) => Boolean(aspect.content && aspect.risk)).length,
);

function cleanDisplayText(value: string | null | undefined): string {
  const text = String(value || '').trim();
  if (!text || ['title', 'risk', 'usage guidance'].includes(text.toLowerCase())) {
    return '';
  }
  return text;
}

function resolveFallbackStabilityLabel(): string {
  const score = reviewScore.value;
  if (score >= 82) {
    return '适合长期使用';
  }
  if (score >= 68) {
    return '可以继续使用';
  }
  return '谨慎长期主用';
}

function showToast(message: string): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, 2200);
}

function isAspectUnlockPending(aspect: DisplayAspect): boolean {
  return unlockingAspectKey.value === aspect.aspect_key || unlockWaitingAspectKey.value === aspect.aspect_key;
}

function resolveScoreBadgeClass(score: number | null | undefined, active: boolean): string {
  const numericScore = Number(score ?? 0);
  if (active) {
    if (numericScore < 60) {
      return 'bg-white text-red-600 border-white/10';
    }
    if (numericScore < 80) {
      return 'bg-white text-amber-500 border-white/10';
    }
    return 'bg-white text-emerald-600 border-white/10';
  }

  if (numericScore < 60) {
    return 'text-red-500 bg-red-50 border-red-200/40';
  }
  if (numericScore < 80) {
    return 'text-amber-500 bg-amber-50 border-amber-200/40';
  }
  return 'text-emerald-600 bg-emerald-50 border-emerald-200/40';
}

function isAspectNotReadyError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 409 && error.detail === 'aspect_not_ready';
}

function isAspectUnlockTimeoutError(error: unknown): boolean {
  return error instanceof Error && error.message === 'aspect_unlock_timeout';
}

function isAspectUnlockCancelledError(error: unknown): boolean {
  return error instanceof Error && error.message === 'aspect_unlock_cancelled';
}

function resolveHarmToneClass(value: string): string {
  if (!value || value === '待生成') {
    return 'bg-slate-50 text-slate-600 border-slate-100';
  }
  if (/^无/.test(value.trim())) {
    return 'bg-green-50 text-green-600 border-green-100';
  }
  return 'bg-red-50 text-red-600 border-red-100';
}

function compactHarmValue(value: string): string {
  if (!value || value === '待生成') {
    return '待定';
  }

  const text = value.replace(/\s+/g, '');
  if (text === '无' || text.startsWith('无')) {
    return '无';
  }

  const scopeMatch = text.match(/[（(]([^）)]+)[）)]/);
  if (scopeMatch?.[1]) {
    return `有·${scopeMatch[1]}`;
  }

  if (text.includes('有')) {
    return '有';
  }

  return text.length > 4 ? text.slice(0, 4) : text;
}

function compactStemRelationValue(value: string): string {
  const mapping: Record<string, string> = {
    天干生地干: '天生地',
    地干生天干: '地生天',
    天干克地干: '天克地',
    地干克天干: '地克天',
  };

  return mapping[value] || value;
}

function isStoredFlagEnabled(value: string | null): boolean {
  return value === 'true' || value === '1';
}

function readStoredFlag(key: string, legacyKey?: string): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  const currentValue = window.localStorage.getItem(key);
  if (currentValue !== null) {
    return isStoredFlagEnabled(currentValue);
  }

  if (!legacyKey) {
    return false;
  }

  const legacyValue = window.localStorage.getItem(legacyKey);
  if (!isStoredFlagEnabled(legacyValue)) {
    return false;
  }

  window.localStorage.setItem(key, 'true');
  window.localStorage.removeItem(legacyKey);
  return true;
}

function writeStoredFlag(key: string, enabled: boolean, legacyKey?: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (legacyKey) {
    window.localStorage.removeItem(legacyKey);
  }
  if (enabled) {
    window.localStorage.setItem(key, 'true');
    return;
  }
  window.localStorage.removeItem(key);
}

function sanitizePhone(value: string): string {
  return value.replace(/\D+/g, '').slice(0, 11);
}

function closeReviewConfirmDialog(): void {
  showReviewConfirmDialog.value = false;
}

function validatePhoneBeforeReview(): string | null {
  const cleanPhone = sanitizePhone(phoneNumber.value);
  phoneNumber.value = cleanPhone;
  if (cleanPhone.length !== 11) {
    setError('phone_format');
    return null;
  }
  return cleanPhone;
}

function setError(nextType: ErrorType, detail = ''): void {
  errorType.value = nextType;
  errorDetail.value = detail;
  appState.value = 'error_state';
}

function resetToInput(): void {
  closeReviewConfirmDialog();
  appState.value = 'input';
  errorType.value = 'none';
  errorDetail.value = '';
  currentProgressStage.value = null;
  currentProgressMessage.value = '';
  waitingVisualPhase.value = 0;
  waitingPoemIndex.value = 0;
  waitingProgressValue.value = 0;
  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  clearWaitingTimers();
  clearUnlockState();
}

function clearUnlockState(): void {
  unlockingAspectKey.value = null;
  unlockWaitingAspectKey.value = null;
  unlockWaitingAttempt.value = 0;
}

function resolveDefaultAspectIndex(aspects: DisplayAspect[]): number {
  return aspects.length ? 0 : -1;
}

function isWaitingFinalPhaseReady(): boolean {
  return waitingVisualPhase.value >= WAITING_FINAL_PHASE_INDEX;
}

function clearWaitingVisualTimers(): void {
  waitingVisualTimers.forEach((timer) => window.clearTimeout(timer));
  waitingVisualTimers = [];
}

function clearWaitingTimers(): void {
  clearWaitingVisualTimers();
  if (waitingPoemTimer) {
    window.clearInterval(waitingPoemTimer);
    waitingPoemTimer = null;
  }
  if (waitingProgressTimer) {
    window.clearInterval(waitingProgressTimer);
    waitingProgressTimer = null;
  }
}

function updateWaitingProgress(): void {
  if (!waitingStartedAt) {
    waitingProgressValue.value = WAITING_PROGRESS_START_PERCENT;
    return;
  }

  const elapsed = Date.now() - waitingStartedAt;
  const ratio = Math.min(1, Math.max(0, elapsed / WAITING_LINEAR_PROGRESS_MS));
  const progress =
    WAITING_PROGRESS_START_PERCENT +
    (WAITING_PROGRESS_HOLD_PERCENT - WAITING_PROGRESS_START_PERCENT) * ratio;
  waitingProgressValue.value = Math.min(WAITING_PROGRESS_HOLD_PERCENT, Number(progress.toFixed(1)));
}

function applyOrDeferCompletedReviewState(review: ReviewRecord, options: { showToastOnComplete?: boolean } = {}): void {
  if (appState.value === 'waiting' && !isWaitingFinalPhaseReady()) {
    pendingCompletedReview.value = review;
    pendingCompletedReviewShouldToast.value = pendingCompletedReviewShouldToast.value || Boolean(options.showToastOnComplete);
    currentProgressStage.value = review.progress_stage;
    currentProgressMessage.value = review.progress_message || '';
    return;
  }

  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  applyCompletedReviewState(review, options);
}

function applyCompletedReviewState(review: ReviewRecord, options: { showToastOnComplete?: boolean } = {}): void {
  clearWaitingTimers();
  phoneNumber.value = sanitizePhone(review.phone_number || review.phone || '');
  gender.value = review.gender;
  currentProgressStage.value = review.progress_stage;
  currentProgressMessage.value = review.progress_message || '';
  errorType.value = 'none';
  errorDetail.value = '';
  closeReviewConfirmDialog();
  appState.value = 'result';
  const aspects = reviewAspects.value;
  const shouldPreserveActiveAspect =
    lastCompletedReviewId === review.id &&
    activeAspect.value >= 0 &&
    activeAspect.value < aspects.length;

  activeAspect.value = shouldPreserveActiveAspect
    ? activeAspect.value
    : resolveDefaultAspectIndex(aspects);
  lastCompletedReviewId = review.id;

  if (options.showToastOnComplete) {
    showToast('评测完成，可查看整体结果与专项分析。');
  }
}

function persistCompletedReviewState(review: ReviewRecord): void {
  applyCompletedReviewState(review);
}

function applyProcessingReviewState(review: ReviewRecord): void {
  phoneNumber.value = sanitizePhone(review.phone_number || review.phone || '');
  gender.value = review.gender;
  currentProgressStage.value = review.progress_stage;
  currentProgressMessage.value = review.progress_message || '评测任务已创建，等待开始';
  errorType.value = 'none';
  errorDetail.value = '';
  closeReviewConfirmDialog();
  appState.value = 'waiting';
}

function applyFailedReviewState(review: ReviewRecord): void {
  phoneNumber.value = sanitizePhone(review.phone_number || review.phone || '');
  gender.value = review.gender;
  closeReviewConfirmDialog();
  setError('review_failed', review.error_message || review.progress_message || '评测生成失败');
}

function handleReviewSyncError(error: unknown): void {
  if (error instanceof ApiError) {
    if (error.status === 402) {
      setError('insufficient_points');
      return;
    }
    if (error.status === 422 && (error.detail === 'phone_must_be_11_digits' || error.detail === 'phone')) {
      setError('phone_format');
      return;
    }
  }

  const message = humanizeError(error);
  if (message.includes('评测时间比预期更长')) {
    setError('review_timeout', message);
    return;
  }
  if (message.includes('评测任务生成失败') || message.includes('review')) {
    setError('review_failed', message);
    return;
  }
  setError('request_failed', message);
}

function startReviewPolling(review: ReviewRecord): Promise<ReviewRecord> {
  if (pollingReviewId.value === review.id && pollingPromise) {
    return pollingPromise;
  }

  pollingReviewId.value = review.id;
  pollingPromise = pollReviewUntilReady(review).finally(() => {
    if (pollingReviewId.value === review.id) {
      pollingReviewId.value = null;
    }
    pollingPromise = null;
  });

  return pollingPromise;
}

function syncViewFromCurrentReview(review: ReviewRecord | null): void {
  if (!review) {
    return;
  }

  if (review.status === 'completed') {
    applyOrDeferCompletedReviewState(review);
    return;
  }

  if (review.status === 'failed') {
    applyFailedReviewState(review);
    return;
  }

  applyProcessingReviewState(review);

  if (pollingReviewId.value === review.id) {
    return;
  }

  void startReviewPolling(review)
    .then((completedReview) => {
      if (disposed) {
        return;
      }

      if (completedReview.status === 'completed') {
        applyOrDeferCompletedReviewState(completedReview);
        return;
      }

      if (completedReview.status === 'failed') {
        applyFailedReviewState(completedReview);
      }
    })
    .catch((error) => {
      if (disposed) {
        return;
      }
      handleReviewSyncError(error);
    });
}

watch(
  reviewAspects,
  (aspects) => {
    if (!aspects.length) {
      activeAspect.value = -1;
      return;
    }
    if (activeAspect.value < 0 || activeAspect.value >= aspects.length) {
      activeAspect.value = resolveDefaultAspectIndex(aspects);
    }
  },
  { immediate: true },
);

watch(
  currentReview,
  (review) => {
    syncViewFromCurrentReview(review);
  },
  { immediate: true },
);

watch(
  waitingVisualPhase,
  () => {
    if (!isWaitingFinalPhaseReady() || !pendingCompletedReview.value) {
      return;
    }
    const review = pendingCompletedReview.value;
    const shouldToast = pendingCompletedReviewShouldToast.value;
    pendingCompletedReview.value = null;
    pendingCompletedReviewShouldToast.value = false;
    applyCompletedReviewState(review, { showToastOnComplete: shouldToast });
  },
);

onMounted(() => {
  void bootstrapApp();
});

onUnmounted(() => {
  disposed = true;
  clearUnlockState();
  clearWaitingTimers();
});

async function pollReviewUntilReady(review: ReviewRecord): Promise<ReviewRecord> {
  let latestReview = review;

  for (let attempt = 0; attempt < REVIEW_READY_RETRY_LIMIT; attempt += 1) {
    if (disposed) {
      return latestReview;
    }

    currentProgressStage.value = latestReview.progress_stage;
    currentProgressMessage.value = latestReview.progress_message || '';

    if (latestReview.status === 'completed') {
      return latestReview;
    }

    if (latestReview.status === 'failed') {
      throw new Error(latestReview.error_message || latestReview.progress_message || '评测任务生成失败');
    }

    await sleep(REVIEW_READY_RETRY_DELAY_MS);
    latestReview = await refreshCurrentReview(latestReview.id);
  }

  throw new Error(REVIEW_TIMEOUT_MESSAGE);
}

async function handleReviewSubmitIntent(): Promise<void> {
  if (state.booting) {
    return;
  }

  const cleanPhone = validatePhoneBeforeReview();
  if (!cleanPhone) {
    return;
  }

  const shouldSkipConfirm = readStoredFlag(
    EASEWISE_STORAGE_KEYS.reviewConfirmSkipPrompt,
    EASEWISE_STORAGE_KEYS.legacyReviewConfirmSkipPrompt,
  );
  skipFutureReviewConfirm.value = shouldSkipConfirm;

  if (shouldSkipConfirm) {
    await handleEvaluate(cleanPhone);
    return;
  }

  skipReviewConfirmHint.value = true;
  showReviewConfirmDialog.value = true;
}

async function handleConfirmReview(): Promise<void> {
  const cleanPhone = validatePhoneBeforeReview();
  if (!cleanPhone) {
    closeReviewConfirmDialog();
    return;
  }

  skipFutureReviewConfirm.value = skipReviewConfirmHint.value;
  writeStoredFlag(
    EASEWISE_STORAGE_KEYS.reviewConfirmSkipPrompt,
    skipReviewConfirmHint.value,
    EASEWISE_STORAGE_KEYS.legacyReviewConfirmSkipPrompt,
  );
  closeReviewConfirmDialog();
  await handleEvaluate(cleanPhone);
}

async function handleEvaluate(preparedPhone?: string): Promise<void> {
  const cleanPhone = preparedPhone ?? validatePhoneBeforeReview();
  if (!cleanPhone) {
    return;
  }
  const selectedGender = gender.value;

  errorType.value = 'none';
  errorDetail.value = '';
  clearUnlockState();
  clearWaitingTimers();
  currentProgressStage.value = 'queued';
  currentProgressMessage.value = '评测任务已创建，等待开始';
  waitingVisualPhase.value = 0;
  waitingPoemIndex.value = 0;
  waitingProgressValue.value = WAITING_PROGRESS_START_PERCENT;
  waitingStartedAt = Date.now();
  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  appState.value = 'waiting';
  waitingVisualTimers = waitingSteps.slice(1).map((_, index) => window.setTimeout(() => {
    if (!disposed && appState.value === 'waiting') {
      waitingVisualPhase.value = index + 1;
    }
  }, WAITING_PHASE_DURATION_MS * (index + 1)));
  waitingPoemTimer = window.setInterval(() => {
    if (!disposed && appState.value === 'waiting') {
      waitingPoemIndex.value = (waitingPoemIndex.value + 1) % waitingPoemLines.length;
    }
  }, WAITING_POEM_INTERVAL_MS);
  waitingProgressTimer = window.setInterval(() => {
    if (!disposed && appState.value === 'waiting') {
      updateWaitingProgress();
    }
  }, 100);

  try {
    await bootstrapApp();
    const review = await submitPhoneReview({
      phone: cleanPhone,
      gender: selectedGender,
      include_markdown: true,
    });
    const completedReview = await startReviewPolling(review);

    if (disposed) {
      return;
    }

    applyOrDeferCompletedReviewState(completedReview, { showToastOnComplete: true });
  } catch (error) {
    handleReviewSyncError(error);
  } finally {
    if (!pendingCompletedReview.value || isWaitingFinalPhaseReady()) {
      clearWaitingTimers();
    }
  }
}

async function handleUnlockAspect(index: number): Promise<void> {
  const aspect = reviewAspects.value[index];
  const review = currentReview.value;

  if (!aspect || !review) {
    return;
  }

  activeAspect.value = index;

  if (aspect.is_unlocked) {
    return;
  }

  try {
    await tryUnlockAspectWithWait(review.id, aspect.aspect_key, aspect.title);
  } catch (error) {
    if (isAspectUnlockCancelledError(error)) {
      return;
    }
    if (isAspectUnlockTimeoutError(error)) {
      showToast('专项内容还在生成中，请稍后再试。');
      return;
    }
    if (error instanceof ApiError && error.status === 402) {
      setError('unlock_points_insufficient');
      return;
    }
    setError('request_failed', humanizeError(error));
  } finally {
    if (unlockingAspectKey.value === aspect.aspect_key) {
      unlockingAspectKey.value = null;
    }
  }
}

async function tryUnlockAspectWithWait(reviewId: string, aspectKey: string, title: string): Promise<void> {
  unlockingAspectKey.value = aspectKey;
  unlockWaitingAspectKey.value = null;
  unlockWaitingAttempt.value = 0;

  try {
    const refreshedReview = await unlockAspect(reviewId, aspectKey);
    persistCompletedReviewState(refreshedReview);
    clearUnlockState();
    showToast(`已解锁「${title}」详细分析。`);
    return;
  } catch (error) {
    if (!isAspectNotReadyError(error)) {
      throw error;
    }
  }

  unlockWaitingAspectKey.value = aspectKey;
  unlockingAspectKey.value = null;
  currentProgressStage.value = 'rendering';
  currentProgressMessage.value = `「${title}」正在后台生成中，马上就好。`;

  for (let attempt = 1; attempt <= ASPECT_UNLOCK_RETRY_LIMIT; attempt += 1) {
    if (disposed || currentReview.value?.id !== reviewId) {
      throw new Error('aspect_unlock_cancelled');
    }

    unlockWaitingAttempt.value = attempt;
    const latestReview = await refreshCurrentReview(reviewId);
    persistCompletedReviewState(latestReview);
    const latestAspect = latestReview.aspects.find((item) => item.aspect_key === aspectKey);
    if (latestAspect?.is_unlocked && latestAspect.content && latestAspect.risk) {
      clearUnlockState();
      showToast(`已解锁「${title}」详细分析。`);
      return;
    }

    try {
      const refreshedReview = await unlockAspect(reviewId, aspectKey);
      persistCompletedReviewState(refreshedReview);
      const unlockedAspect = refreshedReview.aspects.find((item) => item.aspect_key === aspectKey);
      if (unlockedAspect?.is_unlocked) {
        clearUnlockState();
        showToast(`已解锁「${title}」详细分析。`);
        return;
      }
    } catch (error) {
      if (!isAspectNotReadyError(error)) {
        throw error;
      }
    }

    await sleep(ASPECT_UNLOCK_RETRY_DELAY_MS);
  }

  clearUnlockState();
  throw new Error('aspect_unlock_timeout');
}

async function handleCopyServiceContact(): Promise<void> {
  try {
    await navigator.clipboard.writeText(customerServiceContact.value);
    copied.value = true;
    showToast('已复制客服联系方式。');
    window.setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch {
    showToast('复制失败，请手动记录客服联系方式。');
  }
}

function handleSelectNextLockedAspect(): void {
  const nextLockedIndex = reviewAspects.value.findIndex((aspect) => !aspect.is_unlocked);
  if (nextLockedIndex === -1) {
    showToast('当前十二个专项均已预生成。');
    void scrollToAspectSection();
    return;
  }
  activeAspect.value = nextLockedIndex;
  void scrollToAspectSection();
}

function resolveHeaderOffset(): number {
  return 14;
}

function resolveScrollBehavior(): ScrollBehavior {
  if (typeof window === 'undefined') {
    return 'auto';
  }

  return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
}

async function scrollToAspectSection(): Promise<void> {
  await nextTick();

  if (typeof window === 'undefined' || !aspectSectionRef.value) {
    return;
  }

  const sectionTop = aspectSectionRef.value.getBoundingClientRect().top + window.scrollY;
  const scrollTop = Math.max(sectionTop - resolveHeaderOffset(), 0);

  window.scrollTo({
    top: scrollTop,
    left: 0,
    behavior: resolveScrollBehavior(),
  });
}

function handleAspectClick(index: number): void {
  activeAspect.value = index;
  void scrollToAspectSection();
}

function resolveErrorTitle(): string {
  if (errorType.value === 'phone_format') {
    return '手机号码格式不正确';
  }
  if (errorType.value === 'insufficient_points') {
    return '评测积分不足';
  }
  if (errorType.value === 'unlock_points_insufficient') {
    return '解锁积分不足';
  }
  if (errorType.value === 'review_timeout') {
    return '评测仍在生成中';
  }
  if (errorType.value === 'review_failed') {
    return '评测生成失败';
  }
  return '本地 API 连接失败';
}

function resolveErrorBody(): string {
  if (errorType.value === 'phone_format') {
    return '请检查并确保输入的是 11 位有效中国大陆手机号（纯数字，无需空格或特殊字符）。';
  }
  if (errorType.value === 'insufficient_points') {
    return `当前手机号评测需要消耗 ${effectiveBaseReviewPoints.value} 积分。您当前可用积分为 ${userPoints.value} 分。`;
  }
  if (errorType.value === 'unlock_points_insufficient') {
    return `解锁单个专项需要消耗 ${effectiveAspectUnlockPoints.value} 积分。您当前可用积分为 ${userPoints.value} 分。`;
  }
  if (errorType.value === 'review_timeout') {
    return '评测还在后台生成中，没有真的失败。请先到“我的”页面查看进度，稍后再刷新结果。';
  }
  return errorDetail.value || '请检查本地后端服务是否已启动，然后重新尝试。';
}

async function handleExportImage(): Promise<void> {
  if (!currentReview.value) {
    return;
  }

  exportingImage.value = true;
  showToast('正在生成图片，请稍候...');

  await nextTick();
  window.setTimeout(() => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 750;
      canvas.height = 1350;
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        throw new Error('canvas_context_unavailable');
      }

      const grad = ctx.createLinearGradient(0, 0, 0, 1350);
      grad.addColorStop(0, '#FAF9F5');
      grad.addColorStop(1, '#F2EFE9');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 750, 1350);

      ctx.strokeStyle = '#D97706';
      ctx.lineWidth = 4;
      ctx.strokeRect(20, 20, 710, 1310);
      ctx.strokeStyle = '#4F46E5';
      ctx.lineWidth = 1;
      ctx.strokeRect(25, 25, 700, 1300);

      ctx.fillStyle = '#DC2626';
      ctx.fillRect(325, 60, 100, 100);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 24px serif';
      ctx.textAlign = 'center';
      ctx.fillText('易如', 375, 100);
      ctx.fillText('反掌', 375, 135);

      ctx.fillStyle = '#111827';
      ctx.font = 'bold 36px serif';
      ctx.fillText('手机号评测结果图', 375, 220);

      ctx.fillStyle = '#6B7280';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText('EASEWISE PHONE REVIEW', 375, 255);

      ctx.fillStyle = '#FFFFFF';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.05)';
      ctx.shadowBlur = 10;
      ctx.fillRect(60, 290, 630, 130);
      ctx.shadowBlur = 0;

      ctx.fillStyle = '#D97706';
      ctx.fillRect(60, 290, 8, 130);

      ctx.textAlign = 'left';
      ctx.fillStyle = '#111827';
      ctx.font = 'bold 22px sans-serif';
      ctx.fillText(`评测号码：${reviewPhoneDisplay.value}`, 90, 335);

      ctx.fillStyle = '#4B5563';
      ctx.font = '16px sans-serif';
      ctx.fillText(`性别属性：${reviewGenderDisplay.value}`, 90, 370);
      ctx.fillText(truncateText(phoneSummaryTitle.value, 26), 90, 400);

      ctx.fillStyle = '#DC2626';
      ctx.beginPath();
      ctx.arc(610, 355, 45, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#FFFFFF';
      ctx.textAlign = 'center';
      ctx.font = 'bold 13px sans-serif';
      ctx.fillText('评测评分', 610, 345);
      ctx.font = 'bold 28px serif';
      ctx.fillText(String(reviewScore.value), 610, 378);

      const palace = singlePalaceData.value;
      const relationCards = boardRelationCards.value;
      const harmBadges = boardHarmBadges.value;
      const comboBadges = boardSpecialCombos.value;
      const structureCapText = boardStructureCapText.value;

      ctx.fillStyle = '#4F46E5';
      ctx.fillRect(60, 460, 630, 45);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText('★ 奇门遁甲：立体定盘局象 ★', 375, 488);

      const leftBoxX = 80;
      const leftBoxY = 545;
      const leftBoxSize = 220;
      const rightBoxX = 330;
      const rightBoxY = 545;
      const rightBoxW = 340;
      const rightBoxH = 220;
      const riskBannerY = 790;

      ctx.strokeStyle = '#E5E7EB';
      ctx.lineWidth = 1;
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(leftBoxX, leftBoxY, leftBoxSize, leftBoxSize);
      ctx.strokeRect(leftBoxX, leftBoxY, leftBoxSize, leftBoxSize);

      ctx.fillStyle = '#4F46E5';
      ctx.fillRect(leftBoxX - 18, leftBoxY + 90, 34, 42);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 22px serif';
      ctx.textAlign = 'center';
      ctx.fillText(truncateText(palace.trigger, 2), leftBoxX - 1, leftBoxY + 119);

      ctx.textAlign = 'left';
      ctx.fillStyle = '#F3E8FF';
      roundRect(ctx, leftBoxX + 18, leftBoxY + 18, 74, 24, 8);
      ctx.fill();
      ctx.fillStyle = '#6D28D9';
      ctx.font = 'bold 14px serif';
      ctx.fillText(truncateText(palace.deity, 8), leftBoxX + 28, leftBoxY + 34);

      ctx.fillStyle = '#E0E7FF';
      roundRect(ctx, leftBoxX + 126, leftBoxY + 18, 74, 24, 8);
      ctx.fill();
      ctx.fillStyle = '#4338CA';
      ctx.font = 'bold 14px serif';
      ctx.fillText(truncateText(palace.star, 8), leftBoxX + 136, leftBoxY + 34);

      ctx.fillStyle = 'rgba(17, 24, 39, 0.05)';
      ctx.font = 'bold 82px serif';
      ctx.textAlign = 'center';
      ctx.fillText(truncateText(palace.palaceShort, 2), leftBoxX + leftBoxSize / 2, leftBoxY + 132);

      ctx.fillStyle = '#94A3B8';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText(truncateText(palace.palaceName, 8), leftBoxX + leftBoxSize / 2, leftBoxY + 104);
      ctx.fillStyle = '#312E81';
      ctx.font = 'bold 24px serif';
      ctx.fillText(truncateText(palace.direction, 6), leftBoxX + leftBoxSize / 2, leftBoxY + 138);

      ctx.strokeStyle = '#E5E7EB';
      ctx.beginPath();
      ctx.moveTo(leftBoxX + 66, leftBoxY + 176);
      ctx.lineTo(leftBoxX + 66, leftBoxY + 202);
      ctx.stroke();
      ctx.textAlign = 'center';
      ctx.fillStyle = '#4F46E5';
      ctx.font = 'bold 13px serif';
      ctx.fillText(truncateText(palace.heavenStem, 4), leftBoxX + 38, leftBoxY + 182);
      ctx.strokeStyle = '#CBD5E1';
      ctx.beginPath();
      ctx.moveTo(leftBoxX + 24, leftBoxY + 186);
      ctx.lineTo(leftBoxX + 52, leftBoxY + 186);
      ctx.stroke();
      ctx.fillStyle = '#475569';
      ctx.fillText(truncateText(palace.earthStem, 4), leftBoxX + 38, leftBoxY + 200);

      ctx.textAlign = 'left';
      ctx.fillStyle = '#FEE2E2';
      roundRect(ctx, leftBoxX + 118, leftBoxY + 172, 82, 28, 8);
      ctx.fill();
      ctx.fillStyle = '#B91C1C';
      ctx.font = 'bold 16px serif';
      ctx.fillText(truncateText(palace.door, 6), leftBoxX + 132, leftBoxY + 191);

      ctx.fillStyle = '#FFFFFF';
      ctx.strokeStyle = '#E5E7EB';
      ctx.fillRect(rightBoxX, rightBoxY, rightBoxW, rightBoxH);
      ctx.strokeRect(rightBoxX, rightBoxY, rightBoxW, rightBoxH);
      ctx.strokeStyle = '#E5E7EB';
      ctx.beginPath();
      ctx.moveTo(rightBoxX, rightBoxY);
      ctx.lineTo(rightBoxX, rightBoxY + rightBoxH);
      ctx.stroke();

      ctx.fillStyle = '#4F46E5';
      ctx.fillRect(rightBoxX + 18, rightBoxY + 20, 4, 18);
      ctx.fillStyle = '#111827';
      ctx.textAlign = 'left';
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText('易数定盘关系', rightBoxX + 30, rightBoxY + 34);

      relationCards.forEach((item, index) => {
        const cardX = rightBoxX + 18 + index * 156;
        const cardY = rightBoxY + 52;
        ctx.fillStyle = '#F8FAFC';
        roundRect(ctx, cardX, cardY, 146, 64, 12);
        ctx.fill();
        ctx.strokeStyle = '#E5E7EB';
        roundRect(ctx, cardX, cardY, 146, 64, 12);
        ctx.stroke();
        ctx.fillStyle = '#6B7280';
        ctx.font = 'bold 12px sans-serif';
        ctx.fillText(item.label, cardX + 12, cardY + 20);
        ctx.fillStyle = item.valueClass === 'text-red-600' ? '#DC2626' : item.valueClass === 'text-amber-700' ? '#B45309' : item.valueClass === 'text-brand-gold-fixed' ? '#B45309' : '#111827';
        ctx.font = 'bold 19px serif';
        ctx.fillText(truncateText(item.value, 10), cardX + 12, cardY + 49);
      });

      ctx.fillStyle = '#F59E0B';
      ctx.fillRect(rightBoxX + 18, rightBoxY + 136, 4, 18);
      ctx.fillStyle = '#111827';
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText('四害干扰特征', rightBoxX + 30, rightBoxY + 150);

      let harmX = rightBoxX + 18;
      let harmY = rightBoxY + 170;
      harmBadges.forEach((item) => {
        const badgeText = `${item.label} · ${item.value}`;
        const badgeWidth = Math.min(146, Math.max(72, badgeText.length * 11));
        if (harmX + badgeWidth > rightBoxX + rightBoxW - 18) {
          harmX = rightBoxX + 18;
          harmY += 30;
        }
        ctx.fillStyle = item.toneClass.includes('green') ? '#DCFCE7' : item.toneClass.includes('red') ? '#FEE2E2' : '#F8FAFC';
        roundRect(ctx, harmX, harmY, badgeWidth, 22, 8);
        ctx.fill();
        ctx.strokeStyle = item.toneClass.includes('green') ? '#BBF7D0' : item.toneClass.includes('red') ? '#FECACA' : '#E2E8F0';
        roundRect(ctx, harmX, harmY, badgeWidth, 22, 8);
        ctx.stroke();
        ctx.fillStyle = item.toneClass.includes('green') ? '#16A34A' : item.toneClass.includes('red') ? '#DC2626' : '#475569';
        ctx.font = 'bold 10px sans-serif';
        ctx.fillText(truncateText(badgeText, 14), harmX + 8, harmY + 14);
        harmX += badgeWidth + 8;
      });

      ctx.fillStyle = 'rgba(245, 158, 11, 0.02)';
      ctx.strokeStyle = 'rgba(245, 158, 11, 0.35)';
      roundRect(ctx, 80, riskBannerY, 590, 98, 14);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#6B7280';
      ctx.textAlign = 'left';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('特殊组合:', 98, riskBannerY + 28);

      let comboX = 178;
      let comboY = riskBannerY + 13;
      const combosForCanvas = comboBadges.length ? comboBadges : ['当前未检出明显特殊组合'];
      combosForCanvas.forEach((combo) => {
        const text = `【${combo}】`;
        const badgeWidth = Math.min(170, Math.max(110, text.length * 12));
        if (comboX + badgeWidth > 650) {
          comboX = 178;
          comboY += 28;
        }
        ctx.fillStyle = '#FEF3C7';
        roundRect(ctx, comboX, comboY, badgeWidth, 22, 8);
        ctx.fill();
        ctx.strokeStyle = '#FDE68A';
        roundRect(ctx, comboX, comboY, badgeWidth, 22, 8);
        ctx.stroke();
        ctx.fillStyle = '#B45309';
        ctx.font = 'bold 10px sans-serif';
        ctx.fillText(truncateText(text, 18), comboX + 8, comboY + 14);
        comboX += badgeWidth + 8;
      });

      ctx.fillStyle = '#6B7280';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('结构封顶:', 98, riskBannerY + 66);
      ctx.fillStyle = '#4F46E5';
      ctx.font = 'bold 14px serif';
      ctx.fillText(truncateText(structureCapText, 34), 178, riskBannerY + 66);

      ctx.fillStyle = '#111827';
      ctx.font = 'bold 22px serif';
      ctx.textAlign = 'left';
      ctx.fillText('【奇门盘面解析】', 60, 945);

      ctx.fillStyle = '#FFFFFF';
      ctx.strokeStyle = '#E5E7EB';
      roundRect(ctx, 60, 970, 630, 190, 16);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#4F46E5';
      ctx.beginPath();
      ctx.arc(86, 997, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#111827';
      ctx.font = 'bold 15px serif';
      drawWrappedText(ctx, phoneSummaryTitle.value, 98, 1003, 570, 20, 2);

      ctx.fillStyle = '#DC2626';
      ctx.font = 'bold 13px sans-serif';
      ctx.fillText('风险提醒', 82, 1060);
      ctx.fillStyle = '#7F1D1D';
      ctx.font = '13px sans-serif';
      drawWrappedText(ctx, phoneSummaryRisk.value, 82, 1082, 586, 18, 2);

      ctx.fillStyle = '#111827';
      ctx.font = '13px sans-serif';
      drawWrappedText(ctx, phoneSummaryUsageGuidance.value, 82, 1134, 586, 18, 2);

      ctx.fillStyle = '#111827';
      ctx.font = 'bold 22px serif';
      ctx.fillText('【长期使用建议】', 60, 1205);

      ctx.fillStyle = '#FFFFFF';
      ctx.strokeStyle = '#E5E7EB';
      roundRect(ctx, 60, 1230, 630, 58, 16);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#4F46E5';
      ctx.font = 'bold 15px serif';
      ctx.fillText(truncateText(stabilityLabel.value, 24), 82, 1254);
      ctx.fillStyle = '#111827';
      ctx.font = '13px sans-serif';
      drawWrappedText(ctx, stabilityValue.value, 82, 1275, 586, 18, 1);

      ctx.fillStyle = '#B45309';
      ctx.font = 'bold 13px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('—— 易如反掌 · 手机号评测结果 ——', 375, 1310);

      const dataUrl = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `易如反掌_手机号评测_${reviewPhoneDisplay.value}.png`;
      link.href = dataUrl;
      link.click();

      showToast('图片已生成并开始下载。');
    } catch {
      showToast('图片生成失败，请稍后重试。');
    } finally {
      exportingImage.value = false;
    }
  }, 400);
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number,
): void {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function truncateText(text: string, maxLength: number): string {
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}…` : text;
}

function drawWrappedText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number,
  maxLines: number,
): void {
  const chars = text.split('');
  const lines: string[] = [];
  let currentLine = '';

  chars.forEach((char) => {
    const nextLine = currentLine + char;
    if (ctx.measureText(nextLine).width > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = char;
      return;
    }
    currentLine = nextLine;
  });

  if (currentLine) {
    lines.push(currentLine);
  }

  lines.slice(0, maxLines).forEach((line, index) => {
    const shouldEllipsize = index === maxLines - 1 && lines.length > maxLines;
    const displayLine = shouldEllipsize ? `${line.slice(0, Math.max(1, line.length - 1))}…` : line;
    ctx.fillText(displayLine, x, y + index * lineHeight);
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
</script>

<template>
  <div class="pb-32 max-w-md mx-auto w-full relative min-h-screen">
    <transition name="fade">
      <div
        v-if="toast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
      >
        <AlertCircle :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <transition name="fade" mode="out-in">
      <div
        v-if="appState === 'input'"
        key="input-form"
        class="px-margin-mobile space-y-5 pt-3.5"
      >
        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="flex items-center gap-2 mb-2">
            <span class="w-2 h-2 bg-brand-primary rounded-full animate-ping"></span>
            <span class="text-brand-gold-fixed font-serif text-[11px] font-bold tracking-wide leading-none">奇门遁甲手机号综合测评</span>
          </div>
          <p class="text-[13px] text-brand-secondary leading-relaxed">
            输入手机号和性别后，系统会给出整体评分、盘面概览等信息，帮助你更快了解这个号码是否适合长期使用。
          </p>
        </section>

        <form class="space-y-5 font-sans" @submit.prevent="handleReviewSubmitIntent">
          <section class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 text-left">
            <div class="space-y-1.5">
              <label class="text-[11px] font-bold text-brand-secondary tracking-wide flex items-center gap-1">
                <span>手机号码 (中国的11位手机号)</span>
                <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="phoneNumber"
                  type="tel"
                  maxlength="11"
                  enterkeyhint="go"
                  class="w-full bg-brand-paper hover:bg-white text-brand-ink-strong focus:bg-white font-sans text-[15px] font-bold p-3.5 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all placeholder-gray-400 shadow-inner tracking-wider"
                  placeholder="请输入11位中国手机号码"
                />
                <span
                  v-if="phoneNumber.length > 0"
                  @click="phoneNumber = ''"
                  class="absolute right-4 top-1/2 -translate-y-1/2 p-1 bg-gray-200 hover:bg-gray-300 text-gray-500 rounded-full cursor-pointer text-[10px] w-4 h-4 flex items-center justify-center font-bold select-none"
                >
                  ×
                </span>
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[11px] font-bold text-brand-secondary tracking-wide">性别</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-150/40">
                <button
                  type="button"
                  @click="gender = 'male'"
                  class="py-2 text-[13px] font-bold rounded-lg cursor-pointer transition-all outline-none"
                  :class="gender === 'male' ? 'bg-white text-brand-primary shadow-sm border border-gray-100' : 'text-brand-secondary hover:text-brand-primary'"
                >
                  男
                </button>
                <button
                  type="button"
                  @click="gender = 'female'"
                  class="py-2 text-[13px] font-bold rounded-lg cursor-pointer transition-all outline-none"
                  :class="gender === 'female' ? 'bg-white text-brand-primary shadow-sm border border-gray-100' : 'text-brand-secondary hover:text-brand-primary'"
                >
                  女
                </button>
              </div>
            </div>
          </section>

          <section class="space-y-3 pt-1">
            <button
              type="submit"
              class="w-full py-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl font-sans text-[13px] font-bold shadow-md cursor-pointer outline-none transition-all active:scale-[0.985] flex items-center justify-center gap-1.5"
              :disabled="!phoneNumber || state.booting"
            >
              <Sparkles :size="15" fill="currentColor" />
              <span v-if="state.booting">正在连接本地 API...</span>
              <span v-else>立即扣除 <span class="font-sans">{{ effectiveBaseReviewPoints }}</span> 积分深度起盘测算</span>
            </button>
          </section>

          <footer class="bg-gray-50/70 p-3.5 rounded-xl border border-gray-100/70 font-sans text-[11px] text-brand-secondary leading-relaxed text-center">
            <p class="font-bold">使用说明：</p>
            <p class="mt-1">
              当前评测仅支持中国大陆11位手机号。
            </p>
          </footer>
        </form>
      </div>

      <div
        v-else-if="appState === 'waiting'"
        key="waiting-box"
        class="py-10 max-w-md mx-auto px-margin-mobile flex flex-col justify-center min-h-[65vh]"
      >
        <div class="bg-white rounded-2xl p-6 border border-gray-150/75 shadow-sm space-y-6 text-center">
          <div class="relative w-28 h-28 mx-auto flex items-center justify-center select-none">
            <div class="absolute inset-0 bg-brand-primary/5 rounded-full blur-md animate-pulse"></div>

            <svg class="absolute w-28 h-28 text-brand-primary/25 animate-[spin_40s_linear_infinite]" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-dasharray="1 3" stroke-width="1.5" />
              <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" stroke-dasharray="8 4" stroke-width="1.2" />
            </svg>

            <svg class="absolute w-24 h-24 text-brand-accent/40 animate-[spin_24s_linear_infinite_reverse]" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-dasharray="12 6" stroke-width="1.5" stroke-linecap="round" />
              <path d="M 50,4 M 50,96 M 4,50 M 96,50 M 17,17 M 83,83 M 17,83 M 83,17" stroke="currentColor" stroke-width="0.8" stroke-dasharray="2 4" />
            </svg>

            <svg class="absolute w-18 h-18 text-brand-primary/60 animate-[spin_12s_linear_infinite]" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-dasharray="4 2" stroke-width="1" />
            </svg>

            <div class="absolute w-11 h-11 bg-white rounded-full border border-brand-primary/20 shadow-md flex items-center justify-center animate-[spin_8s_ease-in-out_infinite]">
              <svg class="w-6.5 h-6.5 text-brand-primary" viewBox="0 0 100 100" fill="currentColor">
                <path d="M50,0 A50,50 0 0,0 50,100 A25,25 0 0,0 50,50 A25,25 0 0,1 50,0 Z" />
                <circle cx="50" cy="25" r="7.5" fill="white" />
                <path d="M50,100 A50,50 0 0,0 50,0 A25,25 0 0,1 50,50 A25,25 0 0,0 50,100 Z" fill="none" stroke="currentColor" stroke-width="1" />
                <circle cx="50" cy="75" r="7.5" fill="currentColor" />
              </svg>
            </div>
          </div>

          <div class="space-y-1 py-1">
            <h4 class="font-serif text-[17.5px] font-bold text-brand-ink-strong tracking-wide">奇门格局智能推演中</h4>
            <transition name="poem-fade" mode="out-in">
              <p
                :key="waitingPoemLine"
                class="font-serif text-[15px] font-bold text-brand-secondary/85 leading-relaxed tracking-wide"
              >
                {{ waitingPoemLine }}
              </p>
            </transition>
          </div>

          <div class="text-center space-y-1.5 select-none font-sans px-1">
            <div class="flex items-center justify-between text-[11px] font-bold text-brand-secondary">
              <span class="flex items-center gap-1">
                <Sparkles :size="11.5" class="text-brand-primary animate-pulse" fill="currentColor" />
                <span>智能体正在构建和解析格局</span>
              </span>
              <span class="text-brand-primary-strong text-[15px] font-bold font-sans tracking-tight">{{ waitingProgressPercentText }}%</span>
            </div>
            <div class="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden border border-gray-50 relative">
              <div
                class="h-full bg-brand-primary transition-all duration-500 ease-out rounded-full"
                :style="{ width: `${waitingProgressPercent}%` }"
              ></div>
            </div>
          </div>

          <div class="h-px bg-gray-100"></div>

          <div class="space-y-4 px-1">
            <div
              v-for="(step, index) in waitingSteps"
              :key="step.title"
              class="flex items-start gap-3.5 text-left transition-all duration-300"
              :class="index === waitingPhase ? 'opacity-100 scale-[1.01]' : index < waitingPhase ? 'opacity-85' : 'opacity-35'"
            >
              <div class="relative flex items-center justify-center mt-1 shrink-0 select-none">
                <div
                  v-if="index < waitingSteps.length - 1"
                  class="absolute top-5 left-2.5 w-0.5 h-[32px] -ml-[1px]"
                  :class="index < waitingPhase ? 'bg-emerald-500/75' : 'bg-gray-100'"
                ></div>

                <div
                  v-if="index < waitingPhase"
                  class="w-5 h-5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center shadow-xs"
                >
                  <Check :size="11" stroke-width="3" />
                </div>
                <div
                  v-else-if="index === waitingPhase"
                  class="w-5 h-5 rounded-full bg-brand-primary/10 border border-brand-primary flex items-center justify-center shadow-xs text-brand-primary relative"
                >
                  <div class="absolute inset-0 rounded-full border border-brand-primary border-t-transparent animate-spin"></div>
                  <div class="w-1.5 h-1.5 rounded-full bg-brand-primary animate-pulse"></div>
                </div>
                <div
                  v-else
                  class="w-5 h-5 rounded-full bg-gray-50 border border-gray-150 text-[10px] text-gray-400 font-bold flex items-center justify-center"
                >
                  <span>{{ index + 1 }}</span>
                </div>
              </div>

              <div class="space-y-0.5 min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <h5
                    class="text-[15px] font-bold font-serif leading-none transition-colors"
                    :class="index === waitingPhase ? 'text-brand-ink-strong' : index < waitingPhase ? 'text-emerald-700 font-bold' : 'text-brand-secondary/60'"
                  >
                    {{ step.title }}
                  </h5>
                  <span
                    v-if="index === waitingPhase"
                    class="px-1.5 py-0.5 bg-brand-primary/10 text-brand-primary rounded text-[10px] font-bold leading-none animate-pulse shrink-0 font-sans"
                  >
                    正在计算
                  </span>
                </div>
                <p
                  class="text-[11px] leading-relaxed transition-colors tracking-tight font-sans"
                  :class="index === waitingPhase ? 'text-brand-secondary font-medium' : index < waitingPhase ? 'text-gray-500' : 'text-gray-400'"
                >
                  {{ index === waitingPhase ? waitingMessage : step.desc }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else-if="appState === 'result'"
        key="result-view"
        class="px-margin-mobile space-y-5 pt-3.5"
      >
        <section class="flex items-center justify-between">
          <button
            @click="resetToInput"
            class="py-2 px-3.5 bg-white border border-gray-100 hover:bg-gray-50 text-brand-secondary rounded-lg font-sans text-[13px] font-bold cursor-pointer outline-none transition-all flex items-center gap-1 shadow-sm"
          >
            <ArrowLeft :size="13" />
            <span>重新评测</span>
          </button>

          <button
            @click="handleExportImage"
            class="py-2 px-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-lg font-sans text-[13px] font-bold cursor-pointer outline-none transition-all flex items-center gap-1 shadow-sm"
            :disabled="exportingImage"
          >
            <Download :size="13" />
            <span>{{ exportingImage ? '正在生成图片...' : '导出结果图片' }}</span>
          </button>
        </section>

        <section class="bg-white rounded-2xl px-4 py-3 border border-gray-100 shadow-sm relative overflow-hidden flex items-center justify-between gap-2.5 text-left">
          <div class="min-w-0 flex-1 space-y-0.5">
            <div class="flex items-center gap-1">
              <span class="inline-block w-1.5 h-1.5 bg-green-500 rounded-full"></span>
              <span class="text-brand-secondary font-sans text-[11px] font-bold tracking-wide">评测已完成</span>
            </div>

            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="min-w-0 truncate text-[17.5px] leading-tight font-bold text-brand-ink-strong">
                <span class="font-serif">号码：</span><span class="font-serif">{{ reviewPhoneDisplay }}</span>
              </h3>
              <span class="inline-flex items-center rounded-full bg-brand-paper px-2 py-0.5 font-sans text-[11px] font-bold text-brand-secondary shrink-0">
                性别 · {{ reviewGenderDisplay }}
              </span>
            </div>
          </div>

          <div class="text-center shrink-0">
            <div class="w-[72px] h-[72px] rounded-full border-[2.5px] border-brand-accent flex flex-col items-center justify-center bg-brand-primary text-white shadow-md">
              <span class="font-sans text-[10px] opacity-85 leading-none">综合评分</span>
              <span class="font-serif text-[28px] font-black text-brand-accent mt-0.5 leading-none">{{ reviewScore }}</span>
            </div>
          </div>
        </section>

        <section class="space-y-2.5">
          <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5 text-left">
            <Star :size="13" class="text-brand-primary fill-current shrink-0" />
            <span>奇门遁甲：立体定盘局象</span>
          </h4>

          <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm space-y-3.5 font-serif text-brand-ink-strong">
            <div class="grid grid-cols-[160px_minmax(0,1fr)] gap-4 items-stretch">
              <div class="relative w-[160px] h-[160px] bg-brand-paper border border-brand-primary/20 rounded-xl px-4 py-3.5 flex flex-col justify-between text-left shadow-sm shrink-0">
                <div class="absolute -left-3.5 top-1/2 -translate-y-1/2 w-7 h-9 bg-brand-primary border border-brand-primary-strong text-white rounded-md shadow-md flex items-center justify-center font-serif text-[15px] font-black tracking-[0.08em] leading-none z-10 select-none">
                  {{ singlePalaceData.trigger }}
                </div>

                <div class="flex justify-between items-center text-[15px] leading-tight select-none z-10 gap-2">
                  <span class="px-1.5 py-0.5 bg-purple-500/10 text-purple-700 font-serif text-[13px] font-black rounded-md leading-none">
                    {{ singlePalaceData.deity }}
                  </span>
                  <span class="px-1.5 py-0.5 bg-indigo-500/10 text-indigo-700 font-serif text-[13px] font-black rounded-md leading-none">
                    {{ singlePalaceData.star }}
                  </span>
                </div>

                <div class="absolute inset-0 flex items-center justify-center pointer-events-none select-none opacity-[0.05] z-0">
                  <span class="font-serif font-black text-[46px] tracking-widest leading-none">
                    {{ singlePalaceData.palaceShort }}
                  </span>
                </div>

                <div class="text-center z-10 py-0.5">
                  <p class="font-serif font-bold text-slate-400 text-[13px] leading-none mb-1 tracking-[0.18em]">
                    {{ singlePalaceData.palaceName }}
                  </p>
                  <p class="font-serif font-black text-brand-primary-strong text-[22px] leading-none">
                    {{ singlePalaceData.direction }}
                  </p>
                </div>

                <div class="flex justify-between items-end text-[15px] font-black z-10 leading-none gap-3">
                  <div class="flex flex-col items-center justify-center text-[15px] font-serif font-black leading-none border-r border-gray-200 pr-2.5 select-none shrink-0 min-w-[38px]">
                    <span class="text-brand-primary tracking-[0.08em]">{{ singlePalaceData.heavenStem }}</span>
                    <span class="w-5 border-t border-gray-300 my-1"></span>
                    <span class="text-brand-secondary tracking-[0.08em]">{{ singlePalaceData.earthStem }}</span>
                  </div>

                  <span class="px-2 py-1 bg-red-500/10 text-red-700 rounded-md font-serif text-[13px] font-black leading-none">
                    {{ singlePalaceData.door }}
                  </span>
                </div>
              </div>

              <div class="h-[160px] min-w-0 grid grid-rows-2 gap-2 border-l border-gray-100 pl-4">
                <div
                  v-for="item in boardRelationCards"
                  :key="item.label"
                  class="board-relation-card bg-brand-paper hover:bg-gray-50/70 px-3 py-2.5 border border-gray-100/55 rounded-xl transition-all grid grid-cols-[42px_minmax(0,1fr)] items-center gap-2 text-left"
                >
                  <div class="board-relation-label font-serif text-[13px] text-brand-secondary font-black leading-none flex flex-col gap-1.5 pl-1">
                    <span>{{ item.labelTop }}</span>
                    <span>{{ item.labelBottom }}</span>
                  </div>
                  <p class="board-relation-value font-serif font-black text-[20px] leading-none text-right min-w-0" :class="item.valueClass">
                    {{ item.value }}
                  </p>
                </div>
              </div>
            </div>

            <div class="space-y-1.5 text-left bg-white rounded-2xl border border-gray-100 shadow-sm p-3">
              <div class="flex items-center gap-1.5 border-b border-gray-100/60 pb-1">
                <span class="w-1.5 h-3.5 bg-amber-500 rounded-sm"></span>
                <h5 class="font-serif text-[13px] font-black text-brand-ink-strong tracking-wide">四害干扰特征</h5>
              </div>
              <div class="flex flex-nowrap gap-1.5 overflow-x-auto pb-1">
                <span
                  v-for="harm in boardHarmBadges"
                  :key="harm.label"
                  class="px-2.5 py-0.5 font-serif text-[11px] font-black rounded-md border whitespace-nowrap shrink-0"
                  :class="harm.toneClass"
                >
                  {{ harm.label }} {{ harm.compactValue }}
                </span>
              </div>
            </div>

            <div class="bg-amber-500/[0.02] border border-amber-100/70 rounded-xl p-3 space-y-2 text-left text-[13px] font-serif transition-all">
              <div class="flex flex-wrap items-center gap-2 select-none">
                <span class="text-[13px] text-brand-secondary/80 font-black shrink-0">特殊组合:</span>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="combo in (boardSpecialCombos.length ? boardSpecialCombos : ['当前未检出明显特殊组合'])"
                    :key="combo"
                    class="px-2 py-0.5 font-serif text-[11px] font-black bg-amber-500/10 text-amber-700 border border-amber-200/50 rounded-md"
                  >
                    {{ combo }}
                  </span>
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-2 select-none">
                <span class="text-[13px] text-brand-secondary/80 font-black shrink-0">结构封顶:</span>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="item in boardStructureCapTags"
                    :key="item"
                    class="px-2 py-0.5 font-serif text-[11px] font-black bg-amber-500/10 text-amber-700 border border-amber-200/50 rounded-md"
                  >
                    {{ item }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="space-y-2 text-left">
          <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5">
            <Compass :size="13" class="text-brand-primary shrink-0" />
            <span>奇门盘面解析</span>
          </h4>

          <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 font-sans">
            <div class="flex items-start gap-1.5">
              <span class="w-1.5 h-1.5 bg-brand-primary rounded-full shrink-0 mt-[0.6em]"></span>
              <p class="font-serif text-[15px] font-black text-brand-primary-strong leading-relaxed">
                {{ phoneSummaryTitle }}
              </p>
            </div>

            <div class="bg-red-500/[0.03] rounded-xl border border-red-100/80 p-3.5 space-y-2">
              <div class="flex items-center gap-1.5">
                <AlertCircle :size="15" class="text-red-500 shrink-0" />
                <p class="font-serif text-[11px] font-bold text-red-600 tracking-wide">风险提醒</p>
              </div>
              <p class="text-[13px] text-red-700/90 font-medium leading-relaxed">
                {{ phoneSummaryRisk }}
              </p>
            </div>

            <div class="pt-1.5 border-t border-gray-100">
              <p class="text-[13px] text-brand-ink leading-relaxed">
                {{ phoneSummaryUsageGuidance }}
              </p>
            </div>
          </div>
        </section>

        <section class="space-y-2 text-left">
          <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5">
            <Lightbulb :size="13" class="text-brand-primary shrink-0" />
            <span>长期使用建议</span>
          </h4>

          <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm font-sans space-y-3">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-brand-primary/10 flex items-center justify-center shrink-0">
                <Sparkles :size="15" class="text-brand-primary" fill="currentColor" />
              </div>
              <p class="text-[15px] font-serif font-black text-brand-primary leading-tight flex-1 min-w-0">
                {{ stabilityLabel }}
              </p>
            </div>
            <p class="text-[13px] text-brand-ink leading-relaxed font-medium">
              {{ stabilityValue }}
            </p>
          </div>
        </section>

        <section ref="aspectSectionRef" class="space-y-2">
          <div class="flex justify-between items-baseline text-left">
            <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5">
              <Clock :size="13" class="text-brand-primary shrink-0" />
              <span>十二个专项</span>
            </h4>
            <span class="font-sans text-[10px] text-brand-secondary">
              余积分: <span class="text-brand-primary-strong font-sans font-bold">{{ userPoints }}</span>
            </span>
          </div>

          <div class="aspect-grid grid gap-1">
            <button
              v-for="(aspect, idx) in reviewAspects"
              :key="aspect.aspect_key"
              @click="handleAspectClick(idx)"
              class="aspect-tab relative h-[36px] px-2 rounded-lg font-sans text-[10px] font-bold flex items-center justify-between gap-1 transition-all outline-none cursor-pointer border select-none"
              :class="[
                activeAspect === idx
                  ? 'bg-brand-primary text-white border-transparent shadow-sm'
                  : !aspect.is_unlocked
                  ? 'bg-brand-paper/85 text-brand-secondary/70 border-gray-150'
                  : 'bg-white text-brand-secondary border-gray-150 hover:bg-gray-50'
              ]"
            >
              <div class="aspect-tab-main flex items-center gap-1 min-w-0">
                <component
                  :is="aspect.icon"
                  :size="11.5"
                  :class="[
                    activeAspect === idx ? 'text-white' : aspect.is_unlocked ? 'text-brand-primary' : 'text-brand-secondary/40'
                  ]"
                  class="aspect-tab-icon shrink-0"
                />
                <span class="aspect-tab-title truncate tracking-tight">{{ (aspect.short_title || aspect.title).slice(0, 2) }}</span>
              </div>

              <div class="shrink-0 flex items-center">
                <div
                  v-if="isAspectUnlockPending(aspect)"
                  class="w-2.5 h-2.5 border-2 rounded-full animate-spin shrink-0"
                  :class="activeAspect === idx ? 'border-white/40 border-t-white' : 'border-brand-primary/25 border-t-brand-primary'"
                ></div>
                <span
                  v-else-if="aspect.is_unlocked"
                  class="aspect-score-badge text-[8px] font-black px-1 py-0.5 rounded leading-none shrink-0 select-none border"
                  :class="resolveScoreBadgeClass(aspect.score, activeAspect === idx)"
                >
                  <span class="aspect-score-full">{{ aspect.score != null ? `${aspect.score}分` : '已开' }}</span>
                  <span class="aspect-score-short">{{ aspect.score != null ? aspect.score : '开' }}</span>
                </span>
                <span
                  v-else
                  class="text-[8px] font-bold px-1 py-0.5 rounded-sm leading-none shrink-0 select-none border"
                  :class="activeAspect === idx ? 'bg-white/20 text-white border-white/20' : 'text-brand-gold-fixed bg-amber-50 border-amber-200/50'"
                >
                  锁
                </span>
              </div>
            </button>
          </div>
        </section>

        <section class="space-y-3 text-left">
          <transition name="fade" mode="out-in">
            <div
              v-if="selectedAspect"
              :key="selectedAspect.aspect_key"
              class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 text-left"
            >
              <div v-if="selectedAspectUnlockPending" class="py-12 flex flex-col items-center justify-center space-y-4 text-center">
                <div class="relative w-14 h-14 flex items-center justify-center">
                  <div class="absolute inset-0 border-4 border-brand-primary/10 rounded-full animate-pulse"></div>
                  <div class="absolute inset-0 border-4 border-brand-primary border-t-transparent rounded-full animate-spin"></div>
                  <Sparkles :size="18" class="text-brand-primary animate-pulse shrink-0" fill="currentColor" />
                </div>
                <div class="space-y-1.5 max-w-[86%] mx-auto">
                  <h5 class="font-serif text-[15px] font-bold text-brand-ink-strong leading-tight">
                    {{ unlockProcessingHeading }}
                  </h5>
                  <p class="font-sans text-[11px] text-brand-secondary leading-relaxed">
                    {{ unlockWaitingMessage }}
                  </p>
                </div>
              </div>

              <div v-else-if="selectedAspect.is_unlocked" class="space-y-4">
                <div class="flex justify-between items-center pb-3 border-b border-gray-50">
                  <div class="flex items-center gap-2">
                    <component :is="selectedAspect.icon" :size="16" class="text-brand-primary shrink-0" />
                    <span class="font-serif text-[15px] font-extrabold text-brand-ink-strong leading-tight">
                      {{ selectedAspect.short_title || selectedAspect.title }} · 详细结果
                    </span>
                  </div>
                  <span
                    class="px-2.5 py-1 rounded-full font-sans text-[11px] font-bold border"
                    :class="resolveScoreBadgeClass(selectedAspect.score, false)"
                  >
                    专项评分：{{ selectedAspect.score != null ? `${selectedAspect.score}分` : '已解锁' }}
                  </span>
                </div>

                <div class="space-y-3 font-sans text-[13px] text-brand-secondary">
                  <div class="bg-brand-primary/5 p-3 rounded-xl border border-brand-primary/10">
                    <div class="flex items-center gap-1.5">
                      <Sparkles :size="14" class="text-brand-primary shrink-0" fill="currentColor" />
                      <p class="font-serif font-bold text-brand-primary-strong text-[13px]">一句话评价</p>
                    </div>
                    <p class="text-brand-ink mt-1 font-medium">{{ selectedAspect.title }}</p>
                  </div>

                  <div v-if="selectedAspect.risk" class="bg-red-500/[0.03] p-3 rounded-xl border border-red-100/80 font-sans text-[13px] text-red-700 leading-relaxed space-y-1.5">
                    <div class="flex items-center gap-1.5">
                      <AlertCircle :size="14" class="text-red-500 shrink-0" />
                      <p class="font-bold text-red-600">风险提示</p>
                    </div>
                    <p>{{ selectedAspect.risk }}</p>
                  </div>

                  <p class="leading-relaxed whitespace-pre-line text-brand-secondary font-normal">
                    {{ selectedAspect.content }}
                  </p>
                </div>
              </div>

              <div v-else class="py-6 flex flex-col items-center justify-center text-center space-y-4">
                <div class="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary">
                  <Lock :size="22" class="animate-bounce" />
                </div>
                <div class="max-w-[85%] mx-auto">
                  <h5 class="font-serif font-bold text-[15px] text-brand-ink-strong leading-tight">
                    查看「{{ selectedAspect.title }}」详细分析
                  </h5>
                  <p class="font-sans text-[13px] text-brand-secondary mt-1 leading-relaxed">
                    该维度属于深度内容，默认需要额外消耗 <span class="font-sans">{{ selectedAspect.unlock_points || effectiveAspectUnlockPoints }}</span> 积分后查看。
                  </p>
                </div>
                <button
                  @click="handleUnlockAspect(activeAspect)"
                  class="px-6 py-2.5 bg-brand-primary text-white rounded-full font-sans text-[13px] font-bold shadow-sm hover:bg-brand-primary-strong outline-none cursor-pointer flex items-center gap-1.5 mx-auto disabled:opacity-75 disabled:cursor-wait"
                  :disabled="selectedAspectUnlockPending"
                >
                  <span
                    v-if="selectedAspectUnlockPending"
                    class="w-3 h-3 border-2 border-white/40 border-t-white rounded-full animate-spin"
                  ></span>
                  <Lock v-else :size="12" fill="currentColor" />
                  <span>
                    <span v-if="selectedAspectWaitingForGeneration">正在生成专项内容</span>
                    <span v-else-if="selectedAspectUnlockPending">正在读取专项内容</span>
                    <span v-else>
                      消耗 <span class="font-sans">{{ selectedAspect.unlock_points || effectiveAspectUnlockPoints }}</span> 积分立即解锁
                    </span>
                  </span>
                </button>
              </div>
            </div>

            <div
              v-else
              class="p-4 bg-white rounded-2xl border border-gray-100 text-center font-sans text-[13px] text-brand-secondary/80 flex items-center justify-center gap-1.5 shadow-sm"
            >
              <Sparkles :size="13" class="text-brand-primary" fill="currentColor" />
              <span>点击上方卡片，可查看或解锁对应专项的详细分析与风险提示。</span>
            </div>
          </transition>
        </section>

        <section class="bg-white p-4.5 rounded-xl border border-gray-100 flex flex-col gap-3 text-center">
          <span class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide block">
            —— 接下来，你可以继续查看以下内容 ——
          </span>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="emit('navigate-to-tab', 'agent')"
              class="py-3 px-2 bg-brand-primary text-white rounded-lg font-sans text-[13px] font-bold hover:bg-brand-primary-strong transition-all cursor-pointer flex items-center justify-center gap-1.5 outline-none border-none"
            >
              <MessageSquare :size="14" />
              <span>有疑问，去问智能体</span>
            </button>

            <button
              @click="handleSelectNextLockedAspect"
              class="py-3 px-2 bg-white border border-brand-primary text-brand-primary rounded-lg font-sans text-[13px] font-bold hover:bg-brand-primary/5 transition-all cursor-pointer flex items-center justify-center gap-1.5 outline-none"
            >
              <Plus :size="14" />
              <span>继续查看更多维度</span>
            </button>
          </div>
        </section>

        <section class="mt-4">
          <div
            @click="handleCopyServiceContact"
            class="bg-brand-primary/5 hover:bg-brand-primary/10 transition-colors border border-brand-primary/10 rounded-2xl p-4 flex items-center justify-between cursor-pointer group shadow-sm bg-white"
          >
            <div class="flex items-center gap-2.5 text-left">
              <div class="w-8 h-8 rounded-full bg-brand-primary/10 flex items-center justify-center shrink-0">
                <Sparkles :size="16" class="text-brand-primary animate-pulse" fill="currentColor" />
              </div>
              <div class="font-sans">
                <p class="text-[13px] font-bold text-brand-ink-strong">联系客服获取后续支持</p>
                <p class="text-[11px] text-brand-secondary mt-0.5">{{ customerServiceGuidance }}</p>
              </div>
            </div>
            <div class="text-brand-primary font-sans font-bold text-[11px] bg-brand-primary/10 group-hover:bg-brand-primary/20 px-2.5 py-1 rounded-full flex items-center gap-1 shrink-0">
              <span>复制</span>
              <Check v-if="copied" :size="10" />
              <Copy v-else :size="10" />
            </div>
          </div>
        </section>
      </div>

      <div
        v-else-if="appState === 'error_state'"
        key="error-box"
        class="pt-24 pb-32 max-w-md mx-auto px-margin-mobile flex flex-col items-center justify-center min-h-[70vh] text-center space-y-6"
      >
        <div class="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center text-red-600 border border-red-200/60 shadow-sm shrink-0">
          <AlertCircle :size="28" />
        </div>

        <div class="space-y-2.5 max-w-[90%] mx-auto">
          <h3 class="font-serif text-[20px] font-bold text-brand-ink-strong leading-tight">
            {{ resolveErrorTitle() }}
          </h3>
          <p class="font-sans text-[13px] text-brand-secondary leading-relaxed">
            {{ resolveErrorBody() }}
          </p>
        </div>

        <div
          v-if="errorType === 'insufficient_points' || errorType === 'unlock_points_insufficient'"
          class="bg-white p-4.5 rounded-xl border border-gray-100 max-w-[95%] text-left space-y-3.5 shadow-sm"
        >
          <div class="flex items-start gap-2 font-sans text-[13px] text-brand-secondary leading-relaxed">
            <Lightbulb :size="16" class="text-brand-primary shrink-0 mt-0.5" />
            <div>
              <span class="font-bold text-brand-ink-strong">联系客服支持: </span>
              <span>{{ customerServiceGuidance }}</span>
            </div>
          </div>

          <div class="bg-brand-paper p-3 rounded-xl flex items-center justify-between border border-gray-100 font-sans">
            <div class="text-left font-mono">
              <p class="text-[10px] text-brand-secondary">客服联系方式：</p>
              <p class="text-[15px] font-bold text-brand-ink-strong">{{ customerServiceContact }}</p>
            </div>
            <button
              @click="handleCopyServiceContact"
              class="px-3.5 py-1.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[11px] font-bold rounded-lg cursor-pointer outline-none flex items-center gap-1 shrink-0 transition-all shadow-sm"
            >
              <Check v-if="copied" :size="11" />
              <Copy v-else :size="11" />
              <span>{{ copied ? '已复制' : '复制' }}</span>
            </button>
          </div>
        </div>

        <div class="w-full pt-2 flex flex-col gap-2.5 p-1 font-sans">
          <button
            @click="errorType === 'unlock_points_insufficient' ? appState = 'result' : resetToInput()"
            class="w-full py-3 bg-brand-primary text-white rounded-xl font-bold text-[13px] shadow-sm hover:bg-brand-primary-strong active:scale-[0.98] transition-all cursor-pointer outline-none border-none"
          >
            <span>
              {{ errorType === 'unlock_points_insufficient' ? '返回评测结果' : '返回重新输入' }}
            </span>
          </button>

          <button
            v-if="errorType === 'insufficient_points' || errorType === 'unlock_points_insufficient'"
            @click="emit('navigate-to-tab', 'profile')"
            class="w-full py-3 bg-white border border-brand-primary/20 text-brand-primary rounded-xl font-bold text-[13px] hover:bg-brand-primary/5 active:scale-[0.98] transition-all cursor-pointer outline-none"
          >
            <span>前往个人中心查看积分</span>
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div
        v-if="showReviewConfirmDialog"
        class="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50 font-sans"
        @click.self="closeReviewConfirmDialog"
      >
        <div class="bg-white rounded-2xl p-5 max-w-xs w-[88%] border border-gray-100 shadow-xl space-y-3.5 transform transition-all relative">
          <div class="flex items-center justify-center gap-2.5 select-none text-left pt-1">
            <div class="w-9 h-9 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary shrink-0">
              <Sparkles :size="18" fill="currentColor" />
            </div>
            <h4 class="font-serif text-[17.5px] font-bold text-brand-ink-strong leading-none">
              确认开始评测
            </h4>
          </div>

          <div class="px-1 text-center pt-1">
            <p class="text-[13px] text-brand-secondary font-semibold leading-relaxed">
              是否消耗 <span class="text-brand-primary font-sans font-bold text-[15px] mx-0.5">{{ effectiveBaseReviewPoints }}</span> 积分进行手机号评测？
            </p>
          </div>

          <div class="flex items-center justify-center gap-2 py-0.5 select-none">
            <label class="inline-flex items-center gap-2 cursor-pointer">
              <input
                v-model="skipReviewConfirmHint"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-brand-primary focus:ring-brand-primary/40 cursor-pointer accent-brand-primary"
              />
              <span class="text-[13px] text-brand-secondary/90 font-bold">下次不再提示此信息</span>
            </label>
          </div>

          <div class="flex gap-3 pt-1 text-[13px]">
            <button
              type="button"
              class="flex-1 py-2 border border-gray-200 text-gray-600 rounded-xl font-sans font-bold hover:bg-slate-50 transition-colors cursor-pointer outline-none select-none"
              @click="closeReviewConfirmDialog"
            >
              取消
            </button>
            <button
              type="button"
              class="flex-1 py-2 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl font-sans font-bold shadow-sm transition-colors cursor-pointer outline-none select-none"
              @click="handleConfirmReview"
            >
              确认评测
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.poem-fade-enter-active,
.poem-fade-leave-active {
  transition: opacity 0.45s ease, transform 0.45s ease, filter 0.45s ease;
}

.poem-fade-enter-from {
  opacity: 0;
  filter: blur(4px);
  transform: translateY(6px);
}

.poem-fade-leave-to {
  opacity: 0;
  filter: blur(3px);
  transform: translateY(-5px);
}

.board-relation-value {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: keep-all;
}

.aspect-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.aspect-tab-main {
  flex: 1 1 auto;
}

.aspect-tab-title {
  min-width: 0;
  white-space: nowrap;
  word-break: keep-all;
}

.aspect-score-short {
  display: none;
}

@media (max-width: 390px) {
  .board-relation-card {
    grid-template-columns: 36px minmax(0, 1fr);
    gap: 0.375rem;
    padding-left: 0.625rem;
    padding-right: 0.625rem;
  }

  .board-relation-label {
    padding-left: 0;
    font-size: 0.75rem;
  }

  .board-relation-value {
    font-size: 1.125rem;
    letter-spacing: 0;
  }

  .aspect-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 340px) {
  .aspect-tab {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
  }

  .aspect-tab-icon {
    display: none;
  }

  .aspect-score-badge {
    padding-left: 0.1875rem;
    padding-right: 0.1875rem;
  }

  .aspect-score-full {
    display: none;
  }

  .aspect-score-short {
    display: inline;
  }
}
</style>
