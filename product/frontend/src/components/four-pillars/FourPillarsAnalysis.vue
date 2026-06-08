<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, type Component } from 'vue';
import {
  AlertCircle,
  ArrowLeft,
  CalendarDays,
  Check,
  Clock,
  Gem,
  Heart,
  HeartPulse,
  Leaf,
  Lock,
  MapPin,
  Mountain,
  RefreshCw,
  Shield,
  Sparkles,
  TrendingUp,
  UnlockKeyhole,
  User,
  Waves,
} from 'lucide-vue-next';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../../config/pricing';
import { ApiError } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { FourPillarsAspect, FourPillarsReviewRecord, Gender, ReviewProgressStage } from '../../types/api';
import type { FourPillarsLuckCycle, FourPillarsLuckRenderRecord, FourPillarsLuckYearItem } from '../../types/api';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
}>();

type ViewState = 'input' | 'waiting' | 'result' | 'error_state';
type ResultBranch = 'chart' | 'luck';
type LuckPollResult = 'completed' | 'processing' | 'cancelled';
type ErrorType =
  | 'none'
  | 'birth_datetime'
  | 'insufficient_points'
  | 'unlock_points_insufficient'
  | 'module_disabled'
  | 'request_failed'
  | 'review_timeout'
  | 'review_failed';

type DisplayAspect = FourPillarsAspect & {
  icon: Component;
  tint: string;
  textTint: string;
};

type PillarDisplay = {
  key: string;
  label: string;
  ganzhi: string;
  stem: string;
  branch: string;
  stemElement: string;
  branchElement: string;
  stemTenGod: string;
  branchTenGod: string;
};

const {
  state,
  bootstrapApp,
  isGuestUser,
  submitFourPillarsReview,
  refreshCurrentFourPillarsReview,
  refreshFourPillarsLuckAnalysis,
  unlockFourPillarsAspect,
  generateFourPillarsLuckCycle,
  generateFourPillarsLuckYear,
  requestRegisteredUser,
  fourPillarsBasePointsCost,
  fourPillarsAspectUnlockPointsCost,
  customerServiceCopyForScene,
  openCustomerServiceModal,
  humanizeError,
} = useEaseWiseApp();

const viewState = ref<ViewState>('input');
const gender = ref<Gender>('male');
const birthDate = ref('');
const birthTime = ref('');
const birthPlace = ref('');
const profileName = ref('');
const activeAspect = ref(0);
const activeBranch = ref<ResultBranch>('chart');
const activeCycleKey = ref('');
const toast = ref<string | null>(null);
const errorType = ref<ErrorType>('none');
const errorDetail = ref('');
const currentProgressStage = ref<ReviewProgressStage | null>(null);
const currentProgressMessage = ref('');
const pollingReviewId = ref<string | null>(null);
const unlockingAspectKey = ref<string | null>(null);
const unlockWaitingAspectKey = ref<string | null>(null);
const unlockWaitingAttempt = ref(0);
const generatingLuckTargets = ref<string[]>([]);
const selectedLuckYear = ref<number | null>(null);

let disposed = false;
let pollingPromise: Promise<FourPillarsReviewRecord> | null = null;

const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const ASPECT_UNLOCK_RETRY_LIMIT = 45;
const ASPECT_UNLOCK_RETRY_DELAY_MS = 2000;
const LUCK_RENDER_RETRY_LIMIT = 90;
const LUCK_RENDER_RETRY_DELAY_MS = 2000;

