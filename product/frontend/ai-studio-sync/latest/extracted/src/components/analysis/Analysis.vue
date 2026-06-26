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
  AlertCircle,
  Sparkles,
  Lightbulb,
  CheckCircle2,
  MessageSquare,
  Plus,
  Lock,
  Download,
  Volume2,
} from 'lucide-vue-next';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../../config/pricing';
import { EASEWISE_STORAGE_KEYS } from '../../constants/storage';
import { ApiError } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { useVoicePlayback, type VoiceSpeakResult } from '../../composables/useVoicePlayback';
import type { Gender, ReviewAspect, ReviewProgressStage, ReviewRecord } from '../../types/api';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
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
  isGuestUser,
  submitPhoneReview,
  refreshCurrentReview,
  unlockAspect,
  requestRegisteredUser,
  reviewBasePointsCost,
  aspectUnlockPointsCost,
  customerServiceCopyForScene,
  openCustomerServiceModal,
  humanizeError,
} = useEaseWiseApp();

const voicePlayback = useVoicePlayback({
  getAccessToken: () => state.accessToken,
  getVoiceConfig: () => state.runtimeConfig?.modules.voice,
  showToast,
});

const appState = ref<AppViewState>('input');
const phoneNumber = ref('');
const gender = ref<Gender>('male');
const activeAspect = ref(-1);
const errorType = ref<ErrorType>('none');
const errorDetail = ref('');
const toast = ref<string | null>(null);
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
let waitingFastForwardTimer: ReturnType<typeof setInterval> | null = null;
let waitingStartedAt = 0;

const ASPECT_UNLOCK_RETRY_LIMIT = 45;
const ASPECT_UNLOCK_RETRY_DELAY_MS = 2000;
const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const REVIEW_TIMEOUT_MESSAGE = '评测时间比预期更长，请稍后在“我的”页面查看结果。';
const WAITING_PHASE_DURATION_MS = 500;
const WAITING_POEM_INTERVAL_MS = 500;
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

const aspectVoiceNameMap: Record<string, string> = {
  career: '事业',
  wealth: '财运',
  love: '感情',
  health: '健康',
  acad: '学业',
  fortune: '运势',
  investment: '投资',
  travel: '出行',
  social: '人际',
  family: '家庭',
  personality: '性格',
  fengshui: '风水',
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
const voiceEnabled = computed(() => voicePlayback.enabled.value);
const voiceAutoplayEnabled = computed(() => voicePlayback.autoplayEnabled.value);
const phoneSummaryVoiceKey = computed(() => currentReview.value ? `phone_summary:${currentReview.value.id}:${currentReview.value.updated_at || ''}` : null);
const stabilityVoiceKey = computed(() => currentReview.value ? `phone_stability:${currentReview.value.id}:${currentReview.value.updated_at || ''}` : null);
const selectedAspectVoiceKey = computed(
  () => currentReview.value && selectedAspect.value ? `phone_aspect:${currentReview.value.id}:${selectedAspect.value.aspect_key}` : null,
);
const phoneSummaryVoicePlaying = computed(() => Boolean(phoneSummaryVoiceKey.value && voicePlayback.currentKey.value === phoneSummaryVoiceKey.value && voicePlayback.status.value === 'playing'));
const phoneSummaryVoiceLoading = computed(() => Boolean(phoneSummaryVoiceKey.value && voicePlayback.currentKey.value === phoneSummaryVoiceKey.value && voicePlayback.status.value === 'loading'));
const stabilityVoicePlaying = computed(() => Boolean(stabilityVoiceKey.value && voicePlayback.currentKey.value === stabilityVoiceKey.value && voicePlayback.status.value === 'playing'));
const stabilityVoiceLoading = computed(() => Boolean(stabilityVoiceKey.value && voicePlayback.currentKey.value === stabilityVoiceKey.value && voicePlayback.status.value === 'loading'));
const selectedAspectVoicePlaying = computed(() => Boolean(selectedAspectVoiceKey.value && voicePlayback.currentKey.value === selectedAspectVoiceKey.value && voicePlayback.status.value === 'playing'));
const selectedAspectVoiceLoading = computed(() => Boolean(selectedAspectVoiceKey.value && voicePlayback.currentKey.value === selectedAspectVoiceKey.value && voicePlayback.status.value === 'loading'));
const selectedAspectVoiceLabel = computed(() => {
  const aspect = selectedAspect.value;
  if (!aspect) {
    return '听专项';
  }
  const label = aspectVoiceNameMap[aspect.aspect_key] || aspect.short_title || aspect.title || '专项';
  return `听${label}`;
});
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
  () => selectedAspectWaitingForGeneration.value ? `正在生成「${unlockWaitingAspectTitle.value}」` : `正在读取「${unlockProcessingTitle.value}」内容`,
);
const reviewPhoneDisplay = computed(() => currentReview.value?.masked_phone || currentReview.value?.phone || phoneNumber.value);
const reviewGenderDisplay = computed(() => currentReview.value?.gender === 'female' ? '女' : '男');

const stabilityLabel = computed(() => currentReview.value?.stability_detail?.verdict || '良好使用建议');
const stabilityValue = computed(() => currentReview.value?.stability_detail?.content || '适合长期作为主要联络工具。');

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
    trigger: board?.center_basis?.trigger || '待起盘',
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
      valueClass: (relations?.palace_door_relation || '').includes('克') ? 'text-red-655' : 'text-brand-ink-strong',
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
  return riskPairs.map((pair) => `${pair} 风险数`);
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

const phoneSummaryTitle = computed(() => cleanDisplayText(currentReview.value?.phone_summary?.title) || '极具爆发潜力之格局。');
const phoneSummaryRisk = computed(() => cleanDisplayText(currentReview.value?.phone_summary?.risk) || '稍有口舌是非之隐。');
const phoneSummaryUsageGuidance = computed(() => cleanDisplayText(currentReview.value?.phone_summary?.usage_guidance) || '宜沉稳守成，方能步步为营。');

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

