# EaseWise Phase A Pixel-Lock Bundle: Phone Review And Four Pillars

## Purpose

This is a narrow source bundle for AI Studio. It covers only the two core assessment flows that still fail visual/functional parity: 手机号评测 and 四柱八字. Recreate these files exactly at the paths shown before doing any further design work.

## Manifest With Local Source Checksums

- `src/App.vue` | lines: `258` | bytes: `8846` | sha256: `010466c09ad5d49fb691c491e4ab1d624846648f68182b9bca2324f5667946f8`
- `src/components/analysis/Analysis.vue` | lines: `2884` | bytes: `114609` | sha256: `80bd0c7d1da08b3215de0f717ac6f46e18d45599c00be0e09fb4a4cb450190f4`
- `src/components/four-pillars/FourPillarsAnalysis.vue` | lines: `3765` | bytes: `158790` | sha256: `4f60155dae0d454c29ab80d0cbfb0623f8f9037c8d31ebe12e94687872a7da3f`
- `src/components/four-pillars/FourPillarsNatalTable.vue` | lines: `766` | bytes: `29412` | sha256: `b7cc7a1025faeed2f699cab50a930e596ac34c77631f52415ebc678db72fbdb5`
- `src/components/support/ContactServiceModal.vue` | lines: `172` | bytes: `6546` | sha256: `afa0fff7cba1c0c0de201cb11429c341f36c4b92dd0522bed7d94f94b5dc1450`
- `src/composables/useEaseWiseApp.ts` | lines: `1145` | bytes: `37461` | sha256: `135b926f620eafb7c47353c40830190a1f7f21f5a4aafb45a7d840a1f559d3a8`
- `src/lib/api.ts` | lines: `1443` | bytes: `52869` | sha256: `2ce72ba8e74071bc8dd386c65421f36b5e21b5ed041e597d15b60d0a6e75aa62`
- `src/types/api.ts` | lines: `1482` | bytes: `37803` | sha256: `43693423015678aa831ed1087145534dfc9c5ce88eaea88dca5492cf041de7e3`
- `src/config/pricing.ts` | lines: `3` | bytes: `176` | sha256: `68feb7a143f4878e1ae935b59513d54ccea2a7a8a3d1534b7ab01a0fd0fd3746`
- `src/constants/storage.ts` | lines: `14` | bytes: `669` | sha256: `f127ea4a039488679f1783c9f6626d6bb4f5aaf471f9332a3418af9d6f2e7497`
- `src/index.css` | lines: `109` | bytes: `2785` | sha256: `836b4b661012cf09c68a647d0a15dff356b0203ec0aa8d1bd34f8cfcfb917681`

Total source bytes: `449966`

## Source Files

### `src/App.vue`

```vue
<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import BottomNav from './components/layout/BottomNav.vue';
import Home from './components/home/Home.vue';
import Analysis from './components/analysis/Analysis.vue';
import FourPillarsAnalysis from './components/four-pillars/FourPillarsAnalysis.vue';
import MeihuaAnalysis from './components/meihua/MeihuaAnalysis.vue';
import AIAgent from './components/ai-agent/AIAgent.vue';
import Profile from './components/profile/Profile.vue';
import RechargePage from './components/recharge/RechargePage.vue';
import PointsClaimPage from './components/points-claim/PointsClaimPage.vue';
import AuthModal from './components/auth/AuthModal.vue';
import ContactServiceModal from './components/support/ContactServiceModal.vue';
import AdminWorkspace from './components/admin/AdminWorkspace.vue';
import { useEaseWiseApp } from './composables/useEaseWiseApp';

type AppTab = 'home' | 'phone' | 'bazi' | 'meihua' | 'agent' | 'profile' | 'recharge' | 'points-claim';

const activeTab = ref<AppTab>('home');
const routeQuery = ref<Record<string, string>>({});
const { bootstrapApp, requestRegisteredUser } = useEaseWiseApp();
const isAdminRoute = typeof window !== 'undefined' && window.location.pathname.startsWith('/admin');

const title = computed(() => {
  if (isAdminRoute) {
    return '易如反掌后台';
  }
  switch (activeTab.value) {
    case 'home': return '易如反掌';
    case 'phone': return '手机号评测';
    case 'bazi': return '四柱八字评测';
    case 'meihua': return '梅花易数评测';
    case 'agent': return '智能体';
    case 'profile': return '我的';
    case 'recharge': return '积分充值';
    case 'points-claim': return '免费积分领取';
    default: return '易如反掌';
  }
});

function readCurrentRoute(): { tab: AppTab; query: Record<string, string> } {
  if (typeof window === 'undefined') {
    return { tab: 'home', query: {} };
  }

  const url = new URL(window.location.href);
  const query = Object.fromEntries(url.searchParams.entries());
  const page = query.page || '';
  const claimPathMatch = url.pathname.match(/^\/(?:points-claim|claim)\/([^/?#]+)/u);

  if (claimPathMatch) {
    return {
      tab: 'points-claim',
      query: {
        ...query,
        claim_code: decodeURIComponent(claimPathMatch[1]),
      },
    };
  }

  if (url.pathname === '/recharge' || page === 'recharge') {
    return { tab: 'recharge', query };
  }
  if (page === 'phone') {
    return { tab: 'phone', query };
  }
  if (page === 'bazi' || page === 'four-pillars') {
    return { tab: 'bazi', query };
  }
  if (page === 'meihua' || page === 'plum-blossom') {
    return { tab: 'meihua', query };
  }
  if (page === 'agent') {
    return { tab: 'agent', query };
  }
  if (page === 'profile') {
    return { tab: 'profile', query };
  }
  return { tab: 'home', query };
}

function syncRouteState(tab: AppTab, params: Record<string, string | number | undefined> = {}, options: { replace?: boolean } = {}): void {
  if (typeof window === 'undefined' || isAdminRoute) {
    return;
  }

  const normalizedParams = new URLSearchParams();
  if (tab !== 'home' && tab !== 'recharge' && tab !== 'points-claim') {
    normalizedParams.set('page', tab);
  }
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') {
      return;
    }
    normalizedParams.set(key, String(value));
  });

  const nextUrl = new URL(window.location.href);
  if (tab === 'recharge') {
    nextUrl.pathname = '/recharge';
  } else if (tab === 'points-claim') {
    const claimCode = String(params.claim_code || routeQuery.value.claim_code || '').trim();
    nextUrl.pathname = claimCode ? `/points-claim/${encodeURIComponent(claimCode)}` : '/points-claim';
    normalizedParams.delete('claim_code');
  } else {
    nextUrl.pathname = '/';
  }
  nextUrl.search = normalizedParams.toString() ? `?${normalizedParams.toString()}` : '';
  const nextState = { tab, params: Object.fromEntries(normalizedParams.entries()) };
  if (options.replace) {
    window.history.replaceState(nextState, '', `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`);
  } else {
    window.history.pushState(nextState, '', `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`);
  }
}

const navigateToTab = (tab: string, params: Record<string, string | number | undefined> = {}) => {
  const currentActiveElement = typeof document !== 'undefined' ? document.activeElement : null;
  if (currentActiveElement instanceof HTMLElement) {
    currentActiveElement.blur();
  }

  const nextTab = tab as AppTab;
  if (activeTab.value === nextTab && JSON.stringify(routeQuery.value) === JSON.stringify(Object.fromEntries(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')))) {
    return;
  }

  activeTab.value = nextTab;
  routeQuery.value = Object.fromEntries(
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null && value !== '')
      .map(([key, value]) => [key, String(value)]),
  );
  syncRouteState(nextTab, params);

  nextTick(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'auto',
      });
    }
  });
};

async function handlePhoneClick(): Promise<void> {
  const authenticated = await requestRegisteredUser('数字奇门手机号评测');
  if (authenticated) {
    navigateToTab('phone');
  }
}

async function handleBaziClick(): Promise<void> {
  const authenticated = await requestRegisteredUser('四柱八字评测');
  if (authenticated) {
    navigateToTab('bazi');
  }
}

async function handleMeihuaClick(): Promise<void> {
  const authenticated = await requestRegisteredUser('梅花易数评测');
  if (authenticated) {
    navigateToTab('meihua');
  }
}

onMounted(() => {
  if (!isAdminRoute) {
    const initialRoute = readCurrentRoute();
    activeTab.value = initialRoute.tab;
    routeQuery.value = Object.fromEntries(
      Object.entries(initialRoute.query).filter(([key]) => key !== 'page'),
    );
    syncRouteState(initialRoute.tab, routeQuery.value, {replace: true});
    window.addEventListener('popstate', () => {
      const route = readCurrentRoute();
      activeTab.value = route.tab;
      routeQuery.value = Object.fromEntries(
        Object.entries(route.query).filter(([key]) => key !== 'page'),
      );
    });
  }
  void bootstrapApp();
});

watch(title, (value) => {
  if (typeof document !== 'undefined') {
    document.title = value;
  }
}, { immediate: true });
</script>

<template>
  <div v-if="!isAdminRoute" class="min-h-screen bg-slate-950/5 relative overflow-x-hidden">
    <div class="min-h-screen relative max-w-md mx-auto bg-brand-paper shadow-2xl border-x border-gray-100">
      <!-- Main viewport -->
      <main class="font-sans antialiased min-h-screen">
        <div v-if="activeTab === 'home'">
          <Home
            @phone-click="handlePhoneClick"
            @bazi-click="handleBaziClick"
            @meihua-click="handleMeihuaClick"
          />
        </div>
        <div v-else-if="activeTab === 'phone'">
          <Analysis
            @back-to-home="navigateToTab('home')"
            @navigate-to-tab="navigateToTab"
          />
        </div>
        <div v-else-if="activeTab === 'bazi'">
          <FourPillarsAnalysis
            :route-query="routeQuery"
            @back-to-home="navigateToTab('home')"
            @navigate-to-tab="navigateToTab"
          />
        </div>
        <div v-else-if="activeTab === 'meihua'">
          <MeihuaAnalysis
            @back-to-home="navigateToTab('home')"
            @navigate-to-tab="navigateToTab"
          />
        </div>
        <div v-else-if="activeTab === 'agent'">
          <AIAgent />
        </div>
        <div v-else-if="activeTab === 'profile'">
          <Profile
            @navigate-to-tab="navigateToTab"
          />
        </div>
        <div v-else-if="activeTab === 'recharge'">
          <RechargePage
            :route-query="routeQuery"
            @navigate-to-tab="navigateToTab"
          />
        </div>
        <div v-else-if="activeTab === 'points-claim'">
          <PointsClaimPage
            :claim-code="routeQuery.claim_code || ''"
            @navigate-to-tab="navigateToTab"
          />
        </div>
      </main>

      <!-- Tab navigations -->
      <BottomNav
        v-if="activeTab !== 'recharge' && activeTab !== 'points-claim'"
        :active-tab="activeTab === 'phone' || activeTab === 'bazi' || activeTab === 'meihua' ? 'home' : activeTab"
        @update:active-tab="navigateToTab"
      />
    </div>
    <AuthModal v-if="!isAdminRoute" />
    <ContactServiceModal v-if="!isAdminRoute" />
  </div>
  <AdminWorkspace v-else />
</template>
```

### `src/components/analysis/Analysis.vue`

```vue
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
import type { Gender, PhoneReviewAspectStreamDeltaData, PhoneReviewCoreStreamDeltaData, ReviewAspect, ReviewProgressStage, ReviewRecord } from '../../types/api';

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
  is_streaming?: boolean;
};

type AspectStreamDraft = Partial<Pick<ReviewAspect, 'title' | 'risk' | 'content'>> & {
  is_streaming: boolean;
};

type PhoneSummaryStreamDraft = {
  title?: string;
  risk?: string;
  usage_guidance?: string;
  is_streaming: boolean;
};

type StabilityStreamDraft = {
  verdict?: string;
  content?: string;
  is_streaming: boolean;
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
  submitPhoneReviewStream,
  refreshCurrentReview,
  streamUnlockAspect,
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
const waitingAnimationComplete = ref(false);
const baseReviewCoreReady = ref(false);
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
const aspectStreamDrafts = ref<Record<string, AspectStreamDraft>>({});
const phoneSummaryStreamDraft = ref<PhoneSummaryStreamDraft | null>(null);
const stabilityStreamDraft = ref<StabilityStreamDraft | null>(null);
const baseReviewStreamActiveId = ref<string | null>(null);
let disposed = false;
let pollingPromise: Promise<ReviewRecord> | null = null;
let lastCompletedReviewId: string | null = null;
let waitingVisualTimers: ReturnType<typeof setTimeout>[] = [];
let waitingPoemTimer: ReturnType<typeof setInterval> | null = null;
let waitingProgressTimer: ReturnType<typeof setInterval> | null = null;
let waitingStartedAt = 0;
let aspectUnlockAbortController: AbortController | null = null;

const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const REVIEW_TIMEOUT_MESSAGE = '评测时间比预期更长，请稍后在“我的”页面查看结果。';
const WAITING_PHASE_DURATION_MS = 800;
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
const WAITING_LINEAR_PROGRESS_MS = WAITING_PHASE_DURATION_MS * waitingSteps.length;

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
  (currentReview.value?.aspects ?? []).map((aspect) => {
    const draft = aspectStreamDrafts.value[aspect.aspect_key];
    return {
      ...aspect,
      ...(draft
        ? {
            title: draft.title || aspect.title,
            risk: draft.risk ?? aspect.risk,
            content: draft.content ?? aspect.content,
            is_unlocked: true,
            is_streaming: draft.is_streaming,
          }
        : {}),
      ...(aspectUiMap[aspect.aspect_key] || {
        icon: Sparkles,
        tint: 'bg-brand-paper text-brand-secondary',
        textTint: 'text-brand-secondary',
      }),
    };
  }),
);
const selectedAspect = computed(() => reviewAspects.value[activeAspect.value] || null);
const selectedAspectUnlockPending = computed(() => selectedAspect.value ? isAspectUnlockPending(selectedAspect.value) : false);
const selectedAspectDetailReady = computed(() => selectedAspect.value ? hasAspectDetail(selectedAspect.value) : false);
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
    return '正在确认解锁状态，完成后会立即展示。';
  }
  return 'AI 正在实时生成这部分内容，文字会逐步出现在这里。';
});
const unlockProcessingHeading = computed(
  () => selectedAspectWaitingForGeneration.value ? `正在生成「${unlockWaitingAspectTitle.value}」` : `正在解锁「${unlockProcessingTitle.value}」`,
);
const reviewPhoneDisplay = computed(() => currentReview.value?.phone_number || phoneNumber.value);
const reviewGenderDisplay = computed(() => (currentReview.value?.gender || gender.value) === 'male' ? '男' : '女');
const reviewScore = computed(() => currentReview.value?.score ?? 0);
const phoneSummary = computed(() => {
  const base = currentReview.value?.phone_summary ?? null;
  const draft = phoneSummaryStreamDraft.value;
  if (!draft) {
    return base;
  }
  return {
    title: draft.title ?? base?.title ?? '',
    risk: draft.risk ?? base?.risk ?? '',
    usage_guidance: draft.usage_guidance ?? base?.usage_guidance ?? '',
    elements_check: base?.elements_check ?? {},
  };
});
const stabilityDetail = computed(() => {
  const base = currentReview.value?.stability_detail ?? null;
  const draft = stabilityStreamDraft.value;
  if (!draft) {
    return base;
  }
  return {
    verdict: draft.verdict ?? base?.verdict ?? '',
    content: draft.content ?? base?.content ?? '',
    elements_check: base?.elements_check ?? {},
  };
});
const phoneSummaryTitle = computed(() => cleanDisplayText(phoneSummary.value?.title) || '系统会根据盘面结果生成总评。');
const phoneSummaryRisk = computed(() => cleanDisplayText(phoneSummary.value?.risk) || '系统会根据盘面结果生成风险提醒。');
const phoneSummaryUsageGuidance = computed(
  () => cleanDisplayText(phoneSummary.value?.usage_guidance) || '系统会根据盘面结果生成使用建议。',
);

async function ensureRegisteredForAction(reason: string): Promise<boolean> {
  if (state.user && !isGuestUser.value) {
    return true;
  }
  return requestRegisteredUser(reason);
}
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
  if (errorCode === 'autoplay_blocked') {
    return '浏览器拦截了播放，请再点一次播放按钮。';
  }
  if (errorCode === 'audio_play_failed') {
    return '语音文件加载或播放失败。';
  }
  if (errorCode === 'browser_speech_failed') {
    return '浏览器本地语音播报失败。';
  }
  if (errorCode === 'voice_text_empty') {
    return '当前没有可播报的文案。';
  }
  if (errorCode.includes('not_ready')) {
    return '内容还在生成中，请稍后再试。';
  }
  if (errorCode.includes('too_long')) {
    return '播报文案过长，请稍后拆分后再试。';
  }
  if (errorCode.includes('http_') || errorCode.includes('synthesis_failed')) {
    return '云语音服务请求失败，请稍后再试。';
  }
  return '请稍后再试。';
}

function stopVoiceAndDisableAutoplay(): void {
  voicePlayback.setAutoplayEnabled(false);
  showToast('已关闭自动语音播报，可手动播放。');
}

function autoSpeakPhoneSummary(review: ReviewRecord): void {
  void nextTick().then(async () => {
    await speakPhoneSummaryWithAutoFollow(review, true);
  });
}

async function speakPhoneSummaryWithAutoFollow(review: ReviewRecord | null | undefined, auto: boolean) {
  const result = await voicePlayback.speakPhoneSummary(review, { auto });
  if (result.completed && voiceAutoplayEnabled.value) {
    await voicePlayback.speakStability(review, { auto: true });
  }
  return result;
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

function hasAspectDetail(aspect: Pick<ReviewAspect, 'content' | 'risk'> | null | undefined): boolean {
  return Boolean(String(aspect?.content || '').trim() || String(aspect?.risk || '').trim());
}

function resolveAspectUnlockCost(aspect: Pick<ReviewAspect, 'unlock_points'> | null | undefined): number {
  return aspect?.unlock_points ?? effectiveAspectUnlockPoints.value;
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

function isAspectUnlockCancelledError(error: unknown): boolean {
  return error instanceof Error && (error.message === 'aspect_unlock_cancelled' || error.name === 'AbortError');
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
  voicePlayback.stop();
  appState.value = 'input';
  errorType.value = 'none';
  errorDetail.value = '';
  currentProgressStage.value = null;
  currentProgressMessage.value = '';
  waitingVisualPhase.value = 0;
  waitingPoemIndex.value = 0;
  waitingProgressValue.value = 0;
  waitingAnimationComplete.value = false;
  baseReviewCoreReady.value = false;
  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  clearCoreStreamDrafts();
  baseReviewStreamActiveId.value = null;
  clearWaitingTimers();
  clearUnlockState({ abort: true });
}

function clearUnlockState(options: { abort?: boolean } = {}): void {
  if (options.abort && aspectUnlockAbortController) {
    aspectUnlockAbortController.abort();
    aspectUnlockAbortController = null;
  }
  unlockingAspectKey.value = null;
  unlockWaitingAspectKey.value = null;
}

function clearCoreStreamDrafts(): void {
  phoneSummaryStreamDraft.value = null;
  stabilityStreamDraft.value = null;
}

function markBaseReviewCoreReady(): void {
  baseReviewCoreReady.value = true;
  tryRevealWaitingResult();
}

function applyCoreStreamDelta(data: PhoneReviewCoreStreamDeltaData): void {
  if (data.section === 'phone_summary') {
    phoneSummaryStreamDraft.value = {
      ...(phoneSummaryStreamDraft.value || { is_streaming: true }),
      [data.field]: data.text,
      is_streaming: true,
    };
    return;
  }
  if (data.section === 'stability') {
    stabilityStreamDraft.value = {
      ...(stabilityStreamDraft.value || { is_streaming: true }),
      [data.field]: data.text,
      is_streaming: true,
    };
  }
}

function completeWaitingAnimation(): void {
  if (disposed || appState.value !== 'waiting') {
    return;
  }
  waitingAnimationComplete.value = true;
  waitingProgressValue.value = 100;
  tryRevealWaitingResult();
}

function tryRevealWaitingResult(): void {
  if (appState.value !== 'waiting' || !waitingAnimationComplete.value) {
    return;
  }

  if (pendingCompletedReview.value) {
    const review = pendingCompletedReview.value;
    const shouldToast = pendingCompletedReviewShouldToast.value;
    pendingCompletedReview.value = null;
    pendingCompletedReviewShouldToast.value = false;
    applyCompletedReviewState(review, { showToastOnComplete: shouldToast });
    return;
  }

  if (!baseReviewCoreReady.value || !currentReview.value) {
    return;
  }

  revealStreamingReviewShell();
}

function revealStreamingReviewShell(): void {
  clearWaitingTimers();
  waitingProgressValue.value = 100;
  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  if (currentReview.value) {
    phoneNumber.value = sanitizePhone(currentReview.value.phone_number || currentReview.value.phone || '');
    gender.value = currentReview.value.gender;
    currentProgressStage.value = currentReview.value.progress_stage;
    currentProgressMessage.value = currentReview.value.progress_message || currentProgressMessage.value;
  }
  errorType.value = 'none';
  errorDetail.value = '';
  closeReviewConfirmDialog();
  appState.value = 'result';
  if (activeAspect.value < 0 && reviewAspects.value.length) {
    activeAspect.value = resolveDefaultAspectIndex(reviewAspects.value);
  }
}

function applyAspectStreamDelta(aspectKey: string, data: PhoneReviewAspectStreamDeltaData): void {
  const currentDraft = aspectStreamDrafts.value[aspectKey] || { is_streaming: true };
  aspectStreamDrafts.value = {
    ...aspectStreamDrafts.value,
    [aspectKey]: {
      ...currentDraft,
      [data.field]: data.text,
      is_streaming: true,
    },
  };
}

function clearAspectStreamDraft(aspectKey: string): void {
  if (!aspectStreamDrafts.value[aspectKey]) {
    return;
  }
  const nextDrafts = { ...aspectStreamDrafts.value };
  delete nextDrafts[aspectKey];
  aspectStreamDrafts.value = nextDrafts;
}

function resolveDefaultAspectIndex(aspects: DisplayAspect[]): number {
  return aspects.length ? 0 : -1;
}

function isWaitingFinalPhaseReady(): boolean {
  return waitingAnimationComplete.value;
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
  if (appState.value === 'waiting' && !waitingAnimationComplete.value) {
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
  const shouldAutoSpeakOnDisplay = lastCompletedReviewId !== review.id;
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
  if (shouldAutoSpeakOnDisplay || options.showToastOnComplete) {
    autoSpeakPhoneSummary(review);
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
  if (appState.value !== 'result') {
    appState.value = 'waiting';
  }
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
    if (error.status === 403 && error.detail === 'registered_user_required') {
      appState.value = 'input';
      void requestRegisteredUser('手机号评测');
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

  if (baseReviewStreamActiveId.value === review.id) {
    return;
  }

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
  waitingAnimationComplete,
  () => {
    tryRevealWaitingResult();
  },
);

onMounted(() => {
  void bootstrapApp();
});

onUnmounted(() => {
  disposed = true;
  voicePlayback.stop();
  clearUnlockState({ abort: true });
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

  voicePlayback.primeAudioSession();
  const cleanPhone = validatePhoneBeforeReview();
  if (!cleanPhone) {
    return;
  }
  const authenticated = await ensureRegisteredForAction('手机号评测');
  if (!authenticated) {
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
  voicePlayback.primeAudioSession();
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
  voicePlayback.stop();
  voicePlayback.primeAudioSession();
  const cleanPhone = preparedPhone ?? validatePhoneBeforeReview();
  if (!cleanPhone) {
    return;
  }
  const authenticated = await ensureRegisteredForAction('手机号评测');
  if (!authenticated) {
    return;
  }
  const selectedGender = gender.value;

  errorType.value = 'none';
  errorDetail.value = '';
  clearUnlockState();
  clearCoreStreamDrafts();
  baseReviewStreamActiveId.value = null;
  clearWaitingTimers();
  currentProgressStage.value = 'queued';
  currentProgressMessage.value = '评测任务已创建，等待开始';
  waitingVisualPhase.value = 0;
  waitingPoemIndex.value = 0;
  waitingProgressValue.value = WAITING_PROGRESS_START_PERCENT;
  waitingAnimationComplete.value = false;
  baseReviewCoreReady.value = false;
  waitingStartedAt = Date.now();
  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  appState.value = 'waiting';
  waitingVisualTimers = [
    ...waitingSteps.slice(1).map((_, index) => window.setTimeout(() => {
      if (!disposed && appState.value === 'waiting') {
        waitingVisualPhase.value = index + 1;
      }
    }, WAITING_PHASE_DURATION_MS * (index + 1))),
    window.setTimeout(() => {
      completeWaitingAnimation();
    }, WAITING_PHASE_DURATION_MS * waitingSteps.length),
  ];
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
    await submitPhoneReviewStream(
      {
        phone: cleanPhone,
        gender: selectedGender,
        include_markdown: true,
      },
      {
        onCreated: (data) => {
          baseReviewStreamActiveId.value = data.review.id;
          currentProgressStage.value = data.review.progress_stage;
          currentProgressMessage.value = data.review.progress_message || '';
          tryRevealWaitingResult();
        },
        onFactsReady: (data) => {
          baseReviewStreamActiveId.value = data.review.id;
          currentProgressStage.value = data.review.progress_stage;
          currentProgressMessage.value = data.review.progress_message || '';
          tryRevealWaitingResult();
        },
        onCoreStatus: (data) => {
          currentProgressMessage.value = data.message || currentProgressMessage.value;
          markBaseReviewCoreReady();
        },
        onCoreDelta: (data) => {
          applyCoreStreamDelta(data);
          markBaseReviewCoreReady();
        },
        onSectionComplete: (data) => {
          markBaseReviewCoreReady();
          if (data.section === 'phone_summary') {
            const payload = data.payload as Partial<PhoneSummaryStreamDraft>;
            phoneSummaryStreamDraft.value = {
              ...(phoneSummaryStreamDraft.value || { is_streaming: false }),
              title: typeof payload.title === 'string' ? payload.title : phoneSummaryStreamDraft.value?.title,
              risk: typeof payload.risk === 'string' ? payload.risk : phoneSummaryStreamDraft.value?.risk,
              usage_guidance: typeof payload.usage_guidance === 'string' ? payload.usage_guidance : phoneSummaryStreamDraft.value?.usage_guidance,
              is_streaming: false,
            };
          }
          if (data.section === 'stability') {
            const payload = data.payload as Partial<StabilityStreamDraft>;
            stabilityStreamDraft.value = {
              ...(stabilityStreamDraft.value || { is_streaming: false }),
              verdict: typeof payload.verdict === 'string' ? payload.verdict : stabilityStreamDraft.value?.verdict,
              content: typeof payload.content === 'string' ? payload.content : stabilityStreamDraft.value?.content,
              is_streaming: false,
            };
          }
        },
        onComplete: (data) => {
          baseReviewStreamActiveId.value = null;
          baseReviewCoreReady.value = true;
          clearCoreStreamDrafts();
          if (!disposed) {
            applyOrDeferCompletedReviewState(data.review, { showToastOnComplete: true });
          }
        },
        onError: () => {
          baseReviewStreamActiveId.value = null;
        },
      },
    );
  } catch (error) {
    baseReviewStreamActiveId.value = null;
    handleReviewSyncError(error);
  } finally {
    if (appState.value !== 'waiting' || !pendingCompletedReview.value || isWaitingFinalPhaseReady()) {
      clearWaitingTimers();
    }
  }
}

async function handleUnlockAspect(index: number): Promise<void> {
  voicePlayback.primeAudioSession();
  const aspect = reviewAspects.value[index];
  const review = currentReview.value;

  if (!aspect || !review) {
    return;
  }

  activeAspect.value = index;

  if (aspect.is_unlocked && hasAspectDetail(aspect)) {
    return;
  }
  const authenticated = await ensureRegisteredForAction('专项解锁');
  if (!authenticated) {
    return;
  }

  try {
    await streamUnlockAspectForDisplay(review.id, aspect.aspect_key, aspect.title);
  } catch (error) {
    if (isAspectUnlockCancelledError(error)) {
      return;
    }
    if (error instanceof ApiError && error.status === 402) {
      setError('unlock_points_insufficient');
      return;
    }
    if (error instanceof ApiError && error.status === 403 && error.detail === 'registered_user_required') {
      void requestRegisteredUser('专项解锁');
      return;
    }
    setError('request_failed', humanizeError(error));
  } finally {
    if (unlockingAspectKey.value === aspect.aspect_key) {
      unlockingAspectKey.value = null;
    }
    if (unlockWaitingAspectKey.value === aspect.aspect_key) {
      unlockWaitingAspectKey.value = null;
    }
  }
}

async function streamUnlockAspectForDisplay(reviewId: string, aspectKey: string, title: string): Promise<void> {
  if (aspectUnlockAbortController) {
    aspectUnlockAbortController.abort();
  }
  const controller = new AbortController();
  aspectUnlockAbortController = controller;
  unlockingAspectKey.value = aspectKey;
  unlockWaitingAspectKey.value = aspectKey;
  clearAspectStreamDraft(aspectKey);
  currentProgressStage.value = 'rendering';
  currentProgressMessage.value = `正在实时生成「${title}」专项内容`;

  try {
    const result = await streamUnlockAspect(reviewId, aspectKey, {
      signal: controller.signal,
      onStatus: (data) => {
        currentProgressMessage.value = data.message || `正在实时生成「${title}」专项内容`;
      },
      onDelta: (data) => {
        applyAspectStreamDelta(aspectKey, data);
      },
    });
    clearAspectStreamDraft(aspectKey);
    persistCompletedReviewState(result.review);
    clearUnlockState();
    showToast(`已解锁「${title}」详细分析。`);
    autoSpeakUnlockedAspect(result.review, aspectKey);
  } catch (error) {
    clearAspectStreamDraft(aspectKey);
    if (disposed || controller.signal.aborted) {
      throw new Error('aspect_unlock_cancelled');
    }
    throw error;
  } finally {
    if (aspectUnlockAbortController === controller) {
      aspectUnlockAbortController = null;
    }
  }
}

function handleOpenServiceContact(scene = 'review_support'): void {
  openCustomerServiceModal(scene);
}

function handleSelectNextLockedAspect(): void {
  const nextLockedIndex = reviewAspects.value.findIndex((aspect) => !hasAspectDetail(aspect));
  if (nextLockedIndex === -1) {
    showToast('当前十二个专项均已生成。');
    void scrollToAspectSection();
    return;
  }
  activeAspect.value = nextLockedIndex;
  void scrollToAspectSection();
}

function resolveHeaderOffset(): number {
  return 0;
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
  <div class="pt-4 pb-32 max-w-md mx-auto w-full relative min-h-screen">
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
      <div
        v-if="appState === 'input'"
        key="input-form"
        class="px-margin-mobile space-y-5 pt-3.5"
      >
        <div class="flex items-center justify-between">
          <button
            type="button"
            class="h-9 rounded-lg bg-white border border-gray-100 px-3.5 text-brand-secondary font-sans text-[12px] font-bold shadow-sm flex items-center gap-1.5"
            @click="emit('back-to-home')"
          >
            <ArrowLeft :size="14" />
            <span>返回首页</span>
          </button>
        </div>

        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="relative flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5 shrink-0">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-primary/50"></span>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-primary"></span>
            </span>
            <h2 class="font-serif text-[16px] font-black text-brand-gold-fixed leading-snug">奇门遁甲手机号综合测评</h2>
          </div>
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
              <span v-else>立即扣除 <span class="font-sans">{{ effectiveBaseReviewPoints }}</span> 积分，深度智能测算</span>
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
          <div class="flex items-center justify-between gap-2">
            <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5">
              <Compass :size="13" class="text-brand-primary shrink-0" />
              <span>奇门盘面解析</span>
            </h4>
            <div v-if="voiceEnabled" class="flex items-center gap-1">
              <button
                type="button"
                @click="handlePhoneSummaryVoiceClick"
                class="h-[26px] px-2.5 rounded-full border text-[10.5px] font-bold inline-flex items-center gap-1.5 transition-all cursor-pointer outline-none select-none active:scale-95 shadow-[0_1px_4px_rgba(0,0,0,0.03)] disabled:cursor-wait disabled:opacity-85"
                :class="[
                  phoneSummaryVoicePlaying
                    ? 'bg-emerald-500/10 border-emerald-300 text-emerald-700 hover:bg-emerald-500/15'
                    : phoneSummaryVoiceLoading
                      ? 'bg-amber-500/10 border-amber-300 text-amber-700 animate-pulse'
                      : 'bg-neutral-50 hover:bg-neutral-100 border-neutral-200 text-neutral-500 hover:text-neutral-700',
                ]"
                title="播放综合评述"
              >
                <template v-if="phoneSummaryVoiceLoading">
                  <span class="w-2.5 h-2.5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></span>
                  <span class="tracking-tight font-black scale-90 origin-left">载入中...</span>
                </template>
                <template v-else-if="phoneSummaryVoicePlaying">
                  <span class="voice-wave" aria-hidden="true">
                    <span class="voice-wave-bar"></span>
                    <span class="voice-wave-bar" style="animation-delay: 0.16s;"></span>
                    <span class="voice-wave-bar" style="animation-delay: 0.32s;"></span>
                  </span>
                  <span class="tracking-tight text-emerald-600 font-extrabold scale-90 origin-left animate-pulse">播报中</span>
                </template>
                <template v-else>
                  <Volume2 :size="11" />
                  <span class="tracking-tight scale-90 origin-left">听综评</span>
                </template>
              </button>
            </div>
          </div>

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
          <div class="flex items-center justify-between gap-2">
            <h4 class="font-serif text-[13px] font-bold text-brand-secondary tracking-wide flex items-center gap-1.5">
              <Lightbulb :size="13" class="text-brand-primary shrink-0" />
              <span>长期使用建议</span>
            </h4>
            <button
              v-if="voiceEnabled"
              type="button"
              @click="handleStabilityVoiceClick"
              class="h-[26px] px-2.5 rounded-full border text-[10.5px] font-bold inline-flex items-center gap-1.5 transition-all cursor-pointer outline-none select-none active:scale-95 shadow-[0_1px_4px_rgba(0,0,0,0.03)] disabled:cursor-wait disabled:opacity-85"
              :class="[
                stabilityVoicePlaying
                  ? 'bg-emerald-500/10 border-emerald-300 text-emerald-700 hover:bg-emerald-500/15'
                  : stabilityVoiceLoading
                    ? 'bg-amber-500/10 border-amber-300 text-amber-700 animate-pulse'
                    : 'bg-neutral-50 hover:bg-neutral-100 border-neutral-200 text-neutral-500 hover:text-neutral-700',
              ]"
              title="播放长期使用建议"
            >
              <template v-if="stabilityVoiceLoading">
                <span class="w-2.5 h-2.5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></span>
                <span class="tracking-tight font-black scale-90 origin-left">载入中...</span>
              </template>
              <template v-else-if="stabilityVoicePlaying">
                <span class="voice-wave" aria-hidden="true">
                  <span class="voice-wave-bar"></span>
                  <span class="voice-wave-bar" style="animation-delay: 0.16s;"></span>
                  <span class="voice-wave-bar" style="animation-delay: 0.32s;"></span>
                </span>
                <span class="tracking-tight text-emerald-600 font-extrabold scale-90 origin-left animate-pulse">播报中</span>
              </template>
              <template v-else>
                <Volume2 :size="11" />
                <span class="tracking-tight scale-90 origin-left">听建议</span>
              </template>
            </button>
          </div>

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
              <div v-if="selectedAspectUnlockPending && !selectedAspectDetailReady" class="py-12 flex flex-col items-center justify-center space-y-4 text-center">
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

              <div v-else-if="selectedAspectDetailReady" class="space-y-4">
                <div class="flex justify-between items-center pb-3 border-b border-gray-50 gap-2">
                  <div class="flex items-center gap-2">
                    <component :is="selectedAspect.icon" :size="16" class="text-brand-primary shrink-0" />
                    <span class="font-serif text-[15px] font-extrabold text-brand-ink-strong leading-tight">
                      {{ selectedAspect.short_title || selectedAspect.title }} · 详细结果
                    </span>
                  </div>
                  <div class="flex items-center gap-1.5 shrink-0">
                    <button
                      v-if="voiceEnabled"
                      type="button"
                      @click="handleSelectedAspectVoiceClick"
                      class="h-[26px] px-2.5 rounded-full border text-[10.5px] font-bold inline-flex items-center gap-1.5 transition-all cursor-pointer outline-none select-none active:scale-95 shadow-[0_1px_4px_rgba(0,0,0,0.03)] disabled:cursor-wait disabled:opacity-85"
                      :class="[
                        selectedAspectVoicePlaying
                          ? 'bg-emerald-500/10 border-emerald-300 text-emerald-700 hover:bg-emerald-500/15'
                          : selectedAspectVoiceLoading
                            ? 'bg-amber-500/10 border-amber-300 text-amber-700 animate-pulse'
                            : 'bg-neutral-50 hover:bg-neutral-100 border-neutral-200 text-neutral-500 hover:text-neutral-700',
                      ]"
                      :title="`播放${selectedAspectVoiceLabel}`"
                    >
                      <template v-if="selectedAspectVoiceLoading">
                        <span class="w-2.5 h-2.5 border-2 border-amber-600 border-t-transparent rounded-full animate-spin"></span>
                        <span class="tracking-tight font-black scale-90 origin-left">载入中...</span>
                      </template>
                      <template v-else-if="selectedAspectVoicePlaying">
                        <span class="voice-wave" aria-hidden="true">
                          <span class="voice-wave-bar"></span>
                          <span class="voice-wave-bar" style="animation-delay: 0.16s;"></span>
                          <span class="voice-wave-bar" style="animation-delay: 0.32s;"></span>
                        </span>
                        <span class="tracking-tight text-emerald-600 font-extrabold scale-90 origin-left animate-pulse">播报中</span>
                      </template>
                      <template v-else>
                        <Volume2 :size="11" />
                        <span class="tracking-tight scale-90 origin-left">{{ selectedAspectVoiceLabel }}</span>
                      </template>
                    </button>
                    <span
                      class="px-2.5 py-1 rounded-full font-sans text-[11px] font-bold border"
                      :class="resolveScoreBadgeClass(selectedAspect.score, false)"
                    >
                      {{ selectedAspectUnlockPending ? '实时生成中' : `专项评分：${selectedAspect.score != null ? `${selectedAspect.score}分` : '已解锁'}` }}
                    </span>
                  </div>
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
                    生成「{{ selectedAspect.title }}」详细分析
                  </h5>
                  <p class="font-sans text-[13px] text-brand-secondary mt-1 leading-relaxed">
                    点击后将实时生成该维度的深度内容<span v-if="resolveAspectUnlockCost(selectedAspect) > 0">，默认需要消耗 <span class="font-sans">{{ resolveAspectUnlockCost(selectedAspect) }}</span> 积分</span>。
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
                    <span v-else-if="resolveAspectUnlockCost(selectedAspect) <= 0">免费生成并解锁</span>
                    <span v-else>
                      消耗 <span class="font-sans">{{ resolveAspectUnlockCost(selectedAspect) }}</span> 积分立即解锁
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
            @click="handleOpenServiceContact('review_support')"
            class="bg-brand-primary/5 hover:bg-brand-primary/10 transition-colors border border-brand-primary/10 rounded-2xl p-4 flex items-center justify-between cursor-pointer group shadow-sm bg-white"
          >
            <div class="flex items-center gap-2.5 text-left">
              <div class="w-8 h-8 rounded-full bg-brand-primary/10 flex items-center justify-center shrink-0">
                <Sparkles :size="16" class="text-brand-primary animate-pulse" fill="currentColor" />
              </div>
              <div class="font-sans">
                <p class="text-[13px] font-bold text-brand-ink-strong">联系客服获取后续支持</p>
                <p class="text-[11px] text-brand-secondary mt-0.5">{{ customerServiceCopyForScene('review_support') }}</p>
              </div>
            </div>
            <div class="text-brand-primary font-sans font-bold text-[11px] bg-brand-primary/10 group-hover:bg-brand-primary/20 px-2.5 py-1 rounded-full flex items-center gap-1 shrink-0">
              <span>打开</span>
              <MessageSquare :size="10" />
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
              <span>{{ customerServiceCopyForScene('points_insufficient') }}</span>
            </div>
          </div>

          <div class="bg-brand-paper p-3 rounded-xl flex items-center justify-between border border-gray-100 font-sans">
            <div class="text-left font-mono">
              <p class="text-[10px] text-brand-secondary">客服支持：</p>
              <p class="text-[15px] font-bold text-brand-ink-strong">打开客服弹窗</p>
            </div>
            <button
              @click="handleOpenServiceContact('points_insufficient')"
              class="px-3.5 py-1.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[11px] font-bold rounded-lg cursor-pointer outline-none flex items-center gap-1 shrink-0 transition-all shadow-sm"
            >
              <MessageSquare :size="11" />
              <span>联系客服</span>
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
            @click="emit('navigate-to-tab', 'recharge', {
              source: errorType === 'unlock_points_insufficient' ? 'unlock_points_insufficient' : 'insufficient_points',
              return_to: 'phone',
              required_points: errorType === 'unlock_points_insufficient' ? effectiveAspectUnlockPoints : effectiveBaseReviewPoints,
            })"
            class="w-full py-3 bg-white border border-brand-primary/20 text-brand-primary rounded-xl font-bold text-[13px] hover:bg-brand-primary/5 active:scale-[0.98] transition-all cursor-pointer outline-none"
          >
            <span>前往充值</span>
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

.voice-wave {
  display: inline-flex;
  align-items: center;
  gap: 1.5px;
  height: 0.625rem;
  flex-shrink: 0;
}

.voice-wave-bar {
  width: 1.5px;
  height: 0.625rem;
  border-radius: 9999px;
  background: #059669;
  transform-origin: center;
  animation: voice-wave 0.8s ease-in-out infinite alternate;
}

@keyframes voice-wave {
  from {
    transform: scaleY(0.35);
    opacity: 0.65;
  }

  to {
    transform: scaleY(1);
    opacity: 1;
  }
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
```