const aspectUiMap: Record<string, { icon: Component; tint: string; textTint: string }> = {
  personality: { icon: Sparkles, tint: 'bg-brand-paper text-brand-secondary', textTint: 'text-brand-secondary' },
  career: { icon: Shield, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  wealth: { icon: TrendingUp, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  love: { icon: Heart, tint: 'bg-rose-50 text-rose-600', textTint: 'text-rose-600' },
  health: { icon: HeartPulse, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  family_environment: { icon: Mountain, tint: 'bg-slate-50 text-slate-600', textTint: 'text-slate-600' },
};

const elementUiMap: Record<string, { icon: Component; bar: string; text: string }> = {
  木: { icon: Leaf, bar: 'bg-emerald-500', text: 'text-emerald-700' },
  火: { icon: Sparkles, bar: 'bg-red-500', text: 'text-red-700' },
  土: { icon: Mountain, bar: 'bg-amber-500', text: 'text-amber-700' },
  金: { icon: Gem, bar: 'bg-slate-500', text: 'text-slate-700' },
  水: { icon: Waves, bar: 'bg-blue-500', text: 'text-blue-700' },
};

const currentReview = computed(() => state.currentFourPillarsReview);
const userPoints = computed(() => state.points?.balance ?? 0);
const moduleEnabled = computed(() => state.runtimeConfig?.modules.four_pillars?.enabled ?? true);
const effectiveBasePoints = computed(() => fourPillarsBasePointsCost.value ?? DEFAULT_BASE_REVIEW_POINTS);
const effectiveAspectUnlockPoints = computed(
  () => currentReview.value?.aspect_unlock_points ?? fourPillarsAspectUnlockPointsCost.value ?? DEFAULT_ASPECT_UNLOCK_POINTS,
);
const progressMessage = computed(() => currentProgressMessage.value || '四柱命盘正在生成，请稍候。');
const reviewScore = computed(() => currentReview.value?.score ?? 0);
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
const luckAnalysis = computed(() => currentReview.value?.luck_analysis ?? null);
const luckCycles = computed<FourPillarsLuckCycle[]>(() => luckAnalysis.value?.cycles ?? []);
const luckCycleCost = computed(() => luckAnalysis.value?.cycle_points_cost ?? state.runtimeConfig?.modules.four_pillars?.luck_cycle_points_cost ?? 50);
const luckYearCost = computed(() => luckAnalysis.value?.year_points_cost ?? state.runtimeConfig?.modules.four_pillars?.luck_year_points_cost ?? 20);
const luckGenerationEnabled = computed(() => luckAnalysis.value?.enabled ?? state.runtimeConfig?.modules.four_pillars?.luck_generation_enabled ?? true);
const selectedLuckCycle = computed<FourPillarsLuckCycle | null>(() => {
  if (!luckCycles.value.length) return null;
  return luckCycles.value.find((item) => item.cycle_key === activeCycleKey.value)
    || luckCycles.value.find((item) => item.is_current)
    || luckCycles.value[0]
    || null;
});
const selectedLuckYearItem = computed<FourPillarsLuckYearItem | null>(() => {
  const cycle = selectedLuckCycle.value;
  if (!cycle?.year_items?.length) return null;
  if (selectedLuckYear.value) {
    return cycle.year_items.find((item) => item.year === selectedLuckYear.value) || null;
  }
  return cycle.year_items.find((item) => item.is_current) || cycle.year_items[0] || null;
});
const selectedAspect = computed(() => reviewAspects.value[activeAspect.value] || null);
const selectedAspectPending = computed(
  () => Boolean(selectedAspect.value && (unlockingAspectKey.value === selectedAspect.value.aspect_key || unlockWaitingAspectKey.value === selectedAspect.value.aspect_key)),
);
const summary = computed(() => currentReview.value?.summary ?? null);
const chart = computed(() => asRecord(currentReview.value?.chart));
const facts = computed(() => asRecord(currentReview.value?.deterministic_facts));
const dayMaster = computed(() => asRecord(facts.value.day_master));
const strength = computed(() => asRecord(dayMaster.value.strength));
const interactions = computed(() => asRecord(facts.value.interactions));
const elementCounts = computed(() => {
  const counts = asRecord(facts.value.element_counts);
  return ['木', '火', '土', '金', '水'].map((element) => ({
    element,
    value: Number(counts[element] ?? 0),
    ...elementUiMap[element],
  }));
});
const maxElementCount = computed(() => Math.max(1, ...elementCounts.value.map((item) => item.value)));
const pillars = computed<PillarDisplay[]>(() => {
  const rawPillars = asRecord(chart.value.pillars);
  const labels: Record<string, string> = { year: '年柱', month: '月柱', day: '日柱', hour: '时柱' };
  return ['year', 'month', 'day', 'hour'].map((key) => {
    const pillar = asRecord(rawPillars[key]);
    return {
      key,
      label: labels[key],
      ganzhi: String(pillar.ganzhi || '--'),
      stem: String(pillar.stem || '-'),
      branch: String(pillar.branch || '-'),
      stemElement: String(pillar.stem_element || '-'),
      branchElement: String(pillar.branch_element || '-'),
      stemTenGod: String(pillar.stem_ten_god || '-'),
      branchTenGod: String(pillar.branch_ten_god || '-'),
    };
  });
});
const favorableElementsText = computed(() => toStringList(dayMaster.value.favorable_elements).join('、') || '待生成');
const unfavorableElementsText = computed(() => toStringList(dayMaster.value.unfavorable_elements).join('、') || '待生成');
const interactionTags = computed(() => {
  const tags = [
    ...toStringList(interactions.value.combinations),
    ...toStringList(interactions.value.six_harmonies),
    ...toStringList(interactions.value.clashes),
    ...toStringList(interactions.value.harms),
    ...toStringList(interactions.value.breaks),
  ];
  return tags.length ? tags : ['未见明显合冲刑害破'];
});
const recentHistory = computed(() => state.fourPillarsHistory.slice(0, 5));

watch(
  reviewAspects,
  (aspects) => {
    if (!aspects.length) {
      activeAspect.value = 0;
      return;
    }
    if (activeAspect.value < 0 || activeAspect.value >= aspects.length) {
      activeAspect.value = 0;
    }
  },
  { immediate: true },
);

watch(
  luckCycles,
  (cycles) => {
    if (!cycles.length) {
      activeCycleKey.value = '';
      selectedLuckYear.value = null;
      return;
    }
    if (!cycles.some((item) => item.cycle_key === activeCycleKey.value)) {
      activeCycleKey.value = luckAnalysis.value?.current_cycle_key || cycles.find((item) => item.is_current)?.cycle_key || cycles[0].cycle_key;
    }
    const cycle = cycles.find((item) => item.cycle_key === activeCycleKey.value) || cycles[0];
    if (!cycle.year_items.some((item) => item.year === selectedLuckYear.value)) {
      selectedLuckYear.value = cycle.year_items.find((item) => item.is_current)?.year || cycle.year_items[0]?.year || null;
    }
  },
  { immediate: true },
);

watch(
  currentReview,
  (review) => {
    syncViewFromReview(review);
  },
  { immediate: true },
);

onMounted(() => {
  void bootstrapApp();
});

onUnmounted(() => {
  disposed = true;
});

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function toStringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map((item) => String(item || '').trim()).filter(Boolean);
}

function showToast(message: string, duration = 2200): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, duration);
}

function validateBirthInput(): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/u.test(birthDate.value) || !/^\d{2}:\d{2}$/u.test(birthTime.value)) {
    setError('birth_datetime');
    return false;
  }
  const parsed = new Date(`${birthDate.value}T${birthTime.value}:00`);
  if (Number.isNaN(parsed.getTime())) {
    setError('birth_datetime');
    return false;
  }
  return true;
}

function setError(nextType: ErrorType, detail = ''): void {
  errorType.value = nextType;
  errorDetail.value = detail;
  viewState.value = 'error_state';
}

