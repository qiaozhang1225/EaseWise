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
  Search,
  Shield,
  Sparkles,
  TrendingUp,
  UnlockKeyhole,
  User,
  X,
} from 'lucide-vue-next';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../../config/pricing';
import { ApiError, listFourPillarsBirthLocations, resolveFourPillarsInput } from '../../lib/api';
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
type InputMode = 'solar' | 'lunar' | 'bazi';
type InputDrawerTab = InputMode;
type DrawerKind = 'datetime' | 'location' | null;
type LocationScope = 'domestic' | 'overseas';
type WheelScope = 'solar' | 'lunar' | 'domestic-location' | 'overseas-location';
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
  xunKong: string;
  shenShaRows: ShenShaCellItem[];
  isLuck?: boolean;
};

type ShenShaCellItem = {
  name: string;
  meaning: string;
  category: string;
};

type GanzhiDisplayPart = {
  char: string;
  element: string;
  star: string;
};

type BirthLocationOption = {
  id: string;
  scope: string;
  display_name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  country?: string;
  province?: string;
  city?: string;
  district?: string;
  region?: string;
};

type BaziCandidate = {
  birth_date: string;
  birth_time: string;
  solar_datetime: string;
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
const inputMode = ref<InputMode>('solar');
const drawerKind = ref<DrawerKind>(null);
const drawerTab = ref<InputDrawerTab>('solar');
const quickYearOpen = ref(false);
const locationSearch = ref('');
const locationScope = ref<LocationScope>('domestic');
const selectedLocationId = ref('cn-beijing-dongcheng');
const trueSolarPreview = ref<Record<string, unknown> | null>(null);
const lunarInput = ref({ year: 1989, month: 4, day: 18, hour: 8, minute: 0, is_leap_month: false });
const baziInput = ref({ year: '庚辰', month: '戊寅', day: '戊午', hour: '壬子', base_year: 1801, candidate_index: 0 });
const baziCandidates = ref<BaziCandidate[]>([]);
const baziCandidateLoading = ref(false);
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
const waitingStep = ref(1);
const waitingStepProgress = ref([0, 0, 0, 0]);
const waitingPoemIndex = ref(0);

let disposed = false;
let pollingPromise: Promise<FourPillarsReviewRecord> | null = null;
const wheelScrollTimers = new WeakMap<HTMLElement, number>();

const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const ASPECT_UNLOCK_RETRY_LIMIT = 45;
const ASPECT_UNLOCK_RETRY_DELAY_MS = 2000;
const LUCK_RENDER_RETRY_LIMIT = 90;
const LUCK_RENDER_RETRY_DELAY_MS = 2000;
const MAX_SHEN_SHA_ROWS = 3;
const LIFE_STAGE_NAMES = new Set(['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']);

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
const branchOrder = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const stemOrder = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const validGanzhiPairs = branchOrder.flatMap((branch, branchIndex) =>
  stemOrder.filter((_, stemIndex) => stemIndex % 2 === branchIndex % 2).map((stem) => `${stem}${branch}`),
);
const fallbackLocationOptions: BirthLocationOption[] = [
  { id: 'cn-110101', scope: 'domestic', display_name: '中国 北京市 北京市 东城区', latitude: 39.917544, longitude: 116.418757, timezone: 'Asia/Shanghai', country: '中国', province: '北京市', city: '北京市', district: '东城区' },
];
const locationOptions = ref<BirthLocationOption[]>(fallbackLocationOptions);

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
const waitingPoemLines = [
  '三元及第冠群芳',
  '万般皆是命排来',
  '乾坤造化归神妙',
  '五行中和呈造化',
  '大运流年皆有定',
  '推星算理释疑忧',
];
const waitingPoemLine = computed(() => waitingPoemLines[waitingPoemIndex.value] || waitingPoemLines[0]);
const waitingSteps = [
  {
    title: '出生信息与时间校验',
    desc: '校验公历生辰、时区与真太阳时基础信息',
    message: '正在校验出生时间与真太阳时',
    durationMs: 2000,
  },
  {
    title: '排定四柱干支结构',
    desc: '依六十甲子排定年、月、日、时四柱',
    message: '正在精排格造八字乾坤盘',
    durationMs: 2000,
  },
  {
    title: '推演五行旺衰与专项结论',
    desc: '推演日主旺衰、十神格局与专项分支',
    message: '正在推演五行衰旺与十神格局',
    durationMs: 5000,
  },
  {
    title: '生成大运与流年基本盘',
    desc: '生成大运流年基本盘并等待后台结果就绪',
    message: '正在编织大运流年终身基本盘',
    durationMs: 5000,
  },
];
const waitingTotalProgress = computed(() => Math.min(100, Math.round(waitingStepProgress.value.reduce((sum, item) => sum + item, 0) / waitingSteps.length)));
const waitingActionText = computed(() => waitingSteps[waitingStep.value - 1]?.message || progressMessage.value);
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
const selectedLocation = computed(() => locationOptions.value.find((item) => item.id === selectedLocationId.value) || locationOptions.value[0] || fallbackLocationOptions[0]);
const domesticLocations = computed(() => locationOptions.value.filter((item) => item.scope === 'domestic'));
const overseasLocations = computed(() => locationOptions.value.filter((item) => item.scope === 'overseas'));
const domesticProvinces = computed(() => uniqueValues(domesticLocations.value.map((item) => item.province || item.city || '未知地')));
const domesticCities = computed(() => {
  const province = selectedLocation.value.province || domesticProvinces.value[0] || '';
  return uniqueValues(domesticLocations.value.filter((item) => (item.province || item.city) === province).map((item) => item.city || item.province || '北京时间'));
});
const domesticDistricts = computed(() => {
  const province = selectedLocation.value.province || domesticProvinces.value[0] || '';
  const city = selectedLocation.value.city || domesticCities.value[0] || '';
  return uniqueValues(domesticLocations.value.filter((item) => (item.province || item.city) === province && (item.city || item.province) === city).map((item) => item.district || '--'));
});
const overseasCountries = computed(() => uniqueValues(overseasLocations.value.map((item) => item.country || '海外')));
const overseasRegions = computed(() => {
  const country = selectedLocation.value.country || overseasCountries.value[0] || '';
  return uniqueValues(overseasLocations.value.filter((item) => item.country === country).map((item) => item.city || item.region || '地区'));
});
const filteredLocations = computed(() => {
  const keyword = locationSearch.value.trim().toLowerCase();
  if (!keyword) return locationOptions.value;
  return locationOptions.value.filter((item) => item.display_name.toLowerCase().includes(keyword) || item.id.toLowerCase().includes(keyword));
});
const birthDateTimeSummary = computed(() => {
  if (inputMode.value === 'lunar') {
    return `农历 ${lunarInput.value.year}年${lunarInput.value.is_leap_month ? '闰' : ''}${lunarInput.value.month}月${lunarInput.value.day}日 ${String(lunarInput.value.hour).padStart(2, '0')}:${String(lunarInput.value.minute).padStart(2, '0')}`;
  }
  if (inputMode.value === 'bazi') {
    return `${baziInput.value.year} ${baziInput.value.month} ${baziInput.value.day} ${baziInput.value.hour}`;
  }
  return `公历 ${birthDate.value || '---- -- --'} ${birthTime.value || '--:--'}`;
});
const locationSummary = computed(() => selectedLocation.value?.display_name || birthPlace.value || '中国 北京市 东城区');
const trueSolarSummary = computed(() => {
  const display = String(trueSolarPreview.value?.display_text || '');
  const correction = trueSolarPreview.value?.total_correction_minutes;
  if (display) return `${display}（修正 ${correction} 分钟）`;
  return '等待选择时间与地区';
});
const yearOptions = computed(() => Array.from({ length: 299 }, (_, index) => 1801 + index));
const monthOptions = Array.from({ length: 12 }, (_, index) => index + 1);
const dayOptions = Array.from({ length: 31 }, (_, index) => index + 1);
const hourOptions = Array.from({ length: 24 }, (_, index) => index);
const minuteOptions = Array.from({ length: 60 }, (_, index) => index);
const solarHour = computed(() => Number((birthTime.value || '00:00').slice(0, 2)) || 0);
const solarMinute = computed(() => Number((birthTime.value || '00:00').slice(3, 5)) || 0);
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
        xunKong: formatXunKong(pillar.xun_kong, pillar.ganzhi),
        shenShaRows: shenShaRows(pillar.shen_sha, pillar.shen_sha_details),
      });
    });
  }

  columns.push(toLuckColumn('大运', selectedLuckCycle.value, dayStem));
  columns.push(toLuckColumn('流年', selectedLuckYearItem.value, dayStem));
  return columns;
});
const luckHasOverflowingShenSha = computed(() => luckTableColumns.value.some((column) => column.shenShaRows.length > MAX_SHEN_SHA_ROWS));
const favorableElementsList = computed(() => toStringList(dayMaster.value.favorable_elements));
const unfavorableElementsList = computed(() => toStringList(dayMaster.value.unfavorable_elements));

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