### `src/components/four-pillars/FourPillarsAnalysis.vue`

```vue
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch, type Component } from 'vue';
import {
  AlertCircle,
  ArrowLeft,
  BookOpen,
  Building2,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  Clock,
  Compass,
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
  Users,
} from 'lucide-vue-next';
import { DEFAULT_ASPECT_UNLOCK_POINTS, DEFAULT_BASE_REVIEW_POINTS } from '../../config/pricing';
import { ApiError, listFourPillarsBirthLocations, resolveFourPillarsInput } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { FourPillarsAspect, FourPillarsChartDisplay, FourPillarsCoreStreamDeltaData, FourPillarsReviewRecord, FourPillarsSummaryRiskWindow, FourPillarsSummaryTimeHighlight, Gender, ReviewProgressStage } from '../../types/api';
import type { FourPillarsLuckCycle, FourPillarsLuckRenderRecord, FourPillarsLuckYearItem, FourPillarsShenShaDetail } from '../../types/api';
import FourPillarsNatalTable from './FourPillarsNatalTable.vue';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
}>();

const props = defineProps<{
  routeQuery?: Record<string, string>;
}>();

type ViewState = 'input' | 'waiting' | 'result' | 'error_state';
type ResultBranch = 'chart' | 'luck';
type InputMode = 'solar' | 'lunar' | 'bazi';
type InputDrawerTab = InputMode;
type DrawerKind = 'datetime' | 'location' | null;
type LocationScope = 'domestic' | 'overseas';
type WheelScope = 'solar' | 'lunar' | 'domestic-location' | 'overseas-location';
type DateTimeSelectionSource = 'manual' | 'wheel';
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
  is_streaming?: boolean;
};

type AspectStreamDraft = Partial<Pick<FourPillarsAspect, 'title' | 'risk' | 'content'>> & {
  is_streaming: boolean;
};

type LuckStreamDraft = {
  render: FourPillarsLuckRenderRecord;
  result: Record<string, unknown>;
  progress_message: string | null;
};

type SummaryStreamDraft = {
  title?: string;
  comprehensive_text?: string;
  overview?: string;
  risk?: string;
  usage_guidance?: string;
  life_risk_windows?: FourPillarsSummaryRiskWindow[];
  time_highlights?: FourPillarsSummaryTimeHighlight[];
  is_streaming: boolean;
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
  submitFourPillarsReviewStream,
  refreshCurrentFourPillarsReview,
  refreshFourPillarsLuckAnalysis,
  streamUnlockFourPillarsAspect,
  streamGenerateFourPillarsLuckCycle,
  streamGenerateFourPillarsLuckYear,
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
const dateTimeSelectionSource = ref<DateTimeSelectionSource>('wheel');
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
const pendingAspectKeys = ref<string[]>([]);
const aspectStreamDrafts = ref<Record<string, AspectStreamDraft>>({});
const luckStreamDrafts = ref<Record<string, LuckStreamDraft>>({});
const summaryStreamDraft = ref<SummaryStreamDraft | null>(null);
const baseReviewStreamActiveId = ref<string | null>(null);
const generatingLuckTargets = ref<string[]>([]);
const selectedLuckYear = ref<number | null>(null);
const luckShenShaExpanded = ref(false);
const waitingStep = ref(1);
const waitingStepProgress = ref([0, 0, 0, 0]);
const waitingPoemIndex = ref(0);
const waitingAnimationComplete = ref(false);
const baseReviewCoreReady = ref(false);
const pendingCompletedReview = ref<FourPillarsReviewRecord | null>(null);
const pendingCompletedReviewShouldToast = ref(false);

let disposed = false;
let pollingPromise: Promise<FourPillarsReviewRecord> | null = null;
let aspectUnlockAbortController: AbortController | null = null;
const aspectPendingSyncTasks = new Map<string, Promise<void>>();
const wheelScrollTimers = new WeakMap<HTMLElement, number>();
let waitingAnimationTimer: ReturnType<typeof setInterval> | null = null;
let waitingPoemTimer: ReturnType<typeof setInterval> | null = null;
let waitingStartedAt = 0;

const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const ASPECT_PENDING_RETRY_LIMIT = 12;
const ASPECT_PENDING_RETRY_DELAY_MS = 2500;
const MAX_SHEN_SHA_ROWS = 3;
const LIFE_STAGE_NAMES = new Set(['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']);
const ASPECT_PENDING_ERROR_DETAILS = new Set([
  'review_not_ready_for_unlock',
  'aspect_generation_in_progress',
  'aspect_generation_incomplete',
  'aspect_not_ready',
]);

const aspectUiMap: Record<string, { icon: Component; tint: string; textTint: string }> = {
  personality: { icon: Sparkles, tint: 'bg-brand-paper text-brand-secondary', textTint: 'text-brand-secondary' },
  wealth: { icon: TrendingUp, tint: 'bg-blue-50 text-blue-600', textTint: 'text-blue-600' },
  marriage: { icon: Heart, tint: 'bg-rose-50 text-rose-600', textTint: 'text-rose-600' },
  career: { icon: Shield, tint: 'bg-green-50 text-green-600', textTint: 'text-green-600' },
  health: { icon: HeartPulse, tint: 'bg-amber-50 text-amber-600', textTint: 'text-amber-600' },
  fortune: { icon: CalendarDays, tint: 'bg-indigo-50 text-indigo-600', textTint: 'text-indigo-600' },
  investment: { icon: TrendingUp, tint: 'bg-emerald-50 text-emerald-600', textTint: 'text-emerald-600' },
  social: { icon: Users, tint: 'bg-cyan-50 text-cyan-600', textTint: 'text-cyan-600' },
  industry: { icon: Building2, tint: 'bg-violet-50 text-violet-600', textTint: 'text-violet-600' },
  fengshui: { icon: Compass, tint: 'bg-teal-50 text-teal-600', textTint: 'text-teal-600' },
  family: { icon: User, tint: 'bg-orange-50 text-orange-600', textTint: 'text-orange-600' },
  pattern: { icon: BookOpen, tint: 'bg-slate-50 text-slate-600', textTint: 'text-slate-600' },
  love: { icon: Heart, tint: 'bg-rose-50 text-rose-600', textTint: 'text-rose-600' },
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
const routeReviewId = computed(() => String(props.routeQuery?.review_id || props.routeQuery?.report_id || '').trim());
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
    durationMs: 1200,
  },
  {
    title: '排定四柱干支结构',
    desc: '依六十甲子排定年、月、日、时四柱',
    message: '正在精排格造八字乾坤盘',
    durationMs: 1200,
  },
  {
    title: '推演五行旺衰与专项结论',
    desc: '推演日主旺衰、十神格局与专项分支',
    message: '正在推演五行衰旺与十神格局',
    durationMs: 1800,
  },
  {
    title: '生成大运与流年基本盘',
    desc: '生成大运流年基本盘并等待后台结果就绪',
    message: '正在编织大运流年终身基本盘',
    durationMs: 1800,
  },
];
const waitingTotalProgress = computed(() => Math.min(100, Math.round(waitingStepProgress.value.reduce((sum, item) => sum + item, 0) / waitingSteps.length)));
const waitingActionText = computed(() => waitingSteps[waitingStep.value - 1]?.message || progressMessage.value);
const reviewAspects = computed<DisplayAspect[]>(() =>
  (currentReview.value?.aspects ?? []).map((aspect) => {
    const draft = aspectStreamDrafts.value[aspect.aspect_key];
    const isPending = pendingAspectKeys.value.includes(aspect.aspect_key);
    return {
      ...aspect,
      ...(draft
        ? {
            title: draft.title || aspect.title,
            content: draft.content ?? aspect.content,
            risk: draft.risk ?? aspect.risk,
            is_unlocked: true,
          }
        : {}),
      is_streaming: Boolean(draft?.is_streaming || isPending),
      ...(aspectUiMap[aspect.aspect_key] || {
        icon: Sparkles,
        tint: 'bg-brand-paper text-brand-secondary',
        textTint: 'text-brand-secondary',
      }),
    };
  }),
);
const luckAnalysis = computed(() => currentReview.value?.luck_analysis ?? null);
const luckCycles = computed<FourPillarsLuckCycle[]>(() => (luckAnalysis.value?.cycles ?? []).map(applyLuckStreamDraftsToCycle));
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
const baseReviewGenerating = computed(() => Boolean(baseReviewStreamActiveId.value || summaryStreamDraft.value?.is_streaming));
const selectedAspectPending = computed(
  () => Boolean(
    selectedAspect.value
    && (
      unlockingAspectKey.value === selectedAspect.value.aspect_key
      || unlockWaitingAspectKey.value === selectedAspect.value.aspect_key
      || pendingAspectKeys.value.includes(selectedAspect.value.aspect_key)
      || selectedAspect.value.is_streaming
    ),
  ),
);
const summary = computed(() => {
  const base = currentReview.value?.summary ?? null;
  const draft = summaryStreamDraft.value;
  if (!draft) {
    return base;
  }
  return {
    ...(base || { elements_check: {} }),
    title: draft.title ?? '',
    comprehensive_text: draft.comprehensive_text ?? '',
    overview: draft.overview ?? '',
    risk: draft.risk ?? '',
    usage_guidance: draft.usage_guidance ?? '',
    life_risk_windows: draft.is_streaming ? [] : (draft.life_risk_windows ?? base?.life_risk_windows ?? []),
    time_highlights: draft.is_streaming ? [] : (draft.time_highlights ?? base?.time_highlights ?? []),
  };
});
const summaryOverview = computed(() => String(summary.value?.overview || '').trim());
const summaryNarrative = computed(() => {
  const comprehensiveText = String(summary.value?.comprehensive_text || '').trim();
  if (comprehensiveText) {
    return comprehensiveText;
  }
  const risk = String(summary.value?.risk || '').trim();
  const usageGuidance = String(summary.value?.usage_guidance || '').trim();
  return [summaryOverview.value, risk, usageGuidance].filter(Boolean).join(' ');
});
const summaryTimeHighlights = computed<FourPillarsSummaryTimeHighlight[]>(() => {
  const directItems = summary.value?.time_highlights;
  if (Array.isArray(directItems) && directItems.length) {
    return directItems
      .filter((item) => item && (String(item.year || '').trim() || String(item.age || '').trim()) && (String(item.title || '').trim() || String(item.content || '').trim()))
      .slice(0, 3);
  }
  const items = summary.value?.life_risk_windows;
  if (!Array.isArray(items)) {
    return [];
  }
  return items
    .map((item) => ({
      year: String(item.year_range || '').trim(),
      age: String(item.age_range || '').trim(),
      title: String(item.risk_type || '').trim(),
      content: String(item.guidance || '').trim(),
      trigger: String(item.trigger || '').trim(),
    }))
    .filter((item) => (item.year || item.age) && (item.title || item.content))
    .slice(0, 3);
});
const hasSummaryV2 = computed(() => Boolean(String(summary.value?.comprehensive_text || '').trim() || summaryTimeHighlights.value.length));
const chart = computed(() => asRecord(currentReview.value?.chart));
const chartDisplay = computed<FourPillarsChartDisplay | null>(() => currentReview.value?.chart_display ?? null);
const facts = computed(() => asRecord(currentReview.value?.deterministic_facts));

function hasAspectDetail(aspect: DisplayAspect | null): boolean {
  if (!aspect) {
    return false;
  }
  return Boolean(String(aspect.content || '').trim() || String(aspect.risk || '').trim());
}

function hasGeneratedAspectContent(aspect: FourPillarsAspect | DisplayAspect | null | undefined): boolean {
  if (!aspect?.is_unlocked) {
    return false;
  }
  return Boolean(String(aspect.content || '').trim() || String(aspect.risk || '').trim());
}

function applyAspectStreamDelta(aspectKey: string, field: 'title' | 'risk' | 'content', text: string): void {
  const currentDraft = aspectStreamDrafts.value[aspectKey] || { is_streaming: true };
  aspectStreamDrafts.value = {
    ...aspectStreamDrafts.value,
    [aspectKey]: {
      ...currentDraft,
      [field]: text,
      is_streaming: true,
    },
  };
}

function clearAspectStreamDraft(aspectKey: string): void {
  if (!aspectStreamDrafts.value[aspectKey]) {
    return;
  }
  const nextDrafts = { ...aspectStreamDrafts.value };
  delete nextDrafts[aspectKey];
  aspectStreamDrafts.value = nextDrafts;
}

function addPendingAspectKey(aspectKey: string): void {
  if (pendingAspectKeys.value.includes(aspectKey)) {
    return;
  }
  pendingAspectKeys.value = [...pendingAspectKeys.value, aspectKey];
}

function removePendingAspectKey(aspectKey: string): void {
  if (!pendingAspectKeys.value.includes(aspectKey)) {
    return;
  }
  pendingAspectKeys.value = pendingAspectKeys.value.filter((key) => key !== aspectKey);
}

function isPendingAspectGenerationError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 409 && ASPECT_PENDING_ERROR_DETAILS.has(error.detail);
}

function reconcilePendingAspects(review: FourPillarsReviewRecord): void {
  if (!pendingAspectKeys.value.length) {
    return;
  }
  const readyKeys = new Set(
    (review.aspects || [])
      .filter((aspect) => hasGeneratedAspectContent(aspect))
      .map((aspect) => aspect.aspect_key),
  );
  if (!readyKeys.size) {
    return;
  }
  pendingAspectKeys.value = pendingAspectKeys.value.filter((key) => !readyKeys.has(key));
}

function startAspectPendingSync(reviewId: string, aspect: Pick<DisplayAspect, 'aspect_key' | 'short_title' | 'title'>): void {
  const taskKey = `${reviewId}:${aspect.aspect_key}`;
  if (aspectPendingSyncTasks.has(taskKey)) {
    return;
  }
  addPendingAspectKey(aspect.aspect_key);
  const task = pollAspectPendingUntilReady(reviewId, aspect)
    .catch(() => {
      if (!disposed) {
        showToast('专项状态同步失败，可稍后刷新查看。', 3000);
      }
    })
    .finally(() => {
      aspectPendingSyncTasks.delete(taskKey);
      removePendingAspectKey(aspect.aspect_key);
    });
  aspectPendingSyncTasks.set(taskKey, task);
  void task;
}

async function pollAspectPendingUntilReady(reviewId: string, aspect: Pick<DisplayAspect, 'aspect_key' | 'short_title' | 'title'>): Promise<void> {
  const aspectName = aspect.short_title || aspect.title || '专项';
  for (let attempt = 0; attempt < ASPECT_PENDING_RETRY_LIMIT; attempt += 1) {
    if (disposed) {
      return;
    }
    await sleep(ASPECT_PENDING_RETRY_DELAY_MS);
    if (disposed) {
      return;
    }
    const latestReview = await refreshCurrentFourPillarsReview(reviewId);
    syncViewFromReview(latestReview);
    const latestAspect = latestReview.aspects.find((item) => item.aspect_key === aspect.aspect_key);
    if (hasGeneratedAspectContent(latestAspect)) {
      clearAspectStreamDraft(aspect.aspect_key);
      showToast(`「${aspectName}」已生成。`);
      return;
    }
  }
  if (!disposed) {
    showToast(`「${aspectName}」仍在后台生成，可稍后刷新查看。`, 3200);
  }
}
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

watch(
  routeReviewId,
  (reviewId) => {
    if (!reviewId || currentReview.value?.id === reviewId) {
      return;
    }
    void restoreReview(reviewId);
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
  clearWaitingTimers();
  aspectUnlockAbortController?.abort();
});

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function applyLuckStreamDraftsToCycle(cycle: FourPillarsLuckCycle): FourPillarsLuckCycle {
  const cycleDraft = luckStreamDrafts.value[`cycle:${cycle.cycle_key}`];
  const yearItems = cycle.year_items.map((item) => {
    const yearDraft = luckStreamDrafts.value[`year:${cycle.cycle_key}:${item.year}`];
    if (!yearDraft) {
      return item;
    }
    return {
      ...item,
      render_status: 'processing',
      render: draftLuckRender(yearDraft, item.render),
    };
  });
  const hasYearDraft = yearItems.some((item, index) => item !== cycle.year_items[index]);
  if (!cycleDraft && !hasYearDraft) {
    return cycle;
  }
  return {
    ...cycle,
    ...(cycleDraft
      ? {
          render_status: 'processing',
          render: draftLuckRender(cycleDraft, cycle.render),
        }
      : {}),
    year_items: hasYearDraft ? yearItems : cycle.year_items,
  };
}

function draftLuckRender(draft: LuckStreamDraft, fallback: FourPillarsLuckRenderRecord | null): FourPillarsLuckRenderRecord {
  return {
    ...(fallback || draft.render),
    ...draft.render,
    status: 'processing',
    progress_message: draft.progress_message || draft.render.progress_message || 'DeepSeek 正在生成内容',
    result: { ...asRecord(fallback?.result), ...draft.result },
  };
}

function createPendingLuckRender(
  reviewId: string,
  renderType: 'dayun' | 'liunian',
  cycleKey: string,
  year: number | null,
  fallback: FourPillarsLuckRenderRecord | null,
): FourPillarsLuckRenderRecord {
  const now = new Date().toISOString();
  return {
    id: fallback?.id || `stream:${renderType}:${cycleKey}:${year || 0}`,
    render_id: fallback?.render_id || fallback?.id || `stream:${renderType}:${cycleKey}:${year || 0}`,
    review_id: fallback?.review_id || reviewId,
    user_id: fallback?.user_id || '',
    render_type: renderType,
    cycle_key: cycleKey,
    year,
    status: 'processing',
    progress_message: fallback?.progress_message || 'DeepSeek 正在生成内容',
    facts: fallback?.facts || null,
    result: { ...asRecord(fallback?.result) },
    points_cost: fallback?.points_cost || 0,
    error_message: null,
    retry_count: fallback?.retry_count || 0,
    last_attempt_at: fallback?.last_attempt_at || null,
    next_retry_available_at: null,
    is_retryable: false,
    created_at: fallback?.created_at || now,
    updated_at: now,
  };
}

function setLuckStreamDraft(targetKey: string, render: FourPillarsLuckRenderRecord): void {
  luckStreamDrafts.value = {
    ...luckStreamDrafts.value,
    [targetKey]: {
      render,
      result: { ...asRecord(render.result) },
      progress_message: render.progress_message,
    },
  };
}

function appendLuckStreamDelta(targetKey: string, field: string, text: string): void {
  const draft = luckStreamDrafts.value[targetKey];
  if (!draft || !field) {
    return;
  }
  luckStreamDrafts.value = {
    ...luckStreamDrafts.value,
    [targetKey]: {
      ...draft,
      result: {
        ...draft.result,
        [field]: text,
      },
    },
  };
}

function updateLuckStreamStatus(targetKey: string, message: string): void {
  const draft = luckStreamDrafts.value[targetKey];
  if (!draft || !message) {
    return;
  }
  luckStreamDrafts.value = {
    ...luckStreamDrafts.value,
    [targetKey]: {
      ...draft,
      progress_message: message,
    },
  };
}

function clearLuckStreamDraft(targetKey: string): void {
  if (!luckStreamDrafts.value[targetKey]) {
    return;
  }
  const nextDrafts = { ...luckStreamDrafts.value };
  delete nextDrafts[targetKey];
  luckStreamDrafts.value = nextDrafts;
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

function hourBranchLabel(hour: number | string): string {
  const value = Number(hour);
  if (value === 23 || value === 0) return '子时';
  if (value === 1 || value === 2) return '丑时';
  if (value === 3 || value === 4) return '寅时';
  if (value === 5 || value === 6) return '卯时';
  if (value === 7 || value === 8) return '辰时';
  if (value === 9 || value === 10) return '巳时';
  if (value === 11 || value === 12) return '午时';
  if (value === 13 || value === 14) return '未时';
  if (value === 15 || value === 16) return '申时';
  if (value === 17 || value === 18) return '酉时';
  if (value === 19 || value === 20) return '戌时';
  return '亥时';
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
  clearWaitingTimers();
  waitingStep.value = 1;
  waitingStepProgress.value = waitingSteps.map(() => 0);
  waitingPoemIndex.value = 0;
  waitingAnimationComplete.value = false;
  baseReviewCoreReady.value = false;
  pendingCompletedReview.value = null;
  pendingCompletedReviewShouldToast.value = false;
  waitingStartedAt = 0;
}

function clearSummaryStreamDraft(): void {
  summaryStreamDraft.value = null;
}

function guardBaseReviewReadyForDeepSeekAction(actionLabel: string): boolean {
  if (!baseReviewGenerating.value) {
    return true;
  }
  showToast(`综合评述仍在生成中，完成后再${actionLabel}。`, 3200);
  return false;
}

function clearWaitingTimers(): void {
  if (waitingAnimationTimer) {
    window.clearInterval(waitingAnimationTimer);
    waitingAnimationTimer = null;
  }
  if (waitingPoemTimer) {
    window.clearInterval(waitingPoemTimer);
    waitingPoemTimer = null;
  }
}

function startWaitingAnimation(): void {
  resetWaitingAnimation();
  waitingStartedAt = Date.now();
  waitingAnimationTimer = window.setInterval(updateWaitingAnimation, 80);
  waitingPoemTimer = window.setInterval(() => {
    if (!disposed && viewState.value === 'waiting') {
      waitingPoemIndex.value = (waitingPoemIndex.value + 1) % waitingPoemLines.length;
    }
  }, 1000);
  updateWaitingAnimation();
}

function updateWaitingAnimation(): void {
  if (!waitingStartedAt || viewState.value !== 'waiting') {
    return;
  }

  const elapsed = Date.now() - waitingStartedAt;
  let passedDuration = 0;
  let animationDone = true;
  const nextProgress = waitingSteps.map((step, index) => {
    const stepElapsed = elapsed - passedDuration;
    passedDuration += step.durationMs;
    if (stepElapsed <= 0) {
      animationDone = false;
      return 0;
    }
    if (stepElapsed >= step.durationMs) {
      return 100;
    }
    animationDone = false;
    const maxProgress = index === waitingSteps.length - 1 ? 95 : 100;
    return Math.min(maxProgress, Math.max(1, Math.round((stepElapsed / step.durationMs) * maxProgress)));
  });

  waitingStepProgress.value = nextProgress;
  const activeIndex = nextProgress.findIndex((progress) => progress < 100);
  waitingStep.value = activeIndex === -1 ? waitingSteps.length : activeIndex + 1;

  if (animationDone) {
    completeWaitingAnimation();
  }
}

function markBaseReviewCoreReady(): void {
  baseReviewCoreReady.value = true;
  if (!summaryStreamDraft.value) {
    summaryStreamDraft.value = { is_streaming: true };
  }
  tryRevealWaitingResult();
}

function applyCoreSummaryDelta(data: FourPillarsCoreStreamDeltaData): void {
  if (data.section !== 'four_pillars_summary') {
    return;
  }
  summaryStreamDraft.value = {
    ...(summaryStreamDraft.value || { is_streaming: true }),
    [data.field]: data.text,
    is_streaming: true,
  };
}

function completeWaitingAnimation(): void {
  if (disposed || viewState.value !== 'waiting') {
    return;
  }
  waitingAnimationComplete.value = true;
  if (waitingAnimationTimer) {
    window.clearInterval(waitingAnimationTimer);
    waitingAnimationTimer = null;
  }
  tryRevealWaitingResult();
}

function tryRevealWaitingResult(): void {
  if (viewState.value !== 'waiting' || !waitingAnimationComplete.value) {
    return;
  }

  if (pendingCompletedReview.value) {
    const review = pendingCompletedReview.value;
    const shouldToast = pendingCompletedReviewShouldToast.value;
    pendingCompletedReview.value = null;
    pendingCompletedReviewShouldToast.value = false;
    applyCompletedReviewState(review, { showToastOnComplete: shouldToast });
    return;
  }

  if (!baseReviewCoreReady.value || !currentReview.value) {
    return;
  }

  revealStreamingReviewShell();
}

function revealStreamingReviewShell(): void {
  clearWaitingTimers();
  waitingStep.value = waitingSteps.length;
  waitingStepProgress.value = waitingSteps.map(() => 100);
  if (currentReview.value) {
    applyFormFromReview(currentReview.value);
    currentProgressStage.value = currentReview.value.progress_stage;
    currentProgressMessage.value = currentReview.value.progress_message || currentProgressMessage.value;
  }
  errorType.value = 'none';
  errorDetail.value = '';
  viewState.value = 'result';
}

function applyOrDeferCompletedReviewState(review: FourPillarsReviewRecord, options: { showToastOnComplete?: boolean } = {}): void {
  if (viewState.value === 'waiting' && !waitingAnimationComplete.value) {
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

function applyCompletedReviewState(review: FourPillarsReviewRecord, options: { showToastOnComplete?: boolean } = {}): void {
  clearWaitingTimers();
  clearSummaryStreamDraft();
  waitingStep.value = waitingSteps.length;
  waitingStepProgress.value = waitingSteps.map(() => 100);
  applyFormFromReview(review);
  currentProgressStage.value = review.progress_stage;
  currentProgressMessage.value = review.progress_message || '';
  errorType.value = 'none';
  errorDetail.value = '';
  viewState.value = 'result';
  reconcilePendingAspects(review);
  if (options.showToastOnComplete) {
    showToast('四柱评测完成，可查看命盘和专项内容。');
  }
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
  dateTimeSelectionSource.value = 'wheel';
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
    document.querySelectorAll<HTMLElement>('.drawer-sheet .wheel-option.is-selected, .drawer-sheet .picker-wheel-item.text-brand-primary').forEach((item) => {
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
    const options = Array.from(column.querySelectorAll<HTMLElement>('.wheel-option, .picker-wheel-item'));
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
  const options = Array.from(column.querySelectorAll<HTMLElement>('.wheel-option, .picker-wheel-item'));
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
  if (scope === 'solar' || scope === 'lunar') {
    dateTimeSelectionSource.value = 'wheel';
  }
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
  dateTimeSelectionSource.value = 'wheel';
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
  dateTimeSelectionSource.value = 'wheel';
  lunarInput.value = { ...lunarInput.value, [part]: value };
  scrollSelectedWheelOptions();
}

function clampNumber(value: string | number, min: number, max: number, fallback: number): number {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return fallback;
  return Math.min(max, Math.max(min, Math.trunc(numericValue)));
}

function handleSolarManualInput(part: 'year' | 'month' | 'day' | 'hour' | 'minute', event: Event): void {
  dateTimeSelectionSource.value = 'manual';
  const rawValue = String((event.target as HTMLInputElement | null)?.value || '');
  const fallbackMap = {
    year: Number(birthYear.value || 1989),
    month: Number(birthMonth.value || 1),
    day: Number(birthDay.value || 1),
    hour: solarHour.value,
    minute: solarMinute.value,
  };
  const ranges: Record<typeof part, [number, number]> = {
    year: [1801, 2099],
    month: [1, 12],
    day: [1, 31],
    hour: [0, 23],
    minute: [0, 59],
  };
  const [min, max] = ranges[part];
  const nextValue = clampNumber(rawValue, min, max, fallbackMap[part]);
  setSolarPart(part, nextValue);
  dateTimeSelectionSource.value = 'manual';
}

function handleLunarManualInput(part: 'year' | 'month' | 'day' | 'hour' | 'minute', event: Event): void {
  dateTimeSelectionSource.value = 'manual';
  const rawValue = String((event.target as HTMLInputElement | null)?.value || '');
  const fallback = Number(lunarInput.value[part]) || 0;
  const ranges: Record<typeof part, [number, number]> = {
    year: [1801, 2099],
    month: [1, 12],
    day: [1, 31],
    hour: [0, 23],
    minute: [0, 59],
  };
  const [min, max] = ranges[part];
  setLunarPart(part, clampNumber(rawValue, min, max, fallback));
  dateTimeSelectionSource.value = 'manual';
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
  if (dateTimeSelectionSource.value === 'wheel') {
    syncVisibleDateWheelSelection();
  }
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
  pendingAspectKeys.value = [];
  aspectStreamDrafts.value = {};
  luckStreamDrafts.value = {};
  clearSummaryStreamDraft();
  baseReviewStreamActiveId.value = null;
  aspectUnlockAbortController?.abort();
  aspectUnlockAbortController = null;
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
    applyOrDeferCompletedReviewState(review);
    return;
  }
  if (review.status === 'failed') {
    setError('review_failed', review.error_message || review.progress_message || '四柱评测生成失败');
    return;
  }
  if (viewState.value !== 'result') {
    viewState.value = 'waiting';
  }
  if (baseReviewStreamActiveId.value === review.id) {
    return;
  }
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
  clearSummaryStreamDraft();
  luckStreamDrafts.value = {};
  baseReviewStreamActiveId.value = null;
  viewState.value = 'waiting';
  startWaitingAnimation();
  currentProgressStage.value = 'queued';
  currentProgressMessage.value = '四柱评测任务已创建，等待开始';
  try {
    await bootstrapApp();
    await submitFourPillarsReviewStream(
      {
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
      },
      {
        onCreated: (data) => {
          baseReviewStreamActiveId.value = data.review.id;
          currentProgressStage.value = data.review.progress_stage;
          currentProgressMessage.value = data.review.progress_message || '';
          tryRevealWaitingResult();
        },
        onFactsReady: (data) => {
          baseReviewStreamActiveId.value = data.review.id;
          currentProgressStage.value = data.review.progress_stage;
          currentProgressMessage.value = data.review.progress_message || '';
          tryRevealWaitingResult();
        },
        onCoreStatus: (data) => {
          currentProgressMessage.value = data.message || currentProgressMessage.value;
          markBaseReviewCoreReady();
        },
        onCoreDelta: (data) => {
          applyCoreSummaryDelta(data);
          markBaseReviewCoreReady();
        },
        onSectionComplete: (data) => {
          if (data.section !== 'four_pillars_summary') {
            return;
          }
          markBaseReviewCoreReady();
          const payload = data.payload as Partial<SummaryStreamDraft>;
          summaryStreamDraft.value = {
            ...(summaryStreamDraft.value || { is_streaming: false }),
            title: typeof payload.title === 'string' ? payload.title : summaryStreamDraft.value?.title,
            comprehensive_text: typeof payload.comprehensive_text === 'string' ? payload.comprehensive_text : summaryStreamDraft.value?.comprehensive_text,
            overview: typeof payload.overview === 'string' ? payload.overview : summaryStreamDraft.value?.overview,
            risk: typeof payload.risk === 'string' ? payload.risk : summaryStreamDraft.value?.risk,
            usage_guidance: typeof payload.usage_guidance === 'string' ? payload.usage_guidance : summaryStreamDraft.value?.usage_guidance,
            life_risk_windows: Array.isArray(payload.life_risk_windows) ? payload.life_risk_windows : summaryStreamDraft.value?.life_risk_windows,
            time_highlights: Array.isArray(payload.time_highlights) ? payload.time_highlights : summaryStreamDraft.value?.time_highlights,
            is_streaming: false,
          };
          tryRevealWaitingResult();
        },
        onComplete: (data) => {
          baseReviewStreamActiveId.value = null;
          baseReviewCoreReady.value = true;
          clearSummaryStreamDraft();
          if (!disposed) {
            applyOrDeferCompletedReviewState(data.review, { showToastOnComplete: true });
          }
        },
        onError: () => {
          baseReviewStreamActiveId.value = null;
        },
      },
    );
  } catch (error) {
    baseReviewStreamActiveId.value = null;
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
  if (!guardBaseReviewReadyForDeepSeekAction('解锁专项')) {
    return;
  }
  await unlockSelectedAspect(aspect);
}

async function unlockSelectedAspect(aspect: DisplayAspect): Promise<void> {
  const review = currentReview.value;
  if (!review || aspect.is_unlocked) {
    return;
  }
  if (!guardBaseReviewReadyForDeepSeekAction('解锁专项')) {
    return;
  }
  if (pendingAspectKeys.value.includes(aspect.aspect_key) || aspect.is_streaming) {
    showToast(`「${aspect.short_title || aspect.title}」仍在生成中，页面会自动同步。`, 3000);
    return;
  }
  if (unlockingAspectKey.value) {
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
  aspectUnlockAbortController?.abort();
  aspectUnlockAbortController = new AbortController();
  aspectStreamDrafts.value = {
    ...aspectStreamDrafts.value,
    [aspect.aspect_key]: {
      title: aspect.title,
      risk: '',
      content: '',
      is_streaming: true,
    },
  };
  try {
    const result = await streamUnlockFourPillarsAspect(review.id, aspect.aspect_key, {
      signal: aspectUnlockAbortController.signal,
      onStatus: () => {
        unlockWaitingAspectKey.value = aspect.aspect_key;
      },
      onDelta: (data) => {
        applyAspectStreamDelta(aspect.aspect_key, data.field, data.text);
      },
    });
    if (result.review) {
      syncViewFromReview(result.review);
    }
    clearAspectStreamDraft(aspect.aspect_key);
    showToast(`已解锁「${aspect.short_title || aspect.title}」。`);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return;
    }
    if (error instanceof ApiError && error.status === 402) {
      clearAspectStreamDraft(aspect.aspect_key);
      setError('unlock_points_insufficient');
      return;
    }
    if (isPendingAspectGenerationError(error)) {
      addPendingAspectKey(aspect.aspect_key);
      showToast(`「${aspect.short_title || aspect.title}」仍在生成中，页面会自动同步。`, 3200);
      startAspectPendingSync(review.id, aspect);
      return;
    }
    clearAspectStreamDraft(aspect.aspect_key);
    handleReviewSyncError(error);
  } finally {
    unlockingAspectKey.value = null;
    unlockWaitingAspectKey.value = null;
    aspectUnlockAbortController = null;
  }
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
  if (!guardBaseReviewReadyForDeepSeekAction('生成大运综述')) {
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
  setLuckStreamDraft(targetKey, createPendingLuckRender(review.id, 'dayun', cycle.cycle_key, null, cycle.render));
  try {
    await streamGenerateFourPillarsLuckCycle(review.id, cycle.cycle_key, {
      onRender: (data) => {
        setLuckStreamDraft(targetKey, data.render);
      },
      onStatus: (data) => {
        updateLuckStreamStatus(targetKey, data.message);
      },
      onDelta: (data) => {
        appendLuckStreamDelta(targetKey, String(data.field || ''), String(data.text || ''));
      },
    });
    showToast('大运综评已生成。');
  } catch (error) {
    await refreshFourPillarsLuckAnalysis(review.id).catch(() => null);
    showToast(humanizeError(error) || '大运综评生成失败，可稍后重试。', 3600);
  } finally {
    clearLuckStreamDraft(targetKey);
    stopGeneratingLuckTarget(targetKey);
  }
}

async function handleGenerateYear(cycle: FourPillarsLuckCycle | null, yearItem: FourPillarsLuckYearItem | null): Promise<void> {
  const review = currentReview.value;
  if (!review || !cycle || !yearItem || yearItem.render_status === 'completed') {
    return;
  }
  if (!guardBaseReviewReadyForDeepSeekAction('生成流年评测')) {
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
  setLuckStreamDraft(targetKey, createPendingLuckRender(review.id, 'liunian', cycle.cycle_key, yearItem.year, yearItem.render));
  try {
    await streamGenerateFourPillarsLuckYear(review.id, cycle.cycle_key, yearItem.year, {
      onRender: (data) => {
        setLuckStreamDraft(targetKey, data.render);
      },
      onStatus: (data) => {
        updateLuckStreamStatus(targetKey, data.message);
      },
      onDelta: (data) => {
        appendLuckStreamDelta(targetKey, String(data.field || ''), String(data.text || ''));
      },
    });
    showToast(`${yearItem.year} 流年评测已生成。`);
  } catch (error) {
    await refreshFourPillarsLuckAnalysis(review.id).catch(() => null);
    showToast(humanizeError(error) || '流年评测生成失败，可稍后重试。', 3600);
  } finally {
    clearLuckStreamDraft(targetKey);
    stopGeneratingLuckTarget(targetKey);
  }
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

function luckRenderHasText(render: FourPillarsLuckRenderRecord | null | undefined): boolean {
  return Object.values(asRecord(render?.result)).some((value) => String(value || '').trim().length > 0);
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
      if (error.detail === 'invalid_birth_datetime') {
        setError('birth_datetime');
      } else {
        setError('request_failed', humanizeError(error));
      }
      return;
    }
    if (error.status === 409) {
      if (error.detail === 'aspect_generation_failed' || error.detail === 'llm_insufficient_balance') {
        setError('review_failed', humanizeError(error));
        return;
      }
      if (
        error.detail === 'review_not_ready_for_unlock'
        || error.detail === 'aspect_generation_in_progress'
        || error.detail === 'aspect_generation_incomplete'
        || error.detail === 'aspect_not_ready'
      ) {
        setError('review_timeout', humanizeError(error));
        return;
      }
      setError('request_failed', humanizeError(error));
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
          class="h-9 rounded-lg bg-white border border-gray-100 px-3 text-brand-secondary font-sans text-[12px] font-bold flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
          @click="handleHeaderBackAction"
        >
          <ArrowLeft :size="14" class="text-brand-ink-strong" />
          <span>{{ viewState === 'result' ? '重新评测' : '返回首页' }}</span>
        </button>
        <div class="text-center">
          <h1 class="font-serif text-[18px] font-bold text-brand-ink-strong leading-none">四柱八字评测</h1>
          <p class="font-sans text-[11px] text-brand-secondary mt-1">公历生日时辰 · 默认北京时间</p>
        </div>
        <button class="w-9 h-9 rounded-lg bg-white border border-gray-100 flex items-center justify-center shadow-sm cursor-pointer" @click="refreshActiveReview">
          <RefreshCw :size="17" class="text-brand-secondary" />
        </button>
      </div>
    </header>

    <main class="max-w-md mx-auto px-margin-mobile pt-4">
      <section v-if="viewState === 'input'" class="space-y-4">
        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="relative flex h-2.5 w-2.5 shrink-0">
                <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-primary/50"></span>
                <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-primary"></span>
              </span>
              <h2 class="font-serif text-[16px] font-black text-brand-ink-strong leading-snug">四柱八字先天命理排盘</h2>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-brand-primary/10 text-brand-primary-strong text-[11px] font-bold flex items-center h-6">
              {{ effectiveBasePoints }} 积分
            </span>
          </div>
        </section>

        <div class="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm space-y-4">
          <div class="space-y-1.5 text-left">
            <label class="text-[11px] font-bold text-brand-secondary tracking-wide flex items-center gap-1">
              <User :size="13" />
              <span>命造姓名</span>
            </label>
            <input
              v-model="profileName"
              maxlength="64"
              placeholder="请输入姓名（可选）"
              class="w-full bg-brand-paper hover:bg-white text-brand-ink-strong focus:bg-white font-sans text-[14px] font-semibold p-3.5 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all placeholder-gray-400"
            />
          </div>

          <div class="grid grid-cols-2 gap-3 text-left">
            <div class="space-y-1.5">
              <label class="text-[11px] font-bold text-brand-secondary tracking-wide">性别</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-100">
                <button
                  type="button"
                  class="py-2 text-[12px] font-bold rounded-lg cursor-pointer transition-all"
                  :class="gender === 'male' ? 'bg-white text-brand-primary shadow-sm' : 'bg-transparent text-brand-secondary hover:text-brand-ink-strong'"
                  @click="gender = 'male'"
                >
                  男命
                </button>
                <button
                  type="button"
                  class="py-2 text-[12px] font-bold rounded-lg cursor-pointer transition-all"
                  :class="gender === 'female' ? 'bg-white text-brand-primary shadow-sm' : 'bg-transparent text-brand-secondary hover:text-brand-ink-strong'"
                  @click="gender = 'female'"
                >
                  女命
                </button>
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[11px] font-bold text-brand-secondary tracking-wide">历法模式</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-100">
                <button
                  v-for="mode in ['solar', 'lunar']"
                  :key="mode"
                  type="button"
                  class="py-2 text-[12px] font-bold rounded-lg cursor-pointer transition-all"
                  :class="inputMode === mode ? 'bg-white text-brand-primary shadow-sm' : 'bg-transparent text-brand-secondary hover:text-brand-ink-strong'"
                  @click="selectInputMode(mode as InputMode)"
                >
                  {{ mode === 'solar' ? '公历' : '农历' }}
                </button>
              </div>
            </div>
          </div>

          <div class="space-y-1.5 text-left">
            <label class="text-[11px] font-bold text-brand-secondary tracking-wide flex items-center gap-1">
              <CalendarDays :size="13" />
              <span>出生生辰 (公历/农历)</span>
            </label>
            <div
              class="w-full bg-brand-paper hover:bg-white active:bg-gray-50 text-brand-ink-strong font-sans text-[14px] font-bold p-3.5 rounded-xl border border-gray-100 flex items-center justify-between cursor-pointer transition-all shadow-inner select-none"
              @click="openDateDrawer(inputMode)"
            >
              <div class="flex flex-col text-left leading-tight min-w-0">
                <span class="text-[13px] font-bold text-brand-ink-strong truncate">
                  {{ inputMode === 'solar' ? '公历' : '农历' }}：{{ inputMode === 'solar' ? `${birthYear || '1989'}年${birthMonth || '5'}月${birthDay || '22'}日` : `${lunarInput.year}年${lunarInput.month}月${lunarInput.day}日` }}
                </span>
                <span class="text-[11px] font-semibold text-brand-secondary mt-1 truncate">
                  时间：{{ inputMode === 'solar' ? (birthTime || '08:55') : `${twoDigit(lunarInput.hour)}:${twoDigit(lunarInput.minute)}` }} ({{ hourBranchLabel(inputMode === 'solar' ? solarHour : lunarInput.hour) }})
                </span>
              </div>
              <ChevronRight :size="16" class="text-slate-400 shrink-0" />
            </div>
          </div>

          <div class="space-y-1.5 text-left">
            <label class="text-[11px] font-bold text-brand-secondary tracking-wide flex items-center gap-1">
              <MapPin :size="13" />
              <span>出生地区 (真太阳时校准)</span>
            </label>
            <div
              class="w-full bg-brand-paper hover:bg-white active:bg-gray-50 text-brand-ink-strong font-sans text-[14px] font-bold p-3.5 rounded-xl border border-gray-100 flex items-center justify-between cursor-pointer transition-all shadow-inner select-none"
              @click="openLocationDrawer"
            >
              <div class="flex flex-col text-left leading-tight min-w-0">
                <span class="text-[13px] font-bold text-brand-ink-strong truncate">
                  {{ locationSummary }}
                </span>
                <span class="text-[11px] font-bold text-brand-secondary mt-1 flex items-center gap-1 min-w-0">
                  <Sparkles :size="10" class="text-brand-primary shrink-0 animate-pulse" />
                  <span class="truncate">真太阳时 {{ trueSolarSummary }}</span>
                </span>
              </div>
              <ChevronRight :size="16" class="text-slate-400 shrink-0" />
            </div>
          </div>

          <button
            type="button"
            class="w-full h-12 rounded-xl bg-brand-primary hover:bg-brand-primary-strong text-white font-sans text-[14px] font-bold shadow-md disabled:opacity-60 disabled:shadow-none transition-all active:scale-[0.985] flex items-center justify-center gap-1.5"
            :disabled="state.booting || !moduleEnabled"
            @click="void handleSubmit()"
          >
            <Sparkles :size="15" fill="currentColor" />
            <span v-if="state.booting">正在连接本地 API...</span>
            <span v-else-if="moduleEnabled">立即扣除 <span class="font-sans">{{ effectiveBasePoints }}</span> 积分，深度智能测算</span>
            <span v-else>功能暂未开放</span>
          </button>
        </div>
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
            <span class="font-sans font-black text-[12px]">命盘已生成</span>
            <span class="font-sans text-[8px] opacity-85 mt-0.5">结构</span>
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
            <div class="flex items-center justify-between gap-2 pb-2">
              <div class="flex items-center gap-1.5">
                <Sparkles :size="14" class="text-[#2563EB]" />
                <h3 class="font-serif text-[14px] font-bold text-[#1D4ED8]">综合评述</h3>
              </div>
              <span v-if="hasSummaryV2" class="font-sans text-[10px] font-bold text-[#1D4ED8] bg-[#EAF1FF] rounded-full px-2 py-0.5">命盘摘要</span>
            </div>
            <p class="font-serif text-[15px] font-bold text-brand-ink-strong mt-2 leading-snug">{{ summary?.title || '四柱总评生成中' }}</p>
            <p class="font-sans text-[13px] text-brand-ink leading-relaxed mt-2 whitespace-pre-line">
              {{ summaryNarrative || '综合评述生成中。' }}
            </p>

            <div v-if="summaryTimeHighlights.length" class="mt-3 pt-3 border-t border-[#E5EDF8]">
              <div class="flex items-center gap-1.5">
                <CalendarDays :size="13" class="text-[#2563EB]" />
                <p class="font-sans text-[12px] font-black text-brand-ink-strong">时间重点</p>
              </div>
              <div class="mt-2 space-y-1.5">
                <div
                  v-for="item in summaryTimeHighlights"
                  :key="`${item.year}-${item.age}-${item.title}`"
                  class="grid grid-cols-[auto_1fr] gap-2 rounded-lg bg-[#F8FAFF] border border-[#E5EDF8] px-2 py-2"
                >
                  <div class="min-w-[64px] rounded-md bg-[#EAF1FF] text-[#1D4ED8] font-sans font-black text-[10px] px-2 py-1 text-center leading-tight self-start">
                    <span class="block">{{ item.year || item.age || '阶段' }}</span>
                    <span v-if="item.year && item.age" class="block font-medium text-[9px] mt-0.5">{{ item.age }}</span>
                  </div>
                  <div class="min-w-0">
                    <p class="font-sans text-[12px] font-bold text-brand-ink-strong leading-snug">{{ item.title || '阶段提醒' }}</p>
                    <p v-if="item.content" class="font-sans text-[11.5px] text-brand-ink leading-relaxed mt-0.5">{{ item.content }}</p>
                    <p v-if="item.trigger" class="font-sans text-[10.5px] text-brand-secondary leading-relaxed mt-0.5">依据：{{ item.trigger }}</p>
                  </div>
                </div>
              </div>
            </div>
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
              <div class="flex items-center gap-1.5">
                <Sparkles :size="14" class="text-[#2563EB]" />
                <h3 class="font-serif text-[14px] font-bold text-[#1D4ED8]">十二专项</h3>
              </div>
              <span class="font-sans text-[11px] text-brand-secondary">{{ effectiveAspectUnlockPoints }} 积分/项</span>
            </div>
            <div class="grid grid-cols-3 sm:grid-cols-4 gap-1.5">
              <button
                v-for="(aspect, index) in reviewAspects"
                :key="aspect.aspect_key"
                class="h-[58px] rounded-lg border px-1.5 text-center transition-colors flex flex-col items-center justify-center gap-1"
                :class="index === activeAspect ? 'bg-[#EAF1FF] text-[#1D4ED8] border-[#2563EB]' : 'bg-[#F8FAFF] border-[#D8E3F5] text-brand-ink-strong'"
                @click="void handleAspectClick(aspect, index)"
              >
                <div class="flex items-center justify-center gap-1 min-w-0 max-w-full">
                  <span class="w-5 h-5 rounded-full inline-flex items-center justify-center shrink-0" :class="aspect.tint">
                    <component :is="aspect.icon" :size="12" />
                  </span>
                  <span class="font-sans text-[11px] font-bold leading-none truncate">{{ aspect.short_title || aspect.title }}</span>
                </div>
                <div class="font-sans text-[9px] flex items-center gap-0.5" :class="index === activeAspect ? 'text-[#2563EB]' : 'text-brand-secondary'">
                  <RefreshCw v-if="aspect.is_streaming" :size="12" class="animate-spin" />
                  <Check v-else-if="aspect.is_unlocked" :size="12" />
                  <Lock v-else :size="12" />
                  <span>{{ aspect.is_streaming ? '生成中' : (aspect.is_unlocked ? '已生成' : `${aspect.unlock_points || effectiveAspectUnlockPoints}点`) }}</span>
                </div>
              </button>
            </div>

            <div v-if="selectedAspect" class="mt-2 rounded-lg bg-[#F8FAFF] border border-[#D8E3F5] p-3">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="font-sans text-[11px] text-brand-secondary font-bold">{{ selectedAspect.short_title || selectedAspect.title }}</p>
                  <h4 class="font-serif text-[15px] font-bold text-brand-ink-strong mt-1">{{ selectedAspect.title }}</h4>
                </div>
                <button
                  v-if="!selectedAspect.is_unlocked || selectedAspect.is_streaming"
                  class="h-9 px-3 rounded-lg bg-brand-primary text-white font-sans text-[12px] font-bold inline-flex items-center gap-1 disabled:opacity-60"
                  :disabled="selectedAspectPending || baseReviewGenerating"
                  @click="void unlockSelectedAspect(selectedAspect)"
                >
                  <RefreshCw v-if="selectedAspectPending || baseReviewGenerating" :size="14" class="animate-spin" />
                  <UnlockKeyhole v-else :size="14" />
                  {{ baseReviewGenerating ? '综评中' : (selectedAspectPending ? '生成中' : '解锁') }}
                </button>
              </div>
              <div v-if="hasAspectDetail(selectedAspect)" class="mt-3 space-y-2">
                <p v-if="selectedAspect.risk" class="font-sans text-[12px] text-red-600 leading-relaxed bg-white/70 rounded-lg border border-red-100 px-2.5 py-2">
                  {{ selectedAspect.risk }}
                </p>
                <p class="font-sans text-[13px] text-brand-ink leading-relaxed whitespace-pre-line">
                  {{ selectedAspect.content || (selectedAspectPending ? '正在生成专项内容。' : '') }}
                </p>
              </div>
              <p v-else class="font-sans text-[13px] text-brand-secondary leading-relaxed mt-3">
                {{ selectedAspectPending ? '专项内容正在实时生成。' : '解锁后展示完整专项判断、风险提示和现实对照。' }}
              </p>
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
                :disabled="baseReviewGenerating || !luckGenerationEnabled || isGeneratingLuckTarget(`cycle:${selectedLuckCycle.cycle_key}`) || selectedLuckCycle.render_status === 'processing'"
                @click="void handleGenerateCycle(selectedLuckCycle)"
              >
                <RefreshCw v-if="baseReviewGenerating || isGeneratingLuckTarget(`cycle:${selectedLuckCycle.cycle_key}`) || selectedLuckCycle.render_status === 'processing'" :size="14" class="animate-spin" />
                <Sparkles v-else :size="14" />
                {{ baseReviewGenerating ? '综评中' : (selectedLuckCycle.render_status === 'completed' ? '重新查看' : selectedLuckCycle.render_status === 'failed' ? '重试' : '生成综评') }}
              </button>
            </div>
            <div v-if="luckRenderHasText(selectedLuckCycle.render)" class="mt-3 space-y-2">
              <p class="font-serif text-[15px] font-bold text-brand-ink-strong leading-snug">{{ luckRenderText(selectedLuckCycle.render, 'title') || luckRenderText(selectedLuckCycle.render, 'verdict') }}</p>
              <div v-if="luckRenderText(selectedLuckCycle.render, 'core_theme') || luckRenderText(selectedLuckCycle.render, 'verdict')" class="border-l-2 border-slate-300 pl-2">
                <p class="font-sans text-[10px] font-black text-slate-500 leading-none">阶段主轴</p>
                <p class="font-sans text-[12px] text-brand-ink leading-relaxed mt-1">{{ luckRenderText(selectedLuckCycle.render, 'core_theme') || luckRenderText(selectedLuckCycle.render, 'verdict') }}</p>
              </div>
              <div v-if="luckRenderText(selectedLuckCycle.render, 'opportunities')" class="border-l-2 border-emerald-400 bg-emerald-50/70 rounded-r-lg px-2 py-1.5">
                <p class="font-sans text-[10px] font-black text-emerald-700 leading-none">机会与助力</p>
                <p class="font-sans text-[12px] text-emerald-800 leading-relaxed mt-1">{{ luckRenderText(selectedLuckCycle.render, 'opportunities') }}</p>
              </div>
              <div v-if="luckRenderText(selectedLuckCycle.render, 'risks') || luckRenderText(selectedLuckCycle.render, 'risk_warning')" class="border-l-2 border-rose-400 bg-rose-50/70 rounded-r-lg px-2 py-1.5">
                <p class="font-sans text-[10px] font-black text-rose-700 leading-none">风险与消耗</p>
                <p class="font-sans text-[12px] text-rose-700 leading-relaxed mt-1">{{ luckRenderText(selectedLuckCycle.render, 'risks') || luckRenderText(selectedLuckCycle.render, 'risk_warning') }}</p>
              </div>
              <div v-if="luckRenderText(selectedLuckCycle.render, 'action_guidance')" class="border-l-2 border-blue-300 pl-2">
                <p class="font-sans text-[10px] font-black text-blue-600 leading-none">行动建议</p>
                <p class="font-sans text-[12px] text-brand-secondary leading-relaxed mt-1">{{ luckRenderText(selectedLuckCycle.render, 'action_guidance') }}</p>
              </div>
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
                  :disabled="baseReviewGenerating || !luckGenerationEnabled || isGeneratingLuckTarget(`year:${selectedLuckCycle.cycle_key}:${selectedLuckYearItem.year}`) || selectedLuckYearItem.render_status === 'processing'"
                  @click="void handleGenerateYear(selectedLuckCycle, selectedLuckYearItem)"
                >
                  <RefreshCw v-if="baseReviewGenerating || isGeneratingLuckTarget(`year:${selectedLuckCycle.cycle_key}:${selectedLuckYearItem.year}`) || selectedLuckYearItem.render_status === 'processing'" :size="14" class="animate-spin" />
                  <CalendarDays v-else :size="14" />
                  {{ baseReviewGenerating ? '综评中' : (selectedLuckYearItem.render_status === 'completed' ? '重新查看' : selectedLuckYearItem.render_status === 'failed' ? '重试' : '生成') }}
                </button>
              </div>
              <div v-if="luckRenderHasText(selectedLuckYearItem.render)" class="mt-3 space-y-2">
                <p class="font-serif text-[15px] font-bold text-brand-ink-strong leading-snug">{{ luckRenderText(selectedLuckYearItem.render, 'title') || luckRenderText(selectedLuckYearItem.render, 'verdict') }}</p>
                <div v-if="luckRenderText(selectedLuckYearItem.render, 'year_focus') || luckRenderText(selectedLuckYearItem.render, 'work_wealth')" class="border-l-2 border-slate-300 pl-2">
                  <p class="font-sans text-[10px] font-black text-slate-500 leading-none">年度主轴</p>
                  <p class="font-sans text-[12px] text-brand-ink leading-relaxed mt-1">{{ luckRenderText(selectedLuckYearItem.render, 'year_focus') || luckRenderText(selectedLuckYearItem.render, 'work_wealth') }}</p>
                </div>
                <div v-if="luckRenderText(selectedLuckYearItem.render, 'opportunities')" class="border-l-2 border-emerald-400 bg-emerald-50/70 rounded-r-lg px-2 py-1.5">
                  <p class="font-sans text-[10px] font-black text-emerald-700 leading-none">机会与助力</p>
                  <p class="font-sans text-[12px] text-emerald-800 leading-relaxed mt-1">{{ luckRenderText(selectedLuckYearItem.render, 'opportunities') }}</p>
                </div>
                <div v-if="luckRenderText(selectedLuckYearItem.render, 'risks')" class="border-l-2 border-rose-400 bg-rose-50/70 rounded-r-lg px-2 py-1.5">
                  <p class="font-sans text-[10px] font-black text-rose-700 leading-none">风险与消耗</p>
                  <p class="font-sans text-[12px] text-rose-700 leading-relaxed mt-1">{{ luckRenderText(selectedLuckYearItem.render, 'risks') }}</p>
                </div>
                <div v-if="luckRenderText(selectedLuckYearItem.render, 'action_guidance') || luckRenderText(selectedLuckYearItem.render, 'health_love')" class="border-l-2 border-blue-300 pl-2">
                  <p class="font-sans text-[10px] font-black text-blue-600 leading-none">行动建议</p>
                  <p class="font-sans text-[12px] text-brand-secondary leading-relaxed mt-1">{{ luckRenderText(selectedLuckYearItem.render, 'action_guidance') || luckRenderText(selectedLuckYearItem.render, 'health_love') }}</p>
                </div>
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
      <div v-if="drawerKind" class="fixed inset-x-0 top-0 bottom-[96px] z-40 bg-brand-ink-strong/60 backdrop-blur-sm flex items-end justify-center" @click.self="closeDrawer">
        <div class="drawer-sheet w-full max-w-md mx-auto rounded-t-3xl bg-white shadow-2xl flex flex-col pb-8 border-t border-gray-100 max-h-[75vh] overflow-hidden">
          <div class="w-12 h-1 bg-slate-200 rounded-full mx-auto my-3 shrink-0"></div>

          <div v-if="drawerKind === 'datetime'" class="flex flex-col min-h-0">
            <div class="px-5 pb-3 border-b border-gray-100 flex items-center justify-between shrink-0">
              <div class="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg">
                <button
                  v-for="tab in ['solar', 'lunar']"
                  :key="tab"
                  type="button"
                  class="px-3 py-1.5 text-[12px] font-black rounded-md transition-all cursor-pointer"
                  :class="drawerTab === tab ? 'bg-white text-brand-primary shadow-sm' : 'bg-transparent text-slate-500'"
                  @click="drawerTab = tab as InputDrawerTab; selectInputMode(tab as InputMode)"
                >
                  {{ tab === 'solar' ? '公历' : '农历' }}
                </button>
              </div>
              <button type="button" class="px-4 py-1.5 bg-brand-primary text-white font-sans text-[12px] font-bold rounded-lg cursor-pointer" @click="void confirmDateDrawer()">确定</button>
            </div>

            <div class="p-4 bg-brand-paper/50 border-b border-gray-100/50 shrink-0">
              <p class="text-[10px] font-bold text-brand-secondary mb-2 text-left">手动数字输入 (快速调整 · 均输入数字)</p>
              <div class="grid grid-cols-5 gap-1.5">
                <div class="relative">
                  <input :value="drawerTab === 'solar' ? (birthYear || 1989) : lunarInput.year" type="number" min="1801" max="2099" class="w-full text-center h-10 bg-white border border-gray-150 rounded-lg text-[12px] font-bold outline-none focus:border-brand-primary" placeholder="年" @input="drawerTab === 'solar' ? handleSolarManualInput('year', $event) : handleLunarManualInput('year', $event)" />
                  <span class="absolute right-1 top-1/2 -translate-y-1/2 text-[9px] text-slate-400 font-bold scale-95">年</span>
                </div>
                <div class="relative">
                  <input :value="drawerTab === 'solar' ? (birthMonth || 1) : lunarInput.month" type="number" min="1" max="12" class="w-full text-center h-10 bg-white border border-gray-150 rounded-lg text-[12px] font-bold outline-none focus:border-brand-primary" placeholder="月" @input="drawerTab === 'solar' ? handleSolarManualInput('month', $event) : handleLunarManualInput('month', $event)" />
                  <span class="absolute right-1 top-1/2 -translate-y-1/2 text-[9px] text-slate-400 font-bold scale-95">月</span>
                </div>
                <div class="relative">
                  <input :value="drawerTab === 'solar' ? (birthDay || 1) : lunarInput.day" type="number" min="1" max="31" class="w-full text-center h-10 bg-white border border-gray-150 rounded-lg text-[12px] font-bold outline-none focus:border-brand-primary" placeholder="日" @input="drawerTab === 'solar' ? handleSolarManualInput('day', $event) : handleLunarManualInput('day', $event)" />
                  <span class="absolute right-1 top-1/2 -translate-y-1/2 text-[9px] text-slate-400 font-bold scale-95">日</span>
                </div>
                <div class="relative">
                  <input :value="drawerTab === 'solar' ? solarHour : lunarInput.hour" type="number" min="0" max="23" class="w-full text-center h-10 bg-white border border-gray-150 rounded-lg text-[12px] font-bold outline-none focus:border-brand-primary" placeholder="时" @input="drawerTab === 'solar' ? handleSolarManualInput('hour', $event) : handleLunarManualInput('hour', $event)" />
                  <span class="absolute right-1 top-1/2 -translate-y-1/2 text-[9px] text-slate-400 font-bold scale-95">时</span>
                </div>
                <div class="relative">
                  <input :value="drawerTab === 'solar' ? solarMinute : lunarInput.minute" type="number" min="0" max="59" class="w-full text-center h-10 bg-white border border-gray-150 rounded-lg text-[12px] font-bold outline-none focus:border-brand-primary" placeholder="分" @input="drawerTab === 'solar' ? handleSolarManualInput('minute', $event) : handleLunarManualInput('minute', $event)" />
                  <span class="absolute right-1 top-1/2 -translate-y-1/2 text-[9px] text-slate-400 font-bold scale-95">分</span>
                </div>
              </div>
            </div>

            <div class="p-4 grid grid-cols-5 gap-2 overflow-hidden h-44 relative shrink-0">
              <div class="absolute left-4 right-4 top-[72px] h-8 bg-brand-primary/5 rounded-lg border-y border-brand-primary/10 pointer-events-none"></div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, drawerTab, 'year')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="year in yearOptions" :key="`${drawerTab}-year-${year}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center font-mono text-[13px] snap-center shrink-0 font-extrabold w-full" :class="(drawerTab === 'solar' ? Number(birthYear || 1989) : lunarInput.year) === year ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="year" @click="drawerTab === 'solar' ? setSolarPart('year', year) : setLunarPart('year', year)">{{ year }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, drawerTab, 'month')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="month in monthOptions" :key="`${drawerTab}-month-${month}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center font-serif text-[13px] snap-center shrink-0 font-extrabold w-full" :class="(drawerTab === 'solar' ? Number(birthMonth || 1) : lunarInput.month) === month ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="month" @click="drawerTab === 'solar' ? setSolarPart('month', month) : setLunarPart('month', month)">{{ drawerTab === 'solar' ? `${twoDigit(month)}月` : lunarMonthLabel(month) }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, drawerTab, 'day')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="day in dayOptions" :key="`${drawerTab}-day-${day}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center font-serif text-[13px] snap-center shrink-0 font-extrabold w-full" :class="(drawerTab === 'solar' ? Number(birthDay || 1) : lunarInput.day) === day ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="day" @click="drawerTab === 'solar' ? setSolarPart('day', day) : setLunarPart('day', day)">{{ drawerTab === 'solar' ? `${twoDigit(day)}日` : lunarDayLabel(day) }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, drawerTab, 'hour')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="hour in hourOptions" :key="`${drawerTab}-hour-${hour}`" type="button" class="picker-wheel-item h-8 flex flex-col items-center justify-center snap-center shrink-0 leading-none w-full" :class="(drawerTab === 'solar' ? solarHour : lunarInput.hour) === hour ? 'text-brand-primary scale-105' : 'text-slate-400'" :data-value="hour" @click="drawerTab === 'solar' ? setSolarPart('hour', hour) : setLunarPart('hour', hour)">
                  <span class="font-mono text-[13px] font-extrabold">{{ twoDigit(hour) }}</span>
                  <span class="text-[8px] font-bold mt-0.5">{{ hourBranchLabel(hour) }}</span>
                </button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, drawerTab, 'minute')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="minute in minuteOptions" :key="`${drawerTab}-minute-${minute}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center font-mono text-[13px] snap-center shrink-0 font-extrabold w-full" :class="(drawerTab === 'solar' ? solarMinute : lunarInput.minute) === minute ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="minute" @click="drawerTab === 'solar' ? setSolarPart('minute', minute) : setLunarPart('minute', minute)">{{ twoDigit(minute) }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
            </div>
          </div>

          <div v-else class="flex flex-col min-h-0">
            <div class="px-5 pb-3 border-b border-gray-100 flex items-center justify-between shrink-0">
              <div class="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg">
                <button type="button" class="px-3 py-1.5 text-[12px] font-black rounded-md transition-all cursor-pointer" :class="locationScope === 'domestic' ? 'bg-white text-brand-primary shadow-sm' : 'bg-transparent text-slate-500'" @click="locationScope = 'domestic'">国内地区</button>
                <button type="button" class="px-3 py-1.5 text-[12px] font-black rounded-md transition-all cursor-pointer" :class="locationScope === 'overseas' ? 'bg-white text-brand-primary shadow-sm' : 'bg-transparent text-slate-500'" @click="locationScope = 'overseas'">海外地区</button>
              </div>
              <button type="button" class="px-4 py-1.5 bg-brand-primary text-white font-sans text-[12px] font-bold rounded-lg cursor-pointer" @click="closeDrawer">确定</button>
            </div>

            <div class="px-5 py-2.5 bg-brand-paper/50 border-b border-gray-100/50 shrink-0">
              <div class="relative">
                <Search :size="13" class="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary" />
                <input v-model="locationSearch" type="text" class="w-full pl-8 pr-8 h-9 bg-white border border-gray-150 rounded-lg text-[12px] outline-none focus:border-brand-primary" placeholder="搜索省份、城市、区县或国家..." />
                <button v-if="locationSearch" type="button" class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 bg-transparent text-[12px] cursor-pointer" @click="locationSearch = ''">清除</button>
              </div>
            </div>

            <div v-if="locationSearch.trim()" class="overflow-y-auto p-4 space-y-2 max-h-[35vh] text-left scrollbar-none min-h-[176px]">
              <div v-if="filteredLocations.length === 0" class="text-center py-8 text-slate-400 text-[12px]">无匹配地区，请尝试其他关键词</div>
              <button v-for="item in filteredLocations" v-else :key="item.id" type="button" class="p-3 rounded-xl border border-gray-100 flex items-center justify-between cursor-pointer transition-all hover:bg-brand-paper bg-white w-full text-left" :class="selectedLocationId === item.id ? 'border-brand-primary bg-brand-primary/5' : ''" @click="selectLocation(item); locationSearch = ''">
                <div class="min-w-0">
                  <span class="text-[13px] font-bold text-brand-ink-strong truncate block">{{ item.display_name }}</span>
                  <div class="text-[10px] text-brand-secondary mt-0.5 flex items-center gap-1.5 flex-wrap">
                    <span>时区: {{ item.timezone }}</span>
                    <span>·</span>
                    <span>经度: {{ item.longitude.toFixed(2) }}°</span>
                    <span>·</span>
                    <span>纬度: {{ item.latitude.toFixed(2) }}°</span>
                  </div>
                </div>
                <ChevronRight :size="14" class="text-slate-400 shrink-0" />
              </button>
            </div>

            <div v-else-if="locationScope === 'domestic'" class="p-4 grid grid-cols-3 gap-1 overflow-hidden h-44 relative bg-white shrink-0">
              <div class="absolute left-4 right-4 top-[72px] h-8 bg-brand-primary/5 rounded-lg border-y border-brand-primary/10 pointer-events-none"></div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, 'domestic-location', 'province')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="province in domesticProvinces" :key="`province-${province}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center text-[12px] snap-center shrink-0 font-extrabold cursor-pointer px-1 truncate w-full" :class="(selectedLocation.province || selectedLocation.city) === province ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="province" @click="selectDomesticProvince(province)">{{ province }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, 'domestic-location', 'city')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="city in domesticCities" :key="`city-${city}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center text-[12px] snap-center shrink-0 font-extrabold cursor-pointer px-1 truncate w-full" :class="(selectedLocation.city || selectedLocation.province) === city ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="city" @click="selectDomesticCity(city)">{{ city }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, 'domestic-location', 'district')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="district in domesticDistricts" :key="`district-${district}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center text-[12px] snap-center shrink-0 font-extrabold cursor-pointer px-1 truncate w-full" :class="(selectedLocation.district || '--') === district ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="district" @click="selectDomesticDistrict(district)">{{ district }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
            </div>

            <div v-else class="p-4 grid grid-cols-2 gap-3 overflow-hidden h-44 relative bg-white shrink-0">
              <div class="absolute left-4 right-4 top-[72px] h-8 bg-brand-primary/5 rounded-lg border-y border-brand-primary/10 pointer-events-none"></div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, 'overseas-location', 'country')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="country in overseasCountries" :key="`country-${country}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center text-[12px] snap-center shrink-0 font-extrabold cursor-pointer px-1 truncate w-full" :class="selectedLocation.country === country ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="country" @click="selectOverseasCountry(country)">{{ country }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
              <div class="overflow-y-auto h-full scroll-smooth snap-y snap-mandatory select-none text-center relative scrollbar-none" @scroll="handleWheelScroll($event, 'overseas-location', 'region')">
                <div class="h-[72px] shrink-0"></div>
                <button v-for="region in overseasRegions" :key="`region-${region}`" type="button" class="picker-wheel-item h-8 flex items-center justify-center text-[12px] snap-center shrink-0 font-extrabold cursor-pointer px-1 truncate w-full" :class="(selectedLocation.city || selectedLocation.region) === region ? 'text-brand-primary font-black scale-105' : 'text-slate-400 font-normal'" :data-value="region" @click="selectOverseasRegion(region)">{{ region }}</button>
                <div class="h-[72px] shrink-0"></div>
              </div>
            </div>

            <div v-if="!locationSearch.trim()" class="px-5 pt-2 text-left shrink-0">
              <div class="bg-slate-50 rounded-xl p-2.5 flex items-center justify-between text-[11px] text-brand-secondary border border-gray-100">
                <div class="min-w-0 flex-1 pr-2">
                  <span class="font-bold text-slate-700 block">当前选择：</span>
                  <span class="font-bold text-brand-primary truncate block mt-0.5">{{ locationSummary }}</span>
                </div>
                <div class="text-right font-mono text-[10px] space-y-0.5 shrink-0">
                  <div>经度: {{ selectedLocation.longitude.toFixed(2) }}° / 纬度: {{ selectedLocation.latitude.toFixed(2) }}°</div>
                  <div>时区: {{ selectedLocation.timezone }}</div>
                </div>
              </div>
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