function resetToInput(): void {
  viewState.value = 'input';
  errorType.value = 'none';
  errorDetail.value = '';
  currentProgressStage.value = null;
  currentProgressMessage.value = '';
  unlockingAspectKey.value = null;
  unlockWaitingAspectKey.value = null;
  unlockWaitingAttempt.value = 0;
  generatingLuckTargets.value = [];
}

function handleHeaderBackAction(): void {
  if (viewState.value === 'result') {
    resetToInput();
    return;
  }
  emit('back-to-home');
}

function syncViewFromReview(review: FourPillarsReviewRecord | null): void {
  if (!review) {
    return;
  }
  applyFormFromReview(review);
  currentProgressStage.value = review.progress_stage;
  currentProgressMessage.value = review.progress_message || '';
  if (review.status === 'completed') {
    viewState.value = 'result';
    return;
  }
  if (review.status === 'failed') {
    setError('review_failed', review.error_message || review.progress_message || '四柱评测生成失败');
    return;
  }
  viewState.value = 'waiting';
  if (pollingReviewId.value !== review.id) {
    void startReviewPolling(review).catch(handleReviewSyncError);
  }
}

function applyFormFromReview(review: FourPillarsReviewRecord): void {
  gender.value = review.gender;
  birthDate.value = review.birth_date;
  birthTime.value = review.birth_time;
  birthPlace.value = review.birth_place || '';
  profileName.value = review.name || '';
}

async function handleSubmit(): Promise<void> {
  if (state.booting) {
    return;
  }
  if (!moduleEnabled.value) {
    setError('module_disabled');
    return;
  }
  if (!validateBirthInput()) {
    return;
  }
  const authenticated = await requestRegisteredUser('四柱八字评测');
  if (!authenticated || isGuestUser.value) {
    return;
  }
  if (userPoints.value < effectiveBasePoints.value) {
    setError('insufficient_points');
    return;
  }
  viewState.value = 'waiting';
  currentProgressStage.value = 'queued';
  currentProgressMessage.value = '四柱评测任务已创建，等待开始';
  try {
    const review = await submitFourPillarsReview({
      gender: gender.value,
      birth_date: birthDate.value,
      birth_time: birthTime.value,
      timezone: 'Asia/Shanghai',
      birth_place: birthPlace.value.trim() || null,
      name: profileName.value.trim() || null,
      include_markdown: true,
    });
    const completed = await startReviewPolling(review);
    syncViewFromReview(completed);
    showToast('四柱评测完成，可查看命盘和专项内容。');
  } catch (error) {
    handleReviewSyncError(error);
  }
}

function startReviewPolling(review: FourPillarsReviewRecord): Promise<FourPillarsReviewRecord> {
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

async function pollReviewUntilReady(review: FourPillarsReviewRecord): Promise<FourPillarsReviewRecord> {
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
      throw new Error(latestReview.error_message || latestReview.progress_message || '四柱评测生成失败');
    }
    await sleep(REVIEW_READY_RETRY_DELAY_MS);
    latestReview = await refreshCurrentFourPillarsReview(latestReview.id);
  }
  throw new Error('四柱评测时间比预期更长，请稍后在“我的”页面查看结果。');
}

async function handleAspectClick(aspect: DisplayAspect, index: number): Promise<void> {
  activeAspect.value = index;
  if (aspect.is_unlocked) {
    return;
  }
  await unlockSelectedAspect(aspect);
}

async function unlockSelectedAspect(aspect: DisplayAspect): Promise<void> {
  const review = currentReview.value;
  if (!review || aspect.is_unlocked) {
    return;
  }
  const authenticated = await requestRegisteredUser('四柱专项解锁');
  if (!authenticated || isGuestUser.value) {
    return;
  }
  if ((aspect.unlock_points || effectiveAspectUnlockPoints.value) > userPoints.value) {
    setError('unlock_points_insufficient');
    return;
  }
  unlockingAspectKey.value = aspect.aspect_key;
  unlockWaitingAspectKey.value = null;
  unlockWaitingAttempt.value = 0;
  try {
    const refreshed = await unlockAspectWithRetry(review.id, aspect.aspect_key);
    syncViewFromReview(refreshed);
    showToast(`已解锁「${aspect.short_title || aspect.title}」。`);
  } catch (error) {
    handleReviewSyncError(error);
  } finally {
    unlockingAspectKey.value = null;
    unlockWaitingAspectKey.value = null;
    unlockWaitingAttempt.value = 0;
  }
}

async function unlockAspectWithRetry(reviewId: string, aspectKey: string): Promise<FourPillarsReviewRecord> {
  for (let attempt = 0; attempt < ASPECT_UNLOCK_RETRY_LIMIT; attempt += 1) {
    try {
      return await unlockFourPillarsAspect(reviewId, aspectKey);
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 409 && error.detail === 'aspect_not_ready')) {
        throw error;
      }
      unlockWaitingAspectKey.value = aspectKey;
      unlockWaitingAttempt.value = attempt + 1;
      await sleep(ASPECT_UNLOCK_RETRY_DELAY_MS);
      await refreshCurrentFourPillarsReview(reviewId).catch(() => undefined);
    }
  }
  throw new Error('专项内容仍在生成中，请稍后重试。');
}

async function restoreReview(reviewId: string): Promise<void> {
  if (!reviewId) {
    showToast('暂无可刷新的四柱报告。');
    return;
  }
  try {
    const review = await refreshCurrentFourPillarsReview(reviewId);
    syncViewFromReview(review);
  } catch (error) {
    handleReviewSyncError(error);
  }
}