function showToast(message: string, duration = 2200): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, duration);
}

async function handlePhoneSummaryVoiceClick(): Promise<void> {
  voicePlayback.primeAudioSession();
  if (phoneSummaryVoicePlaying.value || phoneSummaryVoiceLoading.value) {
    stopVoiceAndDisableAutoplay();
    return;
  }
  const review = currentReview.value;
  const result = await speakPhoneSummaryWithAutoFollow(review, false);
  if (!result.started) {
    showToast(resolveVoiceFailureMessage('综合评述', result), 3600);
  }
}

async function handleStabilityVoiceClick(): Promise<void> {
  voicePlayback.primeAudioSession();
  if (stabilityVoicePlaying.value || stabilityVoiceLoading.value) {
    stopVoiceAndDisableAutoplay();
    return;
  }
  const result = await voicePlayback.speakStability(currentReview.value);
  if (!result.started) {
    showToast(resolveVoiceFailureMessage('长期建议', result), 3600);
  }
}

async function handleSelectedAspectVoiceClick(): Promise<void> {
  voicePlayback.primeAudioSession();
  if (selectedAspectVoicePlaying.value || selectedAspectVoiceLoading.value) {
    stopVoiceAndDisableAutoplay();
    return;
  }
  const result = await voicePlayback.speakAspect(currentReview.value, selectedAspect.value);
  if (!result.started) {
    showToast(resolveVoiceFailureMessage(selectedAspectVoiceLabel.value || '专项', result), 3600);
  }
}

function resolveVoiceFailureMessage(subject: string, result: VoiceSpeakResult): string {
  const reason = humanizeVoiceError(result.error);
  return reason ? `${subject}无法播报：${reason}` : `${subject}暂时无法播报。`;
}

function humanizeVoiceError(errorCode: string | undefined): string {
  if (!errorCode) {
    return '';
  }
  if (
    errorCode.includes('tts_not_configured') ||
    errorCode.includes('provider_not_configured') ||
    errorCode.includes('provider_not_supported') ||
    errorCode.includes('nls_token_unavailable')
  ) {
    return '云语音服务未配置可用的 TTS 密钥。';
  }
  if (errorCode.includes('nls_token_fetch_failed') || errorCode.includes('nls_token_missing') || errorCode.includes('nls_token_invalid')) {
    return '阿里云语音 Token 获取失败，请检查 NLS 凭据。';
  }
  if (errorCode === 'browser_speech_unavailable') {
    return '当前浏览器不支持本地语音兜底。';
  }
  if (errorCode === 'audio_play_failed') {
    return '音频加载失败，请检查网络。';
  }
  return '基础媒体引擎播放受限。';
}

function stopVoiceAndDisableAutoplay(): void {
  voicePlayback.stop();
  voicePlayback.setAutoplayEnabled(false);
  showToast('伴随语音播报已手动断开，自动循环播放停用。');
}

async function speakPhoneSummaryWithAutoFollow(review: ReviewRecord | null, auto: boolean): Promise<VoiceSpeakResult> {
  return voicePlayback.speakPhoneSummary(review, { auto });
}

function compactHarmValue(value: string | undefined): string {
  const text = String(value || '').trim();
  if (!text || text === '待生成' || text.includes('待')) {
    return '-';
  }
  return text;
}

function resolveHarmToneClass(value: string | undefined): string {
  const text = String(value || '').trim();
  if (!text || text === '待生成' || text === '-') {
    return 'bg-gray-100 text-gray-500 border-gray-200';
  }
  if (text.includes('无') || text === '吉' || text.includes('未')) {
    return 'bg-emerald-50 text-emerald-700 border-emerald-100';
  }
  return 'bg-red-50 text-red-700 border-red-100';
}

function compactStemRelationValue(val: string | undefined): string {
  const text = String(val || '').trim();
  if (!text || text === '待生成') {
    return '-';
  }
  return text;
}

function readStoredFlag(key: string, legacyKey?: string): boolean {
  if (typeof window === 'undefined') return false;
  const value = window.localStorage.getItem(key);
  if (value !== null) return value === 'true';
  if (legacyKey) {
    const leg = window.localStorage.getItem(legacyKey);
    return leg === 'true';
  }
  return false;
}

function writeStoredFlag(key: string, enabled: boolean, legacyKey?: string): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(key, String(enabled));
  if (legacyKey) window.localStorage.removeItem(legacyKey);
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
  voicePlayback.stop();
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
  if (waitingFastForwardTimer) {
    window.clearInterval(waitingFastForwardTimer);
    waitingFastForwardTimer = null;
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

    clearWaitingVisualTimers();
    if (waitingFastForwardTimer) {
      window.clearInterval(waitingFastForwardTimer);
    }

    waitingFastForwardTimer = window.setInterval(() => {
      if (!disposed && appState.value === 'waiting') {
        if (!isWaitingFinalPhaseReady()) {
          waitingVisualPhase.value += 1;
          waitingProgressValue.value = Math.min(100, waitingProgressValue.value + (100 - waitingProgressValue.value) / 2);
        } else {
          // Finished waiting, apply the pending review
          const finalReview = pendingCompletedReview.value;
          const finalShouldToast = pendingCompletedReviewShouldToast.value;
          pendingCompletedReview.value = null;
          pendingCompletedReviewShouldToast.value = false;
          clearWaitingTimers();
          if (finalReview) {
            applyCompletedReviewState(finalReview, { showToastOnComplete: finalShouldToast });
          }
        }
      } else {
        if (waitingFastForwardTimer) {
          window.clearInterval(waitingFastForwardTimer);
          waitingFastForwardTimer = null;
        }
      }
    }, 250);
    return;
  }

  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  applyCompletedReviewState(review, options);
}