.birth-picker-row {
  width: 100%;
  min-height: 62px;
  border: 1px solid transparent;
  border-radius: 16px;
  background: linear-gradient(180deg, #F8FAFF 0%, #F3F7FF 100%);
  padding: 10px 11px;
  display: flex;
  align-items: center;
  gap: 10px;
  text-align: left;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.birth-picker-row:active {
  transform: scale(0.99);
  border-color: rgba(79, 70, 229, 0.24);
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
}

.birth-picker-icon {
  width: 32px;
  height: 32px;
  border-radius: 12px;
  background: #FFFFFF;
  color: #4F46E5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
  flex-shrink: 0;
}

.birth-picker-label {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #64748B;
  font-family: inherit;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
}

.birth-picker-value {
  display: block;
  margin-top: 6px;
  color: #1F2937;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 14px;
  font-weight: 900;
  line-height: 1.18;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.birth-picker-subvalue {
  display: block;
  margin-top: 4px;
  color: #64748B;
  font-size: 10.5px;
  font-weight: 700;
  line-height: 1.1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.birth-picker-chevron {
  color: #CBD5E1;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 28px;
  line-height: 1;
  transform: translateY(-1px);
}

.location-breathing-icon {
  animation: location-breathe 2.4s ease-in-out infinite;
}

.location-live-dot {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: #4F46E5;
  box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4);
  animation: location-dot 1.8s ease-out infinite;
}

@keyframes location-breathe {
  0%, 100% {
    transform: translateY(0);
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
  }
  50% {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(79, 70, 229, 0.18);
  }
}

@keyframes location-dot {
  0% {
    box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.42);
  }
  70% {
    box-shadow: 0 0 0 7px rgba(79, 70, 229, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(79, 70, 229, 0);
  }
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

.manual-date-panel {
  border: 1px solid #EEF2F7;
  border-radius: 18px;
  background: linear-gradient(180deg, #F8FAFF 0%, #F3F7FF 100%);
  padding: 7px;
}

.manual-date-title {
  color: #64748B;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1;
  padding: 1px 4px 6px;
}

.manual-date-grid {
  display: grid;
  gap: 4px;
}

.manual-date-grid.solar,
.manual-date-grid.lunar {
  grid-template-columns: 1.25fr repeat(4, minmax(0, 1fr));
}

.manual-date-field {
  display: flex;
  min-width: 0;
  height: 38px;
  align-items: center;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  background: #FFFFFF;
  padding: 0 5px;
  gap: 1px;
}

.manual-date-field input {
  min-width: 0;
  width: 100%;
  border: 0;
  background: transparent;
  color: #1F2937;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
  outline: none;
  text-align: center;
}

.manual-date-field span {
  color: #94A3B8;
  font-size: 9px;
  font-weight: 900;
  line-height: 1;
  flex-shrink: 0;
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
  background: #EEF2FF;
  color: #4F46E5;
  font-size: 14px;
  font-weight: 900;
}

.wheel-frame,
.location-wheel-frame {
  position: relative;
  display: grid;
  gap: 0;
  height: 184px;
  overflow: hidden;
  border-top: 1px solid #EEF2F7;
  border-bottom: 1px solid #EEF2F7;
  background: #FFFFFF;
}

.wheel-frame {
  grid-template-columns: 1.25fr repeat(4, minmax(0, 1fr));
}

.location-wheel-frame {
  display: grid;
}

.wheel-highlight {
  position: absolute;
  left: 6px;
  right: 6px;
  top: 50%;
  height: 46px;
  border-radius: 15px;
  background: #F3F4F6;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.86);
  transform: translateY(-50%);
  pointer-events: none;
}

.wheel-column {
  position: relative;
  z-index: 1;
  height: 184px;
  overflow-y: auto;
  scroll-snap-type: y mandatory;
  -webkit-overflow-scrolling: touch;
  padding: 69px 0;
  scrollbar-width: none;
}

.wheel-column::-webkit-scrollbar {
  display: none;
}

.wheel-option {
  width: 100%;
  height: 46px;
  scroll-snap-align: center;
  color: #D1D5DB;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  font-weight: 700;
  line-height: 46px;
  text-align: center;
  white-space: nowrap;
  transition: color 0.16s ease, font-size 0.16s ease, transform 0.16s ease;
}

.wheel-option.is-selected {
  color: #111827;
  font-size: 21px;
  font-weight: 950;
  transform: scale(1.02);
}

.wheel-option-hour {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
  line-height: 1;
}

.wheel-option-hour span {
  display: block;
  line-height: 1;
}

.wheel-option-hour small {
  color: #CBD5E1;
  display: block;
  font-size: 8.5px;
  font-weight: 900;
  line-height: 1;
}

.wheel-option-hour.is-selected small {
  color: #4F46E5;
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

.location-preview-card {
  border: 1px solid #EEF2F7;
  border-radius: 18px;
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFF 100%);
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 9px;
}

.location-preview-pulse {
  width: 30px;
  height: 30px;
  border-radius: 12px;
  background: #EEF2FF;
  color: #4F46E5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  animation: location-breathe 2.4s ease-in-out infinite;
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
```

### `src/components/four-pillars/FourPillarsNatalTable.vue`

```vue
<script setup lang="ts">
import { computed, ref } from 'vue';
import { CalendarDays, ChevronDown, ChevronUp, Info, UserRound, X } from 'lucide-vue-next';
import type { FourPillarsChartDisplay, FourPillarsDisplayPillar, FourPillarsPillarKey, FourPillarsShenShaDetail } from '../../types/api';

const props = defineProps<{
  chartDisplay: FourPillarsChartDisplay | null;
  elementCounts?: Array<{ element: string; value: number }>;
  strengthLabel?: string;
  favorableElements?: string[];
  unfavorableElements?: string[];
}>();

const pillarKeys: FourPillarsPillarKey[] = ['year', 'month', 'day', 'hour'];
const MAX_SHEN_SHA_ROWS = 3;
const LIFE_STAGE_NAMES = new Set(['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']);

type ShenShaCellItem = {
  name: string;
  meaning: string;
  category: string;
};

const shenShaExpanded = ref(false);
const infoModalOpen = ref(false);
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

const pillars = computed<FourPillarsDisplayPillar[]>(() => {
  const rawPillars = props.chartDisplay?.pillars;
  if (!rawPillars) return [];
  return pillarKeys.map((key) => rawPillars[key]).filter(Boolean);
});

const hasOverflowingShenSha = computed(() => pillars.value.some((pillar) => shenShaRows(pillar).length > MAX_SHEN_SHA_ROWS));
const profile = computed(() => props.chartDisplay?.profile ?? null);
const structureLabel = computed(() => profile.value?.structure_label || (profile.value?.gender_label === '女命' ? '坤造' : '乾造'));
function pad2(value: string | number): string {
  return String(value).padStart(2, '0');
}

const compactLunarDate = computed(() => {
  const raw = profile.value?.lunar_date || profile.value?.lunar_full_text || '';
  if (!raw) return '-';
  const match = raw.match(/(\d{4})年(?:闰)?(\d{1,2})月(\d{1,2})(?:日)?\s*([子丑寅卯辰巳午未申酉戌亥][时時])?/u);
  if (match) {
    return `${match[1]}-${pad2(match[2])}-${pad2(match[3])}${match[4] ? ` ${match[4].replace('時', '时')}` : ''}`;
  }
  return raw.replace(/^农历\s*/, '').replace(/年/g, '-').replace(/月/g, '-').replace(/日/g, ' ').replace(/\s+/g, ' ').trim();
});
const solarDateText = computed(() => {
  const raw = profile.value?.solar_datetime_text || '';
  const match = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/u);
  if (!match) return raw || '-';
  return `${match[1]}年${Number(match[2])}月${Number(match[3])}日`;
});
const trueSolarTimeText = computed(() => {
  const explicit = String(profile.value?.true_solar_time_text || '').trim();
  if (explicit && explicit !== '未校准') return explicit;
  const effective = String(profile.value?.effective_birth_datetime || '').trim();
  const match = effective.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})/u);
  if (match) return `${match[1]}-${match[2]}-${match[3]} ${match[4]}:${match[5]}`;
  return '按默认北京真太阳时校准';
});
const maxElementCount = computed(() => Math.max(1, ...((props.elementCounts || []).map((item) => Number(item.value) || 0))));
const basicInfoRows = computed(() => [
  { label: '姓名', value: profile.value?.name || '未填写' },
  { label: '性别', value: `${profile.value?.gender_label || '-'} · ${structureLabel.value}` },
  { label: '公历', value: solarDateText.value },
  { label: '农历', value: profile.value?.lunar_date || '-' },
  { label: '生肖', value: profile.value?.zodiac || '-' },
  { label: '出生地区', value: profile.value?.birth_place || '未填写' },
  { label: '出生节气', value: profile.value?.solar_term_context || '-' },
  { label: '星座', value: profile.value?.constellation || '-' },
  { label: '星宿', value: profile.value?.xiu || '-' },
]);
const professionalInfoRows = computed(() => [
  { label: '真太阳时', value: trueSolarTimeText.value },
  { label: '胎元', value: profile.value?.tai_yuan || '-' },
  { label: '空亡', value: profile.value?.empty_branches_text || profile.value?.pillar_xun_kong_text || '-' },
  { label: '命宫', value: profile.value?.ming_gong || '-' },
  { label: '胎息', value: profile.value?.tai_xi || '-' },
  { label: '身宫', value: profile.value?.shen_gong || '-' },
  { label: '命卦', value: profile.value?.life_gua || '-' },
]);
const chartInfoRows = computed(() => [...basicInfoRows.value, ...professionalInfoRows.value]);
const boneWeight = computed(() => profile.value?.bone_weight ?? null);
const boneWeightParts = computed(() => {
  const parts = boneWeight.value?.parts || {};
  return [
    { label: '年', value: parts.year },
    { label: '月', value: parts.month },
    { label: '日', value: parts.day },
    { label: '时', value: parts.hour },
  ].filter((item) => typeof item.value === 'number');
});
const boneWeightVerse = computed(() => {
  const explicit = String(boneWeight.value?.verse || '').trim();
  if (explicit) return explicit;
  if (boneWeight.value?.total_qian === 41) {
    return '此命推来事不同，为人能干亦凡庸，中年还有逍遥福，不比前时运未通';
  }
  return '';
});
const boneWeightVerseLines = computed(() => {
  const verse = boneWeightVerse.value;
  if (!verse) return [];
  const clauses = verse.split(/[，,]/u).map((item) => item.trim()).filter(Boolean);
  if (clauses.length === 4) {
    return [`${clauses[0]}，${clauses[1]}`, `${clauses[2]}，${clauses[3]}`];
  }
  return [verse];
});
const favorableText = computed(() => (props.favorableElements || []).filter(Boolean).join('、') || '-');
const unfavorableText = computed(() => (props.unfavorableElements || []).filter(Boolean).join('、') || '-');

function elementTextClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'text-[#059669]';
  if (value === '火') return 'text-[#E11D48]';
  if (value === '土') return 'text-[#78350F]';
  if (value === '金') return 'text-[#CA8A04]';
  if (value === '水') return 'text-[#2563EB]';
  return 'text-brand-ink-strong';
}

function elementBgClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'bg-[#ECFDF5] border-[#A7F3D0]';
  if (value === '火') return 'bg-[#FFF1F2] border-[#FECDD3]';
  if (value === '土') return 'bg-[#FFFBEB] border-[#FCD34D]';
  if (value === '金') return 'bg-[#FFF7DA] border-[#F4D27A]';
  if (value === '水') return 'bg-[#EFF6FF] border-[#BFDBFE]';
  return 'bg-white border-slate-100';
}

function elementDotClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'bg-[#10B981] border-[#ECFDF5]';
  if (value === '火') return 'bg-[#FB7185] border-[#FFF1F2]';
  if (value === '土') return 'bg-[#D97706] border-[#FFFBEB]';
  if (value === '金') return 'bg-[#D69E2E] border-[#FFF7DA]';
  if (value === '水') return 'bg-[#3B82F6] border-[#EFF6FF]';
  return 'bg-[#CBD5E1] border-white';
}

function cellText(value: string | null | undefined): string {
  return String(value || '').trim() || '-';
}

function elementFromNaYin(value: string | null | undefined): string {
  const text = cellText(value);
  const matched = text.match(/[木火土金水](?!.*[木火土金水])/u);
  return matched?.[0] || '';
}

function getShenShaToneScore(item: ShenShaCellItem): number {
  const text = `${item.category}${item.name}${item.meaning}`;
  if (/[贵人德福喜禄昌合赦喜医昌印舆]/u.test(text)) return 0;
  if (/[煞亡劫灾孤寡空刃鬼差错]/u.test(text)) return 2;
  return 1;
}

function shenShaRows(pillar: FourPillarsDisplayPillar): ShenShaCellItem[] {
  const details = Array.isArray(pillar.shen_sha_details) ? pillar.shen_sha_details : [];
  const detailByName = new Map<string, FourPillarsShenShaDetail>();
  details.forEach((item) => {
    if (item?.name && !detailByName.has(item.name)) {
      detailByName.set(item.name, item);
    }
  });
  const names = Array.isArray(pillar.shen_sha) && pillar.shen_sha.length
    ? pillar.shen_sha
    : details.map((item) => item.name);
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

function visibleShenShaRows(pillar: FourPillarsDisplayPillar): ShenShaCellItem[] {
  const rows = shenShaRows(pillar);
  if (shenShaExpanded.value) return rows;
  if (rows.length > MAX_SHEN_SHA_ROWS) return rows.slice(0, 2);
  return rows;
}
</script>

<template>
  <section class="rounded-xl bg-white shadow-sm overflow-hidden">
    <div v-if="chartDisplay" class="space-y-1.5">
      <div class="mx-2 mt-2 rounded-lg bg-[#F8FAFF] px-2 py-1.5 flex items-center gap-1.5 text-[10.5px] leading-none">
        <span class="font-serif h-9 min-w-[56px] rounded-lg font-black text-white bg-[#2563EB] shrink-0 flex items-center justify-center gap-1 px-1.5">
          <UserRound :size="12" class="shrink-0" />
          <span class="flex flex-col items-start justify-center gap-0.5 text-[9.5px] leading-none">
            <span>{{ chartDisplay.profile.gender_label }}</span>
            <span>{{ structureLabel }}</span>
          </span>
        </span>
        <div class="min-w-0 flex-1 flex items-center gap-1">
          <CalendarDays :size="12" class="shrink-0 text-[#334155]" />
          <div class="min-w-0 flex-1 space-y-0.5">
            <p class="font-mono text-[10.5px] text-[#334155] truncate">
              公历 {{ chartDisplay.profile.solar_datetime_text }}
            </p>
            <p class="font-mono text-[10.5px] text-[#334155] truncate">
              农历 {{ compactLunarDate }}
            </p>
          </div>
        </div>
        <button
          type="button"
          class="shrink-0 h-7 px-1.5 rounded-lg bg-white border border-[#D8E3F5] text-[#1D4ED8] font-sans text-[9.5px] font-black flex items-center gap-0.5 shadow-sm"
          @click="infoModalOpen = true"
        >
          <Info :size="10" />
          更多命盘信息
        </button>
      </div>

      <div class="mx-2 mb-2 rounded-lg bg-white overflow-hidden">
        <div class="overflow-x-auto no-scrollbar">
          <table class="w-full min-w-[320px] table-fixed border-collapse text-center select-text">
            <thead>
              <tr class="bg-[#EAF1FF]">
                <th class="w-[14%] py-1.5 px-1 font-sans text-[10px] font-bold text-[#64748B]">柱别</th>
                <th
                  v-for="pillar in pillars"
                  :key="`${pillar.key}-head`"
                  class="w-[21.5%] py-1.5 px-1 font-serif text-[12px] font-black text-[#1D4ED8]"
                >
                  <span class="block leading-none">{{ pillar.label }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">主星</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-stem-god`" class="natal-cell natal-god">
                  {{ cellText(pillar.stem_ten_god) }}
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">天干</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-stem`" class="natal-cell">
                  <span class="natal-glyph-wrap" :title="pillar.stem_element">
                    <span class="natal-stem-branch" :class="[elementTextClass(pillar.stem_element), elementBgClass(pillar.stem_element)]">
                      <span class="natal-glyph-text">{{ pillar.stem }}</span>
                    </span>
                    <span class="natal-element-dot" :class="elementDotClass(pillar.stem_element)" aria-hidden="true"></span>
                  </span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地支</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-branch`" class="natal-cell">
                  <span class="natal-glyph-wrap" :title="pillar.branch_element">
                    <span class="natal-stem-branch" :class="[elementTextClass(pillar.branch_element), elementBgClass(pillar.branch_element)]">
                      <span class="natal-glyph-text">{{ pillar.branch }}</span>
                    </span>
                    <span class="natal-element-dot" :class="elementDotClass(pillar.branch_element)" aria-hidden="true"></span>
                  </span>
                </td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">藏干</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-hidden`" class="natal-cell natal-hidden-cell">
                  <span
                    v-for="(item, index) in pillar.hidden_stems"
                    :key="`${pillar.key}-${item.stem}`"
                    class="natal-hidden-item"
                  >
                    <span class="natal-hidden-glyph" :class="elementTextClass(item.element)">{{ item.stem }}</span>
                    <span>{{ item.ten_god || pillar.branch_ten_gods[index] || '-' }}</span>
                  </span>
                  <span v-if="!pillar.hidden_stems.length" class="text-[10px] text-[#94A3B8]">-</span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地势</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-dishi`" class="natal-cell natal-text">{{ cellText(pillar.di_shi) }}</td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">自坐</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-sitting`" class="natal-cell natal-text">{{ cellText(pillar.self_sitting) }}</td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">旬空</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-xunkong`" class="natal-cell natal-text">{{ cellText(pillar.xun_kong) }}</td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">纳音</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-nayin`" class="natal-cell natal-text">
                  <span class="natal-nayin" :class="[elementTextClass(elementFromNaYin(pillar.na_yin)), elementBgClass(elementFromNaYin(pillar.na_yin))]">
                    {{ cellText(pillar.na_yin) }}
                  </span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label text-center">
                  <span class="block text-inherit">神煞</span>
                  <button
                    v-if="hasOverflowingShenSha"
                    type="button"
                    class="natal-shen-sha-toggle cursor-pointer outline-none hover:bg-indigo-50/20"
                    :aria-label="shenShaExpanded ? '收起神煞' : '展开神煞'"
                    :title="shenShaExpanded ? '收起神煞详情' : '展开神煞详情'"
                    @click="shenShaExpanded = !shenShaExpanded"
                  >
                    <ChevronUp v-if="shenShaExpanded" :size="10" />
                    <ChevronDown v-else :size="10" />
                  </button>
                </td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-shen-sha`" class="natal-cell natal-shen-sha-cell">
                  <div v-if="shenShaRows(pillar).length" class="flex flex-col items-center justify-center gap-1 w-full">
                    <div class="natal-shen-sha-stack">
                      <span
                        v-for="item in visibleShenShaRows(pillar)"
                        :key="`${pillar.key}-${item.name}`"
                        class="natal-text block"
                        :title="item.meaning || item.name"
                      >
                        {{ item.name }}
                      </span>
                    </div>
                    <span v-if="!shenShaExpanded && shenShaRows(pillar).length > MAX_SHEN_SHA_ROWS" class="text-[9.5px] font-bold text-slate-400 mt-0.5 block whitespace-nowrap">
                      +{{ shenShaRows(pillar).length - 2 }} 更多
                    </span>
                  </div>
                  <span v-else class="text-[10px] text-[#94A3B8]">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <Teleport to="body">
        <transition name="fade-slide">
          <div v-if="infoModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 px-4 py-8" @click.self="infoModalOpen = false">
            <div class="w-full max-w-[360px] max-h-[80vh] overflow-hidden rounded-2xl bg-white border border-[#D8E3F5] shadow-2xl flex flex-col">
              <div class="shrink-0 px-4 py-3 border-b border-[#E2E8F0] flex items-center justify-between gap-3 bg-[#F8FAFF]">
                <div>
                  <p class="font-sans text-[10px] font-black tracking-wide text-[#64748B]">MORE CHART INFO</p>
                  <h3 class="font-serif text-[16px] font-black text-[#1D4ED8] mt-0.5">更多命盘信息</h3>
                </div>
                <button type="button" class="w-8 h-8 rounded-lg bg-white border border-[#D8E3F5] flex items-center justify-center text-[#64748B]" @click="infoModalOpen = false">
                  <X :size="15" />
                </button>
              </div>
              <div class="overflow-y-auto px-4 py-3 space-y-4">
                <section>
                  <div class="natal-info-grid">
                    <div v-for="item in chartInfoRows" :key="`chart-${item.label}`" class="natal-info-item">
                      <span class="natal-info-label">{{ item.label }}</span>
                      <span class="natal-info-value">{{ item.value }}</span>
                    </div>
                  </div>
                </section>

                <section>
                  <h4 class="natal-info-section-title">五行能量</h4>
                  <div class="space-y-2">
                    <div v-for="item in props.elementCounts || []" :key="`element-${item.element}`" class="natal-element-bar-row">
                      <span class="natal-element-bar-label" :class="elementTextClass(item.element)">{{ item.element }}</span>
                      <div class="natal-element-bar-track">
                        <div
                          class="natal-element-bar-fill"
                          :class="elementDotClass(item.element)"
                          :style="{ width: `${Math.max(6, Math.round((Number(item.value) || 0) / maxElementCount * 100))}%` }"
                        ></div>
                      </div>
                      <span class="natal-element-bar-value">{{ item.value }}</span>
                    </div>
                  </div>
                  <div class="natal-info-grid mt-3">
                    <div class="natal-info-item natal-info-item-wide">
                      <span class="natal-info-label">旺衰初判</span>
                      <span class="natal-info-value">{{ props.strengthLabel || '-' }}</span>
                    </div>
                    <div class="natal-info-item">
                      <span class="natal-info-label">喜用候选</span>
                      <span class="natal-info-value">{{ favorableText }}</span>
                    </div>
                    <div class="natal-info-item">
                      <span class="natal-info-label">忌神候选</span>
                      <span class="natal-info-value">{{ unfavorableText }}</span>
                    </div>
                  </div>
                </section>

                <section>
                  <h4 class="natal-info-section-title">袁天罡称骨</h4>
                  <div v-if="boneWeight" class="rounded-xl bg-[#F8FAFF] border border-[#D8E3F5] p-3 space-y-3">
                    <div class="flex items-center justify-between gap-3">
                      <div>
                        <span class="block font-serif text-[18px] font-black text-[#1D4ED8]">{{ boneWeight.total_label }}</span>
                        <span class="block font-sans text-[9.5px] font-bold text-[#64748B] mt-0.5">
                          总骨重 {{ boneWeight.total_qian }} 钱
                        </span>
                      </div>
                      <span class="font-sans text-[10px] font-bold text-[#64748B] text-right leading-snug">
                        {{ boneWeight.year_ganzhi }}年<br />
                        {{ boneWeight.lunar_month }}月{{ boneWeight.lunar_day }}日 · {{ boneWeight.hour_branch }}时
                      </span>
                    </div>

                    <div v-if="boneWeightParts.length" class="grid grid-cols-4 gap-1.5">
                      <div v-for="item in boneWeightParts" :key="`bone-${item.label}`" class="rounded-lg bg-white border border-[#E2E8F0] px-1.5 py-1.5 text-center">
                        <span class="block font-sans text-[9px] font-black text-[#94A3B8]">{{ item.label }}骨</span>
                        <span class="block font-serif text-[12px] font-black text-[#334155] mt-0.5">{{ item.value }}钱</span>
                      </div>
                    </div>

                    <div class="rounded-xl bg-white border border-[#E2E8F0] p-2.5">
                      <span class="block font-sans text-[9.5px] font-black text-[#94A3B8]">格局</span>
                      <p class="font-serif text-[12px] font-black text-brand-ink-strong leading-relaxed mt-1">
                        {{ boneWeight.fate_pattern || boneWeight.summary }}
                      </p>
                    </div>

                    <div v-if="boneWeightVerse" class="rounded-xl bg-white border border-[#E2E8F0] p-2.5">
                      <span class="block font-sans text-[9.5px] font-black text-[#94A3B8]">称骨歌诀</span>
                      <div class="font-serif text-[12px] font-bold text-[#1E293B] leading-relaxed mt-1 space-y-0.5">
                        <p v-for="line in boneWeightVerseLines" :key="line">{{ line }}</p>
                      </div>
                    </div>

                    <p class="font-sans text-[10px] text-[#64748B] leading-relaxed">称骨为传统资料展示，不作为命盘好坏判断依据。</p>
                  </div>
                  <p v-else class="font-sans text-[11px] text-[#64748B] rounded-xl bg-[#F8FAFF] border border-[#D8E3F5] p-3">称骨资料暂未匹配。</p>
                </section>
              </div>
            </div>
          </div>
        </transition>
      </Teleport>

    </div>

    <div v-else class="p-4">
      <p class="font-sans text-[11px] text-[#1D4ED8] font-bold tracking-wide">NATAL CHART</p>
      <p class="font-sans text-[13px] text-brand-secondary mt-2">排盘表正在准备，当前报告会先显示旧版命盘摘要。</p>
    </div>
  </section>
</template>

<style scoped>
.natal-row-label {
  font-family: inherit;
  font-size: 10px;
  font-weight: 800;
  line-height: 1.25;
  color: #1D4ED8;
  background: rgba(234, 241, 255, 0.8);
  padding: 6px 3px;
  vertical-align: middle;
}

.natal-cell {
  padding: 5px 3px;
  text-align: center;
  vertical-align: middle;
}

.natal-god {
  font-family: serif;
  font-size: 11px;
  font-weight: 900;
  color: #1D4ED8;
}

.natal-glyph-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  vertical-align: middle;
}

.natal-stem-branch {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border-width: 1px;
  display: grid;
  place-items: center;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 17px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.58), 0 1px 2px rgba(15, 23, 42, 0.05);
}

.natal-glyph-text {
  display: block;
  width: 100%;
  text-align: center;
  transform: translateY(-0.5px);
}

.natal-element-dot {
  position: absolute;
  top: 50%;
  right: -4px;
  width: 8px;
  height: 8px;
  border: 1.5px solid;
  border-radius: 999px;
  transform: translateY(-50%);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.12);
}

.natal-hidden-cell {
  padding: 5px 3px;
}

.natal-hidden-item {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  border: 1px solid #D8E3F5;
  margin: 1px;
  padding: 2px 3px;
  border-radius: 5px;
  background: #FFFFFF;
  color: #64748B;
  font-size: 9px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.natal-hidden-glyph {
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
  text-shadow: 0 0 0 currentColor;
}

.natal-text {
  font-family: inherit;
  font-size: 10.5px;
  font-weight: 800;
  line-height: 1.25;
  color: #334155;
}

.natal-nayin {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  min-height: 20px;
  border-width: 1px;
  border-radius: 999px;
  padding: 2px 5px;
  font-size: 10px;
  font-weight: 900;
  line-height: 1.1;
  white-space: nowrap;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.48);
}

.natal-shen-sha-toggle {
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

.natal-shen-sha-cell {
  padding: 4px 2px;
  vertical-align: middle;
}

.natal-shen-sha-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
}

.natal-info-section-title {
  margin-bottom: 8px;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 13px;
  font-weight: 900;
  line-height: 1.2;
  color: #1D4ED8;
}

.natal-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.natal-info-item {
  min-width: 0;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  background: #FFFFFF;
  padding: 7px 8px;
}

.natal-info-item-wide {
  grid-column: 1 / -1;
}

.natal-info-label {
  display: block;
  font-size: 9.5px;
  font-weight: 800;
  line-height: 1.2;
  color: #94A3B8;
}

.natal-info-value {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 800;
  line-height: 1.35;
  color: #334155;
  word-break: break-word;
}

.natal-element-bar-row {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) 24px;
  align-items: center;
  gap: 8px;
}

.natal-element-bar-label {
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 13px;
  font-weight: 900;
  line-height: 1;
  text-align: center;
}

.natal-element-bar-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #E2E8F0;
}

.natal-element-bar-fill {
  height: 100%;
  border-width: 0;
  border-radius: inherit;
}

.natal-element-bar-value {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
  color: #64748B;
  text-align: right;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
```

### `src/components/support/ContactServiceModal.vue`

```vue
<script setup lang="ts">
import { computed, ref } from 'vue';
import { Check, Copy, QrCode, X } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const {
  state,
  customerServiceWechatId,
  customerServiceQrCodeUrl,
  customerServiceQrGuidanceText,
  customerServiceCopyButtonText,
  customerServiceUnconfiguredText,
  customerServiceCopyForScene,
  closeCustomerServiceModal,
} = useEaseWiseApp();

const copied = ref(false);
const copyError = ref('');
const qrCodeFailed = ref(false);

const visible = computed(() => state.contactServiceModalVisible);
const scene = computed(() => state.contactServiceScene);
const description = computed(() => customerServiceCopyForScene(scene.value));
const wechatId = computed(() => customerServiceWechatId.value.trim());
const hasWechatId = computed(() => Boolean(wechatId.value));
const hasQrCode = computed(() => Boolean(customerServiceQrCodeUrl.value && !qrCodeFailed.value));
const copyButtonLabel = computed(() => customerServiceCopyButtonText.value.trim() || '复制微信');

async function copyWechatId(): Promise<void> {
  if (!hasWechatId.value) {
    return;
  }
  copyError.value = '';
  try {
    await copyTextToClipboard(wechatId.value);
    copied.value = true;
    window.setTimeout(() => {
      copied.value = false;
    }, 1800);
  } catch {
    copyError.value = '复制失败，请手动长按或选中微信号复制。';
  }
}

async function copyTextToClipboard(text: string): Promise<void> {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const input = document.createElement('textarea');
  input.value = text;
  input.setAttribute('readonly', 'true');
  input.style.position = 'fixed';
  input.style.left = '-9999px';
  input.style.top = '0';
  document.body.appendChild(input);
  input.focus();
  input.select();

  try {
    if (!document.execCommand('copy')) {
      throw new Error('copy_failed');
    }
  } finally {
    document.body.removeChild(input);
  }
}

function handleClose(): void {
  copied.value = false;
  copyError.value = '';
  closeCustomerServiceModal();
}
</script>

<template>
  <transition name="contact-fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-[220] flex items-center justify-center bg-slate-950/45 px-5 py-8 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
    >
      <div class="relative w-full max-w-[360px] overflow-hidden rounded-[28px] border border-white/70 bg-[#fffaf0] shadow-2xl shadow-slate-950/20">
        <div class="absolute -top-16 -right-16 h-36 w-36 rounded-full bg-brand-primary/10 blur-2xl"></div>
        <div class="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-amber-300/20 blur-2xl"></div>

        <button
          type="button"
          class="absolute right-4 top-4 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-brand-secondary shadow-sm outline-none transition-colors hover:text-brand-ink-strong"
          @click="handleClose"
        >
          <X :size="15" />
        </button>

        <div class="relative space-y-5 px-5 pb-5 pt-6 text-center">
          <div class="space-y-1.5 px-7">
            <p class="font-sans text-[10px] font-black uppercase tracking-[0.22em] text-brand-primary">Customer Service</p>
            <h3 class="font-serif text-[22px] font-black leading-tight text-brand-ink-strong">联系客服</h3>
            <p class="font-sans text-[11px] leading-relaxed text-brand-secondary">
              {{ description }}
            </p>
          </div>

          <div class="rounded-[24px] border border-brand-primary/10 bg-white/85 p-4 shadow-sm">
            <div class="mx-auto flex h-48 w-48 items-center justify-center overflow-hidden rounded-[20px] border border-dashed border-brand-primary/20 bg-brand-paper/70">
              <img
                v-if="hasQrCode"
                :src="customerServiceQrCodeUrl"
                alt="客服二维码"
                class="h-full w-full object-cover"
                @error="qrCodeFailed = true"
              />
              <div v-else class="flex flex-col items-center gap-2 px-5 text-center text-brand-secondary">
                <QrCode :size="32" class="text-brand-primary/55" />
                <p class="font-sans text-[11px] leading-relaxed">客服二维码暂未配置</p>
              </div>
            </div>
            <p class="mt-3 font-sans text-[10.5px] leading-relaxed text-brand-secondary">
              {{ customerServiceQrGuidanceText }}
            </p>
          </div>

          <div class="rounded-[20px] border border-gray-100 bg-white/90 p-3 text-left">
            <p class="font-sans text-[10px] font-bold text-brand-secondary">客服微信号</p>
            <div class="mt-1.5 flex items-center justify-between gap-3">
              <span class="min-w-0 break-all font-mono text-[15px] font-black text-brand-ink-strong">
                {{ hasWechatId ? wechatId : '后台暂未配置' }}
              </span>
              <button
                type="button"
                class="shrink-0 rounded-xl px-3 py-2 font-sans text-[11px] font-black shadow-sm outline-none transition-all"
                :class="hasWechatId ? 'bg-brand-primary text-white hover:bg-brand-primary-strong' : 'cursor-not-allowed bg-gray-100 text-gray-400'"
                :disabled="!hasWechatId"
                @click="copyWechatId"
              >
                <span class="inline-flex items-center gap-1">
                  <Check v-if="copied" :size="12" />
                  <Copy v-else :size="12" />
                  <span>{{ copied ? '已复制' : copyButtonLabel }}</span>
                </span>
              </button>
            </div>
            <p v-if="!hasWechatId" class="mt-2 font-sans text-[10px] leading-relaxed text-amber-700">
              {{ customerServiceUnconfiguredText }}
            </p>
            <p v-else-if="copyError" class="mt-2 font-sans text-[10px] leading-relaxed text-red-600">
              {{ copyError }}
            </p>
          </div>

          <p class="px-2 font-sans text-[10px] leading-relaxed text-brand-secondary">
            本平台所有内容仅供娱乐，并无参考价值。
          </p>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.contact-fade-enter-active,
.contact-fade-leave-active {
  transition: opacity 0.18s ease;
}

.contact-fade-enter-from,
.contact-fade-leave-to {
  opacity: 0;
}
</style>
```

### `src/composables/useEaseWiseApp.ts`

```ts
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
```

### `src/lib/api.ts`

```ts
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
  FourPillarsLuckStreamCompleteData,
  FourPillarsLuckStreamDeltaData,
  FourPillarsLuckStreamErrorData,
  FourPillarsLuckStreamRenderData,
  FourPillarsLuckStreamStatusData,
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

export type FourPillarsLuckStreamHandlers = {
  signal?: AbortSignal;
  onRender?: (data: FourPillarsLuckStreamRenderData) => void;
  onStatus?: (data: FourPillarsLuckStreamStatusData) => void;
  onDelta?: (data: FourPillarsLuckStreamDeltaData) => void;
  onComplete?: (data: FourPillarsLuckStreamCompleteData) => void;
  onError?: (data: FourPillarsLuckStreamErrorData) => void;
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
  const configuredValue = import.meta.env.VITE_API_BASE_URL;
  if (configuredValue) {
    return configuredValue.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined') {
    return window.location.origin.replace(/\/+$/, '');
  }

  return 'http://127.0.0.1:8000';
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

export function createPhoneReview(accessToken: string, payload: { phone: string; gender: Gender; include_markdown?: boolean }): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>('/api/v1/phone-qimen/reviews', {
    method: 'POST',
    accessToken,
    body: {
      phone: payload.phone,
      gender: payload.gender,
      include_markdown: payload.include_markdown ?? true,
    },
  });
}

export async function streamCreatePhoneReview(
  accessToken: string,
  payload: { phone: string; gender: Gender; include_markdown?: boolean },
  handlers: PhoneReviewCoreStreamHandlers = {},
): Promise<PhoneReviewCoreStreamCompleteData> {
  let completePayload: PhoneReviewCoreStreamCompleteData | null = null;
  await streamSse('/api/v1/phone-qimen/reviews/stream', {
    method: 'POST',
    accessToken,
    body: {
      phone: payload.phone,
      gender: payload.gender,
      include_markdown: payload.include_markdown ?? true,
    },
    signal: handlers.signal,
    onEvent: (eventName, eventPayload) => {
      if (eventName === 'created') {
        handlers.onCreated?.(eventPayload as PhoneReviewCoreStreamCreatedData);
        return;
      }
      if (eventName === 'facts_ready') {
        handlers.onFactsReady?.(eventPayload as PhoneReviewCoreStreamFactsReadyData);
        return;
      }
      if (eventName === 'core_status') {
        handlers.onCoreStatus?.(eventPayload as PhoneReviewCoreStreamStatusData);
        return;
      }
      if (eventName === 'core_delta') {
        handlers.onCoreDelta?.(eventPayload as PhoneReviewCoreStreamDeltaData);
        return;
      }
      if (eventName === 'section_complete') {
        handlers.onSectionComplete?.(eventPayload as PhoneReviewCoreStreamSectionCompleteData);
        return;
      }
      if (eventName === 'complete') {
        completePayload = eventPayload as PhoneReviewCoreStreamCompleteData;
        handlers.onComplete?.(completePayload);
        return;
      }
      if (eventName === 'error') {
        const errorPayload = eventPayload as PhoneReviewCoreStreamErrorData;
        handlers.onError?.(errorPayload);
        const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
        throw new ApiError(status, errorPayload.detail || 'review_generation_failed', errorPayload);
      }
    },
  });
  if (!completePayload) {
    throw new ApiError(409, 'review_generation_incomplete', null);
  }
  return completePayload;
}

export function listPhoneReviews(accessToken: string, limit = 20): Promise<ReviewListResponse> {
  return requestJson<ReviewListResponse>(`/api/v1/phone-qimen/reviews?limit=${limit}`, {
    accessToken,
  });
}

export function getPhoneReviewDetail(accessToken: string, reviewId: string): Promise<ReviewRecord> {
  return requestJson<ReviewRecord>(`/api/v1/phone-qimen/reviews/${reviewId}`, {
    accessToken,
  });
}

export function unlockPhoneReviewAspect(accessToken: string, reviewId: string, aspectKey: string): Promise<ReviewAspectUnlockResponse> {
  return requestJson<ReviewAspectUnlockResponse>(`/api/v1/phone-qimen/reviews/${reviewId}/aspect-unlocks`, {
    method: 'POST',
    accessToken,
    body: {
      aspect_key: aspectKey,
    },
  });
}

export async function streamPhoneReviewAspectUnlock(
  accessToken: string,
  reviewId: string,
  aspectKey: string,
  handlers: PhoneReviewAspectStreamHandlers = {},
): Promise<PhoneReviewAspectStreamCompleteData> {
  const headers = new Headers();
  headers.set('Accept', 'text/event-stream');
  headers.set('X-Client-Platform', 'h5');
  headers.set('X-Client-Channel', 'h5');
  headers.set('X-Client-Version', 'easewise-local-frontend');
  headers.set('Authorization', `Bearer ${accessToken}`);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/phone-qimen/reviews/${encodeURIComponent(reviewId)}/aspect-unlocks/${encodeURIComponent(aspectKey)}/stream`,
    {
      method: 'POST',
      headers,
      signal: handlers.signal,
    },
  );

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
  let completePayload: PhoneReviewAspectStreamCompleteData | null = null;

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
    const payload = tryParseJson(dataLines.join('\n'));
    if (!payload || typeof payload !== 'object') {
      return;
    }

    if (eventName === 'unlock') {
      handlers.onUnlock?.(payload as PhoneReviewAspectStreamUnlockData);
      return;
    }
    if (eventName === 'status') {
      handlers.onStatus?.(payload as PhoneReviewAspectStreamStatusData);
      return;
    }
    if (eventName === 'delta') {
      handlers.onDelta?.(payload as PhoneReviewAspectStreamDeltaData);
      return;
    }
    if (eventName === 'complete') {
      completePayload = payload as PhoneReviewAspectStreamCompleteData;
      handlers.onComplete?.(completePayload);
      return;
    }
    if (eventName === 'error') {
      const errorPayload = payload as PhoneReviewAspectStreamErrorData;
      handlers.onError?.(errorPayload);
      const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
      throw new ApiError(status, errorPayload.detail || 'aspect_generation_failed', errorPayload);
    }
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
  if (!completePayload) {
    throw new ApiError(409, 'aspect_generation_incomplete', null);
  }
  return completePayload;
}

