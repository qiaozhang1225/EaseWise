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
  Scale,
  Flame,
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
const showReviewConfirmDialog = ref(false);
const aspectSectionRef = ref<HTMLElement | null>(null);
const skipReviewConfirmHint = ref(true);
const skipFutureReviewConfirm = ref(
  readStoredFlag(EASEWISE_STORAGE_KEYS.reviewConfirmSkipPrompt, EASEWISE_STORAGE_KEYS.legacyReviewConfirmSkipPrompt),
);
const pollingReviewId = ref<string | null>(null);
let disposed = false;
let pollingPromise: Promise<ReviewRecord> | null = null;

const waitingSteps = [
  {
    title: '校验号码信息',
    desc: '检查号码格式并准备本次评测参数',
  },
  {
    title: '生成盘面结果',
    desc: '整理综合评分、盘面概览和总评内容',
  },
  {
    title: '整理重点维度',
    desc: '准备长期使用建议和九个重点维度结果',
  },
];

const progressStageToPhase: Record<ReviewProgressStage, number> = {
  queued: 0,
  scoring: 0,
  rendering: 1,
  finalizing: 2,
  completed: 2,
  failed: 2,
};

const aspectUiMap: Record<string, { icon: Component; tint: string; textTint: string }> = {
  career: { icon: Shield, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  wealth: { icon: TrendingUp, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  love: { icon: Heart, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  health: { icon: HeartPulse, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  acad: { icon: BookOpen, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  social: { icon: Users, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  travel: { icon: Compass, tint: 'bg-red-50 text-red-600', textTint: 'text-red-600' },
  law: { icon: Scale, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  risk: { icon: Flame, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
};

const currentReview = computed(() => state.currentReview);
const userPoints = computed(() => state.points?.balance ?? 0);
const effectiveBaseReviewPoints = computed(() => reviewBasePointsCost.value ?? DEFAULT_BASE_REVIEW_POINTS);
const effectiveAspectUnlockPoints = computed(
  () => currentReview.value?.aspect_unlock_points ?? aspectUnlockPointsCost.value ?? DEFAULT_ASPECT_UNLOCK_POINTS,
);
const waitingPhase = computed(() => currentProgressStage.value ? progressStageToPhase[currentProgressStage.value] : 0);
const waitingMessage = computed(
  () => currentProgressMessage.value || waitingSteps[waitingPhase.value]?.desc || '正在准备本次评测内容，请稍候。',
);
const activeBoardGridCell = computed(() => {
  const board = currentReview.value?.board;
  return board?.grid_cells.find((cell) => cell.is_active) ?? null;
});
const reviewAspects = computed<DisplayAspect[]>(() =>
  (currentReview.value?.aspects ?? []).map((aspect) => ({
    ...aspect,
    ...(aspectUiMap[aspect.aspect_id] || {
      icon: Sparkles,
      tint: 'bg-brand-paper text-brand-secondary',
      textTint: 'text-brand-secondary',
    }),
  })),
);
const selectedAspect = computed(() => reviewAspects.value[activeAspect.value] || null);
const reviewPhoneDisplay = computed(() => currentReview.value?.phone_number || phoneNumber.value);
const reviewGenderDisplay = computed(() => (currentReview.value?.gender || gender.value) === 'male' ? '男' : '女');
const reviewScore = computed(() => currentReview.value?.score ?? 0);
const summaryTitle = computed(() => currentReview.value?.summary?.title || '整体判断');
const summaryContent = computed(
  () => currentReview.value?.summary?.content || '系统会根据盘面结果生成整体使用判断。',
);
const boardAnalysisTitle = computed(() => currentReview.value?.board_analysis?.title || '盘面分析 / 总评');
const boardAnalysisContent = computed(
  () => currentReview.value?.board_analysis?.content || '盘面详细说明生成后会显示在这里。',
);
const stabilityLabel = computed(() => currentReview.value?.stability_judgement?.label || '稳定性判断');
const stabilityValue = computed(
  () => currentReview.value?.stability_judgement?.value || '结果生成后会显示稳定性判断',
);
const boardMainAxis = computed(() => currentReview.value?.board?.summary?.main_axis || '盘面主轴生成后会显示在这里。');
const boardMainContradiction = computed(
  () => currentReview.value?.board?.summary?.main_contradiction || '核心矛盾生成后会显示在这里。',
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
      label: '尾干关系',
      labelTop: '尾干',
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
const longTermAdvice = computed(() => {
  const advice = currentReview.value?.long_term_advice ?? [];
  if (advice.length > 0) {
    return advice;
  }
  return ['建议结合整体评分、盘面信息和当前目标，再决定是否作为长期主力号码使用。'];
});

function showToast(message: string): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, 2200);
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
}

function resolveDefaultAspectIndex(aspects: DisplayAspect[]): number {
  const firstUnlockedIndex = aspects.findIndex((aspect) => aspect.is_unlocked);
  return firstUnlockedIndex >= 0 ? firstUnlockedIndex : (aspects.length ? 0 : -1);
}

function applyCompletedReviewState(review: ReviewRecord, options: { showToastOnComplete?: boolean } = {}): void {
  phoneNumber.value = sanitizePhone(review.phone_number || review.phone || '');
  gender.value = review.gender;
  currentProgressStage.value = review.progress_stage;
  currentProgressMessage.value = review.progress_message || '';
  errorType.value = 'none';
  errorDetail.value = '';
  closeReviewConfirmDialog();
  appState.value = 'result';
  activeAspect.value = resolveDefaultAspectIndex(reviewAspects.value);

  if (options.showToastOnComplete) {
    showToast('评测完成，可查看整体结果与重点维度。');
  }
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
    applyCompletedReviewState(review);
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
        applyCompletedReviewState(completedReview);
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

onMounted(() => {
  void bootstrapApp();
});

onUnmounted(() => {
  disposed = true;
});

async function pollReviewUntilReady(review: ReviewRecord): Promise<ReviewRecord> {
  let latestReview = review;

  for (let attempt = 0; attempt < 30; attempt += 1) {
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

    await sleep(900);
    latestReview = await refreshCurrentReview(latestReview.id);
  }

  throw new Error('评测时间比预期更长，请稍后在“我的”页面查看结果。');
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

  errorType.value = 'none';
  errorDetail.value = '';
  currentProgressStage.value = 'queued';
  currentProgressMessage.value = '评测任务已创建，等待开始';
  appState.value = 'waiting';

  try {
    await bootstrapApp();
    const review = await submitPhoneReview({
      phone: cleanPhone,
      gender: gender.value,
      include_markdown: true,
    });
    const completedReview = await startReviewPolling(review);

    if (disposed) {
      return;
    }

    applyCompletedReviewState(completedReview, { showToastOnComplete: true });
  } catch (error) {
    handleReviewSyncError(error);
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
    await unlockAspect(review.id, aspect.aspect_id);
    showToast(`已解锁「${aspect.title}」详细分析。`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 402) {
      setError('unlock_points_insufficient');
      return;
    }
    setError('request_failed', humanizeError(error));
  }
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
    showToast('当前九个重点维度均已解锁。');
    void scrollToAspectSection();
    return;
  }
  activeAspect.value = nextLockedIndex;
  void scrollToAspectSection();
}

function resolveHeaderOffset(): number {
  if (typeof window === 'undefined') {
    return 80;
  }

  const header = document.querySelector('header');
  const headerHeight = header instanceof HTMLElement ? header.offsetHeight : 64;
  return headerHeight + 14;
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
    return `解锁单个重点维度需要消耗 ${effectiveAspectUnlockPoints.value} 积分。您当前可用积分为 ${userPoints.value} 分。`;
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
      ctx.fillText(truncateText(summaryTitle.value, 26), 90, 400);

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

      ctx.textAlign = 'left';
      ctx.fillStyle = '#FEE2E2';
      roundRect(ctx, leftBoxX + 18, leftBoxY + 172, 82, 28, 8);
      ctx.fill();
      ctx.fillStyle = '#B91C1C';
      ctx.font = 'bold 16px serif';
      ctx.fillText(truncateText(palace.door, 6), leftBoxX + 32, leftBoxY + 191);

      ctx.strokeStyle = '#E5E7EB';
      ctx.beginPath();
      ctx.moveTo(leftBoxX + 160, leftBoxY + 176);
      ctx.lineTo(leftBoxX + 160, leftBoxY + 202);
      ctx.stroke();
      ctx.textAlign = 'center';
      ctx.fillStyle = '#4F46E5';
      ctx.font = 'bold 13px monospace';
      ctx.fillText(truncateText(palace.heavenStem, 4), leftBoxX + 188, leftBoxY + 182);
      ctx.strokeStyle = '#CBD5E1';
      ctx.beginPath();
      ctx.moveTo(leftBoxX + 174, leftBoxY + 186);
      ctx.lineTo(leftBoxX + 202, leftBoxY + 186);
      ctx.stroke();
      ctx.fillStyle = '#475569';
      ctx.fillText(truncateText(palace.earthStem, 4), leftBoxX + 188, leftBoxY + 200);

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
      ctx.fillText('【核心使用建议】', 60, 965);

      ctx.fillStyle = '#4B5563';
      ctx.font = '14px sans-serif';
      ctx.fillText(truncateText(stabilityValue.value, 34), 60, 995);
      ctx.fillText(truncateText(longTermAdvice.value[0] || '', 34), 60, 1020);

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

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
</script>

<template>
  <div class="pt-16 pb-32 max-w-md mx-auto w-full relative min-h-screen">
    <transition name="fade">
      <div
        v-if="toast"
        class="fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full text-[13px] shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
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
        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="flex items-center gap-2 mb-2">
            <span class="w-2 h-2 bg-brand-primary rounded-full animate-ping"></span>
            <span class="text-brand-gold-fixed text-[11px] font-bold uppercase tracking-wider">奇门遁甲手机号综合测评</span>
          </div>
          <p class="text-[12px] text-brand-secondary leading-relaxed">
            输入手机号和性别后，系统会给出整体评分、盘面概览等信息，帮助你更快了解这个号码是否适合长期使用。
          </p>
        </section>

        <form class="space-y-5" @submit.prevent="handleReviewSubmitIntent">
          <section class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 text-left">
            <div class="space-y-1.5">
              <label class="text-[11.5px] font-extrabold text-brand-secondary tracking-wide uppercase flex items-center gap-1">
                <span>手机号码 (中国的11位手机号)</span>
                <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  v-model="phoneNumber"
                  type="tel"
                  maxlength="11"
                  enterkeyhint="go"
                  class="w-full bg-brand-paper hover:bg-white text-brand-ink-strong focus:bg-white text-[15px] font-bold p-3.5 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all placeholder-gray-400 font-sans shadow-inner tracking-wider"
                  placeholder="请输入11位中国手机号码"
                />
                <span
                  v-if="phoneNumber.length > 0"
                  @click="phoneNumber = ''"
                  class="absolute right-4 top-1/2 -translate-y-1/2 p-1 bg-gray-200 hover:bg-gray-300 text-gray-500 rounded-full cursor-pointer text-[10px] w-4 h-4 flex items-center justify-center font-bold"
                >
                  ×
                </span>
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[11.5px] font-extrabold text-brand-secondary tracking-wide uppercase">性别</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-150/40">
                <button
                  type="button"
                  @click="gender = 'male'"
                  class="py-2 text-[12.5px] font-bold rounded-lg cursor-pointer transition-all outline-none"
                  :class="gender === 'male' ? 'bg-white text-brand-primary shadow-sm border border-gray-100' : 'text-brand-secondary hover:text-brand-primary'"
                >
                  男
                </button>
                <button
                  type="button"
                  @click="gender = 'female'"
                  class="py-2 text-[12.5px] font-bold rounded-lg cursor-pointer transition-all outline-none"
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
              class="w-full py-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl text-[14px] font-bold shadow-md cursor-pointer outline-none transition-all active:scale-[0.985] flex items-center justify-center gap-1.5"
              :disabled="!phoneNumber || state.booting"
            >
              <Sparkles :size="15" fill="currentColor" />
              <span>{{ state.booting ? '正在连接本地 API...' : `立即扣除 ${effectiveBaseReviewPoints} 积分深度起盘测算` }}</span>
            </button>
          </section>

          <footer class="bg-gray-50/70 p-3.5 rounded-xl border border-gray-100/70 text-[11px] text-brand-secondary leading-relaxed text-center">
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
        class="pt-24 pb-32 max-w-sm mx-auto px-margin-mobile flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6"
      >
        <div class="relative flex items-center justify-center">
          <div class="w-16 h-16 rounded-full border-4 border-brand-primary/10 border-t-brand-primary animate-spin"></div>
          <div class="absolute text-brand-primary">
            <Sparkles :size="24" class="animate-pulse" />
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-[11px] font-bold text-brand-primary">
            阶段 {{ Math.min(waitingPhase + 1, waitingSteps.length) }}/{{ waitingSteps.length }}
          </p>
          <h4 class="font-serif text-[17px] font-bold text-brand-ink-strong">正在生成评测结果...</h4>
          <p class="text-[12.5px] text-brand-secondary leading-relaxed max-w-[85%] mx-auto">
            {{ waitingMessage }}
          </p>
        </div>

        <div class="w-full max-w-[92%] space-y-2.5 text-left">
          <div class="h-2 rounded-full bg-brand-paper overflow-hidden">
            <div
              class="h-full bg-brand-primary rounded-full transition-all duration-500"
              :style="{ width: `${((waitingPhase + 1) / waitingSteps.length) * 100}%` }"
            ></div>
          </div>

          <div
            v-for="(step, index) in waitingSteps"
            :key="step.title"
            class="flex items-start gap-3 rounded-xl border p-3 transition-all"
            :class="index === waitingPhase ? 'bg-white border-brand-primary/20 shadow-sm' : index < waitingPhase ? 'bg-brand-primary/5 border-brand-primary/10' : 'bg-white/70 border-gray-100'"
          >
            <div
              class="mt-0.5 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold shrink-0"
              :class="index < waitingPhase ? 'bg-brand-primary text-white' : index === waitingPhase ? 'bg-brand-primary/10 text-brand-primary' : 'bg-gray-100 text-brand-secondary'"
            >
              <CheckCircle2 v-if="index < waitingPhase" :size="12" />
              <span v-else>{{ index + 1 }}</span>
            </div>
            <div class="space-y-1">
              <p class="text-[12px] font-bold text-brand-ink-strong">{{ step.title }}</p>
              <p class="text-[11px] text-brand-secondary leading-relaxed">{{ index === waitingPhase ? waitingMessage : step.desc }}</p>
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
            class="py-2 px-3.5 bg-white border border-gray-100 hover:bg-gray-50 text-brand-secondary rounded-lg text-[12px] font-bold cursor-pointer outline-none transition-all flex items-center gap-1 shadow-sm"
          >
            <ArrowLeft :size="13" />
            <span>重新评测</span>
          </button>

          <button
            @click="handleExportImage"
            class="py-2 px-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-lg text-[12px] font-bold cursor-pointer outline-none transition-all flex items-center gap-1 shadow-sm"
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
              <span class="text-brand-secondary font-mono text-[11px] font-bold uppercase tracking-wider">评测已完成</span>
            </div>

            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="min-w-0 truncate text-[18px] leading-tight font-bold font-serif text-brand-ink-strong">
                号码：{{ reviewPhoneDisplay }}
              </h3>
              <span class="inline-flex items-center rounded-full bg-brand-paper px-2 py-0.5 text-[11px] font-bold text-brand-secondary shrink-0">
                性别 · {{ reviewGenderDisplay }}
              </span>
            </div>
          </div>

          <div class="text-center shrink-0">
            <div class="w-[72px] h-[72px] rounded-full border-[2.5px] border-brand-accent flex flex-col items-center justify-center bg-brand-primary text-white shadow-md">
              <span class="text-[9.5px] opacity-85 leading-none">综合评分</span>
              <span class="text-[27px] font-serif font-black text-brand-accent mt-0.5 leading-none">{{ reviewScore }}</span>
            </div>
          </div>
        </section>

        <section class="space-y-2.5">
          <h4 class="font-serif text-[12px] font-bold text-brand-secondary tracking-wider uppercase flex items-center gap-1.5 text-left">
            <Star :size="13" class="text-brand-primary fill-current shrink-0" />
            <span>奇门遁甲：立体定盘局象</span>
          </h4>

          <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm space-y-3.5 font-serif text-brand-ink-strong">
            <div class="grid grid-cols-[160px_minmax(0,1fr)] gap-4 items-stretch">
              <div class="relative w-[160px] h-[160px] bg-brand-paper border border-brand-primary/20 rounded-xl px-4 py-3.5 flex flex-col justify-between text-left shadow-sm shrink-0">
                <div class="absolute -left-3.5 top-1/2 -translate-y-1/2 w-7 h-9 bg-brand-primary border border-brand-primary-strong text-white rounded-md shadow-md flex items-center justify-center font-serif text-[15px] font-black tracking-[0.08em] z-10 select-none">
                  {{ singlePalaceData.trigger }}
                </div>

                <div class="flex justify-between items-center text-[12.5px] leading-tight select-none z-10 gap-2">
                  <span class="px-1.5 py-0.5 bg-purple-500/10 text-purple-700 font-serif text-[13.5px] font-black rounded-md leading-none">
                    {{ singlePalaceData.deity }}
                  </span>
                  <span class="px-1.5 py-0.5 bg-indigo-500/10 text-indigo-700 font-serif text-[13.5px] font-black rounded-md leading-none">
                    {{ singlePalaceData.star }}
                  </span>
                </div>

                <div class="absolute inset-0 flex items-center justify-center pointer-events-none select-none opacity-[0.05] z-0">
                  <span class="font-serif font-black text-[60px] tracking-widest">
                    {{ singlePalaceData.palaceShort }}
                  </span>
                </div>

                <div class="text-center z-10 py-0.5">
                  <p class="font-serif font-bold text-slate-400 text-[12px] leading-none mb-1 tracking-[0.18em]">
                    {{ singlePalaceData.palaceName }}
                  </p>
                  <p class="font-serif font-black text-brand-primary-strong text-[21px] leading-none">
                    {{ singlePalaceData.direction }}
                  </p>
                </div>

                <div class="flex justify-between items-end text-[14px] font-black z-10 leading-none gap-3">
                  <span class="px-2 py-1 bg-red-500/10 text-red-700 rounded-md font-serif text-[13.5px] font-black leading-none">
                    {{ singlePalaceData.door }}
                  </span>

                  <div class="flex flex-col items-center justify-center text-[15px] font-serif font-black leading-none border-l border-gray-200 pl-2.5 select-none shrink-0 min-w-[38px]">
                    <span class="text-brand-primary tracking-[0.08em]">{{ singlePalaceData.heavenStem }}</span>
                    <span class="w-5 border-t border-gray-300 my-1"></span>
                    <span class="text-brand-secondary tracking-[0.08em]">{{ singlePalaceData.earthStem }}</span>
                  </div>
                </div>
              </div>

              <div class="h-[160px] min-w-0 grid grid-rows-2 gap-2 border-l border-gray-100 pl-4">
                <div
                  v-for="item in boardRelationCards"
                  :key="item.label"
                  class="bg-brand-paper hover:bg-gray-50/70 px-3 py-2.5 border border-gray-100/55 rounded-xl transition-all grid grid-cols-[42px_minmax(0,1fr)] items-center gap-2 text-left"
                >
                  <div class="font-serif text-[13px] text-brand-secondary font-black leading-none flex flex-col gap-1.5 pl-1">
                    <span>{{ item.labelTop }}</span>
                    <span>{{ item.labelBottom }}</span>
                  </div>
                  <p class="font-serif font-black text-[20px] leading-none text-right min-w-0" :class="item.valueClass">
                    {{ item.value }}
                  </p>
                </div>
              </div>
            </div>

            <div class="space-y-1.5 text-left bg-white rounded-2xl border border-gray-100 shadow-sm p-3">
              <div class="flex items-center gap-1.5 border-b border-gray-100/60 pb-1">
                <span class="w-1.5 h-3.5 bg-amber-500 rounded-sm"></span>
                <h5 class="font-serif text-[12.5px] font-black text-brand-ink-strong tracking-wide">四害干扰特征</h5>
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

            <div class="bg-amber-500/[0.02] border border-amber-100/70 rounded-xl p-3 space-y-2 text-left text-[12.5px] font-serif transition-all">
              <div class="flex flex-wrap items-center gap-2 select-none">
                <span class="text-[12px] text-brand-secondary/80 font-black shrink-0">特殊组合:</span>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="combo in (boardSpecialCombos.length ? boardSpecialCombos : ['当前未检出明显特殊组合'])"
                    :key="combo"
                    class="px-2 py-0.5 font-serif text-[11.5px] font-black bg-amber-500/10 text-amber-700 border border-amber-200/50 rounded-md"
                  >
                    {{ combo }}
                  </span>
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-2 select-none">
                <span class="text-[12px] text-brand-secondary/80 font-black shrink-0">结构封顶:</span>
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="item in boardStructureCapTags"
                    :key="item"
                    class="px-2 py-0.5 font-serif text-[11.5px] font-black bg-amber-500/10 text-amber-700 border border-amber-200/50 rounded-md"
                  >
                    {{ item }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="space-y-2 text-left">
          <h4 class="text-[12px] font-bold text-brand-secondary tracking-wider uppercase flex items-center gap-1.5">
            <Sparkles :size="13" class="text-brand-primary shrink-0" />
            <span>{{ boardAnalysisTitle }}</span>
          </h4>

          <div class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm space-y-3">
            <div class="bg-brand-primary/5 rounded-xl border border-brand-primary/10 p-3">
              <p class="text-[12px] font-bold text-brand-primary-strong">{{ summaryTitle }}</p>
              <p class="mt-1 text-[13px] text-brand-ink leading-relaxed">
                {{ summaryContent }}
              </p>
            </div>
            <div class="bg-brand-paper/70 rounded-xl border border-gray-100 p-3">
              <p class="text-[11px] font-bold text-brand-secondary uppercase tracking-wider">盘面主轴</p>
              <p class="mt-1 text-[12px] font-bold text-brand-ink leading-relaxed">{{ boardMainAxis }}</p>
              <p class="mt-2 text-[12px] text-brand-secondary leading-relaxed">
                核心矛盾：{{ boardMainContradiction }}
              </p>
            </div>
            <p class="text-[12px] text-brand-secondary leading-relaxed">
              {{ boardAnalysisContent }}
            </p>
          </div>
        </section>

        <section class="bg-brand-primary p-5.5 rounded-2xl text-white shadow-sm space-y-4 text-left">
          <h4 class="text-[15px] font-bold flex items-center gap-2">
            <Lightbulb :size="18" class="text-brand-accent shrink-0 animate-pulse" />
            <span>长期使用建议 / 稳定性判断</span>
          </h4>
          <div class="inline-flex items-center rounded-full bg-white/12 px-3 py-1 text-[11px] font-bold text-brand-accent">
            {{ stabilityLabel }}：{{ stabilityValue }}
          </div>
          <ul class="space-y-3 text-[12px] opacity-90 leading-relaxed font-sans">
            <li v-for="advice in longTermAdvice" :key="advice" class="flex gap-2">
              <CheckCircle2 :size="16" class="text-brand-accent shrink-0" fill="currentColor" stroke="#4F46E5" />
              <span>{{ advice }}</span>
            </li>
          </ul>
        </section>

        <section ref="aspectSectionRef" class="space-y-2">
          <div class="flex justify-between items-baseline text-left">
            <h4 class="text-[12px] font-bold text-brand-secondary tracking-wider uppercase flex items-center gap-1.5">
              <Clock :size="13" class="text-brand-primary shrink-0" />
              <span>九个重点维度</span>
            </h4>
            <span class="text-[10px] text-brand-secondary">
              余积分: <span class="text-brand-primary-strong font-black font-sans">{{ userPoints }}</span>
            </span>
          </div>

          <div class="grid grid-cols-3 gap-1.5">
            <button
              v-for="(aspect, idx) in reviewAspects"
              :key="aspect.aspect_id"
              @click="handleAspectClick(idx)"
              class="relative h-[34px] px-2 rounded-xl text-[10.5px] font-extrabold flex items-center justify-between gap-1 transition-all outline-none cursor-pointer border"
              :class="[
                activeAspect === idx
                  ? 'bg-brand-primary text-white border-transparent shadow-sm'
                  : !aspect.is_unlocked
                  ? 'bg-brand-paper/85 text-brand-secondary/70 border-gray-150'
                  : 'bg-white text-brand-secondary border-gray-150 hover:bg-gray-50'
              ]"
            >
              <div class="flex items-center gap-1 min-w-0">
                <component
                  :is="aspect.icon"
                  :size="11.5"
                  :class="[
                    activeAspect === idx ? 'text-white' : aspect.is_unlocked ? 'text-brand-primary' : 'text-brand-secondary/40'
                  ]"
                  class="shrink-0"
                />
                <span class="truncate tracking-tight">{{ (aspect.short_title || aspect.title).slice(0, 2) }}</span>
              </div>

              <div class="shrink-0 flex items-center">
                <span
                  v-if="aspect.is_unlocked"
                  class="text-[8.5px] font-black px-1 py-0.5 rounded-sm leading-none shrink-0"
                  :class="[
                    activeAspect === idx
                      ? 'bg-white/20 text-white'
                      : aspect.level === '上吉' || aspect.level === '中吉'
                      ? 'bg-green-500/10 text-green-600'
                      : aspect.level === '落陷'
                      ? 'bg-red-500/10 text-red-600'
                      : 'bg-amber-500/10 text-amber-600'
                  ]"
                >
                  {{ aspect.level || '已开' }}
                </span>
                <span
                  v-else
                  class="text-[8px] font-bold px-1 py-0.5 rounded-sm leading-none shrink-0"
                  :class="[
                    activeAspect === idx ? 'bg-white/20 text-white' : 'text-brand-gold-fixed bg-amber-50 border border-amber-200/50'
                  ]"
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
              :key="selectedAspect.aspect_id"
              class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 text-left"
            >
              <div v-if="selectedAspect.is_unlocked" class="space-y-4">
                <div class="flex justify-between items-center pb-3 border-b border-gray-50">
                  <div class="flex items-center gap-2">
                    <component :is="selectedAspect.icon" :size="16" class="text-brand-primary shrink-0" />
                    <span class="font-serif text-[15px] font-extrabold text-brand-ink-strong">
                      {{ selectedAspect.title }} · 详细结果
                    </span>
                  </div>
                  <span class="px-2.5 py-1 rounded-full text-[11px] font-bold" :class="selectedAspect.tint">
                    综合考量：{{ selectedAspect.level || '已解锁' }}
                  </span>
                </div>

                <div class="space-y-3 text-[13px] text-brand-secondary">
                  <div class="bg-brand-primary/5 p-3 rounded-xl border border-brand-primary/10">
                    <p class="font-bold text-brand-primary-strong text-[13px]">核心判断</p>
                    <p class="text-brand-ink mt-1 font-medium">{{ selectedAspect.core_judge }}</p>
                  </div>

                  <div>
                    <p class="font-bold text-brand-ink-strong text-[13px] mb-1">详细说明</p>
                    <p class="leading-relaxed whitespace-pre-line text-brand-secondary font-normal">
                      {{ selectedAspect.explain }}
                    </p>
                  </div>

                  <div v-if="selectedAspect.signal" class="pt-2 border-t border-gray-50 flex items-baseline gap-2 text-[12px]">
                    <span class="font-bold text-brand-gold-fixed text-[12px] shrink-0">提示信号：</span>
                    <span class="text-brand-ink leading-relaxed font-semibold">{{ selectedAspect.signal }}</span>
                  </div>

                  <div v-if="selectedAspect.suggestion" class="bg-amber-500/5 p-3 rounded-xl border border-amber-500/10 text-amber-800 text-[12px] leading-relaxed flex items-start gap-1.5">
                    <Lightbulb :size="14" class="text-amber-600 shrink-0 mt-0.5" />
                    <div>
                      <span class="font-bold text-amber-700">使用建议: </span>
                      <span>{{ selectedAspect.suggestion }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="py-6 flex flex-col items-center justify-center text-center space-y-4">
                <div class="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary">
                  <Lock :size="22" class="animate-bounce" />
                </div>
                <div class="max-w-[85%] mx-auto">
                  <h5 class="font-bold text-[15px] font-serif text-brand-ink-strong">
                    查看「{{ selectedAspect.title }}」详细分析
                  </h5>
                  <p class="text-[12px] text-brand-secondary mt-1 leading-relaxed">
                    该维度属于深度内容，默认需要额外消耗 {{ selectedAspect.unlock_points || effectiveAspectUnlockPoints }} 积分后查看。
                  </p>
                </div>
                <button
                  @click="handleUnlockAspect(activeAspect)"
                  class="px-6 py-2.5 bg-brand-primary text-white rounded-full font-bold text-[13px] shadow-sm hover:bg-brand-primary-strong outline-none cursor-pointer flex items-center gap-1.5 mx-auto"
                >
                  <Lock :size="12" fill="currentColor" />
                  <span>消耗 {{ selectedAspect.unlock_points || effectiveAspectUnlockPoints }} 积分立即解锁</span>
                </button>
              </div>
            </div>

            <div
              v-else
              class="p-4 bg-white rounded-2xl border border-gray-100 text-center text-[12px] text-brand-secondary/80 flex items-center justify-center gap-1.5 shadow-sm"
            >
              <Sparkles :size="13" class="text-brand-primary" fill="currentColor" />
              <span>点击上方卡片，可查看或解锁对应维度的详细分析与使用建议。</span>
            </div>
          </transition>
        </section>

        <section class="bg-white p-4.5 rounded-xl border border-gray-100 flex flex-col gap-3 text-center">
          <span class="text-[11px] font-bold text-brand-secondary uppercase tracking-wider block">
            —— 接下来，你可以继续查看以下内容 ——
          </span>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="emit('navigate-to-tab', 'agent')"
              class="py-3 px-2 bg-brand-primary text-white rounded-lg text-[12px] font-bold hover:bg-brand-primary-strong transition-all cursor-pointer flex items-center justify-center gap-1.5 outline-none border-none"
            >
              <MessageSquare :size="14" />
              <span>有疑问，去问智能体</span>
            </button>

            <button
              @click="handleSelectNextLockedAspect"
              class="py-3 px-2 bg-white border border-brand-primary text-brand-primary rounded-lg text-[12px] font-bold hover:bg-brand-primary/5 transition-all cursor-pointer flex items-center justify-center gap-1.5 outline-none"
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
                <p class="text-[13px] font-black text-brand-ink-strong">联系客服获取后续支持</p>
                <p class="text-[11px] text-brand-secondary mt-0.5">{{ customerServiceGuidance }}</p>
              </div>
            </div>
            <div class="text-brand-primary font-bold text-[11px] bg-brand-primary/10 group-hover:bg-brand-primary/20 px-2.5 py-1 rounded-full flex items-center gap-1 shrink-0">
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
          <h3 class="font-serif text-[20px] font-bold text-brand-ink-strong">
            {{ resolveErrorTitle() }}
          </h3>
          <p class="text-[13px] text-brand-secondary leading-relaxed font-sans">
            {{ resolveErrorBody() }}
          </p>
        </div>

        <div
          v-if="errorType === 'insufficient_points' || errorType === 'unlock_points_insufficient'"
          class="bg-white p-4.5 rounded-xl border border-gray-100 max-w-[95%] text-left space-y-3.5 shadow-sm"
        >
          <div class="flex items-start gap-2 text-[12.5px] text-brand-secondary leading-relaxed font-sans">
            <Lightbulb :size="16" class="text-brand-primary shrink-0 mt-0.5" />
            <div>
              <span class="font-bold text-brand-ink-strong">联系客服支持: </span>
              <span>{{ customerServiceGuidance }}</span>
            </div>
          </div>

          <div class="bg-brand-paper p-3 rounded-xl flex items-center justify-between border border-gray-100 font-sans">
            <div class="text-left font-mono">
              <p class="text-[10px] text-brand-secondary">客服联系方式：</p>
              <p class="text-[14px] font-bold text-brand-ink-strong">{{ customerServiceContact }}</p>
            </div>
            <button
              @click="handleCopyServiceContact"
              class="px-3.5 py-1.5 bg-brand-primary text-white hover:bg-brand-primary-strong text-[11px] font-bold rounded-lg cursor-pointer outline-none flex items-center gap-1 shrink-0 transition-all shadow-sm"
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
            class="w-full py-3 bg-brand-primary text-white rounded-xl font-bold text-[14px] shadow-sm hover:bg-brand-primary-strong active:scale-[0.98] transition-all cursor-pointer outline-none border-none"
          >
            <span>
              {{ errorType === 'unlock_points_insufficient' ? '返回评测结果' : '返回重新输入' }}
            </span>
          </button>

          <button
            v-if="errorType === 'insufficient_points' || errorType === 'unlock_points_insufficient'"
            @click="emit('navigate-to-tab', 'profile')"
            class="w-full py-3 bg-white border border-brand-primary/20 text-brand-primary rounded-xl font-bold text-[14px] hover:bg-brand-primary/5 active:scale-[0.98] transition-all cursor-pointer outline-none"
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
            <h4 class="font-serif text-[17.5px] font-black text-brand-ink-strong leading-none">
              确认开始评测
            </h4>
          </div>

          <div class="px-1 text-center pt-1">
            <p class="text-[14px] text-brand-secondary font-semibold leading-relaxed">
              是否消耗 <span class="text-brand-primary font-black text-[15.5px] mx-0.5">{{ effectiveBaseReviewPoints }} 积分</span> 进行手机号评测？
            </p>
          </div>

          <div class="flex items-center justify-center gap-2 py-0.5 select-none">
            <label class="inline-flex items-center gap-2 cursor-pointer">
              <input
                v-model="skipReviewConfirmHint"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-brand-primary focus:ring-brand-primary/40 cursor-pointer accent-brand-primary"
              />
              <span class="text-[12px] text-brand-secondary/90 font-extrabold">下次不再提示此信息</span>
            </label>
          </div>

          <div class="flex gap-3 pt-1 text-[13px]">
            <button
              type="button"
              class="flex-1 py-2 border border-gray-200 text-gray-600 rounded-xl font-bold hover:bg-slate-50 transition-colors cursor-pointer outline-none select-none"
              @click="closeReviewConfirmDialog"
            >
              取消
            </button>
            <button
              type="button"
              class="flex-1 py-2 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl font-black shadow-sm transition-colors cursor-pointer outline-none select-none"
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
</style>