function applyCompletedReviewState(review: ReviewRecord, options: { showToastOnComplete?: boolean } = {}): void {
  const shouldAutoSpeakOnDisplay = lastCompletedReviewId !== review.id;
  lastCompletedReviewId = review.id;
  currentProgressStage.value = review.progress_stage;
  currentProgressMessage.value = review.progress_message || '';
  persistCurrentReview(review);
  appState.value = 'result';
  if (options.showToastOnComplete) {
    showToast('评测报告已就绪！已为您解锁基础宫星格局。');
  }
  if (shouldAutoSpeakOnDisplay && voiceAutoplayEnabled.value) {
    speakPhoneSummaryWithAutoFollow(review, true).catch(() => undefined);
  }
}

function persistCurrentReview(review: ReviewRecord | null): void {
  state.currentReview = review;
  if (review && typeof window !== 'undefined') {
    window.localStorage.setItem(EASEWISE_STORAGE_KEYS.lastReviewId, review.id);
  }
}

async function handlePhoneClick(): Promise<void> {
  const validated = await requestRegisteredUser('手机号评测');
  if (validated) {
    const rawPhone = validatePhoneInput();
    if (!rawPhone) return;
    if (userPoints.value < effectiveBaseReviewPoints.value) {
      setError('insufficient_points');
      return;
    }
    const skipPrompt = readStoredFlag(EASEWISE_STORAGE_KEYS.reviewConfirmSkipPrompt);
    if (skipPrompt) {
      await handleEvaluate(rawPhone);
    } else {
      showReviewConfirmDialog.value = true;
    }
  }
}

function validatePhoneInput(): string | null {
  const cleanPhone = sanitizePhone(phoneNumber.value);
  if (cleanPhone.length !== 11) {
    setError('phone_format');
    return null;
  }
  return cleanPhone;
}

async function handleConfirmReview(): Promise<void> {
  const cleanPhone = validatePhoneInput();
  if (!cleanPhone) return;
  writeStoredFlag(EASEWISE_STORAGE_KEYS.reviewConfirmSkipPrompt, skipReviewConfirmHint.value);
  showReviewConfirmDialog.value = false;
  await handleEvaluate(cleanPhone);
}

async function handleEvaluate(preparedPhone: string): Promise<void> {
  phoneNumber.value = preparedPhone;
  gender.value = gender.value;
  appState.value = 'waiting';
  waitingVisualPhase.value = 0;
  waitingPoemIndex.value = 0;
  waitingProgressValue.value = WAITING_PROGRESS_START_PERCENT;
  currentProgressStage.value = 'queued';
  currentProgressMessage.value = '基础盘面生成中';
  waitingStartedAt = Date.now();
  clearWaitingTimers();
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
    const review = await submitPhoneReview({
      phone: preparedPhone,
      gender: gender.value,
      include_markdown: true,
    });
    const completedReview = await startReviewPolling(review);
    if (!disposed) {
      applyOrDeferCompletedReviewState(completedReview, { showToastOnComplete: true });
    }
  } catch (error) {
    if (!disposed) {
      handleReviewSyncError(error);
    }
  } finally {
    if (!pendingCompletedReview.value || isWaitingFinalPhaseReady()) {
      clearWaitingTimers();
    }
  }
}

async function startReviewPolling(review: ReviewRecord): Promise<ReviewRecord> {
  pollingReviewId.value = review.id;
  pollingPromise = pollReviewUntilReady(review).finally(() => {
    if (pollingReviewId.value === review.id) {
      pollingReviewId.value = null;
    }
    pollingPromise = null;
  });
  return pollingPromise;
}

async function pollReviewUntilReady(review: ReviewRecord): Promise<ReviewRecord> {
  let latestReview = review;
  for (let attempt = 0; attempt < REVIEW_READY_RETRY_LIMIT; attempt += 1) {
    if (disposed) return latestReview;
    currentProgressStage.value = latestReview.progress_stage;
    currentProgressMessage.value = latestReview.progress_message || '';
    if (latestReview.status === 'completed') {
      return latestReview;
    }
    if (latestReview.status === 'failed') {
      throw new Error(latestReview.error_message || latestReview.progress_message || '起盘任务生成失败');
    }
    await sleep(REVIEW_READY_RETRY_DELAY_MS);
    latestReview = await refreshCurrentReview(latestReview.id);
  }
  throw new Error(REVIEW_TIMEOUT_MESSAGE);
}