export function createFourPillarsReview(accessToken: string, payload: FourPillarsCreatePayload): Promise<FourPillarsReviewRecord> {
  return requestJson<FourPillarsReviewRecord>('/api/v1/four-pillars/reviews', {
    method: 'POST',
    accessToken,
    body: {
      timezone: 'Asia/Shanghai',
      include_markdown: true,
      ...payload,
    },
  });
}

export async function streamCreateFourPillarsReview(
  accessToken: string,
  payload: FourPillarsCreatePayload,
  handlers: FourPillarsCoreStreamHandlers = {},
): Promise<FourPillarsCoreStreamCompleteData> {
  let completePayload: FourPillarsCoreStreamCompleteData | null = null;
  await streamSse('/api/v1/four-pillars/reviews/stream', {
    method: 'POST',
    accessToken,
    body: {
      timezone: 'Asia/Shanghai',
      include_markdown: true,
      ...payload,
    },
    signal: handlers.signal,
    onEvent: (eventName, eventPayload) => {
      if (eventName === 'created') {
        handlers.onCreated?.(eventPayload as FourPillarsCoreStreamCreatedData);
        return;
      }
      if (eventName === 'facts_ready') {
        handlers.onFactsReady?.(eventPayload as FourPillarsCoreStreamFactsReadyData);
        return;
      }
      if (eventName === 'core_status') {
        handlers.onCoreStatus?.(eventPayload as FourPillarsCoreStreamStatusData);
        return;
      }
      if (eventName === 'core_delta') {
        handlers.onCoreDelta?.(eventPayload as FourPillarsCoreStreamDeltaData);
        return;
      }
      if (eventName === 'section_complete') {
        handlers.onSectionComplete?.(eventPayload as FourPillarsCoreStreamSectionCompleteData);
        return;
      }
      if (eventName === 'complete') {
        completePayload = eventPayload as FourPillarsCoreStreamCompleteData;
        handlers.onComplete?.(completePayload);
        return;
      }
      if (eventName === 'error') {
        const errorPayload = eventPayload as FourPillarsCoreStreamErrorData;
        handlers.onError?.(errorPayload);
        const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
        throw new ApiError(status, errorPayload.detail || 'review_generation_failed', errorPayload);
      }
    },
  });
  if (!completePayload) {
    throw new ApiError(409, 'review_generation_incomplete', null);
  }
  return completePayload;
}