async function handleGenerateCycle(cycle: FourPillarsLuckCycle | null): Promise<void> {
  const review = currentReview.value;
  if (!review || !cycle || cycle.render_status === 'completed') {
    return;
  }
  const authenticated = await requestRegisteredUser('大运综评生成');
  if (!authenticated || isGuestUser.value) return;
  if (!luckGenerationEnabled.value) {
    showToast('流年大运生成暂未开放。');
    return;
  }
  if (userPoints.value < luckCycleCost.value) {
    setError('unlock_points_insufficient');
    return;
  }
  const targetKey = `cycle:${cycle.cycle_key}`;
  if (isGeneratingLuckTarget(targetKey)) return;
  startGeneratingLuckTarget(targetKey);
  try {
    const render = await generateFourPillarsLuckCycle(review.id, cycle.cycle_key);
    const pollResult = await pollLuckRenderUntilReady(render, targetKey);
    if (pollResult === 'completed') {
      showToast('大运综评已生成。');
    }
  } catch (error) {
    handleReviewSyncError(error);
  } finally {
    stopGeneratingLuckTarget(targetKey);
  }
}

async function handleGenerateYear(cycle: FourPillarsLuckCycle | null, yearItem: FourPillarsLuckYearItem | null): Promise<void> {
  const review = currentReview.value;
  if (!review || !cycle || !yearItem || yearItem.render_status === 'completed') {
    return;
  }
  const authenticated = await requestRegisteredUser('流年评测生成');
  if (!authenticated || isGuestUser.value) return;
  if (!luckGenerationEnabled.value) {
    showToast('流年大运生成暂未开放。');
    return;
  }
  if (userPoints.value < luckYearCost.value) {
    setError('unlock_points_insufficient');
    return;
  }
  const targetKey = `year:${cycle.cycle_key}:${yearItem.year}`;
  if (isGeneratingLuckTarget(targetKey)) return;
  startGeneratingLuckTarget(targetKey);
  try {
    const render = await generateFourPillarsLuckYear(review.id, cycle.cycle_key, yearItem.year);
    const pollResult = await pollLuckRenderUntilReady(render, targetKey);
    if (pollResult === 'completed') {
      showToast(`${yearItem.year} 流年评测已生成。`);
    }
  } catch (error) {
    handleReviewSyncError(error);
  } finally {
    stopGeneratingLuckTarget(targetKey);
  }
}

async function pollLuckRenderUntilReady(render: FourPillarsLuckRenderRecord, targetKey: string): Promise<LuckPollResult> {
  const review = currentReview.value;
  if (!review) return 'cancelled';
  if (render.status === 'completed') {
    await refreshFourPillarsLuckAnalysis(review.id);
    return 'completed';
  }
  for (let attempt = 0; attempt < LUCK_RENDER_RETRY_LIMIT; attempt += 1) {
    if (disposed || !isGeneratingLuckTarget(targetKey)) return 'cancelled';
    await sleep(LUCK_RENDER_RETRY_DELAY_MS);
    const latest = await refreshFourPillarsLuckAnalysis(review.id);
    const found = findLuckRender(latest.cycles, render);
    if (found?.status === 'completed') return 'completed';
    if (found?.status === 'failed' || found?.status === 'retryable') {
      throw new Error(found.error_message || '流年大运生成失败，可稍后重试。');
    }
  }
  showToast('内容仍在生成中，可稍后刷新查看。', 3000);
  return 'processing';
}

function isGeneratingLuckTarget(targetKey: string): boolean {
  return generatingLuckTargets.value.includes(targetKey);
}

function startGeneratingLuckTarget(targetKey: string): void {
  if (isGeneratingLuckTarget(targetKey)) return;
  generatingLuckTargets.value = [...generatingLuckTargets.value, targetKey];
}

function stopGeneratingLuckTarget(targetKey: string): void {
  generatingLuckTargets.value = generatingLuckTargets.value.filter((item) => item !== targetKey);
}

function findLuckRender(cycles: FourPillarsLuckCycle[], render: FourPillarsLuckRenderRecord): FourPillarsLuckRenderRecord | null {
  const cycle = cycles.find((item) => item.cycle_key === render.cycle_key);
  if (!cycle) return null;
  if (render.render_type === 'dayun') return cycle.render;
  return cycle.year_items.find((item) => item.year === render.year)?.render || null;
}

function luckStatusText(status: string | null | undefined): string {
  const value = status || 'not_generated';
  if (value === 'completed') return '已生成';
  if (value === 'processing') return '生成中';
  if (value === 'failed' || value === 'retryable') return '失败可重试';
  return '未生成';
}

function luckRenderText(render: FourPillarsLuckRenderRecord | null | undefined, key: string): string {
  const result = asRecord(render?.result);
  return String(result[key] || '');
}

function handleReviewSyncError(error: unknown): void {
  if (error instanceof ApiError) {
    if (error.status === 402) {
      setError('insufficient_points');
      return;
    }
    if (error.status === 403 && error.detail === 'module_disabled') {
      setError('module_disabled');
      return;
    }
    if (error.status === 422) {
      setError('birth_datetime');
      return;
    }
  }
  const message = humanizeError(error);
  if (message.includes('时间比预期更长')) {
    setError('review_timeout', message);
    return;
  }
  if (message.includes('生成失败')) {
    setError('review_failed', message);
    return;
  }
  setError('request_failed', message);
}

function resolveErrorTitle(): string {
  const titleMap: Record<ErrorType, string> = {
    none: '请稍后重试',
    birth_datetime: '出生信息不完整',
    insufficient_points: '积分不足',
    unlock_points_insufficient: '专项解锁积分不足',
    module_disabled: '功能暂未开放',
    request_failed: '请求失败',
    review_timeout: '生成时间较长',
    review_failed: '生成失败',
  };
  return titleMap[errorType.value];
}