watch([drawerKind, drawerTab, locationScope], () => {
  window.setTimeout(scrollSelectedWheelOptions, 80);
});

onMounted(() => {
  void bootstrapApp();
  void loadBirthLocations();
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

function uniqueValues(values: string[]): string[] {
  return [...new Set(values.map((item) => String(item || '').trim()).filter(Boolean))];
}

function twoDigit(value: number | string): string {
  return String(value).padStart(2, '0');
}

function lunarMonthLabel(value: number): string {
  const labels = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊'];
  return labels[value - 1] || String(value);
}

function lunarDayLabel(value: number): string {
  const prefixes = ['初', '十', '廿', '三'];
  const digits = ['十', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
  if (value === 10) return '初十';
  if (value === 20) return '二十';
  if (value === 30) return '三十';
  const tens = Math.floor(value / 10);
  const ones = value % 10;
  return `${prefixes[tens]}${digits[ones] || ''}`;
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
    xunKong: formatXunKong(item?.xun_kong, String(item?.ganzhi || ('display_ganzhi' in (item || {}) ? (item as FourPillarsLuckCycle).display_ganzhi : '') || '')),
    shenShaRows: shenShaRows(item?.shen_sha, item?.shen_sha_details),
    isLuck: true,
  };
}

function shenShaRows(namesValue: unknown, detailsValue: unknown): ShenShaCellItem[] {
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
  }).filter((item) => item.category !== 'life_stage' && !LIFE_STAGE_NAMES.has(item.name));
  return sortShenShaRows(rows);
}

function sortShenShaRows(rows: ShenShaCellItem[]): ShenShaCellItem[] {
  return rows
    .map((item, index) => ({ ...item, index }))
    .sort((left, right) => {
      const toneDelta = getShenShaToneScore(left) - getShenShaToneScore(right);
      if (toneDelta !== 0) return toneDelta;
      const nameDelta = (SHEN_SHA_NAME_ORDER[left.name] ?? 500) - (SHEN_SHA_NAME_ORDER[right.name] ?? 500);
      if (nameDelta !== 0) return nameDelta;
      const categoryDelta = (SHEN_SHA_CATEGORY_ORDER[left.category] ?? 99) - (SHEN_SHA_CATEGORY_ORDER[right.category] ?? 99);
      if (categoryDelta !== 0) return categoryDelta;
      return left.index - right.index;
    })
    .map(({ index: _index, ...item }) => item);
}

function visibleLuckShenShaRows(column: LuckTableColumn): ShenShaCellItem[] {
  if (luckShenShaExpanded.value) return column.shenShaRows;
  if (column.shenShaRows.length > MAX_SHEN_SHA_ROWS) return column.shenShaRows.slice(0, 2);
  return column.shenShaRows;
}

function getShenShaToneScore(item: ShenShaCellItem): number {
  const text = `${item.category}${item.name}${item.meaning}`;
  if (/[贵人德福喜禄昌合赦喜医昌印舆]/u.test(text)) return 0;
  if (/[煞亡劫灾孤寡空刃鬼差错]/u.test(text)) return 2;
  return 1;
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

function calculateXunKong(ganzhi: string | null | undefined): string {
  const text = String(ganzhi || '').trim();
  if (!text) return '';
  const jiazi = Array.from({ length: 60 }, (_, index) => {
    const stems = Object.keys(stemInfo);
    return `${stems[index % 10]}${branchOrder[index % 12]}`;
  });
  const index = jiazi.indexOf(text);
  if (index < 0) return '';
  const xunStart = Math.floor(index / 10) * 10;
  const usedBranches = new Set(jiazi.slice(xunStart, xunStart + 10).map((item) => item.slice(1, 2)));
  return branchOrder.filter((branch) => !usedBranches.has(branch)).join('');
}

function formatXunKong(value: string | null | undefined, ganzhi: string | null | undefined): string {
  return String(value || '').trim() || calculateXunKong(ganzhi) || '-';
}

function elementBadgeClass(element: string): string {
  if (element === '木') return 'bg-[#ECFDF5] text-[#059669] border-[#A7F3D0]';
  if (element === '火') return 'bg-[#FFF1F2] text-[#E11D48] border-[#FECDD3]';
  if (element === '土') return 'bg-[#FFFBEB] text-[#78350F] border-[#FCD34D]';
  if (element === '金') return 'bg-[#FFF7DA] text-[#CA8A04] border-[#F4D27A]';
  if (element === '水') return 'bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]';
  return 'bg-white text-slate-500 border-slate-100';
}

function elementTextClass(element: string): string {
  if (element === '木') return 'text-[#059669]';
  if (element === '火') return 'text-[#E11D48]';
  if (element === '土') return 'text-[#78350F]';
  if (element === '金') return 'text-[#CA8A04]';
  if (element === '水') return 'text-[#2563EB]';
  return 'text-slate-500';
}

function compactTenGod(value: string | null | undefined): string {
  const text = String(value || '').trim();
  const map: Record<string, string> = {
    比肩: '比',
    劫财: '劫',
    食神: '食',
    伤官: '伤',
    偏财: '财',
    正财: '财',
    七杀: '杀',
    正官: '官',
    偏印: '枭',
    枭神: '枭',
    正印: '印',
    日元: '日',
    日主: '日',
  };
  return map[text] || text.slice(0, 1);
}

function currentDayStem(): string {
  return chartDisplay.value?.pillars?.day?.stem || String(chart.value.day_master || '');
}

function branchMainTenGod(branch: string): string {
  const mainStem = hiddenStemMap[branch]?.[0]?.stem || '';
  return mainStem ? calculateTenGod(currentDayStem(), mainStem) : '';
}

function luckGanzhiParts(ganzhi: string | null | undefined, stemTenGod?: string | null): GanzhiDisplayPart[] {
  return Array.from(String(ganzhi || '-')).map((char) => ({
    char,
    element: elementOfStem(char) || elementOfBranch(char),
    star: compactTenGod(elementOfStem(char) ? (stemTenGod || calculateTenGod(currentDayStem(), char)) : branchMainTenGod(char)),
  }));
}

function showToast(message: string, duration = 2200): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, duration);
}