export function resolveFourPillarsInput(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  return requestJson<Record<string, unknown>>('/api/v1/four-pillars/input/resolve', {
    method: 'POST',
    body: payload,
  });
}

export function listFourPillarsBirthLocations(): Promise<Record<string, unknown>> {
  return requestJson<Record<string, unknown>>('/api/v1/four-pillars/input/locations');
}

export function listFourPillarsReviews(accessToken: string, limit = 20): Promise<FourPillarsReviewListResponse> {
  return requestJson<FourPillarsReviewListResponse>(`/api/v1/four-pillars/reviews?limit=${limit}`, {
    accessToken,
  });
}

export function getFourPillarsReviewDetail(accessToken: string, reviewId: string): Promise<FourPillarsReviewRecord> {
  return requestJson<FourPillarsReviewRecord>(`/api/v1/four-pillars/reviews/${reviewId}`, {
    accessToken,
  });
}

export function unlockFourPillarsReviewAspect(accessToken: string, reviewId: string, aspectKey: string): Promise<FourPillarsAspectUnlockResponse> {
  return requestJson<FourPillarsAspectUnlockResponse>(`/api/v1/four-pillars/reviews/${reviewId}/aspect-unlocks`, {
    method: 'POST',
    accessToken,
    body: {
      aspect_key: aspectKey,
    },
  });
}

export async function streamFourPillarsReviewAspectUnlock(
  accessToken: string,
  reviewId: string,
  aspectKey: string,
  handlers: FourPillarsAspectStreamHandlers = {},
): Promise<FourPillarsAspectStreamCompleteData> {
  const headers = new Headers();
  headers.set('Accept', 'text/event-stream');
  headers.set('X-Client-Platform', 'h5');
  headers.set('X-Client-Channel', 'h5');
  headers.set('X-Client-Version', 'easewise-local-frontend');
  headers.set('Authorization', `Bearer ${accessToken}`);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/aspect-unlocks/${encodeURIComponent(aspectKey)}/stream`,
    {
      method: 'POST',
      headers,
      signal: handlers.signal,
    },
  );

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
  let completePayload: FourPillarsAspectStreamCompleteData | null = null;

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
    const payload = tryParseJson(dataLines.join('\n'));
    if (!payload || typeof payload !== 'object') {
      return;
    }

    if (eventName === 'unlock') {
      handlers.onUnlock?.(payload as FourPillarsAspectStreamUnlockData);
      return;
    }
    if (eventName === 'status') {
      handlers.onStatus?.(payload as FourPillarsAspectStreamStatusData);
      return;
    }
    if (eventName === 'delta') {
      handlers.onDelta?.(payload as FourPillarsAspectStreamDeltaData);
      return;
    }
    if (eventName === 'complete') {
      completePayload = payload as FourPillarsAspectStreamCompleteData;
      handlers.onComplete?.(completePayload);
      return;
    }
    if (eventName === 'error') {
      const errorPayload = payload as FourPillarsAspectStreamErrorData;
      handlers.onError?.(errorPayload);
      const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
      throw new ApiError(status, errorPayload.detail || 'aspect_generation_failed', errorPayload);
    }
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
  if (!completePayload) {
    throw new ApiError(409, 'aspect_generation_incomplete', null);
  }
  return completePayload;
}

export function getFourPillarsLuckCycles(accessToken: string, reviewId: string): Promise<FourPillarsLuckCycleListResponse> {
  return requestJson<FourPillarsLuckCycleListResponse>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles`, {
    accessToken,
  });
}

export function createFourPillarsLuckCycleSummary(accessToken: string, reviewId: string, cycleKey: string): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/summary`, {
    method: 'POST',
    accessToken,
  });
}

export function getFourPillarsLuckCycleSummary(accessToken: string, reviewId: string, cycleKey: string): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/summary`, {
    accessToken,
  });
}