async function handleUnlockAspect(index: number): Promise<void> {
  const aspect = reviewAspects.value[index];
  if (!aspect) return;
  activeAspect.value = index;
  if (aspect.is_unlocked) return;
  const authenticated = await ensureRegisteredForAction('解锁专项');
  if (!authenticated) return;
  if (userPoints.value < (aspect.unlock_points || effectiveAspectUnlockPoints.value)) {
    setError('unlock_points_insufficient');
    return;
  }
  try {
    await tryUnlockAspectWithWait(currentReview.value!.id, aspect.aspect_key, aspect.title);
  } catch (err) {
    if (isAspectNotReadyError(err)) {
      showToast('专项内容还在起盘预热中，请稍后再试。');
    } else {
      setError('request_failed', humanizeError(err));
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
    showToast(`已解锁「${title}」模块详细奇门解读。`);
    autoSpeakUnlockedAspect(refreshedReview, aspectKey);
    return;
  } catch (error) {
    if (!isAspectNotReadyError(error)) {
      throw error;
    }
  }

  unlockWaitingAspectKey.value = aspectKey;
  unlockingAspectKey.value = null;
  currentProgressStage.value = 'rendering';
  currentProgressMessage.value = `「${title}」正在后台排演推算，由于数理庞杂系统正极速生成。`;

  for (let attempt = 1; attempt <= ASPECT_UNLOCK_RETRY_LIMIT; attempt += 1) {
    if (disposed || currentReview.value?.id !== reviewId) {
      throw new Error('aspect_unlock_cancelled');
    }

    unlockWaitingAttempt.value = attempt;
    const latestReview = await refreshCurrentReview(reviewId);
    persistCompletedReviewState(latestReview);
    const latestAspect = latestReview.aspects.find((item) => item.aspect_key === aspectKey);
    if (latestAspect?.is_unlocked && latestAspect.content) {
      clearUnlockState();
      showToast(`已解锁「${title}」模块详细奇门解读。`);
      autoSpeakUnlockedAspect(latestReview, aspectKey);
      return;
    }

    try {
      const refreshedReview = await unlockAspect(reviewId, aspectKey);
      persistCompletedReviewState(refreshedReview);
      const unlockedAspect = refreshedReview.aspects.find((item) => item.aspect_key === aspectKey);
      if (unlockedAspect?.is_unlocked) {
        clearUnlockState();
        showToast(`已解锁「${title}」模块详细奇门解读。`);
        autoSpeakUnlockedAspect(refreshedReview, aspectKey);
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

function persistCompletedReviewState(review: ReviewRecord): void {
  state.currentReview = review;
}

function autoSpeakUnlockedAspect(review: ReviewRecord, aspectKey: string): void {
  const aspect = review.aspects.find((item) => item.aspect_key === aspectKey);
  if (!aspect?.is_unlocked) {
    return;
  }
  void nextTick().then(() => {
    void voicePlayback.speakAspect(review, aspect, { auto: true });
  });
}

function isAspectNotReadyError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 409 && error.detail === 'aspect_not_ready';
}

function isAspectUnlockPending(aspect: DisplayAspect): boolean {
  return unlockingAspectKey.value === aspect.aspect_key || unlockWaitingAspectKey.value === aspect.aspect_key;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function handleReviewSyncError(error: unknown): void {
  if (error instanceof ApiError) {
    if (error.status === 402) {
      setError('insufficient_points');
      return;
    }
  }
  setError('review_failed', humanizeError(error));
}

function handleAspectClick(index: number) {
  activeAspect.value = index;
  handleUnlockAspect(index);
}

function handleSelectNextLockedAspect() {
  const index = reviewAspects.value.findIndex((aspect) => !aspect.is_unlocked);
  if (index !== -1) {
    activeAspect.value = index;
    handleUnlockAspect(index);
  } else {
    showToast('所有专项全景分析目前已解封完结。');
  }
}

onMounted(() => {
  void bootstrapApp();
  if (currentReview.value) {
    phoneNumber.value = currentReview.value.phone_number || currentReview.value.phone || '';
    gender.value = currentReview.value.gender || 'male';
    appState.value = 'result';
  }
});

onUnmounted(() => {
  disposed = true;
  clearWaitingTimers();
  voicePlayback.stop();
});

// Canvas rendering engine setup
async function handleExportImage() {
  exportingImage.value = true;
  showToast('正在为您汇出奇门数理定盘图，请稍候...');
  await nextTick();
  
  setTimeout(() => {
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 750;
      canvas.height = 1350;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      const grad = ctx.createLinearGradient(0, 0, 0, 1350);
      grad.addColorStop(0, '#FAF9F5');
      grad.addColorStop(1, '#F2EFE9');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 750, 1350);
      
      ctx.strokeStyle = '#D97706';
      ctx.lineWidth = 4;
      ctx.strokeRect(20, 20, 710, 1310);
      
      ctx.fillStyle = '#4F46E5';
      ctx.font = 'bold 36px serif';
      ctx.textAlign = 'center';
      ctx.fillText('易如反掌 · 起盘结果', 375, 120);
      
      ctx.fillStyle = '#111827';
      ctx.font = 'bold 22px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(`评测号码：${reviewPhoneDisplay.value}`, 80, 220);
      ctx.fillText(`局象评分：${reviewScore.value} 分`, 80, 260);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.strokeStyle = '#E5E7EB';
      ctx.fillRect(80, 310, 590, 100);
      ctx.strokeRect(80, 310, 590, 100);
      
      ctx.fillStyle = '#1F2937';
      ctx.font = '16px serif';
      ctx.fillText(`本局值符引： ${singlePalaceData.value.trigger}`, 110, 365);
      ctx.fillText(`定宫定位：${singlePalaceData.value.palaceName} [ ${singlePalaceData.value.direction} ]`, 320, 365);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(80, 440, 590, 280);
      ctx.strokeRect(80, 440, 590, 280);
      
      ctx.fillStyle = '#4B5563';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText('【综合命理断案】', 100, 490);
      ctx.fillStyle = '#111827';
      ctx.font = '14px serif';
      drawWrappedText(ctx, phoneSummaryTitle.value, 100, 530, 550, 24, 6);
      
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(80, 750, 590, 220);
      ctx.strokeRect(80, 750, 590, 220);
      
      ctx.fillStyle = '#B45309';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText('【长期使用气运点评】', 100, 800);
      ctx.fillStyle = '#1F2937';
      ctx.font = '14px sans-serif';
      drawWrappedText(ctx, `点评判定：${stabilityLabel.value}`, 100, 840, 550, 22, 1);
      drawWrappedText(ctx, stabilityValue.value, 100, 875, 550, 22, 4);
      
      ctx.shadowColor = 'rgba(0,0,0,0.1)';
      ctx.fillStyle = '#4F46E5';
      ctx.fillRect(180, 1050, 390, 60);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 18px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('扫描或浏览器打开易如反掌查看详情', 375, 1088);
      
      const link = document.createElement('a');
      link.download = `易如反掌_定盘手机报告_${reviewPhoneDisplay.value}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      showToast('图片下载已自动唤醒，格式为高分辨率可印刷 PNG 文件。');
    } catch (e) {
      showToast('图片流渲染偶遇阻断，请换用更高版本浏览器重试。');
    } finally {
      exportingImage.value = false;
    }
  }, 350);
}

function drawWrappedText(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, maxWidth: number, lineHeight: number, maxLines: number) {
  const words = text.split('');
  let line = '';
  let lineCount = 0;
  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n];
    const metrics = ctx.measureText(testLine);
    const testWidth = metrics.width;
    if (testWidth > maxWidth && n > 0) {
      ctx.fillText(line, x, y);
      line = words[n];
      y += lineHeight;
      lineCount++;
      if (lineCount >= maxLines - 1) {
        ctx.fillText(line + '...', x, y);
        return;
      }
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, x, y);
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto w-full relative min-h-screen">
    <!-- Action dynamic toasts -->
    <transition name="fade">
      <div
        v-if="toast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-2xl font-sans text-[13px] shadow-lg font-medium flex items-start gap-2 max-w-[90%] leading-relaxed"
      >
        <AlertCircle :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <transition name="fade" mode="out-in">
      <!-- INPUT FORM -->
      <div v-if="appState === 'input'" key="input-form" class="px-margin-mobile space-y-5 pt-3.5">
        <div class="flex items-center justify-between">
          <button
            type="button"
            class="h-9 rounded-full bg-white border border-gray-100 px-3.5 text-brand-secondary font-sans text-[12px] font-bold shadow-sm flex items-center gap-1.5 cursor-pointer"
            @click="emit('back-to-home')"
          >
            <ArrowLeft :size="14" />
            <span>返回首页</span>
          </button>
        </div>

        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="flex items-center gap-2 mb-2">
            <span class="w-2 h-2 bg-brand-primary rounded-full animate-ping"></span>
            <span class="text-brand-gold-fixed font-serif text-[11px] font-bold tracking-wide leading-none">奇门遁甲手机号综合测评</span>
          </div>
          <p class="text-[13px] text-brand-secondary leading-relaxed">
            输入手机号和性别后，系统将通过本命卦象定位归属，深度推演您手机号背后的九星八门吉凶祸福。
          </p>
        </section>

        <form class="space-y-5 font-sans" @submit.prevent="handlePhoneClick">
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
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[11px] font-bold text-brand-secondary tracking-wide">性别</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-150/40">
                <button
                  type="button"
                  @click="gender = 'male'"
                  class="py-2 text-[13px] font-bold rounded-lg cursor-pointer transition-all outline-none border-none"
                  :class="gender === 'male' ? 'bg-white text-brand-primary shadow-sm border border-gray-100' : 'text-brand-secondary hover:text-brand-primary'"
                >
                  男
                </button>
                <button
                  type="button"
                  @click="gender = 'female'"
                  class="py-2 text-[13px] font-bold rounded-lg cursor-pointer transition-all outline-none border-none"
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
              class="w-full py-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl font-sans text-[13px] font-bold shadow-md cursor-pointer outline-none transition-all active:scale-[0.985] flex items-center justify-center gap-1.5 border-none"
              :disabled="!phoneNumber || state.booting"
            >
              <Sparkles :size="15" fill="currentColor" />
              <span>立即扣除 {{ effectiveBaseReviewPoints }} 积分深度起盘测算</span>
            </button>
          </section>
        </form>
      </div>

      <!-- WAITING STATE -->
      <div v-else-if="appState === 'waiting'" key="waiting-box" class="py-10 max-w-md mx-auto px-margin-mobile flex flex-col justify-center min-h-[65vh]">
        <div class="bg-white rounded-2xl p-6 border border-gray-150/75 shadow-sm space-y-6 text-center">
          <div class="relative w-28 h-28 mx-auto flex items-center justify-center select-none">
            <div class="absolute inset-0 bg-brand-primary/5 rounded-full blur-md animate-pulse"></div>
            <div class="absolute w-12 h-12 bg-white rounded-full border border-brand-primary/20 shadow-md flex items-center justify-center">
              <Sparkles :size="24" class="text-brand-primary" />
            </div>
          </div>

          <div class="space-y-1 py-1">
            <h4 class="font-serif text-[17.5px] font-bold text-brand-ink-strong tracking-wide">数理命格同步推演中</h4>
            <p class="font-serif text-[15px] font-bold text-brand-secondary/85 leading-relaxed tracking-wide">
              {{ waitingPoemLine }}
            </p>
          </div>

          <div class="text-center space-y-1.5">
            <div class="flex items-center justify-between text-[11px] font-bold text-brand-secondary">
              <span>正在推算三元九运星盘</span>
              <span class="text-brand-primary">{{ waitingProgressPercentText }}%</span>
            </div>
            <div class="w-full h-1.5 bg-gray-150 rounded-full overflow-hidden">
              <div class="bg-brand-primary h-full transition-all duration-300" :style="{ width: `${waitingProgressPercent}%` }"></div>
            </div>
          </div>

          <div class="h-px bg-gray-100"></div>

          <div class="space-y-4 px-1 text-left">
            <div
              v-for="(step, index) in waitingSteps"
              :key="step.title"
              class="flex items-start gap-3.5 transition-all duration-300"
              :class="index === waitingPhase ? 'opacity-100 scale-[1.01]' : index < waitingPhase ? 'opacity-80' : 'opacity-35'"
            >
              <div class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5"
                   :class="index < waitingPhase ? 'bg-emerald-100 text-emerald-700' : index === waitingPhase ? 'bg-brand-primary text-white' : 'bg-gray-100 text-gray-400'">
                <span v-if="index < waitingPhase">✓</span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div>
                <h5 class="font-serif text-[14px] font-bold text-brand-ink-strong">{{ step.title }}</h5>
                <p class="text-[11px] text-brand-secondary mt-0.5">{{ index === waitingPhase ? waitingMessage : step.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- COMPLETED RESULT -->
      <div v-else-if="appState === 'result'" key="result-view" class="px-margin-mobile space-y-5 pt-3.5">
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
            class="py-2 px-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-lg font-sans text-[13px] font-bold cursor-pointer outline-none transition-all flex items-center gap-1 shadow-sm border-none"
            :disabled="exportingImage"
          >
            <Download :size="13" />
            <span>{{ exportingImage ? '图片汇出中...' : '生成起盘定盘图' }}</span>
          </button>
        </section>

        <!-- Profile Score Widget -->
        <section class="bg-white rounded-2xl px-4 py-4 border border-gray-100 shadow-sm flex items-center justify-between gap-2.5 text-left">
          <div class="min-w-0 flex-1 space-y-1">
            <div class="flex items-center gap-1">
              <span class="inline-block w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
              <span class="text-brand-secondary font-sans text-[11px] font-bold tracking-wide">卦命定盘解析已完成</span>
            </div>
            <h3 class="font-serif text-[18px] font-bold text-brand-ink-strong leading-tight">
              号码：{{ reviewPhoneDisplay }}
            </h3>
            <p class="text-[11px] text-brand-secondary">所属本命：{{ reviewGenderDisplay }}命人</p>
          </div>
          <div class="w-16 h-16 rounded-full bg-brand-primary text-white flex flex-col items-center justify-center shadow-md shrink-0">
            <span class="text-[9px] scale-90 opacity-80 leading-none">综合评分</span>
            <span class="text-[24px] font-serif font-bold mt-1 text-brand-accent leading-none">{{ reviewScore }}</span>
          </div>
        </section>

        <!-- Qimen board display -->
        <section class="space-y-2.5">
          <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5 text-left">
            <Star :size="13" class="text-brand-primary fill-current shrink-0" />
            <span>奇门定局：天人地定盘局象</span>
          </h4>

          <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm space-y-3.5 text-left">
            <div class="grid grid-cols-[160px_1fr] gap-4 items-center">
              <!-- Active Palace Card -->
              <div class="relative w-[160px] h-[160px] bg-brand-paper border border-brand-primary/20 rounded-xl px-4 py-3.5 flex flex-col justify-between shadow-sm">
                <!-- Trigger badge left -->
                <div class="absolute -left-3.5 top-1/2 -translate-y-1/2 bg-brand-primary text-white px-2 py-1.5 rounded font-serif text-[12px] font-bold">
                  {{ singlePalaceData.trigger }}
                </div>
                <div class="flex justify-between items-center text-[12px] font-serif font-bold">
                  <span class="text-purple-700 bg-purple-50 px-1 py-0.5 rounded">{{ singlePalaceData.deity }}</span>
                  <span class="text-indigo-700 bg-indigo-50 px-1 py-0.5 rounded">{{ singlePalaceData.star }}</span>
                </div>
                <div class="text-center">
                  <p class="text-[11px] font-serif text-slate-400 tracking-wider">{{ singlePalaceData.palaceName }}</p>
                  <p class="text-[20px] font-serif font-bold text-brand-primary-strong mt-1">{{ singlePalaceData.direction }}</p>
                </div>
                <div class="flex justify-between items-end text-[11px]">
                  <div class="flex flex-col select-none pr-1">
                    <span class="text-brand-primary font-bold">{{ singlePalaceData.heavenStem }}</span>
                    <span class="border-t border-gray-200 my-0.5"></span>
                    <span class="text-slate-500 font-bold">{{ singlePalaceData.earthStem }}</span>
                  </div>
                  <span class="text-red-750 bg-red-50 text-red-700 px-1 py-0.5 rounded font-serif font-bold">{{ singlePalaceData.door }}</span>
                </div>
              </div>

              <!-- Relation and aspect checks -->
              <div class="h-[160px] grid grid-rows-2 gap-2">
                <div v-for="item in boardRelationCards" :key="item.label" class="bg-brand-paper p-3 border border-gray-100 rounded-xl flex items-center justify-between">
                  <div class="text-[11px]">
                    <p class="font-bold text-brand-ink-strong">{{ item.labelTop }}</p>
                    <p class="text-brand-secondary">{{ item.labelBottom }}</p>
                  </div>
                  <span class="font-serif font-black text-[16px]" :class="item.valueClass">{{ item.value }}</span>
                </div>
              </div>
            </div>

            <!-- Risks & Four Harms list -->
            <div class="bg-amber-50/50 p-3.5 border border-amber-200/40 rounded-xl space-y-2">
              <div class="pb-1 border-b border-amber-100 flex items-center gap-1.5">
                <span class="w-[3px] h-3 bg-amber-500 rounded-full"></span>
                <span class="text-[12px] font-bold text-amber-800">数理特征与奇门克应</span>
              </div>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="badge in boardHarmBadges" :key="badge.label" class="px-2 py-0.5 text-[10px] font-bold border rounded-lg" :class="badge.toneClass">
                  {{ badge.label }} | {{ badge.compactValue }}
                </span>
              </div>
              <div class="text-[11px] leading-relaxed pt-1.5 space-y-1">
                <p><span class="text-amber-800 font-bold">特殊组合：</span>{{ boardSpecialCombos.join('、') || '暂无干扰组合' }}</p>
                <p><span class="text-amber-800 font-bold">限局特征：</span>{{ boardStructureCapText }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Text details and narrations -->
        <section class="space-y-4">
          <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 overflow-hidden text-left">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <span class="w-1 h-4 bg-brand-primary rounded-full"></span>
                <h4 class="font-serif text-[15px] font-bold text-brand-ink-strong">综合定局点评</h4>
              </div>
              <button
                v-if="voiceEnabled"
                @click="handlePhoneSummaryVoiceClick"
                class="flex items-center gap-1 text-[11px] font-bold text-brand-primary bg-brand-primary/5 hover:bg-brand-primary/10 px-2.5 py-1 rounded-full cursor-pointer border-none"
              >
                <Volume2 :size="12" />
                <span>{{ phoneSummaryVoicePlaying ? '播放中...' : '听综评' }}</span>
              </button>
            </div>

            <div class="space-y-3 font-sans">
              <p class="font-serif text-[15px] font-bold text-brand-primary-strong leading-relaxed">{{ phoneSummaryTitle }}</p>
              <div class="bg-red-50 p-3 rounded-xl border border-red-100/50 text-[12.5px] text-red-700 leading-relaxed font-sans">
                <p class="font-bold flex items-center gap-1 mb-1">
                  <AlertCircle :size="13" /> 风险提醒
                </p>
                <p>{{ phoneSummaryRisk }}</p>
              </div>
              <p class="text-[13px] text-brand-secondary leading-relaxed font-medium border-t border-gray-50 pt-2">{{ phoneSummaryUsageGuidance }}</p>
            </div>
          </div>

          <!-- Long-term stability advice -->
          <div class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4 text-left">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <span class="w-1 h-4 bg-brand-primary rounded-full"></span>
                <h4 class="font-serif text-[15px] font-bold text-brand-ink-strong">长期使用定语</h4>
              </div>
              <button
                v-if="voiceEnabled"
                @click="handleStabilityVoiceClick"
                class="flex items-center gap-1 text-[11px] font-bold text-brand-primary bg-brand-primary/5 hover:bg-brand-primary/10 px-2.5 py-1 rounded-full cursor-pointer border-none"
              >
                <Volume2 :size="12" />
                <span>{{ stabilityVoicePlaying ? '播放中...' : '听建议' }}</span>
              </button>
            </div>

            <div class="space-y-2">
              <div class="flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-lg text-[13px] font-bold border border-emerald-100">
                <span>☯</span>
                <span>{{ stabilityLabel }}</span>
              </div>
              <p class="text-[13px] text-brand-secondary leading-relaxed font-medium pt-1">
                {{ stabilityValue }}
              </p>
            </div>
          </div>
        </section>

        <!-- Twelve Aspects Section -->
        <section ref="aspectSectionRef" class="space-y-2 text-left">
          <div class="flex justify-between items-baseline">
            <h4 class="font-serif text-[13.5px] font-bold text-brand-secondary tracking-wide">十二个专项维度的深度排演</h4>
            <span class="text-[11px] text-brand-secondary">当前可用充值代币: <strong class="text-brand-primary-strong">{{ userPoints }}</strong></span>
          </div>

          <div class="grid grid-cols-4 gap-1.5">
            <button
              v-for="(aspect, idx) in reviewAspects"
              :key="aspect.aspect_key"
              @click="handleAspectClick(idx)"
              class="relative py-2 px-1 rounded-xl font-sans text-[11px] font-bold flex flex-col items-center justify-center gap-1 outline-none cursor-pointer border shadow-sm transition-all h-14"
              :class="activeAspect === idx ? 'bg-brand-primary text-white border-transparent' : aspect.is_unlocked ? 'bg-white text-brand-ink border-gray-150' : 'bg-brand-paper text-brand-secondary border-transparent'"
            >
              <span class="truncate max-w-full text-center">{{ aspect.short_title || aspect.title }}</span>
              <span class="text-[8.5px] font-black scale-90 px-1 py-0.5 rounded leading-none"
                    :class="activeAspect === idx ? 'bg-white/20 text-white' : aspect.is_unlocked ? 'bg-brand-primary/10 text-brand-primary' : 'bg-brand-gold-fixed/15 text-brand-gold-fixed'">
                {{ aspect.is_unlocked ? `${aspect.score || '已开'}` : `${aspect.unlock_points || effectiveAspectUnlockPoints}点` }}
              </span>
            </button>
          </div>

          <!-- Active aspect details card -->
          <div v-if="selectedAspect" class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm space-y-4">
            <!-- Loading unlocking state -->
            <div v-if="selectedAspectUnlockPending" class="py-8 flex flex-col items-center justify-center text-center space-y-3">
              <Loader2 class="animate-spin text-brand-primary w-8 h-8" />
              <div class="space-y-1">
                <h5 class="font-serif text-[14px] font-bold text-brand-ink-strong">{{ unlockProcessingHeading }}</h5>
                <p class="text-[11px] text-brand-secondary">{{ unlockWaitingMessage }}</p>
              </div>
            </div>

            <div v-else-if="selectedAspect.is_unlocked" class="space-y-3.5">
              <div class="flex justify-between items-center pb-2 border-b border-gray-100 gap-2">
                <span class="font-serif text-[15px] font-bold text-brand-ink-strong">
                  {{ selectedAspect.short_title || selectedAspect.title }} · 解谱结果
                </span>
                <div class="flex items-center gap-2">
                  <button
                    v-if="voiceEnabled"
                    @click="handleSelectedAspectVoiceClick"
                    class="flex items-center gap-1 text-[11px] font-bold text-brand-primary bg-brand-primary/5 hover:bg-brand-primary/10 px-2.5 py-1 rounded-full cursor-pointer border-none"
                  >
                    <Volume2 :size="12" />
                    <span>{{ selectedAspectVoicePlaying ? '播放中...' : '听专项' }}</span>
                  </button>
                  <span class="bg-emerald-50 text-emerald-600 border border-emerald-100 px-2.5 py-0.5 rounded-lg text-[10px] font-bold">
                    得评分 {{ selectedAspect.score }}
                  </span>
                </div>
              </div>

              <div class="space-y-3">
                <p class="font-serif text-[14.5px] font-bold text-brand-primary leading-relaxed">{{ selectedAspect.title }}</p>
                <div v-if="selectedAspect.risk" class="bg-red-50 p-3 rounded-xl border border-red-100/50 text-[12px] text-red-700 leading-relaxed font-sans mt-2">
                  <p class="font-bold flex items-center gap-1 mb-1">
                    <AlertCircle :size="13" /> 风险批点
                  </p>
                  <p>{{ selectedAspect.risk }}</p>
                </div>
                <p class="text-[13px] text-brand-secondary leading-relaxed whitespace-pre-line font-medium">{{ selectedAspect.content }}</p>
              </div>
            </div>

            <!-- Locked Aspect CTA -->
            <div v-else class="py-10 flex flex-col items-center justify-center text-center space-y-4">
              <div class="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary">
                <Lock :size="20" class="animate-bounce" />
              </div>
              <div class="space-y-1 max-w-[85%] mx-auto">
                <h5 class="font-serif font-black text-[15px] text-brand-ink-strong">解锁「{{ selectedAspect.title }}」详细分析</h5>
                <p class="text-[12px] text-brand-secondary leading-relaxed">
                  为了保持高品质奇门格局推导精确大模型排演，解封此独立维度需要额外扣除 <strong class="text-brand-ink-strong">{{ selectedAspect.unlock_points || effectiveAspectUnlockPoints }}</strong> 积分。
                </p>
              </div>
              <button
                @click="handleUnlockAspect(activeAspect)"
                class="px-6 py-2.5 bg-brand-primary text-white text-[12.5px] font-bold rounded-full cursor-pointer shadow-sm hover:bg-brand-primary-strong active:scale-95 transition-all outline-none border-none"
              >
                消耗 {{ selectedAspect.unlock_points || effectiveAspectUnlockPoints }} 积分即刻起谱
              </button>
            </div>
          </div>
        </section>

        <!-- Suggest Actions -->
        <section class="bg-white p-4.5 rounded-xl border border-gray-100 flex flex-col gap-3 text-center text-left">
          <span class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide text-center">
            关于数理批点是否有疑惑？
          </span>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="emit('navigate-to-tab', 'agent')"
              class="py-3 px-2 bg-brand-primary text-white rounded-lg font-sans text-[13px] font-bold hover:bg-brand-primary-strong transition-all cursor-pointer flex items-center justify-center gap-1.5 outline-none border-none"
            >
              <MessageSquare :size="14" />
              <span>有疑问，咨询专属助手</span>
            </button>

            <button
              @click="handleSelectNextLockedAspect"
              class="py-3 px-2 bg-white border border-brand-primary text-brand-primary rounded-lg font-sans text-[13px] font-bold hover:bg-brand-primary/5 transition-all cursor-pointer flex items-center justify-center gap-1.5 outline-none"
            >
              <Plus :size="14" />
              <span>继续解锁后续维度</span>
            </button>
          </div>
        </section>
      </div>

      <!-- ERROR STATE -->
      <div v-else-if="appState === 'error_state'" key="error-box" class="pt-24 pb-32 max-w-md mx-auto px-margin-mobile flex flex-col items-center justify-center min-h-[70vh] text-center space-y-6">
        <div class="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center text-red-600 border border-red-200/60 shadow-sm shrink-0">
          <AlertCircle :size="28" />
        </div>

        <div class="space-y-2.5 max-w-[90%] mx-auto">
          <h3 class="font-serif text-[18px] font-black text-brand-ink-strong">
            {{ errorType === 'phone_format' ? '号码输入格式有误' : errorType === 'insufficient_points' ? '充值代币积分不足' : '本地接口同步故障' }}
          </h3>
          <p class="font-sans text-[13px] text-brand-secondary leading-relaxed">
            {{ errorType === 'phone_format' ? '该号码长度或构造非正常的 11 位数字，请确认后重新排演。' : errorType === 'insufficient_points' ? `起盘评测本次需要消耗 ${effectiveBaseReviewPoints} 积分，您目前仅有 ${userPoints} 积分。` : errorDetail || '连接故障，请检查 node api 服务器状态。' }}
          </p>
        </div>

        <div class="w-full pt-2 flex flex-col gap-3 font-sans">
          <button
            @click="resetToInput"
            class="w-full py-3 bg-brand-primary text-white rounded-xl font-bold text-[13px] shadow-sm hover:bg-brand-primary-strong cursor-pointer border-none"
          >
            返回重新输入
          </button>
          <button
            v-if="errorType === 'insufficient_points' || errorType === 'unlock_points_insufficient'"
            @click="emit('navigate-to-tab', 'recharge', { source: 'phone', required_points: effectiveBaseReviewPoints })"
            class="w-full py-3 bg-white border border-brand-primary/20 text-brand-primary rounded-xl font-bold text-[13px] hover:bg-brand-primary/5 cursor-pointer"
          >
            前往充值积分
          </button>
        </div>
      </div>
    </transition>

    <!-- CONFIRM POPLAND DIALOG -->
    <transition name="fade">
      <div v-if="showReviewConfirmDialog" class="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-50">
        <div class="bg-white rounded-2xl p-5 max-w-xs w-[88%] shadow-xl space-y-4 text-center relative border border-gray-100">
          <div class="w-10 h-10 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary mx-auto animate-pulse">
            <Sparkles :size="20" fill="currentColor" />
          </div>
          <h4 class="font-serif text-[17px] font-bold text-brand-ink-strong">确认扣积分起盘</h4>
          <p class="text-[12.5px] text-brand-secondary leading-relaxed">
            将扣除 <strong class="text-brand-primary-strong">{{ effectiveBaseReviewPoints }}</strong> 积分开启本号码推演，是否为您归位定盘？
          </p>
          <div class="flex items-center justify-center gap-1.5">
            <input type="checkbox" v-model="skipReviewConfirmHint" id="skip-hint" class="accent-brand-primary" />
            <label for="skip-hint" class="text-[11.5px] text-brand-secondary font-bold cursor-pointer">下次直接评测，不再强制唤醒此弹窗</label>
          </div>
          <div class="flex gap-2">
            <button @click="closeReviewConfirmDialog" class="flex-1 py-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg text-xs font-bold border-none cursor-pointer">取消</button>
            <button @click="handleConfirmReview" class="flex-1 py-2 bg-brand-primary text-white rounded-lg text-xs font-bold border-none cursor-pointer">确认起盘</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.aspect-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
</style>