function resetWaitingAnimation(): void {
  waitingStep.value = 1;
  waitingStepProgress.value = [0, 0, 0, 0];
  waitingPoemIndex.value = 0;
}

async function runTimedProgressStep(stepIndex: number, durationMs: number, maxProgress = 100): Promise<void> {
  waitingStep.value = stepIndex + 1;
  const tickMs = stepIndex < 2 ? 50 : 100;
  const ticks = Math.max(1, Math.round(durationMs / tickMs));
  for (let i = 1; i <= ticks; i += 1) {
    if (disposed) {
      return;
    }
    await sleep(tickMs);
    waitingStepProgress.value[stepIndex] = Math.min(maxProgress, Math.round((i / ticks) * maxProgress));
  }
}

async function runGenerationWaitingAnimation(reviewPromise: Promise<FourPillarsReviewRecord>): Promise<void> {
  resetWaitingAnimation();
  let apiCompleted = false;
  let apiError: unknown = null;
  const poemTimer = window.setInterval(() => {
    waitingPoemIndex.value = (waitingPoemIndex.value + 1) % waitingPoemLines.length;
  }, 1000);

  reviewPromise
    .then(() => {
      apiCompleted = true;
    })
    .catch((error) => {
      apiError = error;
    });

  try {
    for (let index = 0; index < waitingSteps.length; index += 1) {
      if (apiError) {
        throw apiError;
      }
      const maxProgress = index === waitingSteps.length - 1 ? 95 : 100;
      await runTimedProgressStep(index, waitingSteps[index].durationMs, maxProgress);
    }
    while (!apiCompleted && !apiError && !disposed) {
      await sleep(100);
    }
    if (apiError) {
      throw apiError;
    }
    waitingStepProgress.value[3] = 100;
    await sleep(300);
  } finally {
    window.clearInterval(poemTimer);
  }
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

async function loadBirthLocations(): Promise<void> {
  try {
    const payload = await listFourPillarsBirthLocations();
    const items = Array.isArray(payload.locations) ? payload.locations.map(normalizeBirthLocation).filter(Boolean) as BirthLocationOption[] : [];
    if (items.length) {
      locationOptions.value = items;
      const defaultLocationId = String(payload.default_location_id || '');
      if (defaultLocationId && items.some((item) => item.id === defaultLocationId)) {
        selectedLocationId.value = defaultLocationId;
      } else if (!items.some((item) => item.id === selectedLocationId.value)) {
        selectedLocationId.value = items[0].id;
      }
      birthPlace.value = selectedLocation.value.display_name;
      void refreshTrueSolarPreview();
    }
  } catch {
    locationOptions.value = fallbackLocationOptions;
  }
}

function normalizeBirthLocation(value: unknown): BirthLocationOption | null {
  if (!value || typeof value !== 'object') return null;
  const item = value as Record<string, unknown>;
  const latitude = Number(item.latitude);
  const longitude = Number(item.longitude);
  const id = String(item.id || '').trim();
  if (!id || !Number.isFinite(latitude) || !Number.isFinite(longitude)) return null;
  return {
    id,
    scope: String(item.scope || ''),
    display_name: String(item.display_name || item.name || id),
    latitude,
    longitude,
    timezone: String(item.timezone || 'Asia/Shanghai'),
    country: String(item.country || ''),
    province: String(item.province || ''),
    city: String(item.city || ''),
    district: String(item.district || ''),
    region: String(item.region || ''),
  };
}

function openDateDrawer(tab: InputDrawerTab = inputMode.value): void {
  drawerTab.value = tab;
  drawerKind.value = 'datetime';
  if (tab === 'bazi') {
    syncBaziFromCurrentDate();
  }
  void refreshTrueSolarPreview();
}

function openLocationDrawer(): void {
  locationScope.value = selectedLocation.value.scope === 'overseas' ? 'overseas' : 'domestic';
  drawerKind.value = 'location';
  void refreshTrueSolarPreview();
}

function closeDrawer(): void {
  drawerKind.value = null;
}

function scrollSelectedWheelOptions(): void {
  if (!drawerKind.value) return;
  window.requestAnimationFrame(() => {
    document.querySelectorAll<HTMLElement>('.drawer-sheet .wheel-option.is-selected').forEach((item) => {
      item.scrollIntoView({ block: 'center', inline: 'nearest' });
    });
  });
}

function handleWheelScroll(event: Event, scope: WheelScope, part: string): void {
  const column = event.currentTarget as HTMLElement | null;
  if (!column) return;
  const previousTimer = wheelScrollTimers.get(column);
  if (previousTimer) {
    window.clearTimeout(previousTimer);
  }
  const timer = window.setTimeout(() => {
    const centerY = column.getBoundingClientRect().top + column.clientHeight / 2;
    const options = Array.from(column.querySelectorAll<HTMLElement>('.wheel-option'));
    const centered = options.reduce<HTMLElement | null>((nearest, item) => {
      if (!nearest) return item;
      const itemCenter = item.getBoundingClientRect().top + item.clientHeight / 2;
      const nearestCenter = nearest.getBoundingClientRect().top + nearest.clientHeight / 2;
      return Math.abs(itemCenter - centerY) < Math.abs(nearestCenter - centerY) ? item : nearest;
    }, null);
    const value = centered?.dataset.value || '';
    if (!value) return;
    applyWheelSelection(scope, part, value);
  }, 120);
  wheelScrollTimers.set(column, timer);
}

function centeredWheelValue(column: HTMLElement): string {
  const centerY = column.getBoundingClientRect().top + column.clientHeight / 2;
  const options = Array.from(column.querySelectorAll<HTMLElement>('.wheel-option'));
  const centered = options.reduce<HTMLElement | null>((nearest, item) => {
    if (!nearest) return item;
    const itemCenter = item.getBoundingClientRect().top + item.clientHeight / 2;
    const nearestCenter = nearest.getBoundingClientRect().top + nearest.clientHeight / 2;
    return Math.abs(itemCenter - centerY) < Math.abs(nearestCenter - centerY) ? item : nearest;
  }, null);
  return centered?.dataset.value || '';
}

function syncVisibleDateWheelSelection(): void {
  if (drawerKind.value !== 'datetime') return;
  if (drawerTab.value !== 'solar' && drawerTab.value !== 'lunar') return;
  const columns = Array.from(document.querySelectorAll<HTMLElement>('.drawer-sheet .wheel-frame .wheel-column'));
  const parts = ['year', 'month', 'day', 'hour', 'minute'];
  columns.slice(0, parts.length).forEach((column, index) => {
    const value = centeredWheelValue(column);
    if (value) applyWheelSelection(drawerTab.value, parts[index], value);
  });
}

function applyWheelSelection(scope: WheelScope, part: string, value: string): void {
  if (scope === 'solar') {
    const numericValue = Number(value);
    if (part === 'year') birthYear.value = String(numericValue);
    if (part === 'month') birthMonth.value = String(numericValue);
    if (part === 'day') birthDay.value = String(numericValue);
    if (part === 'hour' || part === 'minute') {
      const [hour = '00', minute = '00'] = (birthTime.value || '00:00').split(':');
      birthTime.value = `${part === 'hour' ? twoDigit(numericValue) : hour}:${part === 'minute' ? twoDigit(numericValue) : minute}`;
    }
    void refreshTrueSolarPreview();
    return;
  }
  if (scope === 'lunar') {
    lunarInput.value = { ...lunarInput.value, [part]: Number(value) };
    return;
  }
  if (scope === 'domestic-location') {
    if (part === 'province') selectDomesticProvince(value);
    if (part === 'city') selectDomesticCity(value);
    if (part === 'district') selectDomesticDistrict(value);
    return;
  }
  if (part === 'country') selectOverseasCountry(value);
  if (part === 'region') selectOverseasRegion(value);
}

function selectInputMode(mode: InputMode): void {
  inputMode.value = mode;
  drawerTab.value = mode;
}

function setSolarPart(part: 'year' | 'month' | 'day' | 'hour' | 'minute', value: number): void {
  if (part === 'year') birthYear.value = String(value);
  if (part === 'month') birthMonth.value = String(value);
  if (part === 'day') birthDay.value = String(value);
  if (part === 'hour' || part === 'minute') {
    const [hour = '00', minute = '00'] = (birthTime.value || '00:00').split(':');
    birthTime.value = `${part === 'hour' ? String(value).padStart(2, '0') : hour}:${part === 'minute' ? String(value).padStart(2, '0') : minute}`;
  }
  scrollSelectedWheelOptions();
  void refreshTrueSolarPreview();
}

function setLunarPart(part: keyof typeof lunarInput.value, value: number | boolean): void {
  lunarInput.value = { ...lunarInput.value, [part]: value };
  scrollSelectedWheelOptions();
}

function selectLocation(location: BirthLocationOption): void {
  selectedLocationId.value = location.id;
  locationScope.value = location.scope === 'overseas' ? 'overseas' : 'domestic';
  birthPlace.value = location.display_name;
  scrollSelectedWheelOptions();
  void refreshTrueSolarPreview();
}

function selectDomesticProvince(province: string): void {
  const next = domesticLocations.value.find((item) => (item.province || item.city) === province);
  if (next) selectLocation(next);
}

function selectDomesticCity(city: string): void {
  const province = selectedLocation.value.province || domesticProvinces.value[0] || '';
  const next = domesticLocations.value.find((item) => (item.province || item.city) === province && (item.city || item.province) === city);
  if (next) selectLocation(next);
}

function selectDomesticDistrict(district: string): void {
  const province = selectedLocation.value.province || domesticProvinces.value[0] || '';
  const city = selectedLocation.value.city || domesticCities.value[0] || '';
  const next = domesticLocations.value.find((item) => (item.province || item.city) === province && (item.city || item.province) === city && (item.district || '--') === district);
  if (next) selectLocation(next);
}

function selectOverseasCountry(country: string): void {
  const next = overseasLocations.value.find((item) => item.country === country);
  if (next) selectLocation(next);
}

function selectOverseasRegion(region: string): void {
  const country = selectedLocation.value.country || overseasCountries.value[0] || '';
  const next = overseasLocations.value.find((item) => item.country === country && (item.city || item.region) === region);
  if (next) selectLocation(next);
}

async function confirmDateDrawer(): Promise<void> {
  syncVisibleDateWheelSelection();
  inputMode.value = drawerTab.value;
  if (drawerTab.value === 'solar') {
    closeDrawer();
    void refreshTrueSolarPreview();
    return;
  }
  if (drawerTab.value === 'lunar') {
    try {
      const resolved = await resolveFourPillarsInput({
        mode: 'lunar',
        lunar_input: lunarInput.value,
        birth_location: selectedLocation.value,
      });
      applyBirthDateParts(String(resolved.birth_date || birthDate.value));
      birthTime.value = String(resolved.birth_time || birthTime.value);
      closeDrawer();
      void refreshTrueSolarPreview();
    } catch {
      toast.value = '农历日期转换失败，请稍后重试。';
    }
    return;
  }
  if (drawerTab.value === 'bazi') {
    try {
      await searchBaziCandidates();
      const selected = baziCandidates.value[baziInput.value.candidate_index] || baziCandidates.value[0];
      if (selected) {
        applyBirthDateParts(selected.birth_date);
        birthTime.value = selected.birth_time;
      }
      closeDrawer();
      void refreshTrueSolarPreview();
    } catch {
      toast.value = '四柱候选查询失败，请稍后重试。';
    }
  }
}

async function refreshTrueSolarPreview(): Promise<void> {
  if (!birthDate.value || !birthTime.value) return;
  const resolved = await resolveFourPillarsInput({
    mode: 'solar',
    birth_date: birthDate.value,
    birth_time: birthTime.value,
    timezone: selectedLocation.value.timezone,
    birth_location: selectedLocation.value,
  }).catch(() => null);
  const preview = resolved?.true_solar_time;
  trueSolarPreview.value = preview && typeof preview === 'object' ? preview as Record<string, unknown> : null;
}

async function searchBaziCandidates(): Promise<void> {
  baziCandidateLoading.value = true;
  try {
    const resolved = await resolveFourPillarsInput({
      mode: 'bazi',
      bazi_input: { ...baziInput.value, target_year: Number(birthYear.value || new Date().getFullYear()) },
    });
    const items = Array.isArray(resolved.candidates) ? resolved.candidates : [];
    baziCandidates.value = items.map((item) => item as BaziCandidate);
  } finally {
    baziCandidateLoading.value = false;
  }
}

function syncBaziFromCurrentDate(): void {
  const rawPillars = chart.value.pillars as Record<string, { ganzhi?: string }> | undefined;
  if (!rawPillars) return;
  baziInput.value = {
    ...baziInput.value,
    year: String(rawPillars.year?.ganzhi || baziInput.value.year),
    month: String(rawPillars.month?.ganzhi || baziInput.value.month),
    day: String(rawPillars.day?.ganzhi || baziInput.value.day),
    hour: String(rawPillars.hour?.ganzhi || baziInput.value.hour),
  };
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
  resetWaitingAnimation();
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
    const reviewReadyPromise = submitFourPillarsReview({
      gender: gender.value,
      birth_date: birthDate.value,
      birth_time: birthTime.value,
      timezone: selectedLocation.value.timezone || 'Asia/Shanghai',
      birth_place: birthPlace.value.trim() || selectedLocation.value.display_name,
      name: profileName.value.trim() || null,
      input_mode: inputMode.value,
      calendar_input: { birth_date: birthDate.value, birth_time: birthTime.value },
      lunar_input: inputMode.value === 'lunar' ? lunarInput.value : null,
      bazi_input: inputMode.value === 'bazi' ? { ...baziInput.value, target_year: Number(birthYear.value || new Date().getFullYear()) } : null,
      birth_location: selectedLocation.value,
      include_markdown: true,
    }).then((review) => startReviewPolling(review));
    await runGenerationWaitingAnimation(reviewReadyPromise);
    const completed = await reviewReadyPromise;
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
        <div class="w-9 h-9"></div>
      </div>
    </header>

    <main class="max-w-md mx-auto px-margin-mobile pt-4">
      <section v-if="viewState === 'input'" class="space-y-4">
        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="relative flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5 shrink-0">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-primary/50"></span>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-primary"></span>
            </span>
            <h2 class="font-serif text-[16px] font-black text-brand-gold-fixed leading-snug">四柱八字综合测评</h2>
          </div>
        </section>

        <div class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm">

          <div class="space-y-2.5">
            <label class="block">
              <span class="font-sans text-[11px] text-brand-secondary font-bold flex items-center gap-1.5 mb-1">
                <User :size="13" /> 姓名
              </span>
              <input v-model="profileName" maxlength="64" placeholder="可选" class="w-full h-10 rounded-xl bg-brand-paper border border-transparent px-3 font-sans text-[13px] text-brand-ink-strong outline-none focus:border-brand-primary" />
            </label>

            <div class="grid grid-cols-[112px_1fr] gap-2 items-center">
              <div class="grid grid-cols-2 rounded-xl bg-brand-paper p-1">
                <button class="h-8 rounded-lg text-[12px] font-bold" :class="gender === 'male' ? 'bg-brand-primary text-white' : 'text-brand-secondary'" @click="gender = 'male'">男</button>
                <button class="h-8 rounded-lg text-[12px] font-bold" :class="gender === 'female' ? 'bg-brand-primary text-white' : 'text-brand-secondary'" @click="gender = 'female'">女</button>
              </div>
              <div class="grid grid-cols-2 rounded-xl bg-brand-paper p-1 w-[148px] justify-self-end">
                <button v-for="mode in ['solar', 'lunar']" :key="mode" class="h-8 rounded-lg text-[11px] font-bold" :class="inputMode === mode ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary'" @click="selectInputMode(mode as InputMode)">
                  {{ mode === 'solar' ? '公历' : '农历' }}
                </button>
              </div>
            </div>

            <button type="button" class="w-full rounded-xl bg-brand-paper border border-transparent px-3 py-2.5 text-left" @click="openDateDrawer(inputMode)">
              <span class="font-sans text-[11px] text-brand-secondary font-bold flex items-center gap-1.5">
                <CalendarDays :size="13" /> 出生日期
              </span>
              <span class="block font-serif text-[14px] text-brand-ink-strong font-bold mt-1 truncate">{{ birthDateTimeSummary }}</span>
            </button>

            <button type="button" class="w-full rounded-xl bg-brand-paper border border-transparent px-3 py-2.5 text-left" @click="openLocationDrawer">
              <span class="font-sans text-[11px] text-brand-secondary font-bold flex items-center gap-1.5">
                <MapPin :size="13" /> 出生地区
              </span>
              <span class="block font-serif text-[14px] text-brand-ink-strong font-bold mt-1 truncate">{{ locationSummary }}</span>
              <span class="block font-sans text-[10.5px] text-brand-secondary mt-1 truncate">真太阳时 {{ trueSolarSummary }}</span>
            </button>
          </div>
        </div>

        <button
          class="w-full h-12 rounded-xl bg-brand-primary hover:bg-brand-primary-strong text-white font-sans text-[13px] font-bold shadow-md disabled:opacity-60 disabled:shadow-none transition-all active:scale-[0.985] flex items-center justify-center gap-1.5"
          :disabled="state.booting || !moduleEnabled"
          @click="void handleSubmit()"
        >
          <Sparkles :size="15" fill="currentColor" />
          <span v-if="state.booting">正在连接本地 API...</span>
          <span v-else-if="moduleEnabled">立即扣除 <span class="font-sans">{{ effectiveBasePoints }}</span> 积分，深度智能测算</span>
          <span v-else>功能暂未开放</span>
        </button>
      </section>

      <section v-else-if="viewState === 'waiting'" class="py-10 flex flex-col justify-center min-h-[65vh]">
        <div class="bg-white rounded-2xl p-6 border border-gray-150/75 shadow-sm space-y-6 text-center">
          <div class="relative w-28 h-28 mx-auto flex items-center justify-center select-none">
            <div class="absolute inset-0 bg-brand-primary/5 rounded-full blur-md animate-pulse"></div>
            <svg class="absolute w-28 h-28 text-brand-primary/25 animate-[spin_40s_linear_infinite]" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-dasharray="1 3" stroke-width="1.5" />
            </svg>
            <div class="absolute w-12 h-12 bg-white rounded-full border border-brand-primary/20 shadow-md flex items-center justify-center">
              <Sparkles :size="24" class="text-brand-primary animate-pulse" />
            </div>
          </div>

          <div class="space-y-1 py-1">
            <h2 class="font-serif text-[18px] font-bold text-brand-ink-strong tracking-wide">四柱八字命盘推演中</h2>
            <p class="font-serif text-[15px] font-bold text-brand-secondary/85 leading-relaxed tracking-wide min-h-[1.6em]">
              {{ waitingPoemLine }}
            </p>
          </div>

          <div class="text-center space-y-1.5">
            <div class="flex items-center justify-between text-[11px] font-bold text-brand-secondary">
              <span>{{ waitingActionText }}</span>
              <span class="text-brand-primary">{{ waitingTotalProgress }}%</span>
            </div>
            <div class="w-full h-1.5 bg-gray-150 rounded-full overflow-hidden">
              <div class="bg-brand-primary h-full transition-all duration-300" :style="{ width: `${waitingTotalProgress}%` }"></div>
            </div>
          </div>

          <div class="h-px bg-gray-100"></div>

          <div class="space-y-4 px-1 text-left">
            <div
              v-for="(step, index) in waitingSteps"
              :key="step.title"
              class="flex items-start gap-3.5 transition-all duration-300"
              :class="waitingStepProgress[index] > 0 ? 'opacity-100' : 'opacity-55'"
            >
              <span
                class="waiting-step mt-0.5"
                :class="waitingStepProgress[index] >= 100 ? 'is-done' : (waitingStep === index + 1 ? 'is-active' : '')"
              >
                {{ waitingStepProgress[index] >= 100 ? '✓' : index + 1 }}
              </span>
              <span class="min-w-0 flex-1">
                <span class="block font-sans text-[12px] font-bold text-brand-ink-strong">{{ step.title }}</span>
                <span class="block font-sans text-[10.5px] text-brand-secondary/80 leading-relaxed mt-0.5">{{ step.desc }}</span>
              </span>
              <RefreshCw v-if="waitingStep === index + 1 && waitingStepProgress[index] < 100" :size="12" class="mt-1 text-brand-primary animate-spin shrink-0" />
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
          <FourPillarsNatalTable
            :chart-display="chartDisplay"
            :element-counts="elementCounts"
            :strength-label="String(strength.label || '')"
            :favorable-elements="favorableElementsList"
            :unfavorable-elements="unfavorableElementsList"
          />

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
              <table class="w-full min-w-[330px] table-fixed border-collapse text-center">
                <thead>
                  <tr class="bg-[#EAF1FF]">
                    <th class="luck-row-label luck-sticky-col luck-head-label w-[36px]">项目</th>
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
                      <span class="luck-glyph" :class="elementTextClass(column.stemElement)">{{ column.stem }}</span>
                    </td>
                  </tr>
                  <tr class="bg-white">
                    <td class="luck-row-label">地支</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-branch`" class="luck-cell" :class="column.isLuck ? 'bg-[#DBEAFE]/20' : ''">
                      <span class="luck-glyph" :class="elementTextClass(column.branchElement)">{{ column.branch }}</span>
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
                    <td v-for="column in luckTableColumns" :key="`${column.label}-dishi`" class="luck-cell luck-text luck-compact-text" :class="column.isLuck ? 'bg-[#DBEAFE]/25 text-[#1E3A8A]' : ''">
                      {{ column.diShi }}
                    </td>
                  </tr>
                  <tr class="bg-[#F8FAFF]">
                    <td class="luck-row-label">自坐</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-sitting`" class="luck-cell luck-text luck-compact-text" :class="column.isLuck ? 'bg-[#DBEAFE]/25 text-[#1E3A8A]' : ''">
                      {{ column.selfSitting }}
                    </td>
                  </tr>
                  <tr class="bg-white">
                    <td class="luck-row-label">旬空</td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-xunkong`" class="luck-cell luck-text luck-compact-text" :class="column.isLuck ? 'bg-[#DBEAFE]/25 text-[#1E3A8A]' : ''">
                      {{ column.xunKong }}
                    </td>
                  </tr>
                  <tr class="bg-[#F8FAFF]">
                    <td class="luck-row-label text-center">
                      <span class="block text-inherit">神煞</span>
                      <button
                        v-if="luckHasOverflowingShenSha"
                        type="button"
                        class="luck-shen-sha-toggle cursor-pointer outline-none hover:bg-indigo-50/20"
                        :aria-label="luckShenShaExpanded ? '收起神煞' : '展开神煞'"
                        :title="luckShenShaExpanded ? '收起神煞详情' : '展开神煞详情'"
                        @click="luckShenShaExpanded = !luckShenShaExpanded"
                      >
                        <ChevronUp v-if="luckShenShaExpanded" :size="10" />
                        <ChevronDown v-else :size="10" />
                      </button>
                    </td>
                    <td v-for="column in luckTableColumns" :key="`${column.label}-shen-sha`" class="luck-cell luck-shen-sha" :class="column.isLuck ? 'bg-[#DBEAFE]/20 text-[#1E3A8A]' : ''">
                      <div v-if="column.shenShaRows.length" class="flex flex-col items-center justify-center gap-1 w-full">
                        <div class="luck-shen-sha-stack">
                          <span
                            v-for="item in visibleLuckShenShaRows(column)"
                            :key="`${column.label}-${item.name}`"
                            class="luck-text luck-compact-text block"
                            :title="item.meaning || item.name"
                          >
                            {{ item.name }}
                          </span>
                        </div>
                        <span v-if="!luckShenShaExpanded && column.shenShaRows.length > MAX_SHEN_SHA_ROWS" class="text-[9.5px] font-bold text-slate-400 mt-0.5 block whitespace-nowrap">
                          +{{ column.shenShaRows.length - 2 }} 更多
                        </span>
                      </div>
                      <span v-else class="text-[10px] text-[#94A3B8]">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="bg-[#F8FAFF]">
              <div class="grid grid-cols-[36px_minmax(0,1fr)]">
                <div class="luck-side-label">大运</div>
                <div class="min-w-0 max-w-full overflow-x-scroll no-scrollbar luck-scroll" role="region" aria-label="大运横向选择">
                  <div class="inline-flex min-w-max">
                    <button
                      v-for="cycle in luckCycles"
                      :key="cycle.cycle_key"
                      class="w-[38px] min-h-[78px] py-1 px-0.5 transition-colors text-center flex flex-col items-center justify-center relative shrink-0"
                      :class="cycle.cycle_key === selectedLuckCycle?.cycle_key ? 'bg-[#DBEAFE] text-[#1D4ED8] font-black' : 'bg-white text-[#475569]'"
                      @click="activeCycleKey = cycle.cycle_key; selectedLuckYear = cycle.year_items.find((item) => item.is_current)?.year || cycle.year_items[0]?.year || null"
                    >
                      <span v-if="cycle.is_current" class="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-[#2563EB]"></span>
                      <span class="font-mono text-[8px] leading-none">{{ cycle.start_age ?? '-' }}岁</span>
                      <span v-if="!cycle.ganzhi" class="luck-strip-ganzhi luck-xiaoyun-label">
                        <span class="luck-xiaoyun-main">
                          <span class="luck-ganzhi-char">小</span>
                          <span class="luck-ganzhi-char">运</span>
                        </span>
                        <span class="luck-xiaoyun-note" aria-label="起运前">起运前</span>
                      </span>
                      <span v-else class="luck-strip-ganzhi luck-ganzhi-stack">
                        <span
                          v-for="(part, index) in luckGanzhiParts(cycle.display_ganzhi || cycle.ganzhi || '', cycle.stem_ten_god)"
                          :key="`${cycle.cycle_key}-ganzhi-${index}`"
                          class="luck-ganzhi-line"
                        >
                          <span class="luck-ganzhi-char" :class="elementTextClass(part.element)">{{ part.char }}</span>
                          <span class="luck-ganzhi-star">{{ part.star }}</span>
                        </span>
                      </span>
                      <span class="font-mono text-[7px] leading-none mt-1 text-[#64748B]">{{ cycle.start_year }}</span>
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="selectedLuckCycle" class="grid grid-cols-[36px_minmax(0,1fr)]">
                <div class="luck-side-label">流年</div>
                <div class="min-w-0 max-w-full overflow-x-scroll no-scrollbar luck-scroll" role="region" aria-label="流年横向选择">
                  <div class="inline-flex min-w-max">
                    <button
                      v-for="item in selectedLuckCycle.year_items"
                      :key="item.year"
                      class="w-[38px] min-h-[78px] py-1 px-0.5 transition-colors flex flex-col items-center justify-center text-center relative shrink-0"
                      :class="item.year === selectedLuckYear ? 'bg-[#DBEAFE] text-[#1D4ED8] font-black' : 'bg-white text-[#475569]'"
                      @click="selectedLuckYear = item.year"
                    >
                      <span v-if="item.is_current" class="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-[#2563EB]"></span>
                      <span class="font-mono text-[8px] leading-none">{{ item.age ?? '-' }}岁</span>
                      <span class="luck-year-ganzhi luck-ganzhi-stack">
                        <span
                          v-for="(part, index) in luckGanzhiParts(item.ganzhi, item.stem_ten_god)"
                          :key="`${item.year}-ganzhi-${index}`"
                          class="luck-ganzhi-line"
                        >
                          <span class="luck-ganzhi-char" :class="elementTextClass(part.element)">{{ part.char }}</span>
                          <span class="luck-ganzhi-star">{{ part.star }}</span>
                        </span>
                      </span>
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
                <h3 class="font-serif text-[15px] font-bold text-[#1D4ED8] mt-1">大运中评 · <span :class="(selectedLuckCycle.display_ganzhi || selectedLuckCycle.ganzhi) ? '' : 'text-[#64748B]'">{{ selectedLuckCycle.display_ganzhi || selectedLuckCycle.ganzhi || '小运' }}</span></h3>
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

    <transition name="drawer-overlay">
      <div v-if="drawerKind" class="fixed inset-x-0 top-0 bottom-[84px] z-40 bg-slate-950/40 flex items-end" @click.self="closeDrawer">
        <div class="drawer-sheet w-full max-w-md mx-auto rounded-t-[24px] bg-white shadow-2xl border-t border-[#D8E3F5] max-h-[82vh] overflow-hidden flex flex-col">
          <div class="shrink-0 px-4 py-3 border-b border-[#E2E8F0] flex items-center justify-between">
            <div>
              <p class="font-sans text-[10px] font-black tracking-wide text-brand-secondary">{{ drawerKind === 'datetime' ? 'BIRTH INPUT' : 'BIRTH LOCATION' }}</p>
              <h3 class="font-serif text-[17px] font-black text-brand-ink-strong">{{ drawerKind === 'datetime' ? '选择出生信息' : '选择出生地区' }}</h3>
            </div>
            <button type="button" class="w-8 h-8 rounded-lg bg-brand-paper flex items-center justify-center text-brand-secondary" @click="closeDrawer">
              <X :size="16" />
            </button>
          </div>

          <div v-if="drawerKind === 'datetime'" class="overflow-y-auto p-3 space-y-3">
            <div class="flex items-center justify-between gap-3">
              <div class="grid grid-cols-2 rounded-2xl bg-brand-paper p-1 w-[190px]">
                <button v-for="tab in ['solar', 'lunar']" :key="tab" type="button" class="h-9 rounded-xl text-[13px] font-black" :class="drawerTab === tab ? 'bg-white text-brand-ink-strong shadow-sm' : 'text-brand-secondary'" @click="drawerTab = tab as InputDrawerTab">
                  {{ tab === 'solar' ? '公历' : '农历' }}
                </button>
              </div>
              <button type="button" class="h-10 px-6 rounded-full bg-[#111111] text-[#F1D7A8] text-[14px] font-black shadow-sm" @click="void confirmDateDrawer()">确定</button>
            </div>

            <div v-if="drawerTab === 'solar'" class="space-y-2">
              <div class="wheel-tabs">
                <button type="button" class="wheel-tab is-active" @click="quickYearOpen = !quickYearOpen">年 ⇄</button>
                <span>月</span>
                <span>日</span>
                <span>时</span>
                <span>分</span>
              </div>
              <div class="wheel-frame">
                <div class="wheel-highlight"></div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'solar', 'year')">
                  <button v-for="year in yearOptions" :key="`solar-year-${year}`" type="button" class="wheel-option" :class="Number(birthYear || 1989) === year ? 'is-selected' : ''" :data-value="year" @click="setSolarPart('year', year)">{{ year }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'solar', 'month')">
                  <button v-for="month in monthOptions" :key="`solar-month-${month}`" type="button" class="wheel-option" :class="Number(birthMonth || 1) === month ? 'is-selected' : ''" :data-value="month" @click="setSolarPart('month', month)">{{ twoDigit(month) }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'solar', 'day')">
                  <button v-for="day in dayOptions" :key="`solar-day-${day}`" type="button" class="wheel-option" :class="Number(birthDay || 1) === day ? 'is-selected' : ''" :data-value="day" @click="setSolarPart('day', day)">{{ twoDigit(day) }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'solar', 'hour')">
                  <button v-for="hour in hourOptions" :key="`solar-hour-${hour}`" type="button" class="wheel-option" :class="solarHour === hour ? 'is-selected' : ''" :data-value="hour" @click="setSolarPart('hour', hour)">{{ twoDigit(hour) }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'solar', 'minute')">
                  <button v-for="minute in minuteOptions" :key="`solar-minute-${minute}`" type="button" class="wheel-option" :class="solarMinute === minute ? 'is-selected' : ''" :data-value="minute" @click="setSolarPart('minute', minute)">{{ twoDigit(minute) }}</button>
                </div>
              </div>
              <div v-if="quickYearOpen" class="grid grid-cols-5 gap-1 max-h-36 overflow-y-auto rounded-xl bg-brand-paper p-2">
                <button v-for="year in yearOptions" :key="`quick-${year}`" class="h-8 rounded-lg text-[11px] font-bold" :class="String(year) === birthYear ? 'bg-brand-primary text-white' : 'bg-white text-brand-secondary'" @click="setSolarPart('year', year)">{{ year }}</button>
              </div>
            </div>

            <div v-else-if="drawerTab === 'lunar'" class="space-y-2">
              <div class="wheel-tabs">
                <button type="button" class="wheel-tab is-active" @click="quickYearOpen = !quickYearOpen">年 ⇄</button>
                <span>月</span>
                <span>日</span>
                <span>时</span>
                <span>分</span>
              </div>
              <div class="wheel-frame">
                <div class="wheel-highlight"></div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'lunar', 'year')">
                  <button v-for="year in yearOptions" :key="`lunar-year-${year}`" type="button" class="wheel-option" :class="lunarInput.year === year ? 'is-selected' : ''" :data-value="year" @click="setLunarPart('year', year)">{{ year }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'lunar', 'month')">
                  <button v-for="month in monthOptions" :key="`lunar-month-${month}`" type="button" class="wheel-option" :class="lunarInput.month === month ? 'is-selected' : ''" :data-value="month" @click="setLunarPart('month', month)">{{ lunarMonthLabel(month) }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'lunar', 'day')">
                  <button v-for="day in dayOptions" :key="`lunar-day-${day}`" type="button" class="wheel-option" :class="lunarInput.day === day ? 'is-selected' : ''" :data-value="day" @click="setLunarPart('day', day)">{{ lunarDayLabel(day) }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'lunar', 'hour')">
                  <button v-for="hour in hourOptions" :key="`lunar-hour-${hour}`" type="button" class="wheel-option" :class="lunarInput.hour === hour ? 'is-selected' : ''" :data-value="hour" @click="setLunarPart('hour', hour)">{{ twoDigit(hour) }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'lunar', 'minute')">
                  <button v-for="minute in minuteOptions" :key="`lunar-minute-${minute}`" type="button" class="wheel-option" :class="lunarInput.minute === minute ? 'is-selected' : ''" :data-value="minute" @click="setLunarPart('minute', minute)">{{ twoDigit(minute) }}</button>
                </div>
              </div>
            </div>

          </div>

          <div v-else class="overflow-y-auto p-3 space-y-3">
            <div class="flex items-center justify-between gap-3">
              <div class="grid grid-cols-2 gap-1 rounded-2xl bg-brand-paper p-1 w-[190px]">
                <button class="h-9 rounded-xl text-[13px] font-black" :class="locationScope === 'domestic' ? 'bg-white text-brand-ink-strong shadow-sm' : 'text-brand-secondary'" @click="locationScope = 'domestic'">国内</button>
                <button class="h-9 rounded-xl text-[13px] font-black" :class="locationScope === 'overseas' ? 'bg-white text-brand-ink-strong shadow-sm' : 'text-brand-secondary'" @click="locationScope = 'overseas'">海外</button>
              </div>
              <button class="h-10 px-6 rounded-full bg-[#111111] text-[#F1D7A8] text-[14px] font-black shadow-sm" @click="closeDrawer">确定</button>
            </div>
            <div class="relative">
              <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary" />
              <input v-model="locationSearch" class="w-full h-10 rounded-xl bg-brand-paper pl-9 pr-3 text-[13px] outline-none" placeholder="搜索城市 / 国家 / 区县" />
            </div>
            <div v-if="!locationSearch.trim() && locationScope === 'domestic'" class="space-y-3">
              <div class="location-wheel-labels grid grid-cols-3">
                <span>省份</span>
                <span>城市</span>
                <span>区县</span>
              </div>
              <div class="location-wheel-frame grid-cols-3">
                <div class="wheel-highlight"></div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'domestic-location', 'province')">
                  <button v-for="province in domesticProvinces" :key="`province-${province}`" class="wheel-option" :class="(selectedLocation.province || selectedLocation.city) === province ? 'is-selected' : ''" :data-value="province" @click="selectDomesticProvince(province)">{{ province }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'domestic-location', 'city')">
                  <button v-for="city in domesticCities" :key="`city-${city}`" class="wheel-option" :class="(selectedLocation.city || selectedLocation.province) === city ? 'is-selected' : ''" :data-value="city" @click="selectDomesticCity(city)">{{ city }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'domestic-location', 'district')">
                  <button v-for="district in domesticDistricts" :key="`district-${district}`" class="wheel-option" :class="(selectedLocation.district || '--') === district ? 'is-selected' : ''" :data-value="district" @click="selectDomesticDistrict(district)">{{ district }}</button>
                </div>
              </div>
            </div>
            <div v-else-if="!locationSearch.trim()" class="space-y-3">
              <div class="location-wheel-labels grid grid-cols-2">
                <span>国家</span>
                <span>地区</span>
              </div>
              <div class="location-wheel-frame grid-cols-2">
                <div class="wheel-highlight"></div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'overseas-location', 'country')">
                  <button v-for="country in overseasCountries" :key="`country-${country}`" class="wheel-option" :class="selectedLocation.country === country ? 'is-selected' : ''" :data-value="country" @click="selectOverseasCountry(country)">{{ country }}</button>
                </div>
                <div class="wheel-column" @scroll="handleWheelScroll($event, 'overseas-location', 'region')">
                  <button v-for="region in overseasRegions" :key="`region-${region}`" class="wheel-option" :class="(selectedLocation.city || selectedLocation.region) === region ? 'is-selected' : ''" :data-value="region" @click="selectOverseasRegion(region)">{{ region }}</button>
                </div>
              </div>
            </div>
            <div v-else class="grid grid-cols-1 gap-2 max-h-72 overflow-y-auto">
              <button v-for="item in filteredLocations" :key="item.id" class="rounded-xl border px-3 py-2 text-left" :class="selectedLocationId === item.id ? 'border-brand-primary bg-brand-primary/5' : 'border-gray-100 bg-white'" @click="selectLocation(item)">
                <span class="block font-serif text-[14px] font-bold text-brand-ink-strong">{{ item.display_name }}</span>
                <span class="block font-mono text-[10px] text-brand-secondary mt-1">{{ item.latitude.toFixed(4) }}, {{ item.longitude.toFixed(4) }} · {{ item.timezone }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
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

.drawer-overlay-enter-active,
.drawer-overlay-leave-active {
  transition: opacity 0.22s ease;
}

.drawer-overlay-enter-from,
.drawer-overlay-leave-to {
  opacity: 0;
}

.drawer-sheet {
  transform: translateY(0);
  transition: transform 0.26s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.drawer-overlay-enter-from .drawer-sheet,
.drawer-overlay-leave-to .drawer-sheet {
  transform: translateY(100%);
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
  position: sticky;
  left: 0;
  z-index: 3;
  background: #F3F7FF;
  color: #1D4ED8;
  font-family: inherit;
  font-size: 9.5px;
  font-weight: 800;
  padding: 5px 2px;
  box-shadow: 1px 0 0 rgba(216, 227, 245, 0.9);
}

.luck-head-label {
  color: #64748B;
  padding: 6px 3px;
  z-index: 5;
}

.luck-sticky-col {
  width: 36px;
  min-width: 36px;
  max-width: 36px;
}

.luck-side-label {
  background: #F3F7FF;
  color: #1D4ED8;
  font-family: inherit;
  font-size: 9.5px;
  font-weight: 800;
  line-height: 1.2;
  padding: 5px 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 1px 0 0 rgba(216, 227, 245, 0.9);
}

.luck-cell {
  min-height: 32px;
  padding: 3px 2px;
  font-size: 10px;
  line-height: 1.15;
  vertical-align: middle;
}

.luck-glyph {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 16px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
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
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-weight: 900;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
}

.luck-strip-ganzhi {
  min-width: 24px;
  min-height: 36px;
  margin-top: 4px;
  font-size: 14px;
  line-height: 1;
}

.luck-year-ganzhi {
  min-width: 24px;
  min-height: 36px;
  margin-top: 4px;
  font-size: 14px;
  line-height: 1;
}

.luck-ganzhi-stack {
  flex-direction: column;
  gap: 3px;
}

.luck-ganzhi-line {
  display: grid;
  grid-template-columns: 1em 0.75em;
  align-items: center;
  justify-content: center;
  column-gap: 2px;
  line-height: 1;
}

.luck-ganzhi-char {
  font-size: 14px;
  font-weight: 900;
}

.luck-ganzhi-star {
  color: #111827;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 9px;
  font-weight: 900;
  line-height: 1;
}

.luck-xiaoyun-label {
  color: #64748B;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  line-height: 1;
  text-align: center;
}

.luck-xiaoyun-main {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  line-height: 1;
}

.luck-xiaoyun-note {
  color: #111827;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 9px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  transform: translateY(-1px);
  writing-mode: vertical-rl;
  text-orientation: upright;
  white-space: nowrap;
}

.drawer-picker {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4px;
}

.drawer-picker > span {
  color: #64748B;
  font-family: inherit;
  font-size: 10.5px;
  font-weight: 800;
  line-height: 1.2;
}

.drawer-picker select {
  width: 100%;
  height: 42px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: #F5F7FB;
  color: #1F2937;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 13px;
  font-weight: 800;
  outline: none;
  padding: 0 8px;
}

.wheel-tabs {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  align-items: center;
  gap: 4px;
  padding: 0 4px;
  color: #1F2937;
  font-size: 15px;
  font-weight: 900;
  text-align: center;
}

.wheel-tab {
  height: 34px;
  border-radius: 999px;
  background: #F7F4EA;
  color: #A0864F;
  font-size: 14px;
  font-weight: 900;
}

.wheel-frame,
.location-wheel-frame {
  position: relative;
  display: grid;
  gap: 0;
  height: 176px;
  overflow: hidden;
  border-top: 1px solid #EEF2F7;
  border-bottom: 1px solid #EEF2F7;
}

.wheel-frame {
  grid-template-columns: 1.25fr repeat(4, minmax(0, 1fr));
}

.location-wheel-frame {
  display: grid;
}

.wheel-highlight {
  position: absolute;
  left: 8px;
  right: 8px;
  top: 50%;
  height: 42px;
  border-radius: 14px;
  background: #F3F4F6;
  transform: translateY(-50%);
  pointer-events: none;
}

.wheel-column {
  position: relative;
  z-index: 1;
  height: 176px;
  overflow-y: auto;
  scroll-snap-type: y mandatory;
  -webkit-overflow-scrolling: touch;
  padding: 67px 0;
  scrollbar-width: none;
}

.wheel-column::-webkit-scrollbar {
  display: none;
}

.wheel-option {
  width: 100%;
  height: 42px;
  scroll-snap-align: center;
  color: #D1D5DB;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  font-weight: 700;
  line-height: 42px;
  text-align: center;
  white-space: nowrap;
}

.wheel-option.is-selected {
  color: #111827;
  font-size: 21px;
  font-weight: 950;
}

.wheel-frame::before,
.wheel-frame::after,
.location-wheel-frame::before,
.location-wheel-frame::after {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 2;
  height: 52px;
  content: "";
  pointer-events: none;
}

.wheel-frame::before,
.location-wheel-frame::before {
  top: 0;
  background: linear-gradient(180deg, #FFFFFF 0%, rgba(255, 255, 255, 0.72) 58%, rgba(255, 255, 255, 0) 100%);
}

.wheel-frame::after,
.location-wheel-frame::after {
  bottom: 0;
  background: linear-gradient(0deg, #FFFFFF 0%, rgba(255, 255, 255, 0.72) 58%, rgba(255, 255, 255, 0) 100%);
}

.location-wheel-labels {
  color: #1F2937;
  font-size: 15px;
  font-weight: 900;
  text-align: center;
}

.location-wheel-frame .wheel-option {
  font-size: 15px;
}

.location-wheel-frame .wheel-option.is-selected {
  font-size: 20px;
}

.luck-scroll {
  touch-action: pan-x;
  overscroll-behavior-x: contain;
  -webkit-overflow-scrolling: touch;
}

.luck-mini {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  border: 1px solid #D8E3F5;
  border-radius: 5px;
  background: #FFFFFF;
  color: #64748B;
  padding: 1.5px 2px;
  margin: 1px;
  font-size: 8.5px;
  font-weight: 700;
}

.luck-text {
  color: #334155;
  font-family: inherit;
  font-size: 10px;
  font-weight: 800;
  line-height: 1.25;
}

.luck-compact-text {
  font-size: 9px;
  line-height: 1.15;
}

.luck-shen-sha {
  color: #475569;
  font-family: inherit;
  font-size: 9px;
  font-weight: 800;
  line-height: 1.15;
  word-break: keep-all;
  vertical-align: middle;
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
}
</style>