export function createFourPillarsLuckYearSummary(accessToken: string, reviewId: string, cycleKey: string, year: number): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/years/${encodeURIComponent(String(year))}`, {
    method: 'POST',
    accessToken,
  });
}

export function getFourPillarsLuckYearSummary(accessToken: string, reviewId: string, cycleKey: string, year: number): Promise<FourPillarsLuckRenderRecord> {
  return requestJson<FourPillarsLuckRenderRecord>(`/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/years/${encodeURIComponent(String(year))}`, {
    accessToken,
  });
}

async function streamFourPillarsLuckRender(
  accessToken: string,
  path: string,
  handlers: FourPillarsLuckStreamHandlers = {},
): Promise<FourPillarsLuckStreamCompleteData> {
  const headers = new Headers();
  headers.set('Accept', 'text/event-stream');
  headers.set('X-Client-Platform', 'h5');
  headers.set('X-Client-Channel', 'h5');
  headers.set('X-Client-Version', 'easewise-local-frontend');
  headers.set('Authorization', `Bearer ${accessToken}`);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers,
    signal: handlers.signal,
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
  let completePayload: FourPillarsLuckStreamCompleteData | null = null;

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
    const payload = tryParseJson(dataLines.join('\n'));
    if (!payload || typeof payload !== 'object') {
      return;
    }

    if (eventName === 'render') {
      handlers.onRender?.(payload as FourPillarsLuckStreamRenderData);
      return;
    }
    if (eventName === 'status') {
      handlers.onStatus?.(payload as FourPillarsLuckStreamStatusData);
      return;
    }
    if (eventName === 'delta') {
      handlers.onDelta?.(payload as FourPillarsLuckStreamDeltaData);
      return;
    }
    if (eventName === 'complete') {
      completePayload = payload as FourPillarsLuckStreamCompleteData;
      handlers.onComplete?.(completePayload);
      return;
    }
    if (eventName === 'error') {
      const errorPayload = payload as FourPillarsLuckStreamErrorData;
      handlers.onError?.(errorPayload);
      const status = errorPayload.detail === 'insufficient_points' ? 402 : 409;
      throw new ApiError(status, errorPayload.detail || 'luck_generation_failed', errorPayload);
    }
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
  if (!completePayload) {
    throw new ApiError(409, 'luck_generation_incomplete', null);
  }
  return completePayload;
}

export function streamFourPillarsLuckCycleSummary(
  accessToken: string,
  reviewId: string,
  cycleKey: string,
  handlers: FourPillarsLuckStreamHandlers = {},
): Promise<FourPillarsLuckStreamCompleteData> {
  return streamFourPillarsLuckRender(
    accessToken,
    `/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/summary/stream`,
    handlers,
  );
}

export function streamFourPillarsLuckYearSummary(
  accessToken: string,
  reviewId: string,
  cycleKey: string,
  year: number,
  handlers: FourPillarsLuckStreamHandlers = {},
): Promise<FourPillarsLuckStreamCompleteData> {
  return streamFourPillarsLuckRender(
    accessToken,
    `/api/v1/four-pillars/reviews/${encodeURIComponent(reviewId)}/luck-cycles/${encodeURIComponent(cycleKey)}/years/${encodeURIComponent(String(year))}/stream`,
    handlers,
  );
}

export function createVoiceNarration(accessToken: string, payload: VoiceNarrationRequest): Promise<VoiceNarrationResponse> {
  return requestJson<VoiceNarrationResponse>('/api/v1/voice/narrations', {
    method: 'POST',
    accessToken,
    body: payload,
  });
}

type QueryValue = string | number | boolean | null | undefined;

export function getInternalDashboard(adminToken: string, params: Record<string, QueryValue> = {}): Promise<DashboardResponse> {
  return requestJson<DashboardResponse>(`/api/v1/internal/dashboard${toQueryString(params)}`, {
    adminToken,
  });
}

export function listInternalLlmApiKeys(adminToken: string, params: Record<string, QueryValue> = {}): Promise<LlmApiKeyListResponse> {
  return requestJson<LlmApiKeyListResponse>(`/api/v1/internal/llm/api-keys${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalLlmConcurrency(adminToken: string): Promise<LlmConcurrencyStatusResponse> {
  return requestJson<LlmConcurrencyStatusResponse>('/api/v1/internal/llm/concurrency', {
    adminToken,
  });
}

export type InternalLlmApiKeyPayload = {
  provider: string;
  model: string;
  display_name: string;
  masked_key?: string | null;
  secret_ref?: string | null;
  secret_value?: string | null;
  enabled: boolean;
  priority: number;
  max_concurrency?: number;
  cooldown_seconds?: number;
  remark?: string | null;
  last_operator?: string | null;
};

export function createInternalLlmApiKey(adminToken: string, payload: InternalLlmApiKeyPayload): Promise<LlmApiKeyResponse> {
  return requestJson<LlmApiKeyResponse>('/api/v1/internal/llm/api-keys', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function updateInternalLlmApiKey(adminToken: string, keyId: string, payload: InternalLlmApiKeyPayload): Promise<LlmApiKeyResponse> {
  return requestJson<LlmApiKeyResponse>(`/api/v1/internal/llm/api-keys/${encodeURIComponent(keyId)}`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function deleteInternalLlmApiKey(adminToken: string, keyId: string): Promise<{status: string}> {
  return requestJson<{status: string}>(`/api/v1/internal/llm/api-keys/${encodeURIComponent(keyId)}`, {
    method: 'DELETE',
    adminToken,
  });
}

export function listInternalUsageRecords(adminToken: string, params: Record<string, QueryValue>): Promise<UsageRecordListResponse> {
  return requestJson<UsageRecordListResponse>(`/api/v1/internal/platform/usage-records${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalUsageRecord(adminToken: string, usageRecordId: string): Promise<UsageRecordDetailResponse> {
  return requestJson<UsageRecordDetailResponse>(`/api/v1/internal/platform/usage-records/${encodeURIComponent(usageRecordId)}`, {
    adminToken,
  });
}

export function getInternalPhoneQimenSummary(adminToken: string): Promise<InternalPhoneQimenSummaryResponse> {
  return requestJson<InternalPhoneQimenSummaryResponse>('/api/v1/internal/phone-qimen/summary', {
    adminToken,
  });
}

export function listInternalPhoneQimenReviews(adminToken: string, params: Record<string, QueryValue> = {}): Promise<InternalPhoneQimenReviewListResponse> {
  return requestJson<InternalPhoneQimenReviewListResponse>(`/api/v1/internal/phone-qimen/reviews${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPhoneQimenReview(adminToken: string, reviewId: string): Promise<InternalPhoneQimenReviewDetailResponse> {
  return requestJson<InternalPhoneQimenReviewDetailResponse>(`/api/v1/internal/phone-qimen/reviews/${encodeURIComponent(reviewId)}`, {
    adminToken,
  });
}

export function getInternalFourPillarsSummary(adminToken: string): Promise<InternalFourPillarsSummaryResponse> {
  return requestJson<InternalFourPillarsSummaryResponse>('/api/v1/internal/four-pillars/summary', {
    adminToken,
  });
}

export function listInternalFourPillarsReviews(adminToken: string, params: Record<string, QueryValue> = {}): Promise<InternalFourPillarsReviewListResponse> {
  return requestJson<InternalFourPillarsReviewListResponse>(`/api/v1/internal/four-pillars/reviews${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalFourPillarsReview(adminToken: string, reviewId: string): Promise<InternalFourPillarsReviewDetailResponse> {
  return requestJson<InternalFourPillarsReviewDetailResponse>(`/api/v1/internal/four-pillars/reviews/${encodeURIComponent(reviewId)}`, {
    adminToken,
  });
}

export function listInternalUsers(adminToken: string, queryOrParams?: string | Record<string, QueryValue>): Promise<InternalUserListResponse> {
  const params = typeof queryOrParams === 'string' ? {query: queryOrParams} : (queryOrParams || {});
  return requestJson<InternalUserListResponse>(`/api/v1/internal/users${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalUserAdminSummary(adminToken: string, userId: string): Promise<InternalUserAdminSummaryResponse> {
  return requestJson<InternalUserAdminSummaryResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/admin-summary`, {
    adminToken,
  });
}

export function listInternalRechargeOrders(adminToken: string, params: Record<string, QueryValue>): Promise<RechargeOrderListResponse> {
  return requestJson<RechargeOrderListResponse>(`/api/v1/internal/billing/recharge-orders${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalRechargeOrder(adminToken: string, orderId: string): Promise<RechargeOrderResponse> {
  return requestJson<RechargeOrderResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}`, {
    adminToken,
  });
}

export function reviewInternalRechargeOrder(adminToken: string, orderId: string, payload: {action: 'approve' | 'reject'; review_note?: string | null}): Promise<RechargeOrderReviewResponse> {
  return requestJson<RechargeOrderReviewResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function manualCompleteInternalRechargeOrder(adminToken: string, orderId: string, payload: {payment_method?: string | null; payment_reference?: string | null; operator_note?: string | null}): Promise<RechargeOrderManualCompleteResponse> {
  return requestJson<RechargeOrderManualCompleteResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}/manual-complete`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function createInternalRechargeOrderRefund(adminToken: string, orderId: string, payload: {reason?: string | null; operator_note?: string | null}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/billing/recharge-orders/${encodeURIComponent(orderId)}/refunds`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function reviewInternalRefund(adminToken: string, refundId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; operator_note?: string | null}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/billing/refunds/${encodeURIComponent(refundId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function retryInternalRefund(adminToken: string, refundId: string, payload: {operator_note?: string | null} = {}): Promise<RefundRequestResponse> {
  return requestJson<RefundRequestResponse>(`/api/v1/internal/billing/refunds/${encodeURIComponent(refundId)}/retry`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function adjustInternalUserPoints(adminToken: string, userId: string, payload: {delta: number; biz_type?: string | null; biz_id?: string | null; idempotency_key?: string | null; remark?: string | null; reason?: string | null; operator_note?: string | null}): Promise<ManualPointsAdjustResponse> {
  return requestJson<ManualPointsAdjustResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/points/adjust`, {
    method: 'POST',
    adminToken,
    body: {
      biz_type: 'admin_manual_adjust',
      ...payload,
    },
  });
}

export function adjustInternalUserRebatePoints(adminToken: string, userId: string, payload: {delta: number; reason?: string | null; operator_note?: string | null}): Promise<RebatePointsAdjustResponse> {
  return requestJson<RebatePointsAdjustResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/rebate-points/adjust`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalPointsClaimLinks(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PointsClaimLinkListResponse> {
  return requestJson<PointsClaimLinkListResponse>(`/api/v1/internal/points-claims${toQueryString(params)}`, {
    adminToken,
  });
}

export function createInternalPointsClaimLink(adminToken: string, payload: {title: string; points_amount: number; display_value_cents: number; expires_in_hours?: number | null; expires_at?: string | null; operator_note?: string | null}): Promise<PointsClaimLinkResponse> {
  return requestJson<PointsClaimLinkResponse>('/api/v1/internal/points-claims', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function getInternalPointsClaimLink(adminToken: string, claimLinkId: string): Promise<PointsClaimLinkResponse> {
  return requestJson<PointsClaimLinkResponse>(`/api/v1/internal/points-claims/${encodeURIComponent(claimLinkId)}`, {
    adminToken,
  });
}

export function disableInternalPointsClaimLink(adminToken: string, claimLinkId: string, payload: {operator_note?: string | null} = {}): Promise<PointsClaimLinkResponse> {
  return requestJson<PointsClaimLinkResponse>(`/api/v1/internal/points-claims/${encodeURIComponent(claimLinkId)}/disable`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalPointsClaimRecords(adminToken: string, claimLinkId: string, params: Record<string, QueryValue> = {}): Promise<PointsClaimRecordListResponse> {
  return requestJson<PointsClaimRecordListResponse>(`/api/v1/internal/points-claims/${encodeURIComponent(claimLinkId)}/records${toQueryString(params)}`, {
    adminToken,
  });
}

export function updateInternalUserStatus(adminToken: string, userId: string, payload: {status: string; reason?: string | null; operator_note?: string | null}): Promise<InternalUserResponse> {
  return requestJson<InternalUserResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/status`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function updateInternalUserIdentity(adminToken: string, userId: string, payload: {identity_level: string; reason?: string | null; operator_note?: string | null}): Promise<InternalUserResponse> {
  return requestJson<InternalUserResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/identity`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function updateInternalUserPromoterParent(adminToken: string, userId: string, payload: {promoter_parent_user_id?: string | null; reason?: string | null; operator_note?: string | null}): Promise<InternalUserResponse> {
  return requestJson<InternalUserResponse>(`/api/v1/internal/users/${encodeURIComponent(userId)}/promoter-parent`, {
    method: 'PATCH',
    adminToken,
    body: payload,
  });
}

export function listInternalPromotionApplications(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PromotionApplicationListResponse> {
  return requestJson<PromotionApplicationListResponse>(`/api/v1/internal/promotion/applications${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPromotionApplication(adminToken: string, applicationId: string): Promise<PromotionApplicationResponse> {
  return requestJson<PromotionApplicationResponse>(`/api/v1/internal/promotion/applications/${encodeURIComponent(applicationId)}`, {
    adminToken,
  });
}

export function reviewInternalPromotionApplication(adminToken: string, applicationId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; review_note?: string | null; operator_note?: string | null}): Promise<PromotionApplicationResponse> {
  return requestJson<PromotionApplicationResponse>(`/api/v1/internal/promotion/applications/${encodeURIComponent(applicationId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function listInternalPromotionCommissions(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PromotionCommissionListResponse> {
  return requestJson<PromotionCommissionListResponse>(`/api/v1/internal/promotion/commissions${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPromotionCommission(adminToken: string, commissionId: string): Promise<PromotionCommissionResponse> {
  return requestJson<PromotionCommissionResponse>(`/api/v1/internal/promotion/commissions/${encodeURIComponent(commissionId)}`, {
    adminToken,
  });
}

export function listInternalPromotionWithdrawals(adminToken: string, params: Record<string, QueryValue> = {}): Promise<PromotionWithdrawalListResponse> {
  return requestJson<PromotionWithdrawalListResponse>(`/api/v1/internal/promotion/withdrawals${toQueryString(params)}`, {
    adminToken,
  });
}

export function getInternalPromotionWithdrawal(adminToken: string, withdrawalId: string): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}`, {
    adminToken,
  });
}

export function reviewInternalPromotionWithdrawal(adminToken: string, withdrawalId: string, payload: {action: 'approve' | 'reject'; reject_reason?: string | null; review_note?: string | null; operator_note?: string | null}): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}/review`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function retryInternalPromotionWithdrawalPayout(adminToken: string, withdrawalId: string, payload: {operator_note?: string | null} = {}): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}/retry-payout`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function markInternalPromotionWithdrawalPaid(adminToken: string, withdrawalId: string, payload: {payout_method?: string | null; payout_proof?: string | null; operator_note?: string | null}): Promise<PromotionWithdrawalResponse> {
  return requestJson<PromotionWithdrawalResponse>(`/api/v1/internal/promotion/withdrawals/${encodeURIComponent(withdrawalId)}/mark-paid`, {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function getInternalPromotionRules(adminToken: string): Promise<PromotionRulesResponse> {
  return requestJson<PromotionRulesResponse>('/api/v1/internal/promotion/rules', {
    adminToken,
  });
}

export function updateInternalPromotionRules(adminToken: string, payload: Partial<PromotionRulesResponse>): Promise<PromotionRulesResponse> {
  return requestJson<PromotionRulesResponse>('/api/v1/internal/promotion/rules', {
    method: 'PUT',
    adminToken,
    body: payload,
  });
}

export function listInternalRuntimeConfig(adminToken: string, params: Record<string, QueryValue> = {}): Promise<RuntimeConfigListResponse> {
  return requestJson<RuntimeConfigListResponse>(`/api/v1/internal/runtime-config${toQueryString(params)}`, {
    adminToken,
  });
}

export function updateInternalRuntimeConfig(adminToken: string, entries: RuntimeConfigEntryUpsertRequest[]): Promise<RuntimeConfigListResponse> {
  return requestJson<RuntimeConfigListResponse>('/api/v1/internal/runtime-config', {
    method: 'PUT',
    adminToken,
    body: {
      entries,
    },
  });
}

export function updateInternalInitialPointsConfig(adminToken: string, payload: RuntimeInitialPointsUpdateRequest): Promise<RuntimeInitialPointsUpdateResponse> {
  return requestJson<RuntimeInitialPointsUpdateResponse>('/api/v1/internal/runtime-config/initial-points', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function getInternalRuntimeConfigSchema(adminToken: string): Promise<RuntimeConfigSchemaResponse> {
  return requestJson<RuntimeConfigSchemaResponse>('/api/v1/internal/runtime-config/schema', {
    adminToken,
  });
}

export function uploadInternalCustomerServiceQrCode(adminToken: string, payload: {image_data_url: string}): Promise<RuntimeConfigEntryResponse> {
  return requestJson<RuntimeConfigEntryResponse>('/api/v1/internal/customer-service/qr-code', {
    method: 'POST',
    adminToken,
    body: payload,
  });
}

export function deleteInternalCustomerServiceQrCode(adminToken: string): Promise<RuntimeConfigEntryResponse> {
  return requestJson<RuntimeConfigEntryResponse>('/api/v1/internal/customer-service/qr-code', {
    method: 'DELETE',
    adminToken,
  });
}

function toQueryString(params: Record<string, QueryValue>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) {
      continue;
    }
    const normalizedValue = String(value).trim();
    if (normalizedValue) {
      searchParams.set(key, normalizedValue);
    }
  }
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}
```

### `src/types/api.ts`

```ts
export type Gender = 'male' | 'female';
export type ReviewStatus = 'processing' | 'completed' | 'failed' | 'retryable';
export type ReviewProgressStage = 'queued' | 'scoring' | 'rendering' | 'finalizing' | 'completed' | 'failed';
export type VoiceNarrationScene = 'phone_summary' | 'phone_stability' | 'phone_aspect';
export type VoiceNarrationFormat = 'mp3';
export type VoiceMode = 'hybrid' | 'browser' | 'cloud';

export interface ReviewPhoneSummary {
  title: string;
  risk: string;
  usage_guidance: string;
  elements_check: Record<string, string>;
}

export interface ReviewStabilityDetail {
  verdict: string;
  content: string;
  elements_check: Record<string, string>;
}

export interface ReviewBoardCenterBasis {
  trigger: string;
}

export interface ReviewBoardActiveBasis {
  palace: string;
  direction: string | null;
  god: string;
  star: string;
  door: string;
  heaven_stem: string;
  earth_stem: string;
}

export interface ReviewBoardGridCell {
  slot_id: string;
  palace_key: string;
  palace_name: string;
  direction: string | null;
  wuxing: string | null;
  is_active: boolean;
}

export interface ReviewBoardRelations {
  palace_door_relation: string | null;
  stem_pair_relation: string | null;
}

export interface ReviewBoardFourHarms {
  emptiness: string;
  door_pressure: string;
  tomb: string;
  punishment_hit: string;
}

export interface ReviewBoardRisks {
  four_harms: ReviewBoardFourHarms;
  pattern_flags: string[];
  risk_pairs: string[];
  structural_cap_reasons: string[];
}

export interface ReviewBoard {
  center_basis: ReviewBoardCenterBasis;
  active_basis: ReviewBoardActiveBasis | null;
  grid_cells: ReviewBoardGridCell[];
  relations: ReviewBoardRelations | null;
  risks: ReviewBoardRisks | null;
}

export interface ReviewAspect {
  aspect_key: string;
  title: string;
  short_title: string | null;
  score: number | null;
  is_unlocked: boolean;
  unlock_points: number;
  content: string | null;
  risk: string | null;
  elements_check: Record<string, string>;
}

export interface ReviewRecord {
  id: string;
  report_id: string;
  phone: string;
  phone_number: string;
  masked_phone: string;
  gender: Gender;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  score: number | null;
  phone_summary?: ReviewPhoneSummary | null;
  board: ReviewBoard | null;
  stability_detail?: ReviewStabilityDetail | null;
  aspects: ReviewAspect[];
  aspect_unlock_points: number | null;
  free_aspect_keys: string[];
  unlock_enforcement_enabled: boolean | null;
  score_markdown: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewSummary {
  id: string;
  report_id: string;
  phone: string;
  phone_number: string;
  masked_phone: string;
  gender: Gender;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  score: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewListResponse {
  items: ReviewSummary[];
  total: number;
  limit: number;
  offset: number;
}

export type PhoneReviewCoreStreamSection = 'phone_summary' | 'stability' | string;
export type PhoneReviewCoreStreamDeltaField = 'title' | 'risk' | 'usage_guidance' | 'verdict' | 'content' | string;

export interface PhoneReviewCoreStreamReviewData {
  review: ReviewRecord;
  points: PointsAccountResponse | null;
}

export type PhoneReviewCoreStreamCreatedData = PhoneReviewCoreStreamReviewData;
export type PhoneReviewCoreStreamFactsReadyData = PhoneReviewCoreStreamReviewData;
export type PhoneReviewCoreStreamCompleteData = PhoneReviewCoreStreamReviewData;

export interface PhoneReviewCoreStreamStatusData {
  section: PhoneReviewCoreStreamSection;
  message: string;
}

export interface PhoneReviewCoreStreamDeltaData {
  section: PhoneReviewCoreStreamSection;
  field: PhoneReviewCoreStreamDeltaField;
  delta: string;
  text: string;
}

export interface PhoneReviewCoreStreamSectionCompleteData {
  section: PhoneReviewCoreStreamSection;
  payload: Record<string, unknown>;
  model_name?: string | null;
}

export interface PhoneReviewCoreStreamErrorData {
  detail: string;
  message?: string;
  refunded?: boolean;
}

export interface FourPillarsSummaryJudgement {
  key: string;
  label: string;
  title: string;
  content: string;
  basis?: string;
  level?: string;
}

export interface FourPillarsSummaryRiskWindow {
  age_range: string;
  year_range: string;
  risk_type: string;
  trigger: string;
  guidance: string;
  level?: string;
}

export interface FourPillarsSummaryTimeHighlight {
  year: string;
  age?: string;
  title: string;
  content: string;
  trigger?: string;
}

export interface FourPillarsSummaryFavorableStrategy {
  favorable_elements?: string[];
  unfavorable_elements?: string[];
  supportive_environments?: string[];
  avoid_patterns?: string[];
  action_guidance?: string;
}

export interface FourPillarsSummary {
  title: string;
  comprehensive_text?: string;
  overview?: string;
  risk: string;
  usage_guidance: string;
  key_judgements?: FourPillarsSummaryJudgement[];
  life_risk_windows?: FourPillarsSummaryRiskWindow[];
  time_highlights?: FourPillarsSummaryTimeHighlight[];
  favorable_strategy?: FourPillarsSummaryFavorableStrategy;
  elements_check: Record<string, string>;
}

export type FourPillarsPillarKey = 'year' | 'month' | 'day' | 'hour';

export interface FourPillarsDisplayHiddenStem {
  stem: string;
  element: string;
  ten_god: string;
}

export interface FourPillarsShenShaDetail {
  name: string;
  category: string;
  basis: string;
  basis_value: string;
  target: string;
  target_value: string;
  rule: string;
  meaning: string;
}

export interface FourPillarsDisplayPillar {
  key: FourPillarsPillarKey;
  label: string;
  ganzhi: string;
  stem: string;
  branch: string;
  stem_element: string;
  branch_element: string;
  stem_ten_god: string;
  branch_ten_gods: string[];
  hidden_stems: FourPillarsDisplayHiddenStem[];
  na_yin: string;
  xun_kong: string;
  di_shi: string;
  self_sitting: string;
  shen_sha: string[];
  shen_sha_details?: FourPillarsShenShaDetail[];
}

export interface FourPillarsChartDisplay {
  profile: {
    name?: string | null;
    gender_label: string;
    structure_label?: string | null;
    zodiac: string | null;
    solar_datetime_text: string;
    lunar_date: string;
    lunar_full_text: string | null;
    birth_place: string | null;
    timezone: string;
    solar_term_context: string | null;
    input_mode?: string | null;
    standard_birth_datetime?: string | null;
    effective_birth_datetime?: string | null;
    true_solar_time?: Record<string, unknown> | null;
    birth_location?: Record<string, unknown> | null;
    true_solar_time_text?: string | null;
    constellation?: string | null;
    xiu?: string | null;
    tai_yuan?: string | null;
    tai_xi?: string | null;
    ming_gong?: string | null;
    shen_gong?: string | null;
    life_gua?: string | null;
    empty_branches_text?: string | null;
    pillar_xun_kong_text?: string | null;
    bone_weight?: {
      total_qian: number;
      total_label: string;
      summary: string;
      fate_pattern?: string | null;
      verse?: string | null;
      year_ganzhi: string;
      lunar_month: number;
      lunar_day: number;
      hour_branch: string;
      parts: Record<string, number>;
      rules: Record<string, string>;
      sources: Array<{ title: string; url: string }>;
    } | null;
  };
  pillars: Record<FourPillarsPillarKey, FourPillarsDisplayPillar>;
  element_status: Array<{
    element: '木' | '火' | '土' | '金' | '水';
    status: '旺' | '相' | '休' | '囚' | '死' | '';
  }>;
}

export interface FourPillarsAspect {
  aspect_key: string;
  title: string;
  short_title: string | null;
  is_unlocked: boolean;
  unlock_points: number;
  content: string | null;
  risk: string | null;
  elements_check: Record<string, string>;
}

export interface FourPillarsLuckRenderRecord {
  id: string;
  render_id: string;
  review_id: string;
  user_id: string;
  render_type: 'dayun' | 'liunian';
  cycle_key: string;
  year: number | null;
  status: ReviewStatus;
  progress_message: string | null;
  facts: Record<string, unknown> | null;
  result: Record<string, unknown> | null;
  points_cost: number;
  error_message: string | null;
  retry_count: number;
  last_attempt_at: string | null;
  next_retry_available_at: string | null;
  is_retryable: boolean;
  created_at: string;
  updated_at: string;
}

export interface FourPillarsLuckYearItem {
  year: number;
  age: number | null;
  ganzhi: string;
  stem?: string | null;
  branch?: string | null;
  stem_ten_god?: string | null;
  stem_element?: string | null;
  branch_element?: string | null;
  di_shi?: string | null;
  xun_kong?: string | null;
  shen_sha?: string[];
  shen_sha_details?: FourPillarsShenShaDetail[];
  is_current: boolean;
  render_status: 'not_generated' | ReviewStatus | string;
  render: FourPillarsLuckRenderRecord | null;
}

export interface FourPillarsLuckCycle {
  cycle_key: string;
  start_year: number;
  end_year: number;
  start_age: number | null;
  end_age: number | null;
  ganzhi: string | null;
  display_ganzhi: string | null;
  is_current: boolean;
  stem?: string | null;
  branch?: string | null;
  stem_ten_god?: string | null;
  stem_element?: string | null;
  branch_element?: string | null;
  di_shi?: string | null;
  xun_kong?: string | null;
  shen_sha?: string[];
  shen_sha_details?: FourPillarsShenShaDetail[];
  render_status: 'not_generated' | ReviewStatus | string;
  render: FourPillarsLuckRenderRecord | null;
  year_items: FourPillarsLuckYearItem[];
}

export interface FourPillarsLuckAnalysis {
  enabled: boolean;
  cycle_points_cost: number;
  year_points_cost: number;
  current_cycle_key: string | null;
  cycles: FourPillarsLuckCycle[];
}

export interface FourPillarsLuckCycleListResponse {
  luck_analysis: FourPillarsLuckAnalysis;
}

export type FourPillarsLuckStreamDeltaField =
  | 'title'
  | 'trend_tendency'
  | 'core_theme'
  | 'opportunities'
  | 'risks'
  | 'action_guidance'
  | 'year_focus'
  | string;

export interface FourPillarsLuckStreamRenderData {
  render: FourPillarsLuckRenderRecord;
  points: PointsAccountResponse | null;
}

export interface FourPillarsLuckStreamStatusData {
  message: string;
}

export interface FourPillarsLuckStreamDeltaData {
  field: FourPillarsLuckStreamDeltaField;
  delta: string;
  text: string;
}

export interface FourPillarsLuckStreamCompleteData {
  render: FourPillarsLuckRenderRecord;
  luck_analysis: FourPillarsLuckAnalysis;
  points: PointsAccountResponse | null;
}

export interface FourPillarsLuckStreamErrorData {
  detail: string;
  message?: string;
  refunded?: boolean;
}

export interface FourPillarsCreatePayload {
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone?: string | null;
  birth_place?: string | null;
  name?: string | null;
  input_mode?: 'solar' | 'lunar' | 'bazi' | string | null;
  calendar_input?: Record<string, unknown> | null;
  lunar_input?: Record<string, unknown> | null;
  bazi_input?: Record<string, unknown> | null;
  birth_location?: Record<string, unknown> | null;
  include_markdown?: boolean;
}

export interface FourPillarsReviewRecord {
  id: string;
  report_id: string;
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birth_place: string | null;
  name: string | null;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  input_profile: Record<string, unknown>;
  chart: Record<string, unknown> | null;
  chart_display: FourPillarsChartDisplay | null;
  summary: FourPillarsSummary | null;
  deterministic_facts: Record<string, unknown>;
  aspects: FourPillarsAspect[];
  analysis_branches: Record<string, unknown>;
  luck_analysis: FourPillarsLuckAnalysis | null;
  aspect_unlock_points: number | null;
  free_aspect_keys: string[];
  unlock_enforcement_enabled: boolean | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface FourPillarsReviewSummary {
  id: string;
  report_id: string;
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birth_place: string | null;
  name: string | null;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface FourPillarsReviewListResponse {
  items: FourPillarsReviewSummary[];
  total: number;
  limit: number;
  offset: number;
}

export type FourPillarsCoreStreamSection = 'four_pillars_summary' | string;
export type FourPillarsCoreStreamDeltaField = 'title' | 'comprehensive_text' | 'overview' | 'risk' | 'usage_guidance' | string;

export interface FourPillarsCoreStreamReviewData {
  review: FourPillarsReviewRecord;
  points: PointsAccountResponse | null;
}

export type FourPillarsCoreStreamCreatedData = FourPillarsCoreStreamReviewData;
export type FourPillarsCoreStreamFactsReadyData = FourPillarsCoreStreamReviewData;
export type FourPillarsCoreStreamCompleteData = FourPillarsCoreStreamReviewData;

export interface FourPillarsCoreStreamStatusData {
  section: FourPillarsCoreStreamSection;
  message: string;
}

export interface FourPillarsCoreStreamDeltaData {
  section: FourPillarsCoreStreamSection;
  field: FourPillarsCoreStreamDeltaField;
  delta: string;
  text: string;
}

export interface FourPillarsCoreStreamSectionCompleteData {
  section: FourPillarsCoreStreamSection;
  payload: Record<string, unknown>;
  model_name?: string | null;
}

export interface FourPillarsCoreStreamErrorData {
  detail: string;
  message?: string;
  refunded?: boolean;
}

export interface FourPillarsAspectUnlockResponse {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  points: PointsAccountResponse | null;
  aspect: FourPillarsAspect | null;
}

export interface FourPillarsAspectUnlockListResponse {
  items: FourPillarsAspectUnlockResponse[];
  available_aspect_keys: string[];
  free_aspect_keys: string[];
  unlocked_aspect_keys: string[];
  aspect_unlock_points_cost: number;
  unlock_enforcement_enabled: boolean;
  aspects: FourPillarsAspect[];
}

export interface AlmanacResponse {
  solar_date: string;
  display_date: string;
  weekday_label: string;
  lunar_date: string;
  lunar_full_text: string;
  ganzhi_year: string;
  ganzhi_month: string;
  ganzhi_day: string;
  zodiac_year: string;
  zodiac_month: string;
  zodiac_day: string;
  yi: string[];
  ji: string[];
  yi_summary: string;
  ji_summary: string;
  solar_term: string | null;
  festivals: string[];
  pengzu_gan: string;
  pengzu_zhi: string;
  pengzu_summary: string;
  chong: string;
  sha: string;
  zhi_xing: string;
  tian_shen: string;
  tian_shen_luck: string;
  ji_shen: string[];
  xiong_sha: string[];
}

export interface DashboardMetric {
  label: string;
  value: number;
  display_value: string;
  unit: string | null;
  trend_value: number | null;
  trend_label: string | null;
}

export interface DashboardSection {
  title: string;
  summary: string | null;
  metrics: DashboardMetric[];
}

export interface DashboardResponse {
  generated_at: string;
  revenue: Record<string, unknown>;
  users: Record<string, unknown>;
  orders: Record<string, unknown>;
  promotion: Record<string, unknown>;
  llm: Record<string, unknown>;
  sections: DashboardSection[];
}

export interface UserResponse {
  user_id: string;
  uid: string | null;
  status: string;
  identity_level: string;
  nickname: string | null;
  avatar_url: string | null;
  profile_completed: boolean;
  created_at: string;
  updated_at: string;
  last_active_at: string;
}

export interface PointsAccountResponse {
  balance: number;
  frozen_balance: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface PointsLedgerEntryResponse {
  ledger_id: string;
  change_type: string;
  delta: number;
  balance_after: number;
  biz_type: string;
  biz_id: string | null;
  idempotency_key: string | null;
  remark: string | null;
  created_at: string;
}

export interface PointsLedgerListResponse {
  items: PointsLedgerEntryResponse[];
}

export interface PointsClaimLinkResponse {
  claim_link_id: string;
  claim_code: string;
  claim_url: string;
  title: string;
  points_amount: number;
  display_value_cents: number;
  status: string;
  effective_status: string;
  valid_from: string;
  expires_at: string;
  claimed_user_count: number;
  granted_points_total: number;
  duplicate_attempt_count: number;
  created_by: string | null;
  disabled_by: string | null;
  disabled_at: string | null;
  operator_note: string | null;
  created_at: string;
  updated_at: string;
}

export interface PointsClaimLinkListResponse {
  items: PointsClaimLinkResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PointsClaimRecordResponse {
  claim_record_id: string;
  claim_link_id: string;
  claim_code: string | null;
  claim_title: string | null;
  user_id: string;
  user_uid: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  week_key: string;
  week_starts_at: string;
  status: string;
  points_amount_snapshot: number;
  display_value_cents_snapshot: number;
  ledger_id: string | null;
  failure_reason: string | null;
  request_ip: string | null;
  user_agent: string | null;
  created_at: string;
  updated_at: string;
}

export interface PointsClaimRecordListResponse {
  items: PointsClaimRecordResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PublicPointsClaimLinkResponse {
  claim_code: string;
  title: string;
  points_amount: number;
  display_value_cents: number;
  status: string;
  effective_status: string;
  valid_from: string;
  expires_at: string;
  current_user_claim_status: string | null;
  current_user_claim_record: PointsClaimRecordResponse | null;
}

export interface PointsClaimSubmitResponse {
  claim_status: string;
  message: string;
  points: PointsAccountResponse | null;
  ledger: PointsLedgerEntryResponse | null;
  record: PointsClaimRecordResponse | null;
  already_claimed_record: PointsClaimRecordResponse | null;
}

export interface RechargePackageResponse {
  package_key: string;
  title: string;
  description: string | null;
  price_cents: number;
  points_amount: number;
  bonus_points: number;
  total_points: number;
  enabled: boolean;
  sort_order: number;
}

export interface RechargePackageListResponse {
  items: RechargePackageResponse[];
}

export interface ModuleRuntimeConfigResponse {
  enabled: boolean;
  base_points_cost: number | null;
  aspect_unlock_points_cost?: number | null;
  free_aspect_keys?: string[] | null;
  aspect_order?: string[] | null;
  unlock_enforcement_enabled?: boolean | null;
  luck_cycle_points_cost?: number | null;
  luck_year_points_cost?: number | null;
  luck_generation_enabled?: boolean | null;
  metaphysics_skill_enabled?: boolean | null;
}

export interface VoiceRuntimeConfigResponse {
  enabled: boolean;
  mode: VoiceMode;
  autoplay_default_enabled: boolean;
  provider: string;
  default_voice_key: string;
  cache_enabled: boolean;
  max_chars_per_request: number;
}

export interface PublicRuntimeConfigResponse {
  channel: string | null;
  points: {
    initial_grant: number;
  };
  recharge: {
    packages: RechargePackageResponse[];
  };
  customer_service: {
    wechat_id: string | null;
    contact_url: string | null;
    qr_code_url: string | null;
    guidance_text: string;
    qr_guidance_text: string;
    copy_button_text: string;
    unconfigured_text: string;
    copy: Record<string, string>;
  };
  compliance: {
    safe_mode_enabled: boolean;
    safe_modules: string[];
    hidden_modules: string[];
    hidden_pages: string[];
  };
  modules: {
    phone_review: ModuleRuntimeConfigResponse;
    four_pillars: ModuleRuntimeConfigResponse;
    agent: ModuleRuntimeConfigResponse;
    almanac: ModuleRuntimeConfigResponse;
    voice: VoiceRuntimeConfigResponse;
  };
}

export interface PhoneStatusRequest {
  phone: string;
}

export type VoiceNarrationRequest =
  | { scene: 'phone_summary'; review_id: string; voice_key?: string | null }
  | { scene: 'phone_stability'; review_id: string; voice_key?: string | null }
  | { scene: 'phone_aspect'; review_id: string; aspect_key: string; voice_key?: string | null };

export interface VoiceNarrationResponse {
  narration_id: string;
  scene: VoiceNarrationScene;
  text_hash: string;
  audio_url: string;
  provider: string;
  voice_key: string;
  format: VoiceNarrationFormat;
  char_count: number;
  cached: boolean;
}

export interface PhoneStatusResponse {
  registered: boolean;
  normalized_phone: string;
  next_action: 'login' | 'register';
}

export interface PhonePasswordRegisterRequest {
  phone: string;
  password: string;
  confirm_password: string;
}

export interface PhonePasswordLoginRequest {
  phone: string;
  password: string;
}

export interface UserProfileUpdateRequest {
  nickname?: string | null;
  avatar_url?: string | null;
}

export interface AvatarUploadRequest {
  image_data_url: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface PasswordChangeResponse {
  status: string;
}

export interface AuthLoginResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: UserResponse;
  points: PointsAccountResponse;
}

export interface CurrentUserResponse {
  user: UserResponse;
  points: PointsAccountResponse;
}

export interface ReviewAspectUnlockResponse {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  points: PointsAccountResponse | null;
  aspect: ReviewAspect | null;
}

export type PhoneReviewAspectStreamDeltaField = 'title' | 'risk' | 'content';

export interface PhoneReviewAspectStreamUnlockData {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  status: string;
  points: PointsAccountResponse | null;
}

export interface PhoneReviewAspectStreamStatusData {
  message: string;
}

export interface PhoneReviewAspectStreamDeltaData {
  field: PhoneReviewAspectStreamDeltaField;
  delta: string;
  text: string;
}

export interface PhoneReviewAspectStreamCompleteData {
  aspect: ReviewAspect | null;
  review: ReviewRecord;
  points: PointsAccountResponse | null;
}

export interface PhoneReviewAspectStreamErrorData {
  detail: string;
  message?: string;
  refunded?: boolean;
}

export type FourPillarsAspectStreamDeltaField = 'title' | 'risk' | 'content';

export interface FourPillarsAspectStreamUnlockData {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  points_cost: number;
  usage_record_id: string;
  unlocked_at: string;
  status: string;
  points: PointsAccountResponse | null;
}

export interface FourPillarsAspectStreamStatusData {
  message: string;
}

export interface FourPillarsAspectStreamDeltaData {
  field: FourPillarsAspectStreamDeltaField;
  delta: string;
  text: string;
}

export interface FourPillarsAspectStreamCompleteData {
  aspect: FourPillarsAspect | null;
  review: FourPillarsReviewRecord;
  points: PointsAccountResponse | null;
}

export interface FourPillarsAspectStreamErrorData {
  detail: string;
  message?: string;
  refunded?: boolean;
}

export interface InternalUserResponse {
  user_id: string;
  uid: string | null;
  status: string;
  identity_level: string;
  primary_identity_type: string;
  registered_channel: string | null;
  promoter_parent_user_id: string | null;
  nickname: string | null;
  avatar_url: string | null;
  profile_completed: boolean;
  points_balance: number;
  frozen_balance: number;
  withdrawable_balance_cents: number;
  frozen_commission_cents: number;
  withdrawn_amount_cents: number;
  rebate_points_balance: number;
  rebate_frozen_balance: number;
  primary_phone: string | null;
  phone_verified_at: string | null;
  primary_unionid: string | null;
  first_login_at: string;
  registered_at: string;
  created_at: string;
  updated_at: string;
  last_active_at: string;
  openid: string | null;
  unionid: string | null;
}

export interface InternalUserListResponse {
  items: InternalUserResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface RefundRequestResponse {
  refund_id: string;
  order_id: string;
  user_id: string;
  status: string;
  reason: string | null;
  operator_note: string | null;
  reject_reason: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  retry_count: number;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromotionCommissionResponse {
  commission_id: string;
  promoter_user_id: string;
  promoter_nickname: string | null;
  invited_user_id: string | null;
  invited_user_nickname: string | null;
  order_id: string | null;
  order_amount_cents: number;
  commission_rate: number;
  commission_amount_cents: number;
  commission_points: number;
  commission_type: string;
  status: string;
  remark: string | null;
  created_at: string;
  updated_at: string;
  settled_at: string | null;
  revoked_at: string | null;
}

export interface RechargeOrderResponse {
  order_id: string;
  user_id: string;
  user_status: string | null;
  user_nickname: string | null;
  channel: string | null;
  status: string;
  raw_status: string | null;
  package_key: string;
  package_title: string;
  amount_cents: number;
  points_amount: number;
  bonus_points: number;
  total_points: number;
  source: string;
  external_order_id: string | null;
  proof_url: string | null;
  remark: string | null;
  review_note: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  paid_at: string | null;
  completed_at: string | null;
  closed_at: string | null;
  refund_requests: RefundRequestResponse[];
  commission_records: PromotionCommissionResponse[];
  payment_transactions: PaymentTransactionResponse[];
  latest_payment: PaymentTransactionResponse | null;
  granted_ledger_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaymentTransactionResponse {
  transaction_id: string;
  order_id: string;
  user_id: string;
  provider: string;
  payment_method: string;
  amount_cents: number;
  status: string;
  provider_transaction_id: string | null;
  prepay_id: string | null;
  idempotency_key: string | null;
  payment_params: Record<string, unknown>;
  client_message: string | null;
  failure_reason: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RechargeOrderPaymentStatusResponse {
  order: RechargeOrderResponse;
  latest_payment: PaymentTransactionResponse | null;
}

export interface RechargeOrderListResponse {
  items: RechargeOrderResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface RechargeOrderReviewResponse {
  order: RechargeOrderResponse;
  points: PointsAccountResponse;
  ledger: PointsLedgerEntryResponse | null;
}

export interface RechargeOrderManualCompleteResponse {
  order: RechargeOrderResponse;
  points: PointsAccountResponse;
  ledger: PointsLedgerEntryResponse | null;
}

export interface RechargeOrderSummaryResponse {
  order_id: string;
  package_title: string;
  amount_cents: number;
  status: string;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  paid_at: string | null;
  completed_at: string | null;
}

export interface UsageRecordResponse {
  usage_record_id: string;
  user_id: string;
  scene: string;
  feature_key: string;
  feature_name: string | null;
  channel: string | null;
  target_id: string | null;
  points_cost: number;
  normal_points_cost: number;
  rebate_points_cost: number;
  status: string;
  user_status: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  user_avatar_url: string | null;
  request_payload_summary: Record<string, unknown> | null;
  result_summary: Record<string, unknown> | null;
  llm_key_id: string | null;
  llm_key_name: string | null;
  llm_model: string | null;
  llm_priority_class: string | null;
  llm_wait_ms: number | null;
  llm_duration_ms: number | null;
  llm_retry_count: number;
  llm_error_type: string | null;
  llm_error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface UsageRecordListResponse {
  items: UsageRecordResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternalUserAdminSummaryResponse {
  user: InternalUserResponse;
  recent_orders: RechargeOrderSummaryResponse[];
  recent_order_count: number;
  recent_recharge_amount_cents: number;
  latest_order_status: string | null;
  total_recharge_amount_cents: number;
  total_withdraw_amount_cents: number;
  promoter_parent_user_id: string | null;
  identity_level: string;
}

export interface UsageRecordDetailResponse {
  record: UsageRecordResponse;
  user: InternalUserResponse;
  recent_orders: RechargeOrderSummaryResponse[];
}

export interface InternalPhoneQimenSummaryResponse {
  generated_at: string;
  today_review_count: number;
  week_review_count: number;
  total_review_count: number;
  completed_review_count: number;
  failed_review_count: number;
  success_rate: number;
  average_generation_seconds: number | null;
  aspect_unlock_count: number;
  aspect_unlock_rate: number;
  review_points_cost: number;
  voice_request_count: number;
}

export interface InternalPhoneQimenReviewItemResponse {
  review_id: string;
  user_id: string | null;
  user_uid: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  phone: string;
  gender: Gender;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  error_message: string | null;
  channel: string | null;
  base_points_cost: number;
  unlock_count: number;
  voice_count: number;
  generation_duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface InternalPhoneQimenReviewListResponse {
  items: InternalPhoneQimenReviewItemResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternalPhoneQimenAspectUnlockRecordResponse {
  unlock_id: string;
  review_id: string;
  user_id: string;
  aspect_key: string;
  aspect_name: string;
  points_cost: number;
  usage_record_id: string | null;
  unlocked_at: string;
}

export interface InternalPhoneQimenReviewDetailResponse {
  review: InternalPhoneQimenReviewItemResponse;
  unlock_records: InternalPhoneQimenAspectUnlockRecordResponse[];
  voice_records: UsageRecordResponse[];
}

export interface InternalFourPillarsSummaryResponse extends InternalPhoneQimenSummaryResponse {}

export interface InternalFourPillarsReviewItemResponse {
  review_id: string;
  user_id: string | null;
  user_uid: string | null;
  user_nickname: string | null;
  user_phone: string | null;
  gender: Gender;
  birth_date: string;
  birth_time: string;
  timezone: string;
  birth_place: string | null;
  name: string | null;
  status: ReviewStatus;
  progress_stage: ReviewProgressStage | null;
  progress_message: string | null;
  error_message: string | null;
  channel: string | null;
  base_points_cost: number;
  unlock_count: number;
  voice_count: number;
  generation_duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface InternalFourPillarsReviewListResponse {
  items: InternalFourPillarsReviewItemResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface InternalFourPillarsAspectUnlockRecordResponse extends InternalPhoneQimenAspectUnlockRecordResponse {}

export interface InternalFourPillarsReviewDetailResponse {
  review: InternalFourPillarsReviewItemResponse;
  unlock_records: InternalFourPillarsAspectUnlockRecordResponse[];
  luck_render_records: FourPillarsLuckRenderRecord[];
}

export interface LlmApiKeyResponse {
  key_id: string;
  provider: string;
  model: string;
  display_name: string;
  masked_key: string;
  secret_ref: string;
  secret_configured: boolean;
  enabled: boolean;
  priority: number;
  max_concurrency: number;
  cooldown_seconds: number;
  current_inflight: number;
  available_slots: number;
  cooldown_until: string | null;
  last_rate_limited_at: string | null;
  last_error_message: string | null;
  last_used_at: string | null;
  remark: string | null;
  last_operator: string | null;
  created_at: string;
  updated_at: string;
}

export interface LlmApiKeyListResponse {
  items: LlmApiKeyResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface LlmConcurrencyKeyResponse {
  key_id: string;
  display_name: string;
  provider: string;
  model: string;
  enabled: boolean;
  priority: number;
  max_concurrency: number;
  cooldown_seconds: number;
  current_inflight: number;
  available_slots: number;
  cooldown_until: string | null;
  last_rate_limited_at: string | null;
  last_error_message: string | null;
  last_used_at: string | null;
}

export interface LlmConcurrencyStatusResponse {
  backend: string;
  backend_available: boolean;
  backend_error: string | null;
  redis_configured: boolean;
  global_inflight: number;
  foreground_waiting: number;
  background_waiting: number;
  foreground_inflight: number;
  background_inflight: number;
  enabled_key_count: number;
  total_capacity: number;
  recent_429_count: number;
  recent_timeout_count: number;
  avg_wait_ms: number;
  avg_duration_ms: number;
  config: Record<string, unknown>;
  keys: LlmConcurrencyKeyResponse[];
}

export interface RuntimeConfigEntryResponse {
  entry_id: string;
  scope_type: 'global' | 'channel';
  scope_key: string;
  config_key: string;
  value: unknown;
  updated_at: string;
}

export interface RuntimeConfigListResponse {
  items: RuntimeConfigEntryResponse[];
}

export interface RuntimeConfigEntryUpsertRequest {
  scope_type: 'global' | 'channel';
  scope_key: string;
  config_key: string;
  value: unknown;
}

export interface RuntimeInitialPointsUpdateRequest {
  initial_grant: number;
  apply_scope: 'future_users' | 'all_users';
  reason?: string | null;
}

export interface RuntimeInitialPointsUpdateResponse {
  previous_initial_grant: number;
  initial_grant: number;
  delta: number;
  apply_scope: 'future_users' | 'all_users';
  target_user_count: number;
  affected_user_count: number;
  adjusted_points_total: number;
  zeroed_user_count: number;
  operation_id: string;
  entry: RuntimeConfigEntryResponse;
}

export interface RuntimeConfigSchemaItemResponse {
  config_key: string;
  label: string;
  value_type: string;
  default_value: unknown;
  scope_type: 'global' | 'channel';
  scope_key: string;
  group: string;
  high_risk: boolean;
  description: string | null;
  admin_group?: string | null;
  admin_section?: string | null;
  advanced?: boolean;
  sort_order?: number;
  input_options?: Array<{value: string; label: string}>;
  help_text?: string | null;
  admin_hidden?: boolean;
}

export interface RuntimeConfigSchemaResponse {
  items: RuntimeConfigSchemaItemResponse[];
}

export interface RebatePointsAccountResponse {
  user_id: string;
  balance: number;
  frozen_balance: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface ManualPointsAdjustResponse {
  user: InternalUserResponse;
  points: PointsAccountResponse;
  ledger: PointsLedgerEntryResponse;
}

export interface RebatePointsAdjustResponse {
  user: InternalUserResponse;
  rebate_points: RebatePointsAccountResponse;
}

export interface PromotionApplicationResponse {
  application_id: string;
  user_id: string;
  user_nickname: string | null;
  current_identity_level: string | null;
  requested_level: string;
  status: string;
  applicant_name: string | null;
  applicant_phone: string | null;
  reject_reason: string | null;
  review_note: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromotionApplicationListResponse {
  items: PromotionApplicationResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromotionCommissionListResponse {
  items: PromotionCommissionResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromotionWithdrawalResponse {
  withdrawal_id: string;
  user_id: string;
  user_nickname: string | null;
  identity_level: string | null;
  status: string;
  withdrawable_balance_snapshot_cents: number;
  frozen_commission_snapshot_cents: number;
  points_used: number;
  amount_cents: number;
  rebate_points_balance_snapshot: number;
  cash_rate_snapshot: number;
  reject_reason: string | null;
  review_note: string | null;
  payout_method: string | null;
  payout_proof: string | null;
  payout_failure_reason: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromotionWithdrawalListResponse {
  items: PromotionWithdrawalResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface PromotionRulesResponse {
  normal_threshold_cents: number;
  senior_threshold_cents: number;
  normal_commission_rate: number;
  senior_commission_rate: number;
  min_withdraw_cents: number;
  order_completion_days: number;
}
```

### `src/config/pricing.ts`

```ts
// Fallback values only. Runtime config from the backend is the source of truth.
export const DEFAULT_BASE_REVIEW_POINTS = 100;
export const DEFAULT_ASPECT_UNLOCK_POINTS = 50;
```

### `src/constants/storage.ts`

```ts
export const EASEWISE_STORAGE_KEYS = {
  points: 'easewise_points',
  lastPhoneReport: 'easewise_last_phone_report',
  lastFourPillarsReport: 'easewise_last_four_pillars_report',
  accessToken: 'easewise_access_token',
  lastReviewId: 'easewise_last_review_id',
  lastFourPillarsReviewId: 'easewise_last_four_pillars_review_id',
  userSnapshot: 'easewise_user_snapshot',
  agentConversation: 'easewise_agent_conversation',
  voiceEnabled: 'easewise_voice_enabled',
  voiceAutoplayEnabled: 'easewise_voice_autoplay_enabled',
  reviewConfirmSkipPrompt: 'phoneqimen_skip_evaluation_hint',
  legacyReviewConfirmSkipPrompt: 'easewise_review_confirm_skip_prompt'
} as const;
```

### `src/index.css`

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600;700&family=Noto+Sans:wght@400;500;600&display=swap');
@import "tailwindcss";

@theme {
  --font-sans: "Noto Sans", "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif;
  --font-serif: "Noto Serif", "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", serif;
  --font-mono: "JetBrains Mono", "Sarasa Mono SC", "Fira Code", "Courier New", monospace;

  --color-brand-primary: #4F46E5;
  --color-brand-primary-strong: #4338CA;
  --color-brand-secondary: #64748B;
  --color-brand-paper: #F3F5FB;
  --color-brand-ink: #1F2937;
  --color-brand-ink-strong: #0F172A;
  --color-brand-accent: #FDE68A;
  --color-brand-gold-fixed: #F59E0B;

  --spacing-margin-mobile: 16px;
  --spacing-section-padding: 24px;
}

@layer base {
  html {
    font-family: var(--font-sans);
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    @apply bg-brand-paper text-brand-ink font-sans antialiased;
    background-color: #F3F5FB;
    background-image: radial-gradient(#CBD5E1 0.5px, transparent 0.5px);
    background-size: 20px 20px;
    min-height: 100dvh;
  }
}

.oriental-pattern {
  background-image: radial-gradient(#F59E0B 0.5px, transparent 0.5px);
  background-size: 24px 24px;
  opacity: 0.05;
}

.hairline-border {
  border: 0.5px solid rgba(79, 70, 229, 0.15);
}

.qimen-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  background-color: #CBD5E1;
}

.qimen-cell {
  aspect-ratio: 1/1;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 4px;
}

/* Hide scrollbar for Chrome, Safari and Opera */
.no-scrollbar::-webkit-scrollbar,
.scrollbar-none::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.no-scrollbar,
.scrollbar-none {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

@keyframes bazi-gentle-float {
  0%,
  100% {
    transform: translateY(0) scale(1);
    filter: drop-shadow(0 2px 4px rgba(79, 70, 229, 0.1));
  }
  50% {
    transform: translateY(-5px) scale(1.06);
    filter: drop-shadow(0 6px 10px rgba(79, 70, 229, 0.2));
  }
}

.bazi-float {
  animation: bazi-gentle-float 3.2s ease-in-out infinite;
}

@keyframes meihua-gentle-sway {
  0%,
  100% {
    transform: rotate(0deg) scale(1);
    filter: drop-shadow(0 2px 4px rgba(79, 70, 229, 0.15));
  }
  50% {
    transform: rotate(15deg) scale(1.08);
    filter: drop-shadow(0 6px 12px rgba(79, 70, 229, 0.35));
  }
}

.meihua-sway {
  animation: meihua-gentle-sway 4s ease-in-out infinite;
}
```
