<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, type Component } from 'vue';
import {
  AlertCircle,
  ArrowLeft,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronUp,
  Clock,
  Heart,
  HeartPulse,
  Lock,
  MapPin,
  Mountain,
  RefreshCw,
  Shield,
  Sparkles,
  TrendingUp,
  UnlockKeyhole,
  User,
} from 'lucide-vue-next';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../../config/pricing';
import { ApiError } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { FourPillarsAspect, FourPillarsChartDisplay, FourPillarsReviewRecord, Gender, ReviewProgressStage } from '../../types/api';
import type { FourPillarsLuckCycle, FourPillarsLuckRenderRecord, FourPillarsLuckYearItem, FourPillarsShenShaDetail } from '../../types/api';
import FourPillarsNatalTable from './FourPillarsNatalTable.vue';

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

type LuckTableColumn = {
  label: string;
  ganzhi: string;
  stem: string;
  branch: string;
  stemElement: string;
  branchElement: string;
  stemTenGod: string;
  hiddenStems: Array<{ stem: string; element: string; ten_god: string }>;
  diShi: string;
  selfSitting: string;
  shenShaRows: ShenShaCellItem[];
  isLuck?: boolean;
};

type ShenShaCellItem = {
  name: string;
  meaning: string;
  category: string;
};
const SHEN_SHA_NAME_ORDER: Record<string, number> = {
  天乙贵人: 10,
  太极贵人: 20,
  福星贵人: 30,
  天德贵人: 40,
  月德贵人: 41,
  天德合: 42,
  月德合: 43,
  文昌: 50,
  国印贵人: 51,
  金舆: 60,
  禄神: 61,
  天喜: 70,
  红鸾: 71,
  童子: 72,
  天医: 80,
  华盖: 90,
  将星: 100,
  桃花: 110,
  驿马: 120,
  孤辰: 130,
  寡宿: 131,
  魁罡: 140,
  天赦: 150,
  羊刃: 200,
  飞刃: 201,
  亡神: 210,
  劫煞: 211,
  灾煞: 212,
  元辰: 213,
  勾煞: 214,
  绞煞: 215,
  五鬼: 216,
  阴阳差错: 220,
  长生: 800,
  沐浴: 801,
  冠带: 802,
  临官: 803,
  帝旺: 804,
  衰: 805,
  病: 806,
  死: 807,
  墓: 808,
  绝: 809,
  胎: 810,
  养: 811,
  空亡: 900,
  墓库: 910,
};
const SHEN_SHA_CATEGORY_ORDER: Record<string, number> = {
  support: 10,
  talent: 20,
  wealth: 30,
  relationship: 40,
  spiritual: 45,
  movement: 50,
  health: 55,
  risk: 60,
  life_stage: 80,
  structure: 90,
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
const birthYear = ref('');
const birthMonth = ref('');
const birthDay = ref('');
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
const luckShenShaExpanded = ref(false);

let disposed = false;
let pollingPromise: Promise<FourPillarsReviewRecord> | null = null;

const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const ASPECT_UNLOCK_RETRY_LIMIT = 45;
const ASPECT_UNLOCK_RETRY_DELAY_MS = 2000;
const LUCK_RENDER_RETRY_LIMIT = 90;
const LUCK_RENDER_RETRY_DELAY_MS = 2000;
const MAX_SHEN_SHA_ROWS = 3;

const aspectUiMap: Record<string, { icon: Component; tint: string; textTint: string }> = {
  personality: { icon: Sparkles, tint: 'bg-brand-paper text-brand-secondary', textTint: 'text-brand-secondary' },
  career: { icon: Shield, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  wealth: { icon: TrendingUp, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  love: { icon: Heart, tint: 'bg-rose-50 text-rose-600', textTint: 'text-rose-600' },
  health: { icon: HeartPulse, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  family_environment: { icon: Mountain, tint: 'bg-slate-50 text-slate-600', textTint: 'text-slate-600' },
};

const stemInfo: Record<string, { element: '木' | '火' | '土' | '金' | '水'; yinYang: 'yin' | 'yang' }> = {
  甲: { element: '木', yinYang: 'yang' },
  乙: { element: '木', yinYang: 'yin' },
  丙: { element: '火', yinYang: 'yang' },
  丁: { element: '火', yinYang: 'yin' },
  戊: { element: '土', yinYang: 'yang' },
  己: { element: '土', yinYang: 'yin' },
  庚: { element: '金', yinYang: 'yang' },
  辛: { element: '金', yinYang: 'yin' },
  壬: { element: '水', yinYang: 'yang' },
  癸: { element: '水', yinYang: 'yin' },
};

const elementProduces: Record<string, string> = { 木: '火', 火: '土', 土: '金', 金: '水', 水: '木' };
const elementControls: Record<string, string> = { 木: '土', 土: '水', 水: '火', 火: '金', 金: '木' };
const hiddenStemMap: Record<string, Array<{ stem: string; element: string }>> = {
  子: [{ stem: '癸', element: '水' }],
  丑: [{ stem: '己', element: '土' }, { stem: '癸', element: '水' }, { stem: '辛', element: '金' }],
  寅: [{ stem: '甲', element: '木' }, { stem: '丙', element: '火' }, { stem: '戊', element: '土' }],
  卯: [{ stem: '乙', element: '木' }],
  辰: [{ stem: '戊', element: '土' }, { stem: '乙', element: '木' }, { stem: '癸', element: '水' }],
  巳: [{ stem: '丙', element: '火' }, { stem: '庚', element: '金' }, { stem: '戊', element: '土' }],
  午: [{ stem: '丁', element: '火' }, { stem: '己', element: '土' }],
  未: [{ stem: '己', element: '土' }, { stem: '丁', element: '火' }, { stem: '乙', element: '木' }],
  申: [{ stem: '庚', element: '金' }, { stem: '壬', element: '水' }, { stem: '戊', element: '土' }],
  酉: [{ stem: '辛', element: '金' }],
  戌: [{ stem: '戊', element: '土' }, { stem: '辛', element: '金' }, { stem: '丁', element: '火' }],
  亥: [{ stem: '壬', element: '水' }, { stem: '甲', element: '木' }],
};

const currentReview = computed(() => state.currentFourPillarsReview);
const birthDate = computed(() => buildBirthDate());
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
const chartDisplay = computed<FourPillarsChartDisplay | null>(() => currentReview.value?.chart_display ?? null);
const facts = computed(() => asRecord(currentReview.value?.deterministic_facts));
const dayMaster = computed(() => asRecord(facts.value.day_master));
const strength = computed(() => asRecord(dayMaster.value.strength));
const elementCounts = computed(() => {
  const counts = asRecord(facts.value.element_counts);
  return ['木', '火', '土', '金', '水'].map((element) => ({
    element,
    value: Number(counts[element] ?? 0),
  }));
});
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
const luckTableColumns = computed<LuckTableColumn[]>(() => {
  const columns: LuckTableColumn[] = [];
  const rawPillars = chartDisplay.value?.pillars;
  const dayStem = rawPillars?.day?.stem || String(chart.value.day_master || '');
  if (rawPillars) {
    (['year', 'month', 'day', 'hour'] as const).forEach((key) => {
      const pillar = rawPillars[key];
      columns.push({
        label: pillar.label,
        ganzhi: pillar.ganzhi,
        stem: pillar.stem,
        branch: pillar.branch,
        stemElement: pillar.stem_element,
        branchElement: pillar.branch_element,
        stemTenGod: pillar.stem_ten_god,
        hiddenStems: pillar.hidden_stems.map((item) => ({ ...item, ten_god: item.ten_god || '-' })),
        diShi: pillar.di_shi,
        selfSitting: pillar.self_sitting,
        shenShaRows: shenShaRows(pillar.shen_sha, pillar.shen_sha_details, pillar.di_shi),
      });
    });
  }

  columns.push(toLuckColumn('大运', selectedLuckCycle.value, dayStem));
  columns.push(toLuckColumn('流年', selectedLuckYearItem.value, dayStem));
  return columns;
});
const luckHasOverflowingShenSha = computed(() => luckTableColumns.value.some((column) => column.shenShaRows.length > MAX_SHEN_SHA_ROWS));
const favorableElementsText = computed(() => toStringList(dayMaster.value.favorable_elements).join('、') || '待生成');
const unfavorableElementsText = computed(() => toStringList(dayMaster.value.unfavorable_elements).join('、') || '待生成');
const elementRatioSummary = computed(() => {
  const ratioText = elementCounts.value.map((item) => `${item.element}${item.value}`).join('、');
  const parts = [`五行比例：${ratioText || '待生成'}`];
  if (strength.value.label) parts.push(`旺衰初判：${strength.value.label}`);
  if (favorableElementsText.value !== '待生成') parts.push(`喜用候选：${favorableElementsText.value}`);
  if (unfavorableElementsText.value !== '待生成') parts.push(`节制：${unfavorableElementsText.value}`);
  return `${parts.join('；')}。`;
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

function toLuckColumn(
  label: '大运' | '流年',
  item: FourPillarsLuckCycle | FourPillarsLuckYearItem | null,
  dayStem: string,
): LuckTableColumn {
  const stem = String(item?.stem || '').trim();
  const branch = String(item?.branch || '').trim();
  const hiddenStems = (hiddenStemMap[branch] || []).map((hidden) => ({
    stem: hidden.stem,
    element: hidden.element,
    ten_god: calculateTenGod(dayStem, hidden.stem),
  }));
  return {
    label,
    ganzhi: String(item?.ganzhi || ('display_ganzhi' in (item || {}) ? (item as FourPillarsLuckCycle).display_ganzhi : '') || '-'),
    stem: stem || '-',
    branch: branch || '-',
    stemElement: String(item?.stem_element || elementOfStem(stem) || '-'),
    branchElement: String(item?.branch_element || elementOfBranch(branch) || '-'),
    stemTenGod: String(item?.stem_ten_god || calculateTenGod(dayStem, stem) || '-'),
    hiddenStems,
    diShi: String(item?.di_shi || calculateDiShi(dayStem, branch) || '-'),
    selfSitting: calculateDiShi(stem, branch),
    shenShaRows: shenShaRows(item?.shen_sha, item?.shen_sha_details, String(item?.di_shi || calculateDiShi(dayStem, branch) || '')),
    isLuck: true,
  };
}

function shenShaRows(namesValue: unknown, detailsValue: unknown, diShiValue: unknown = ''): ShenShaCellItem[] {
  const details = Array.isArray(detailsValue) ? detailsValue as FourPillarsShenShaDetail[] : [];
  const detailByName = new Map<string, FourPillarsShenShaDetail>();
  details.forEach((item) => {
    if (item?.name && !detailByName.has(item.name)) {
      detailByName.set(item.name, item);
    }
  });
  const names = toStringList(namesValue).length ? toStringList(namesValue) : details.map((item) => item.name);
  const rows = [...new Set(names.map((item) => String(item || '').trim()).filter(Boolean))].map((name) => {
    const detail = detailByName.get(name);
    return {
      name,
      meaning: String(detail?.meaning || ''),
      category: String(detail?.category || ''),
    };
  });
  const diShi = String(diShiValue || '').trim();
  if (diShi && diShi !== '-' && !rows.some((item) => item.name === diShi)) {
    rows.push({
      name: diShi,
      meaning: '十二长生地势',
      category: 'life_stage',
    });
  }
  return sortShenShaRows(rows);
}

function sortShenShaRows(rows: ShenShaCellItem[]): ShenShaCellItem[] {
  return rows
    .map((item, index) => ({ ...item, index }))
    .sort((left, right) => {
      const nameDelta = (SHEN_SHA_NAME_ORDER[left.name] ?? 500) - (SHEN_SHA_NAME_ORDER[right.name] ?? 500);
      if (nameDelta !== 0) return nameDelta;
      const categoryDelta = (SHEN_SHA_CATEGORY_ORDER[left.category] ?? 99) - (SHEN_SHA_CATEGORY_ORDER[right.category] ?? 99);
      if (categoryDelta !== 0) return categoryDelta;
      return left.index - right.index;
    })
    .map(({ index: _index, ...item }) => item);
}

function visibleLuckShenShaRows(column: LuckTableColumn): ShenShaCellItem[] {
  return luckShenShaExpanded.value ? column.shenShaRows : column.shenShaRows.slice(0, MAX_SHEN_SHA_ROWS);
}

function shenShaToneClass(item: ShenShaCellItem): string {
  const text = `${item.category}${item.name}${item.meaning}`;
  if (/[贵人德福喜禄昌合]/u.test(text)) return 'shen-sha-positive';
  if (/[煞亡劫灾孤寡空刃]/u.test(text)) return 'shen-sha-caution';
  return 'shen-sha-neutral';
}

function calculateTenGod(dayStem: string, targetStem: string): string {
  if (!dayStem || !targetStem || dayStem === '-' || targetStem === '-') return '-';
  if (dayStem === targetStem) return '日元';
  const self = stemInfo[dayStem];
  const target = stemInfo[targetStem];
  if (!self || !target) return '-';
  const samePolarity = self.yinYang === target.yinYang;
  if (self.element === target.element) return samePolarity ? '比肩' : '劫财';
  if (elementProduces[target.element] === self.element) return samePolarity ? '偏印' : '正印';
  if (elementProduces[self.element] === target.element) return samePolarity ? '食神' : '伤官';
  if (elementControls[self.element] === target.element) return samePolarity ? '偏财' : '正财';
  if (elementControls[target.element] === self.element) return samePolarity ? '七杀' : '正官';
  return '-';
}

function elementOfStem(stem: string): string {
  return stemInfo[stem]?.element || '';
}

function elementOfBranch(branch: string): string {
  const hidden = hiddenStemMap[branch]?.[0];
  return hidden?.element || '';
}

function calculateDiShi(dayStem: string, branch: string): string {
  const branchOrder = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
  const stages = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养'];
  const startMap: Record<string, { start: string; dir: 1 | -1 }> = {
    甲: { start: '亥', dir: 1 },
    乙: { start: '午', dir: -1 },
    丙: { start: '寅', dir: 1 },
    丁: { start: '酉', dir: -1 },
    戊: { start: '寅', dir: 1 },
    己: { start: '酉', dir: -1 },
    庚: { start: '巳', dir: 1 },
    辛: { start: '子', dir: -1 },
    壬: { start: '申', dir: 1 },
    癸: { start: '卯', dir: -1 },
  };
  const config = startMap[dayStem];
  const startIndex = branchOrder.indexOf(config?.start || '');
  const targetIndex = branchOrder.indexOf(branch);
  if (!config || startIndex < 0 || targetIndex < 0) return '-';
  let diff = (targetIndex - startIndex) * config.dir;
  if (diff < 0) diff += 12;
  return stages[diff % 12];
}

function elementBadgeClass(element: string): string {
  if (element === '木') return 'bg-[#ECFDF5] text-[#059669] border-[#A7F3D0]';
  if (element === '火') return 'bg-[#FFF1F2] text-[#E11D48] border-[#FECDD3]';
  if (element === '土') return 'bg-[#FFFBEB] text-[#B45309] border-[#FCD34D]';
  if (element === '金') return 'bg-[#FFF7DA] text-[#B7791F] border-[#F4D27A]';
  if (element === '水') return 'bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]';
  return 'bg-white text-slate-500 border-slate-100';
}

function ganzhiElementClasses(ganzhi: string | null | undefined): string[] {
  const text = String(ganzhi || '');
  const stem = text.match(/[甲乙丙丁戊己庚辛壬癸]/u)?.[0] || '';
  const element = elementOfStem(stem);
  return elementBadgeClass(element).split(' ');
}

function showToast(message: string, duration = 2200): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, duration);
}

function sanitizeDatePart(value: string, maxLength: number): string {
  return String(value || '').replace(/\D/gu, '').slice(0, maxLength);
}

function buildBirthDate(): string {
  const yearText = sanitizeDatePart(birthYear.value, 4);
  const monthText = sanitizeDatePart(birthMonth.value, 2);
  const dayText = sanitizeDatePart(birthDay.value, 2);
  if (!/^\d{4}$/u.test(yearText) || !/^\d{1,2}$/u.test(monthText) || !/^\d{1,2}$/u.test(dayText)) {
    return '';
  }
  return `${yearText}-${monthText.padStart(2, '0')}-${dayText.padStart(2, '0')}`;
}

function applyBirthDateParts(value: string): void {
  const match = String(value || '').match(/^(\d{4})-(\d{2})-(\d{2})$/u);
  if (!match) {
    birthYear.value = '';
    birthMonth.value = '';
    birthDay.value = '';
    return;
  }
  birthYear.value = match[1];
  birthMonth.value = String(Number(match[2]));
  birthDay.value = String(Number(match[3]));
}

function validateBirthInput(): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/u.test(birthDate.value) || !/^\d{2}:\d{2}$/u.test(birthTime.value)) {
    setError('birth_datetime');
    return false;
  }
  const parsed = new Date(`${birthDate.value}T${birthTime.value}:00`);
  const [yearText, monthText, dayText] = birthDate.value.split('-');
  if (
    Number.isNaN(parsed.getTime())
    || parsed.getFullYear() !== Number(yearText)
    || parsed.getMonth() + 1 !== Number(monthText)
    || parsed.getDate() !== Number(dayText)
  ) {
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
  applyBirthDateParts(review.birth_date);
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
    birth_datetime: '请填写有效的出生年月日和出生时间。',
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
          class="h-9 rounded-lg bg-white border border-gray-100 px-3 text-brand-secondary font-sans text-[12px] font-bold flex items-center justify-center gap-1.5 shadow-sm"
          @click="handleHeaderBackAction"
        >
          <ArrowLeft :size="14" class="text-brand-ink-strong" />
          <span>{{ viewState === 'result' ? '重新评测' : '返回首页' }}</span>
        </button>
        <div class="text-center">
          <h1 class="font-serif text-[18px] font-bold text-brand-ink-strong leading-none">四柱八字评测</h1>
          <p class="font-sans text-[11px] text-brand-secondary mt-1">公历生日时辰 · 默认北京时间</p>
        </div>
        <button class="w-9 h-9 rounded-lg bg-white border border-gray-100 flex items-center justify-center shadow-sm" @click="refreshActiveReview">
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
              <div class="grid grid-cols-[1.15fr_0.85fr_0.85fr] gap-2">
                <div class="relative">
                  <input
                    v-model="birthYear"
                    inputmode="numeric"
                    pattern="[0-9]*"
                    maxlength="4"
                    placeholder="1989"
                    class="w-full h-12 rounded-xl bg-brand-paper border border-transparent pl-3 pr-8 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary"
                    @input="birthYear = sanitizeDatePart(birthYear, 4)"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 font-sans text-[12px] font-bold text-brand-secondary">年</span>
                </div>
                <div class="relative">
                  <input
                    v-model="birthMonth"
                    inputmode="numeric"
                    pattern="[0-9]*"
                    maxlength="2"
                    placeholder="5"
                    class="w-full h-12 rounded-xl bg-brand-paper border border-transparent pl-3 pr-8 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary"
                    @input="birthMonth = sanitizeDatePart(birthMonth, 2)"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 font-sans text-[12px] font-bold text-brand-secondary">月</span>
                </div>
                <div class="relative">
                  <input
                    v-model="birthDay"
                    inputmode="numeric"
                    pattern="[0-9]*"
                    maxlength="2"
                    placeholder="22"
                    class="w-full h-12 rounded-xl bg-brand-paper border border-transparent pl-3 pr-8 font-sans text-[14px] text-brand-ink-strong outline-none focus:border-brand-primary"
                    @input="birthDay = sanitizeDatePart(birthDay, 2)"
                  />
                  <span class="absolute right-3 top-1/2 -translate-y-1/2 font-sans text-[12px] font-bold text-brand-secondary">日</span>
                </div>
              </div>
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

      <section v-else-if="viewState === 'waiting'" class="py-8 flex flex-col justify-center min-h-[62vh]">
        <div class="bg-white rounded-2xl p-5 border border-gray-150/75 shadow-sm space-y-5 text-center">
          <div class="relative w-28 h-28 mx-auto flex items-center justify-center select-none">
            <div class="absolute inset-0 bg-brand-primary/5 rounded-full blur-md animate-pulse"></div>
            <svg class="absolute w-28 h-28 text-brand-primary/25 animate-[spin_40s_linear_infinite]" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-dasharray="1 3" stroke-width="1.5" />
              <circle cx="50" cy="50" r="42" fill="none" stroke="currentColor" stroke-dasharray="8 4" stroke-width="1.2" />
            </svg>
            <svg class="absolute w-24 h-24 text-brand-accent/40 animate-[spin_24s_linear_infinite_reverse]" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-dasharray="12 6" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <div class="absolute w-11 h-11 bg-white rounded-full border border-brand-primary/20 shadow-md flex items-center justify-center animate-[spin_8s_ease-in-out_infinite]">
              <Sparkles :size="20" class="text-brand-primary" />
            </div>
          </div>

          <div class="space-y-1">
            <h2 class="font-serif text-[18px] font-bold text-brand-ink-strong tracking-wide">四柱命盘智能推演中</h2>
            <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">{{ progressMessage }}</p>
          </div>

          <div class="space-y-2.5 text-left">
            <div class="flex items-center gap-2.5">
              <span class="waiting-step is-done">✓</span>
              <span class="font-sans text-[12px] font-bold text-brand-ink-strong">出生信息与时区校验</span>
            </div>
            <div class="flex items-center gap-2.5" :class="currentProgressStage === 'queued' ? 'opacity-55' : 'opacity-100'">
              <span class="waiting-step" :class="currentProgressStage !== 'queued' ? 'is-active' : ''">2</span>
              <span class="font-sans text-[12px] font-bold text-brand-ink-strong">排定四柱干支结构</span>
              <RefreshCw v-if="currentProgressStage === 'scoring'" :size="12" class="ml-auto text-brand-primary animate-spin" />
            </div>
            <div class="flex items-center gap-2.5" :class="['rendering', 'finalizing', 'completed'].includes(currentProgressStage || '') ? 'opacity-100' : 'opacity-55'">
              <span class="waiting-step" :class="['rendering', 'finalizing', 'completed'].includes(currentProgressStage || '') ? 'is-active' : ''">3</span>
              <span class="font-sans text-[12px] font-bold text-brand-ink-strong">推演五行旺衰与专项结论</span>
              <RefreshCw v-if="currentProgressStage === 'rendering'" :size="12" class="ml-auto text-brand-primary animate-spin" />
            </div>
            <div class="flex items-center gap-2.5" :class="currentProgressStage === 'completed' ? 'opacity-100' : 'opacity-55'">
              <span class="waiting-step" :class="currentProgressStage === 'completed' ? 'is-active' : ''">4</span>
              <span class="font-sans text-[12px] font-bold text-brand-ink-strong">生成大运与流年基础盘</span>
            </div>
          </div>
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

      <section v-else class="space-y-3">
        <div class="grid grid-cols-[1fr_auto] items-center gap-2">
          <div class="grid grid-cols-2 gap-1 rounded-lg bg-white border border-gray-100 p-1 shadow-sm">
            <button
              class="h-9 rounded-lg font-sans text-[12px] font-bold transition-colors"
              :class="activeBranch === 'chart' ? 'bg-brand-primary text-white shadow-sm' : 'bg-brand-paper text-brand-secondary'"
              @click="activeBranch = 'chart'"
            >
              命盘分析
            </button>
            <button
              class="h-9 rounded-lg font-sans text-[12px] font-bold transition-colors"
              :class="activeBranch === 'luck' ? 'bg-brand-primary text-white shadow-sm' : 'bg-brand-paper text-brand-secondary'"
              @click="activeBranch = 'luck'"
            >
              大运分析
            </button>
          </div>
          <div class="px-3 py-1.5 rounded-lg bg-[#1D4ED8] text-white shadow-sm flex flex-col items-center justify-center leading-none">
            <span class="font-mono font-black text-[13px]">{{ reviewScore || '--' }}分</span>
            <span class="font-sans text-[8px] opacity-85 mt-0.5">综合</span>
          </div>
        </div>

        <div v-if="activeBranch === 'chart'" class="space-y-4">
          <FourPillarsNatalTable :chart-display="chartDisplay" :element-summary="elementRatioSummary" />

          <div class="bg-white rounded-xl border border-[#D8E3F5] p-3 shadow-sm">
            <div class="flex items-center gap-1.5 pb-2">
              <Sparkles :size="14" class="text-[#2563EB]" />
              <h3 class="font-serif text-[14px] font-bold text-[#1D4ED8]">综评</h3>
            </div>
            <p class="font-serif text-[15px] font-bold text-brand-ink-strong mt-2 leading-snug">{{ summary?.title || '四柱总评生成中' }}</p>
            <p class="font-sans text-[12px] text-brand-secondary leading-relaxed mt-2">{{ summary?.risk || '风险提醒生成中。' }}</p>
            <p class="font-sans text-[12px] text-brand-ink leading-relaxed mt-2">{{ summary?.usage_guidance || '使用建议生成中。' }}</p>
          </div>

          <div v-if="!chartDisplay" class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">
            <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong mb-3">四柱概览</h3>
            <div class="grid grid-cols-4 gap-2">
              <div v-for="pillar in pillars" :key="pillar.key" class="bg-brand-paper rounded-xl p-2 text-center min-h-[116px]">
                <p class="font-sans text-[10px] font-bold text-brand-secondary">{{ pillar.label }}</p>
                <div class="mt-1 flex items-center justify-center gap-1">
                  <span class="legacy-ganzhi-glyph" :class="elementBadgeClass(pillar.stemElement)">{{ pillar.stem }}</span>
                  <span class="legacy-ganzhi-glyph" :class="elementBadgeClass(pillar.branchElement)">{{ pillar.branch }}</span>
                </div>
                <p class="font-sans text-[10px] text-brand-primary-strong mt-1 leading-tight">{{ pillar.stemTenGod }} · {{ pillar.branchTenGod }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-[#D8E3F5] p-3 shadow-sm">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-serif text-[14px] font-bold text-[#1D4ED8]">专项</h3>
              <span class="font-sans text-[11px] text-brand-secondary">{{ effectiveAspectUnlockPoints }} 积分/项</span>
            </div>
            <div class="grid grid-cols-3 gap-1.5">
              <button
                v-for="(aspect, index) in reviewAspects"
                :key="aspect.aspect_key"
                class="h-[46px] rounded-lg border px-1.5 text-center transition-colors flex flex-col items-center justify-center"
                :class="index === activeAspect ? 'bg-[#EAF1FF] text-[#1D4ED8] border-[#2563EB]' : 'bg-[#F8FAFF] border-[#D8E3F5] text-brand-ink-strong'"
                @click="void handleAspectClick(aspect, index)"
              >
                <div class="font-sans text-[11px] font-bold leading-none truncate max-w-full">{{ aspect.short_title || aspect.title }}</div>
                <div class="font-sans text-[9px] mt-1 flex items-center gap-0.5" :class="index === activeAspect ? 'text-[#2563EB]' : 'text-brand-secondary'">
                  <Check v-if="aspect.is_unlocked" :size="12" />
                  <Lock v-else :size="12" />
                  <span>{{ aspect.is_unlocked ? `${aspect.score ?? '--'}分` : `${aspect.unlock_points || effectiveAspectUnlockPoints}点` }}</span>
                </div>
              </button>
            </div>

            <div v-if="selectedAspect" class="mt-2 rounded-lg bg-[#F8FAFF] border border-[#D8E3F5] p-3">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedAspect.short_title || selectedAspect.title }}</p>
                  <h4 class="font-serif text-[15px] font-bold text-brand-ink-strong mt-1">{{ selectedAspect.title }}</h4>
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

        <div v-else class="space-y-3">
          <div class="bg-white rounded-xl border border-[#D8E3F5] overflow-hidden shadow-sm">
            <div class="overflow-x-auto no-scrollbar">
              <table class="w-full min-w-[360px] table-fixed border-collapse text-center">
                <thead>
                  <tr class="bg-[#EAF1FF]">
                    <th class="w-[42px] py-1.5 px-1 font-sans text-[10px] text-[#64748B]">项目</th>
                    <th
                      v-for="column in luckTableColumns"
                      :key="`${column.label}-head`"
                      class="py-1.5 px-0.5 font-serif text-[10.5px] font-bold"
                      :class="column.isLuck ? 'bg-[#DBEAFE]/70 text-[#1D4ED8]' : 'text-[#334155]'"
                    >
                      {{ column.label }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="bg-[#F8FAFF]">
                    <td class="luck-row-label">主星</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-god`" class="luck-cell font-serif font-bold" :class="column.isLuck ? 'bg-[#DBEAFE]/35 text-[#1D4ED8]' : 'text-[#334155]'">
                      {{ column.stemTenGod }}
                    </td>
                  </tr>
                  <tr class="bg-white">
                    <td class="luck-row-label">天干</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-stem`" class="luck-cell" :class="column.isLuck ? 'bg-[#DBEAFE]/20' : ''">
                      <span class="luck-glyph" :class="elementBadgeClass(column.stemElement)">{{ column.stem }}</span>
                    </td>
                  </tr>
                  <tr class="bg-white">
                    <td class="luck-row-label">地支</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-branch`" class="luck-cell" :class="column.isLuck ? 'bg-[#DBEAFE]/20' : ''">
                      <span class="luck-glyph" :class="elementBadgeClass(column.branchElement)">{{ column.branch }}</span>
                    </td>
                  </tr>
                  <tr class="bg-[#F8FAFF]">
                    <td class="luck-row-label">藏干</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-hidden`" class="luck-cell" :class="column.isLuck ? 'bg-[#DBEAFE]/20' : ''">
                      <span v-if="!column.hiddenStems.length" class="text-[10px] text-[#94A3B8]">-</span>
                      <span v-for="hidden in column.hiddenStems" :key="`${column.label}-${hidden.stem}`" class="luck-mini">
                        <span class="font-serif font-black" :class="elementBadgeClass(hidden.element)">{{ hidden.stem }}</span>
                        <span>{{ hidden.ten_god }}</span>
                      </span>
                    </td>
                  </tr>
                  <tr class="bg-white">
                    <td class="luck-row-label">地势</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-dishi`" class="luck-cell luck-text" :class="column.isLuck ? 'bg-[#DBEAFE]/25 text-[#1E3A8A]' : ''">
                      {{ column.diShi }}
                    </td>
                  </tr>
                  <tr class="bg-[#F8FAFF]">
                    <td class="luck-row-label">自坐</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-sitting`" class="luck-cell luck-text" :class="column.isLuck ? 'bg-[#DBEAFE]/25 text-[#1E3A8A]' : ''">
                      {{ column.selfSitting }}
                    </td>
                  </tr>
                  <tr class="bg-white">
                    <td class="luck-row-label">
                      <span class="block">神煞</span>
                      <button
                        v-if="luckHasOverflowingShenSha"
                        type="button"
                        class="luck-shen-sha-toggle"
                        :aria-label="luckShenShaExpanded ? '收起神煞' : '展开神煞'"
                        :title="luckShenShaExpanded ? '收起神煞' : '展开神煞'"
                        @click="luckShenShaExpanded = !luckShenShaExpanded"
                      >
                        <ChevronUp v-if="luckShenShaExpanded" :size="11" />
                        <ChevronDown v-else :size="11" />
                      </button>
                    </td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-shen-sha`" class="luck-cell luck-shen-sha" :class="column.isLuck ? 'bg-[#DBEAFE]/20 text-[#1E3A8A]' : ''">
                      <div v-if="column.shenShaRows.length" class="luck-shen-sha-stack">
                        <span
                          v-for="item in visibleLuckShenShaRows(column)"
                          :key="`${column.label}-${item.name}`"
                          class="luck-shen-sha-item"
                          :class="shenShaToneClass(item)"
                          :title="item.meaning || item.name"
                        >
                          {{ item.name }}
                        </span>
                      </div>
                      <span v-else class="text-[10px] text-[#94A3B8]">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="bg-[#F8FAFF]">
              <div class="grid grid-cols-[34px_1fr]">
                <div class="px-1 py-1.5 bg-[#F3F7FF] font-serif font-black text-[11px] text-[#1D4ED8] flex items-center justify-center">大运</div>
                <div class="overflow-x-auto no-scrollbar">
                  <div class="flex min-w-max">
                    <button
                      v-for="cycle in luckCycles"
                      :key="cycle.cycle_key"
                      class="w-[34px] min-h-[76px] py-1 px-0.5 transition-colors text-center flex flex-col items-center justify-center relative"
                      :class="cycle.cycle_key === selectedLuckCycle?.cycle_key ? 'bg-[#DBEAFE] text-[#1D4ED8] font-black' : 'bg-white text-[#475569]'"
                      @click="activeCycleKey = cycle.cycle_key; selectedLuckYear = cycle.year_items.find((item) => item.is_current)?.year || cycle.year_items[0]?.year || null"
                    >
                      <span v-if="cycle.is_current" class="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-[#2563EB]"></span>
                      <span class="font-mono text-[8px] leading-none">{{ cycle.start_age ?? '-' }}岁</span>
                      <span class="luck-strip-ganzhi vertical-ganzhi" :class="ganzhiElementClasses(cycle.display_ganzhi || cycle.ganzhi || '')">{{ cycle.display_ganzhi || cycle.ganzhi || '-' }}</span>
                      <span class="font-mono text-[7px] leading-none mt-1 text-[#64748B]">{{ cycle.start_year }}</span>
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="selectedLuckCycle" class="grid grid-cols-[34px_1fr]">
                <div class="px-1 py-1.5 bg-[#F3F7FF] font-serif font-black text-[11px] text-[#1D4ED8] flex items-center justify-center">流年</div>
                <div class="overflow-x-auto no-scrollbar">
                  <div class="flex min-w-max">
                    <button
                      v-for="item in selectedLuckCycle.year_items"
                      :key="item.year"
                      class="w-[38px] py-1 px-0.5 transition-colors flex flex-col items-center text-center relative"
                      :class="item.year === selectedLuckYear ? 'bg-[#DBEAFE] text-[#1D4ED8] font-black' : 'bg-white text-[#475569]'"
                      @click="selectedLuckYear = item.year"
                    >
                      <span v-if="item.is_current" class="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-[#2563EB]"></span>
                      <span class="font-mono text-[8px] leading-none">{{ item.age ?? '-' }}岁</span>
                      <span class="luck-year-ganzhi" :class="ganzhiElementClasses(item.ganzhi)">{{ item.ganzhi }}</span>
                      <span class="font-mono text-[7px] leading-none mt-1 text-[#64748B]">{{ item.year }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedLuckCycle" class="bg-white rounded-xl border border-[#D8E3F5] p-3 shadow-sm">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedLuckCycle.start_year }}-{{ selectedLuckCycle.end_year }} · {{ selectedLuckCycle.start_age }}-{{ selectedLuckCycle.end_age }} 岁</p>
                <h3 class="font-serif text-[15px] font-bold text-[#1D4ED8] mt-1">大运中评 · {{ selectedLuckCycle.display_ganzhi || selectedLuckCycle.ganzhi || '起运前' }}</h3>
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
            <div v-if="selectedLuckCycle.render?.result" class="mt-3 space-y-2">
              <p class="font-serif text-[15px] font-bold text-brand-ink-strong leading-snug">{{ luckRenderText(selectedLuckCycle.render, 'title') || luckRenderText(selectedLuckCycle.render, 'verdict') }}</p>
              <p class="font-sans text-[12px] text-brand-ink leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'core_theme') || luckRenderText(selectedLuckCycle.render, 'verdict') }}</p>
              <p class="font-sans text-[12px] text-emerald-700 leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'opportunities') }}</p>
              <p class="font-sans text-[12px] text-red-600 leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'risks') || luckRenderText(selectedLuckCycle.render, 'risk_warning') }}</p>
              <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">{{ luckRenderText(selectedLuckCycle.render, 'action_guidance') }}</p>
            </div>
            <p v-else class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-4">
              {{ selectedLuckCycle.render_status === 'processing' ? '大运综评正在生成中。' : '点击生成后查看这一阶段的十年主轴、机会、风险和行动建议。' }}
            </p>
          </div>

          <div v-if="selectedLuckCycle && selectedLuckYearItem" class="bg-white rounded-xl border border-[#D8E3F5] p-3 shadow-sm">
            <div class="rounded-lg bg-[#F8FAFF] border border-[#D8E3F5] p-3">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedLuckYearItem.year }} · {{ selectedLuckYearItem.age }} 岁 · {{ selectedLuckYearItem.stem_ten_god }}</p>
                  <h4 class="font-serif text-[15px] font-bold text-[#1D4ED8] mt-1">流年中评 · {{ selectedLuckYearItem.ganzhi }}</h4>
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
              <div v-if="selectedLuckYearItem.render?.result" class="mt-3 space-y-2">
                <p class="font-serif text-[15px] font-bold text-brand-ink-strong leading-snug">{{ luckRenderText(selectedLuckYearItem.render, 'title') || luckRenderText(selectedLuckYearItem.render, 'verdict') }}</p>
                <p class="font-sans text-[12px] text-brand-ink leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'year_focus') || luckRenderText(selectedLuckYearItem.render, 'work_wealth') }}</p>
                <p class="font-sans text-[12px] text-emerald-700 leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'opportunities') }}</p>
                <p class="font-sans text-[12px] text-red-600 leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'risks') }}</p>
                <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">{{ luckRenderText(selectedLuckYearItem.render, 'action_guidance') || luckRenderText(selectedLuckYearItem.render, 'health_love') }}</p>
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

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.waiting-step {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  background: #F3F7FF;
  color: #94A3B8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
  font-size: 10px;
  font-weight: 900;
  border: 1px solid #E2E8F0;
  flex-shrink: 0;
}

.waiting-step.is-active,
.waiting-step.is-done {
  background: #EAF1FF;
  color: #1D4ED8;
  border-color: #BFDBFE;
}

.luck-row-label {
  background: #F3F7FF;
  color: #1D4ED8;
  font-family: inherit;
  font-size: 10px;
  font-weight: 800;
  padding: 6px 3px;
}

.luck-cell {
  min-height: 36px;
  padding: 4px 3px;
  font-size: 10.5px;
  line-height: 1.2;
  vertical-align: middle;
}

.luck-glyph {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border-width: 1px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 17px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.58), 0 1px 2px rgba(15, 23, 42, 0.05);
}

.vertical-ganzhi {
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 0;
}

.legacy-ganzhi-glyph {
  width: 26px;
  height: 26px;
  border-width: 1px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 15px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
}

.luck-strip-ganzhi,
.luck-year-ganzhi {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-width: 1px;
  border-radius: 999px;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-weight: 900;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.55);
}

.luck-strip-ganzhi {
  min-width: 22px;
  min-height: 34px;
  padding: 4px 2px;
  margin-top: 4px;
  font-size: 14px;
  line-height: 1;
}

.luck-year-ganzhi {
  min-width: 28px;
  min-height: 22px;
  padding: 2px 4px;
  margin-top: 4px;
  font-size: 11px;
  line-height: 1;
}

.luck-mini {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  border: 1px solid #D8E3F5;
  border-radius: 5px;
  background: #FFFFFF;
  color: #64748B;
  padding: 2px 3px;
  margin: 1px;
  font-size: 9px;
  font-weight: 700;
}

.luck-text {
  color: #334155;
  font-family: serif;
  font-weight: 800;
}

.luck-shen-sha {
  color: #475569;
  font-family: inherit;
  font-size: 9px;
  font-weight: 800;
  line-height: 1.35;
  word-break: keep-all;
  vertical-align: top;
}

.luck-shen-sha-toggle {
  width: 18px;
  height: 14px;
  margin: 3px auto 0;
  border: 1px solid #BFDBFE;
  border-radius: 999px;
  color: #1D4ED8;
  background: #FFFFFF;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.luck-shen-sha-stack {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.luck-shen-sha-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid;
  border-radius: 999px;
  padding: 2px 5px;
  font-size: 8.5px;
  font-weight: 800;
  line-height: 1.15;
  white-space: nowrap;
}

.luck-shen-sha-item.shen-sha-positive {
  background: #F8FAFF;
  border-color: #BFDBFE;
  color: #1D4ED8;
}

.luck-shen-sha-item.shen-sha-caution {
  background: #FFF7ED;
  border-color: #FED7AA;
  color: #C2410C;
}

.luck-shen-sha-item.shen-sha-neutral {
  background: #F8FAFC;
  border-color: #E2E8F0;
  color: #475569;
}
</style>