function resolveErrorMessage(): string {
  if (errorDetail.value) {
    return errorDetail.value;
  }
  const messageMap: Record<ErrorType, string> = {
    none: '请稍后重试。',
    birth_datetime: '请选择有效的出生日期和出生时间。',
    insufficient_points: '当前积分不足，可充值后继续生成四柱评测。',
    unlock_points_insufficient: '当前积分不足，可充值后继续解锁专项内容。',
    module_disabled: '四柱八字评测当前未开放。',
    request_failed: '服务暂时不可用，请稍后重试。',
    review_timeout: '评测任务仍在后台生成，可稍后从历史记录恢复。',
    review_failed: '本次四柱评测生成失败。',
  };
  return messageMap[errorType.value];
}

function formatDateTime(dateText: string, timeText: string): string {
  return `${dateText || '--'} ${timeText || '--'}`;
}

function scoreToneClass(score: number | null | undefined): string {
  const value = Number(score ?? 0);
  if (value >= 82) {
    return 'text-emerald-600';
  }
  if (value >= 68) {
    return 'text-amber-600';
  }
  return 'text-red-600';
}

function refreshActiveReview(): void {
  void restoreReview(currentReview.value?.id || '');
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
</script>

<template>
  <div class="min-h-screen bg-brand-paper pb-28">
    <transition name="fade-slide">
      <div
        v-if="toast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
      >
        <Sparkles :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <header class="sticky top-0 z-20 bg-brand-paper/95 backdrop-blur border-b border-white/80">
      <div class="max-w-md mx-auto px-margin-mobile py-3 flex items-center justify-between">
        <button
          class="h-9 rounded-full bg-white border border-gray-100 px-3 text-brand-secondary font-sans text-[12px] font-bold flex items-center justify-center gap-1.5 shadow-sm"
          @click="handleHeaderBackAction"
        >
          <ArrowLeft :size="14" class="text-brand-ink-strong" />
          <span>{{ viewState === 'result' ? '重新评测' : '返回首页' }}</span>
        </button>
        <div class="text-center">
          <h1 class="font-serif text-[18px] font-bold text-brand-ink-strong leading-none">四柱八字评测</h1>
          <p class="font-sans text-[11px] text-brand-secondary mt-1">公历生日时辰 · 默认北京时间</p>
        </div>
        <button class="w-9 h-9 rounded-full bg-white border border-gray-100 flex items-center justify-center shadow-sm" @click="refreshActiveReview">
          <RefreshCw :size="17" class="text-brand-secondary" />
        </button>
      </div>
    </header>

    <main class="max-w-md mx-auto px-margin-mobile pt-4">
      <section v-if="viewState === 'input'" class="space-y-4">
        <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
          <div class="flex items-start justify-between gap-3 mb-4">
            <div>
              <p class="font-sans text-[11px] text-brand-primary-strong font-bold tracking-wide">FOUR PILLARS</p>
              <h2 class="font-serif text-[20px] font-bold text-brand-ink-strong mt-1">输入出生信息</h2>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-brand-primary/10 text-brand-primary-strong text-[11px] font-bold">
              {{ effectiveBasePoints }} 积分
            </span>
          </div>

          <div class="grid grid-cols-2 gap-2 mb-4">
            <button
              class="h-11 rounded-xl border font-sans text-[13px] font-bold transition-colors"
              :class="gender === 'male' ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
              @click="gender = 'male'"
            >
              男
            </button>
            <button
              class="h-11 rounded-xl border font-sans text-[13px] font-bold transition-colors"
              :class="gender === 'female' ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
              @click="gender = 'female'"
            >
              女
            </button>
          </div>

          <div class="space-y-3">
            <label class="block">
              <span class="font-sans text-[12px] text-brand-secondary font-bold flex items-center gap-1.5 mb-1.5">
                <CalendarDays :size="14" /> 出生日期
              </span>
              <input v-model="birthDate" type="date" class="w-full h-12 rounded-xl bg-brand-paper border border-transparent px-3 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary" />
            </label>
            <label class="block">
              <span class="font-sans text-[12px] text-brand-secondary font-bold flex items-center gap-1.5 mb-1.5">
                <Clock :size="14" /> 出生时间
              </span>
              <input v-model="birthTime" type="time" class="w-full h-12 rounded-xl bg-brand-paper border border-transparent px-3 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary" />
            </label>
            <label class="block">
              <span class="font-sans text-[12px] text-brand-secondary font-bold flex items-center gap-1.5 mb-1.5">
                <User :size="14" /> 姓名
              </span>
              <input v-model="profileName" maxlength="64" placeholder="可选" class="w-full h-12 rounded-xl bg-brand-paper border border-transparent px-3 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary" />
            </label>
            <label class="block">
              <span class="font-sans text-[12px] text-brand-secondary font-bold flex items-center gap-1.5 mb-1.5">
                <MapPin :size="14" /> 出生地
              </span>
              <input v-model="birthPlace" maxlength="128" placeholder="可选，默认中国大陆时区" class="w-full h-12 rounded-xl bg-brand-paper border border-transparent px-3 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary" />
            </label>
          </div>

          <button
            class="mt-5 w-full h-12 rounded-xl bg-brand-primary text-white font-sans text-[14px] font-bold shadow-md disabled:opacity-60 disabled:shadow-none"
            :disabled="state.booting || !moduleEnabled"
            @click="void handleSubmit()"
          >
            {{ moduleEnabled ? '生成四柱评测' : '功能暂未开放' }}
          </button>
        </div>

        <div v-if="recentHistory.length" class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-serif text-[16px] font-bold text-brand-ink-strong">历史记录</h3>
            <span class="text-[11px] font-bold text-brand-secondary">{{ recentHistory.length }} 条</span>
          </div>
          <div class="space-y-2">
            <button
              v-for="item in recentHistory"
              :key="item.id"
              class="w-full bg-brand-paper rounded-xl px-3 py-2.5 flex items-center justify-between text-left"
              @click="void restoreReview(item.id)"
            >
              <span>
                <span class="block font-sans text-[13px] font-bold text-brand-ink-strong">{{ formatDateTime(item.birth_date, item.birth_time) }}</span>
                <span class="block font-sans text-[11px] text-brand-secondary mt-0.5">{{ item.status === 'completed' ? '已完成' : item.progress_message || item.status }}</span>
              </span>
              <span class="font-serif text-[20px] font-bold" :class="scoreToneClass(item.score)">{{ item.score ?? '--' }}</span>
            </button>
          </div>
        </div>
      </section>

      <section v-else-if="viewState === 'waiting'" class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm text-center">
        <div class="mx-auto w-14 h-14 rounded-full bg-brand-primary/10 flex items-center justify-center mb-4">
          <RefreshCw :size="26" class="text-brand-primary animate-spin" />
        </div>
        <h2 class="font-serif text-[20px] font-bold text-brand-ink-strong">命盘生成中</h2>
        <p class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-2">{{ progressMessage }}</p>
        <div class="mt-4 rounded-xl bg-brand-paper p-3 text-left">
          <p class="font-sans text-[11px] text-brand-secondary">当前阶段</p>
          <p class="font-sans text-[13px] font-bold text-brand-ink-strong mt-1">{{ currentProgressStage || 'queued' }}</p>
        </div>
      </section>

      <section v-else-if="viewState === 'error_state'" class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
        <div class="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mb-3">
          <AlertCircle :size="24" class="text-red-500" />
        </div>
        <h2 class="font-serif text-[20px] font-bold text-brand-ink-strong">{{ resolveErrorTitle() }}</h2>
        <p class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-2">{{ resolveErrorMessage() }}</p>
        <div class="grid grid-cols-2 gap-2 mt-5">
          <button class="h-11 rounded-xl bg-brand-paper text-brand-ink-strong font-sans text-[13px] font-bold" @click="resetToInput">重新填写</button>
          <button
            class="h-11 rounded-xl bg-brand-primary text-white font-sans text-[13px] font-bold"
            @click="errorType.includes('insufficient') ? emit('navigate-to-tab', 'recharge') : openCustomerServiceModal('review_support', customerServiceCopyForScene('review_support'))"
          >
            {{ errorType.includes('insufficient') ? '去充值' : '联系客服' }}
          </button>
        </div>
      </section>

      <section v-else class="space-y-4">
        <div class="bg-brand-primary text-white rounded-2xl p-5 shadow-md">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="font-sans text-[12px] text-white/70 font-bold">{{ formatDateTime(currentReview?.birth_date || birthDate, currentReview?.birth_time || birthTime) }}</p>
              <h2 class="font-serif text-[22px] font-bold mt-1">命盘综合评测</h2>
              <p class="font-sans text-[12px] text-white/75 mt-1">{{ currentReview?.timezone || 'Asia/Shanghai' }} · {{ currentReview?.gender === 'female' ? '女' : '男' }}</p>
            </div>
            <div class="text-right">
              <p class="font-serif text-[42px] leading-none font-bold">{{ reviewScore || '--' }}</p>
              <p class="font-sans text-[11px] text-white/70 mt-1">综合分</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
          <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">总评</h3>
          <p class="font-serif text-[18px] font-bold text-brand-ink-strong mt-3 leading-snug">{{ summary?.title || '四柱总评生成中' }}</p>
          <p class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-3">{{ summary?.risk || '风险提醒生成中。' }}</p>
          <p class="font-sans text-[13px] text-brand-ink leading-relaxed mt-3">{{ summary?.usage_guidance || '使用建议生成中。' }}</p>
        </div>

        <div class="grid grid-cols-2 gap-2 bg-white rounded-2xl border border-gray-100 p-2 shadow-sm">
          <button
            class="h-10 rounded-xl font-sans text-[13px] font-bold transition-colors"
            :class="activeBranch === 'chart' ? 'bg-brand-primary text-white' : 'bg-brand-paper text-brand-secondary'"
            @click="activeBranch = 'chart'"
          >
            命盘分析
          </button>
          <button
            class="h-10 rounded-xl font-sans text-[13px] font-bold transition-colors"
            :class="activeBranch === 'luck' ? 'bg-brand-primary text-white' : 'bg-brand-paper text-brand-secondary'"
            @click="activeBranch = 'luck'"
          >
            大运分析
          </button>
        </div>

        <div v-if="activeBranch === 'chart'" class="space-y-4">
          <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong mb-3">四柱概览</h3>
            <div class="grid grid-cols-4 gap-2">
              <div v-for="pillar in pillars" :key="pillar.key" class="bg-brand-paper rounded-xl p-2 text-center min-h-[116px]">
                <p class="font-sans text-[10px] font-bold text-brand-secondary">{{ pillar.label }}</p>
                <p class="font-serif text-[22px] font-bold text-brand-ink-strong mt-1">{{ pillar.ganzhi }}</p>
                <p class="font-sans text-[10px] text-brand-secondary mt-1">{{ pillar.stemElement }} / {{ pillar.branchElement }}</p>
                <p class="font-sans text-[10px] text-brand-primary-strong mt-1 leading-tight">{{ pillar.stemTenGod }} · {{ pillar.branchTenGod }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">五行比例</h3>
              <span class="font-sans text-[11px] text-brand-secondary">日主 {{ chart.day_master || '--' }}</span>
            </div>
            <div class="space-y-2.5">
              <div v-for="item in elementCounts" :key="item.element" class="grid grid-cols-[36px_1fr_28px] gap-2 items-center">
                <span class="font-sans text-[12px] font-bold flex items-center gap-1" :class="item.text">
                  <component :is="item.icon" :size="13" />{{ item.element }}
                </span>
                <div class="h-2.5 rounded-full bg-brand-paper overflow-hidden">
                  <div class="h-full rounded-full" :class="item.bar" :style="{ width: `${Math.max(8, item.value / maxElementCount * 100)}%` }"></div>
                </div>
                <span class="font-sans text-[12px] font-bold text-brand-secondary text-right">{{ item.value }}</span>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 mt-4">
              <div class="bg-brand-paper rounded-xl p-3">
                <p class="font-sans text-[11px] text-brand-secondary">旺衰初判</p>
                <p class="font-sans text-[13px] font-bold text-brand-ink-strong mt-1 leading-snug">{{ strength.label || '待生成' }}</p>
              </div>
              <div class="bg-brand-paper rounded-xl p-3">
                <p class="font-sans text-[11px] text-brand-secondary">喜用候选</p>
                <p class="font-sans text-[13px] font-bold text-brand-ink-strong mt-1">{{ favorableElementsText }}</p>
                <p class="font-sans text-[11px] text-brand-secondary mt-1">节制：{{ unfavorableElementsText }}</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-1.5 mt-4">
              <span v-for="tag in interactionTags" :key="tag" class="px-2 py-1 rounded-lg bg-brand-paper text-brand-secondary font-sans text-[11px] font-bold">
                {{ tag }}
              </span>
            </div>
          </div>

          <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">专项内容</h3>
              <span class="font-sans text-[11px] text-brand-secondary">{{ effectiveAspectUnlockPoints }} 积分/项</span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="(aspect, index) in reviewAspects"
                :key="aspect.aspect_key"
                class="rounded-xl border p-3 text-left transition-colors"
                :class="index === activeAspect ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper border-transparent text-brand-ink-strong'"
                @click="void handleAspectClick(aspect, index)"
              >
                <div class="flex items-center justify-between gap-2">
                  <component :is="aspect.icon" :size="18" :class="index === activeAspect ? 'text-white' : aspect.textTint" />
                  <span class="font-serif text-[18px] font-bold">{{ aspect.score ?? '--' }}</span>
                </div>
                <div class="font-sans text-[13px] font-bold mt-2">{{ aspect.short_title || aspect.title }}</div>
                <div class="font-sans text-[10px] mt-1 flex items-center gap-1" :class="index === activeAspect ? 'text-white/70' : 'text-brand-secondary'">
                  <Check v-if="aspect.is_unlocked" :size="12" />
                  <Lock v-else :size="12" />
                  <span>{{ aspect.is_unlocked ? '已解锁' : `${aspect.unlock_points || effectiveAspectUnlockPoints} 积分` }}</span>
                </div>
              </button>
            </div>

            <div v-if="selectedAspect" class="mt-4 rounded-xl bg-brand-paper p-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedAspect.short_title || selectedAspect.title }}</p>
                  <h4 class="font-serif text-[18px] font-bold text-brand-ink-strong mt-1">{{ selectedAspect.title }}</h4>
                </div>
                <button
                  v-if="!selectedAspect.is_unlocked"
                  class="h-9 px-3 rounded-lg bg-brand-primary text-white font-sans text-[12px] font-bold inline-flex items-center gap-1 disabled:opacity-60"
                  :disabled="selectedAspectPending"
                  @click="void unlockSelectedAspect(selectedAspect)"
                >
                  <UnlockKeyhole :size="14" />
                  {{ selectedAspectPending ? '生成中' : '解锁' }}
                </button>
              </div>
              <p class="font-sans text-[13px] text-brand-ink leading-relaxed mt-3">
                {{ selectedAspect.content || (selectedAspectPending ? `专项内容正在生成中，第 ${unlockWaitingAttempt || 1} 次确认。` : '解锁后展示完整专项内容。') }}
              </p>
              <p v-if="selectedAspect.risk" class="font-sans text-[13px] text-red-600 leading-relaxed mt-3">{{ selectedAspect.risk }}</p>
            </div>
          </div>
        </div>

        <div v-else class="space-y-4">
          <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">大运时间轴</h3>
              <span class="font-sans text-[11px] text-brand-secondary">综评 {{ luckCycleCost }} / 流年 {{ luckYearCost }} 积分</span>
            </div>
            <div class="flex gap-2 overflow-x-auto pb-1">
              <button
                v-for="cycle in luckCycles"
                :key="cycle.cycle_key"
                class="shrink-0 min-w-[94px] rounded-xl border px-3 py-2 text-left"
                :class="cycle.cycle_key === selectedLuckCycle?.cycle_key ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper border-transparent text-brand-ink-strong'"
                @click="activeCycleKey = cycle.cycle_key; selectedLuckYear = cycle.year_items.find((item) => item.is_current)?.year || cycle.year_items[0]?.year || null"
              >
                <span class="block font-serif text-[17px] font-bold">{{ cycle.display_ganzhi || cycle.ganzhi || '起运前' }}</span>
                <span class="block font-sans text-[10px] mt-1">{{ cycle.start_year }}-{{ cycle.end_year }}</span>
                <span class="block font-sans text-[10px] mt-1">{{ cycle.is_current ? '当前大运' : luckStatusText(cycle.render_status) }}</span>
              </button>
            </div>
          </div>

          <div v-if="selectedLuckCycle" class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedLuckCycle.start_year }}-{{ selectedLuckCycle.end_year }} · {{ selectedLuckCycle.start_age }}-{{ selectedLuckCycle.end_age }} 岁</p>
                <h3 class="font-serif text-[19px] font-bold text-brand-ink-strong mt-1">{{ selectedLuckCycle.display_ganzhi || selectedLuckCycle.ganzhi || '起运前' }} 大运</h3>
                <p class="font-sans text-[12px] text-brand-secondary mt-1">{{ selectedLuckCycle.stem_ten_god || '过渡阶段' }} · {{ luckStatusText(selectedLuckCycle.render_status) }}</p>
              </div>
              <button
                class="h-9 px-3 rounded-lg bg-brand-primary text-white font-sans text-[12px] font-bold inline-flex items-center gap-1 disabled:opacity-60"
                :disabled="!luckGenerationEnabled || isGeneratingLuckTarget(`cycle:${selectedLuckCycle.cycle_key}`) || selectedLuckCycle.render_status === 'processing'"
                @click="void handleGenerateCycle(selectedLuckCycle)"
              >
                <RefreshCw v-if="isGeneratingLuckTarget(`cycle:${selectedLuckCycle.cycle_key}`) || selectedLuckCycle.render_status === 'processing'" :size="14" class="animate-spin" />
                <Sparkles v-else :size="14" />
                {{ selectedLuckCycle.render_status === 'completed' ? '重新查看' : selectedLuckCycle.render_status === 'failed' ? '重试' : '生成综评' }}
              </button>
            </div>
            <div v-if="selectedLuckCycle.render?.result" class="mt-4 space-y-3">
              <p class="font-serif text-[18px] font-bold text-brand-ink-strong leading-snug">{{ luckRenderText(selectedLuckCycle.render, 'title') }}</p>
              <p class="font-sans text-[13px] text-brand-ink leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'core_theme') }}</p>
              <p class="font-sans text-[13px] text-emerald-700 leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'opportunities') }}</p>
              <p class="font-sans text-[13px] text-red-600 leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'risks') }}</p>
              <p class="font-sans text-[13px] text-brand-secondary leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'action_guidance') }}</p>
            </div>
            <p v-else class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-4">
              {{ selectedLuckCycle.render_status === 'processing' ? '大运综评正在生成中。' : '点击生成后查看这一阶段的十年主轴、机会、风险和行动建议。' }}
            </p>
          </div>

          <div v-if="selectedLuckCycle" class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">流年拆解</h3>
              <span class="font-sans text-[11px] text-brand-secondary">{{ selectedLuckCycle.start_year }}-{{ selectedLuckCycle.end_year }}</span>
            </div>
            <div class="grid grid-cols-5 gap-2">
              <button
                v-for="item in selectedLuckCycle.year_items"
                :key="item.year"
                class="rounded-xl border px-2 py-2 text-center"
                :class="item.year === selectedLuckYear ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper border-transparent text-brand-ink-strong'"
                @click="selectedLuckYear = item.year"
              >
                <span class="block font-sans text-[11px] font-bold">{{ item.year }}</span>
                <span class="block font-serif text-[15px] font-bold mt-0.5">{{ item.ganzhi }}</span>
              </button>
            </div>

            <div v-if="selectedLuckYearItem" class="mt-4 rounded-xl bg-brand-paper p-4">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedLuckYearItem.year }} · {{ selectedLuckYearItem.age }} 岁 · {{ selectedLuckYearItem.stem_ten_god }}</p>
                  <h4 class="font-serif text-[18px] font-bold text-brand-ink-strong mt-1">{{ selectedLuckYearItem.ganzhi }} 流年</h4>
                  <p class="font-sans text-[11px] text-brand-secondary mt-1">{{ luckStatusText(selectedLuckYearItem.render_status) }}</p>
                </div>
                <button
                  class="h-9 px-3 rounded-lg bg-brand-primary text-white font-sans text-[12px] font-bold inline-flex items-center gap-1 disabled:opacity-60"
                  :disabled="!luckGenerationEnabled || isGeneratingLuckTarget(`year:${selectedLuckCycle.cycle_key}:${selectedLuckYearItem.year}`) || selectedLuckYearItem.render_status === 'processing'"
                  @click="void handleGenerateYear(selectedLuckCycle, selectedLuckYearItem)"
                >
                  <RefreshCw v-if="isGeneratingLuckTarget(`year:${selectedLuckCycle.cycle_key}:${selectedLuckYearItem.year}`) || selectedLuckYearItem.render_status === 'processing'" :size="14" class="animate-spin" />
                  <CalendarDays v-else :size="14" />
                  {{ selectedLuckYearItem.render_status === 'completed' ? '重新查看' : selectedLuckYearItem.render_status === 'failed' ? '重试' : '生成' }}
                </button>
              </div>
              <div v-if="selectedLuckYearItem.render?.result" class="mt-4 space-y-3">
                <p class="font-serif text-[17px] font-bold text-brand-ink-strong leading-snug">{{ luckRenderText(selectedLuckYearItem.render, 'title') }}</p>
                <p class="font-sans text-[13px] text-brand-ink leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'year_focus') }}</p>
                <p class="font-sans text-[13px] text-emerald-700 leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'opportunities') }}</p>
                <p class="font-sans text-[13px] text-red-600 leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'risks') }}</p>
                <p class="font-sans text-[13px] text-brand-secondary leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'action_guidance') }}</p>
              </div>
              <p v-else class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-3">
                {{ selectedLuckYearItem.render_status === 'processing' ? '这一年正在生成中。' : '点击生成后查看这一年的事业、财富、关系和健康触发点。' }}
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -12px);
}
</style>
