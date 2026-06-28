# EaseWise Local H5 Repair Bundle For New AI Studio Project
## Usage
Paste this bundle into the new AI Studio project after `easewise.zip` has been used as the shell. Reconstruct every file at the exact path shown. This bundle restores the current local H5 frontend source of truth, including CSS, routes, Four Pillars, Meihua, profile, API client, types, and state.
## Manifest
- `.env.example` (116 bytes)
- `.gitignore` (73 bytes)
- `index.html` (298 bytes)
- `package.json` (770 bytes)
- `tsconfig.json` (484 bytes)
- `vite.config.ts` (1120 bytes)
- `src/main.ts` (116 bytes)
- `src/App.vue` (8846 bytes)
- `src/index.css` (2785 bytes)
- `src/vite-env.d.ts` (186 bytes)
- `src/config/pricing.ts` (176 bytes)
- `src/constants/storage.ts` (669 bytes)
- `src/types/api.ts` (37104 bytes)
- `src/lib/api.ts` (48164 bytes)
- `src/composables/useEaseWiseApp.ts` (34993 bytes)
- `src/composables/useVoicePlayback.ts` (17125 bytes)
- `src/components/admin/AdminSelect.vue` (4065 bytes)
- `src/components/ai-agent/AIAgent.vue` (13492 bytes)
- `src/components/analysis/Analysis.vue` (114609 bytes)
- `src/components/auth/AuthModal.vue` (22416 bytes)
- `src/components/four-pillars/FourPillarsAnalysis.vue` (148008 bytes)
- `src/components/four-pillars/FourPillarsNatalTable.vue` (29440 bytes)
- `src/components/home/Home.vue` (19656 bytes)
- `src/components/layout/BottomNav.vue` (1422 bytes)
- `src/components/layout/Header.vue` (1288 bytes)
- `src/components/meihua/MeihuaAnalysis.vue` (25422 bytes)
- `src/components/points-claim/PointsClaimPage.vue` (21294 bytes)
- `src/components/profile/AmbassadorDetail.vue` (9205 bytes)
- `src/components/profile/Profile.vue` (48184 bytes)
- `src/components/profile/SystemIntro.vue` (39656 bytes)
- `src/components/recharge/RechargePage.vue` (36568 bytes)
- `src/components/support/ContactServiceModal.vue` (6546 bytes)

Total source bytes: `694296`

## Files

### `.env.example`

```bash
# Leave empty during local development so Vite proxies /api to the backend.
VITE_API_BASE_URL=
VITE_APP_BASE_PATH=/
```

### `.gitignore`

```gitignore
node_modules/
build/
dist/
coverage/
.DS_Store
*.log
.env*
!.env.example
```

### `index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>易如反掌</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

### `package.json`

```json
{
  "name": "easewise-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --port=3000 --host=0.0.0.0",
    "build": "vite build",
    "preview": "vite preview",
    "clean": "rm -rf dist server.js",
    "lint": "tsc --noEmit"
  },
  "dependencies": {
    "@google/genai": "^1.29.0",
    "@tailwindcss/vite": "^4.1.14",
    "dotenv": "^17.2.3",
    "express": "^4.21.2",
    "lucide-vue-next": "^1.0.0",
    "vite": "^6.2.3",
    "vue": "^3.5.34"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^22.14.0",
    "@vitejs/plugin-vue": "^6.0.7",
    "autoprefixer": "^10.4.21",
    "esbuild": "^0.25.0",
    "tailwindcss": "^4.1.14",
    "typescript": "~5.8.2",
    "vite": "^6.2.3"
  }
}
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "experimentalDecorators": true,
    "useDefineForClassFields": false,
    "module": "ESNext",
    "lib": [
      "ES2022",
      "DOM",
      "DOM.Iterable"
    ],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "isolatedModules": true,
    "moduleDetection": "force",
    "allowJs": true,
    "paths": {
      "@/*": [
        "./*"
      ]
    },
    "allowImportingTsExtensions": true,
    "noEmit": true
  }
}
```

### `vite.config.ts`

```ts
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import {defineConfig, loadEnv} from 'vite';

export default defineConfig(({mode}) => {
  const env = loadEnv(mode, '.', '');
  return {
    base: env.VITE_APP_BASE_PATH || '/',
    plugins: [vue(), tailwindcss()],
    define: {
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modifyâfile watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
        '/health': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
  };
});
```

### `src/main.ts`

```ts
import { createApp } from 'vue';
import App from './App.vue';
import './index.css';

createApp(App).mount('#root');
```

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

### `src/vite-env.d.ts`

```ts
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
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
  score: number | null;
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
  score: number | null;
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
  score_markdown: string | null;
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
  score: number | null;
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
  streamFourPillarsReviewAspectUnlock,
  streamPhoneReviewAspectUnlock,
  type FourPillarsCoreStreamHandlers,
  type FourPillarsAspectStreamHandlers,
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
        score: aspect.score ?? item.score,
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
        score: review.score,
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

### `src/composables/useVoicePlayback.ts`

```ts
import { computed, ref } from 'vue';
import { EASEWISE_STORAGE_KEYS } from '../constants/storage';
import { ApiError, createVoiceNarration, getApiBaseUrl } from '../lib/api';
import type { ReviewAspect, ReviewRecord, VoiceNarrationRequest, VoiceRuntimeConfigResponse } from '../types/api';

type VoicePlaybackStatus = 'idle' | 'loading' | 'playing' | 'error';

type SpeakOptions = {
  auto?: boolean;
};

export type VoiceSpeakResult = {
  started: boolean;
  completed: boolean;
  stopped?: boolean;
  error?: string;
};

type VoicePlaybackOptions = {
  getAccessToken: () => string | null;
  getVoiceConfig: () => VoiceRuntimeConfigResponse | null | undefined;
  showToast?: (message: string) => void;
};

const autoSpokenKeys = new Set<string>();
const SILENT_AUDIO_DATA_URL = 'data:audio/wav;base64,UklGRiYAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQIAAAAAAA==';

export function useVoicePlayback(options: VoicePlaybackOptions) {
  const status = ref<VoicePlaybackStatus>('idle');
  const currentKey = ref<string | null>(null);
  const error = ref<string | null>(null);
  const primed = ref(false);
  const storedEnabled = ref(readStoredBoolean(EASEWISE_STORAGE_KEYS.voiceEnabled));
  const storedAutoplayEnabled = ref(readStoredBoolean(EASEWISE_STORAGE_KEYS.voiceAutoplayEnabled));
  let currentAudio: HTMLAudioElement | null = null;
  let unlockedAudio: HTMLAudioElement | null = null;
  let speechRunId = 0;
  let activeResolve: ((result: VoiceSpeakResult) => void) | null = null;

  const voiceConfig = computed(() => options.getVoiceConfig() ?? null);
  const enabled = computed(() => {
    if (voiceConfig.value?.enabled === false) {
      return false;
    }
    return storedEnabled.value ?? true;
  });
  const autoplayEnabled = computed(() => {
    if (!enabled.value) {
      return false;
    }
    return storedAutoplayEnabled.value ?? voiceConfig.value?.autoplay_default_enabled ?? true;
  });
  const browserSpeechSupported = computed(() => typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window);
  const manualStartNeeded = computed(() => status.value === 'error' && error.value === 'autoplay_blocked');

  function primeAudioSession(): void {
    primed.value = true;
    if (typeof window === 'undefined') {
      return;
    }
    if (browserSpeechSupported.value) {
      void window.speechSynthesis.getVoices();
    }
    if (status.value === 'loading' || status.value === 'playing') {
      return;
    }
    const audio = ensureUnlockedAudio();
    audio.muted = false;
    audio.volume = 1;
    audio.src = SILENT_AUDIO_DATA_URL;
    audio.load();
    void audio.play()
      .then(() => {
        audio.pause();
        audio.currentTime = 0;
      })
      .catch(() => {
        // Browsers can still reject this on some platforms; playback will fall back later.
      });
  }

  function setAutoplayEnabled(nextEnabled: boolean): void {
    storedAutoplayEnabled.value = nextEnabled;
    writeStoredBoolean(EASEWISE_STORAGE_KEYS.voiceAutoplayEnabled, nextEnabled);
    if (!nextEnabled && (status.value === 'playing' || status.value === 'loading')) {
      stop();
    }
  }

  function setEnabled(nextEnabled: boolean): void {
    storedEnabled.value = nextEnabled;
    writeStoredBoolean(EASEWISE_STORAGE_KEYS.voiceEnabled, nextEnabled);
    if (!nextEnabled) {
      stop();
    }
  }

  function toggleAutoplayEnabled(): void {
    setAutoplayEnabled(!autoplayEnabled.value);
  }

  async function speakPhoneSummary(review: ReviewRecord | null | undefined, speakOptions: SpeakOptions = {}): Promise<VoiceSpeakResult> {
    if (!review?.id) {
      return createVoiceResult(false);
    }
    const text = buildPhoneSummaryNarrationText(review);
    if (!text) {
      return createVoiceResult(false);
    }
    const key = `phone_summary:${review.id}:${review.updated_at || ''}`;
    const requestPayload: VoiceNarrationRequest = {
      scene: 'phone_summary',
      review_id: review.id,
      voice_key: voiceConfig.value?.default_voice_key ?? null,
    };
    return speakNarration({ key, text, requestPayload, auto: Boolean(speakOptions.auto) });
  }

  async function speakStability(review: ReviewRecord | null | undefined, speakOptions: SpeakOptions = {}): Promise<VoiceSpeakResult> {
    if (!review?.id) {
      return createVoiceResult(false);
    }
    const text = buildStabilityNarrationText(review);
    if (!text) {
      return createVoiceResult(false);
    }
    const key = `phone_stability:${review.id}:${review.updated_at || ''}`;
    const requestPayload: VoiceNarrationRequest = {
      scene: 'phone_stability',
      review_id: review.id,
      voice_key: voiceConfig.value?.default_voice_key ?? null,
    };
    return speakNarration({ key, text, requestPayload, auto: Boolean(speakOptions.auto) });
  }

  async function speakAspect(review: ReviewRecord | null | undefined, aspect: ReviewAspect | null | undefined, speakOptions: SpeakOptions = {}): Promise<VoiceSpeakResult> {
    if (!review?.id || !aspect?.aspect_key || !aspect.is_unlocked) {
      return createVoiceResult(false);
    }
    const text = buildAspectNarrationText(aspect);
    if (!text) {
      return createVoiceResult(false);
    }
    const key = `phone_aspect:${review.id}:${aspect.aspect_key}`;
    const requestPayload: VoiceNarrationRequest = {
      scene: 'phone_aspect',
      review_id: review.id,
      aspect_key: aspect.aspect_key,
      voice_key: voiceConfig.value?.default_voice_key ?? null,
    };
    return speakNarration({ key, text, requestPayload, auto: Boolean(speakOptions.auto) });
  }

  function stop(): void {
    speechRunId += 1;
    if (currentAudio) {
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio.pause();
      currentAudio.removeAttribute('src');
      currentAudio.load();
      currentAudio = null;
    }
    if (typeof window !== 'undefined' && browserSpeechSupported.value) {
      window.speechSynthesis.cancel();
    }
    status.value = 'idle';
    currentKey.value = null;
    error.value = null;
    resolveActivePlayback(createVoiceResult(false, { stopped: true }));
  }

  async function speakNarration({
    key,
    text,
    requestPayload,
    auto,
  }: {
    key: string;
    text: string;
    requestPayload: VoiceNarrationRequest;
    auto: boolean;
  }): Promise<VoiceSpeakResult> {
    if (!enabled.value) {
      return createVoiceResult(false);
    }
    if (auto) {
      if (!autoplayEnabled.value || autoSpokenKeys.has(key)) {
        return createVoiceResult(false);
      }
      autoSpokenKeys.add(key);
    }

    stop();
    const runId = speechRunId + 1;
    speechRunId = runId;
    currentKey.value = key;
    error.value = null;
    status.value = 'loading';

    const mode = voiceConfig.value?.mode ?? 'hybrid';
    const shouldUseCloud = mode !== 'browser' && Boolean(options.getAccessToken());
    if (shouldUseCloud) {
      try {
        const narration = await createVoiceNarration(options.getAccessToken() || '', requestPayload);
        if (speechRunId !== runId || currentKey.value !== key) {
          return createVoiceResult(false, { stopped: true });
        }
        const audioResult = await playAudioUrl(resolveAudioUrl(narration.audio_url), key, runId, auto);
        if (audioResult.completed || (audioResult.started && !audioResult.error) || mode === 'cloud' || !browserSpeechSupported.value) {
          return audioResult;
        }
        if (speechRunId !== runId || currentKey.value !== key) {
          return createVoiceResult(false, { stopped: true });
        }
        error.value = null;
        status.value = 'loading';
      } catch (cloudError) {
        if (mode === 'cloud' || !browserSpeechSupported.value) {
          applyVoiceError(cloudError, auto);
          return createVoiceResult(false, { error: normalizeVoiceError(cloudError) });
        }
      }
    }

    if (!browserSpeechSupported.value) {
      const nextError = new Error('browser_speech_unavailable');
      applyVoiceError(nextError, auto);
      return createVoiceResult(false, { error: normalizeVoiceError(nextError) });
    }

    try {
      if (speechRunId !== runId || currentKey.value !== key) {
        return createVoiceResult(false, { stopped: true });
      }
      return await speakWithBrowser(text, key, runId);
    } catch (browserError) {
      applyVoiceError(browserError, auto);
      return createVoiceResult(false, { error: normalizeVoiceError(browserError) });
    }
  }

  function playAudioUrl(audioUrl: string, key: string, runId: number, auto: boolean): Promise<VoiceSpeakResult> {
    const audio = ensureUnlockedAudio();
    currentAudio = audio;
    audio.onended = null;
    audio.onerror = null;
    audio.muted = false;
    audio.volume = 1;
    audio.preload = 'auto';
    audio.src = audioUrl;
    audio.load();

    return new Promise<VoiceSpeakResult>((resolve) => {
      activeResolve = resolve;
      audio.onended = () => {
        if (currentKey.value !== key || speechRunId !== runId) {
          return;
        }
        if (currentKey.value === key && speechRunId === runId) {
          status.value = 'idle';
          currentKey.value = null;
        }
        resolveActivePlayback(createVoiceResult(true, { completed: true }));
      };
      audio.onerror = () => {
        if (currentKey.value !== key || speechRunId !== runId) {
          return;
        }
        const nextError = new Error('audio_play_failed');
        if (currentKey.value === key && speechRunId === runId) {
          applyVoiceError(nextError, auto);
        }
        resolveActivePlayback(createVoiceResult(true, { error: normalizeVoiceError(nextError) }));
      };
      audio.play()
        .then(() => {
          if (currentKey.value === key && speechRunId === runId) {
            status.value = 'playing';
          }
        })
        .catch((playError: unknown) => {
          if (currentKey.value !== key || speechRunId !== runId) {
            return;
          }
          if (currentKey.value === key && speechRunId === runId) {
            applyVoiceError(playError, auto);
          }
          resolveActivePlayback(createVoiceResult(false, { error: normalizeVoiceError(playError) }));
        });
    });
  }

  function ensureUnlockedAudio(): HTMLAudioElement {
    if (!unlockedAudio) {
      unlockedAudio = new Audio();
      unlockedAudio.preload = 'auto';
      unlockedAudio.setAttribute('playsinline', 'true');
      unlockedAudio.setAttribute('webkit-playsinline', 'true');
    }
    return unlockedAudio;
  }

  function speakWithBrowser(text: string, key: string, runId: number): Promise<VoiceSpeakResult> {
    if (!browserSpeechSupported.value) {
      throw new Error('browser_speech_unavailable');
    }
    const speechSynthesis = window.speechSynthesis;
    const chunks = splitSpeechText(text);
    if (!chunks.length) {
      throw new Error('voice_text_empty');
    }

    speechSynthesis.cancel();
    status.value = 'playing';

    return new Promise<VoiceSpeakResult>((resolve) => {
      activeResolve = resolve;
      let chunkIndex = 0;
      const speakNext = () => {
        if (speechRunId !== runId) {
          return;
        }
        const chunk = chunks[chunkIndex];
        if (!chunk) {
          if (currentKey.value === key) {
            status.value = 'idle';
            currentKey.value = null;
          }
          resolveActivePlayback(createVoiceResult(true, { completed: true }));
          return;
        }
        chunkIndex += 1;
        const utterance = new SpeechSynthesisUtterance(chunk);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.95;
        utterance.pitch = 1;
        const voice = resolveChineseVoice();
        if (voice) {
          utterance.voice = voice;
        }
        utterance.onend = speakNext;
        utterance.onerror = () => {
          if (speechRunId === runId) {
            const nextError = new Error('browser_speech_failed');
            applyVoiceError(nextError, false);
            resolveActivePlayback(createVoiceResult(true, { error: normalizeVoiceError(nextError) }));
          }
        };
        speechSynthesis.speak(utterance);
      };
      speakNext();
    });
  }

  function applyVoiceError(rawError: unknown, auto: boolean): void {
    status.value = 'error';
    error.value = normalizeVoiceError(rawError);
    if (auto) {
      options.showToast?.('语音播报未能自动开始，可点击播放按钮手动收听。');
    }
  }

  function resolveActivePlayback(result: VoiceSpeakResult): void {
    if (!activeResolve) {
      return;
    }
    const resolve = activeResolve;
    activeResolve = null;
    resolve(result);
  }

  return {
    status,
    currentKey,
    error,
    enabled,
    autoplayEnabled,
    browserSpeechSupported,
    manualStartNeeded,
    primed,
    primeAudioSession,
    setAutoplayEnabled,
    setEnabled,
    toggleAutoplayEnabled,
    speakPhoneSummary,
    speakStability,
    speakAspect,
    stop,
    buildPhoneSummaryNarrationText,
    buildStabilityNarrationText,
    buildAspectNarrationText,
  };
}

function buildPhoneSummaryNarrationText(review: ReviewRecord): string {
  const summary = review.phone_summary;
  if (!summary) {
    return '';
  }
  return joinNarrationParts([
    '综合评述',
    summary.title,
    '风险提醒',
    summary.risk,
    '使用建议',
    summary.usage_guidance,
  ]);
}

function buildStabilityNarrationText(review: ReviewRecord): string {
  const stability = review.stability_detail;
  if (!stability) {
    return '';
  }
  return joinNarrationParts([
    '长期使用建议',
    stability.verdict,
    stability.content,
  ]);
}

function buildAspectNarrationText(aspect: ReviewAspect): string {
  if (!aspect.is_unlocked || !aspect.content) {
    return '';
  }
  const aspectTitle = aspect.short_title || aspect.title;
  return joinNarrationParts([
    `${aspectTitle}专项`,
    aspect.title,
    aspect.risk ? '风险提示' : '',
    aspect.risk,
    aspect.content,
  ]);
}

function createVoiceResult(started: boolean, detail: Partial<VoiceSpeakResult> = {}): VoiceSpeakResult {
  return {
    started,
    completed: false,
    ...detail,
  };
}

function joinNarrationParts(parts: Array<string | null | undefined>): string {
  const cleaned = parts
    .map((part) => cleanVoiceText(part))
    .filter(Boolean);
  return cleaned.length ? `${cleaned.join('。')}。` : '';
}

function cleanVoiceText(value: string | null | undefined): string {
  const text = String(value || '').trim();
  if (!text || ['title', 'risk', 'usage guidance'].includes(text.toLowerCase())) {
    return '';
  }
  return text.replace(/\s+/g, ' ').replace(/[｛｝{}*_`#>~]+/g, '').replace(/[。]+$/g, '').trim();
}

function splitSpeechText(text: string): string[] {
  const cleanText = cleanVoiceText(text);
  if (!cleanText) {
    return [];
  }
  const maxLength = 120;
  const chunks: string[] = [];
  let buffer = '';
  const sentences = cleanText.split(/(?<=[。！？!?；;])/);
  for (const sentence of sentences) {
    const candidate = `${buffer}${sentence}`.trim();
    if (candidate.length <= maxLength) {
      buffer = candidate;
      continue;
    }
    if (buffer) {
      chunks.push(buffer);
      buffer = '';
    }
    let remaining = sentence.trim();
    while (remaining.length > maxLength) {
      chunks.push(remaining.slice(0, maxLength));
      remaining = remaining.slice(maxLength);
    }
    buffer = remaining;
  }
  if (buffer) {
    chunks.push(buffer);
  }
  return chunks;
}

function resolveChineseVoice(): SpeechSynthesisVoice | null {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return null;
  }
  const voices = window.speechSynthesis.getVoices();
  return (
    voices.find((voice) => voice.lang.toLowerCase().startsWith('zh-cn')) ||
    voices.find((voice) => voice.lang.toLowerCase().startsWith('zh')) ||
    voices.find((voice) => /chinese|mandarin|中文|普通话/i.test(voice.name)) ||
    null
  );
}

function resolveAudioUrl(audioUrl: string): string {
  if (/^https?:\/\//i.test(audioUrl)) {
    return audioUrl;
  }
  const baseUrl = getApiBaseUrl();
  const normalizedPath = audioUrl.startsWith('/') ? audioUrl : `/${audioUrl}`;
  return `${baseUrl}${normalizedPath}`;
}

function normalizeVoiceError(rawError: unknown): string {
  if (rawError instanceof DOMException && rawError.name === 'NotAllowedError') {
    return 'autoplay_blocked';
  }
  if (rawError instanceof ApiError) {
    return rawError.detail;
  }
  if (rawError instanceof Error && rawError.message) {
    return rawError.message;
  }
  return 'voice_playback_failed';
}

function readStoredBoolean(key: string): boolean | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const value = window.localStorage.getItem(key);
  if (value === null) {
    return null;
  }
  return value === 'true' || value === '1';
}

function writeStoredBoolean(key: string, value: boolean): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem(key, value ? 'true' : 'false');
}
```

### `src/components/admin/AdminSelect.vue`

```vue
<script setup lang="ts">
import { computed, ref } from 'vue';
import { Check, ChevronDown } from 'lucide-vue-next';

type SelectValue = string | number | boolean | null;

interface AdminSelectOption {
  value: SelectValue;
  label: string;
  dotClass?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<{
  modelValue: SelectValue;
  options: AdminSelectOption[];
  placeholder?: string;
  minWidthClass?: string;
  panelWidthClass?: string;
  align?: 'left' | 'right';
  buttonClass?: string;
}>(), {
  placeholder: '请选择',
  minWidthClass: 'min-w-[140px]',
  panelWidthClass: 'w-56',
  align: 'left',
  buttonClass: '',
});

const emit = defineEmits<{
  (event: 'update:modelValue', value: SelectValue): void;
  (event: 'change', value: SelectValue): void;
}>();

const open = ref(false);

const selectedOption = computed(() => props.options.find((option) => option.value === props.modelValue) ?? null);
const selectedLabel = computed(() => selectedOption.value?.label ?? props.placeholder);
const selectedDotClass = computed(() => selectedOption.value?.dotClass ?? 'bg-indigo-500');

function selectOption(option: AdminSelectOption) {
  if (option.disabled) return;
  emit('update:modelValue', option.value);
  emit('change', option.value);
  open.value = false;
}

function isSelected(option: AdminSelectOption) {
  return option.value === props.modelValue;
}
</script>

<template>
  <div class="relative z-20" :class="minWidthClass">
    <button
      type="button"
      @click="open = !open"
      class="w-full flex items-center justify-between gap-3 bg-gray-50 hover:bg-white border border-gray-100 hover:border-gray-100 text-brand-ink-strong p-2.5 px-4 rounded-xl text-xs font-semibold select-none cursor-pointer transition-colors duration-150 focus:border-brand-primary focus:bg-white outline-none"
      :class="buttonClass"
    >
      <span class="flex items-center gap-2 min-w-0">
        <span class="w-2 h-2 rounded-full inline-block shrink-0" :class="selectedDotClass"></span>
        <span class="truncate">{{ selectedLabel }}</span>
      </span>
      <ChevronDown
        :size="14"
        class="text-brand-secondary transition-transform duration-200 shrink-0"
        :class="{ 'rotate-180': open }"
      />
    </button>

    <div
      v-if="open"
      @click="open = false"
      class="fixed inset-0 z-[60] bg-transparent"
    ></div>

    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="open"
        class="absolute mt-1.5 bg-white border border-gray-100 rounded-xl shadow-lg z-[70] py-1 origin-top"
        :class="[panelWidthClass, align === 'right' ? 'right-0' : 'left-0']"
      >
        <div class="p-1 space-y-0.5">
          <button
            v-for="option in options"
            :key="String(option.value)"
            type="button"
            :disabled="option.disabled"
            @click="selectOption(option)"
            class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium cursor-pointer transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            :class="[
              isSelected(option)
                ? 'bg-brand-primary/10 text-brand-primary font-black'
                : 'text-brand-ink hover:bg-gray-50'
            ]"
          >
            <span class="flex items-center gap-2.5 min-w-0">
              <span class="w-2 h-2 rounded-full inline-block shrink-0" :class="option.dotClass ?? 'bg-indigo-500'"></span>
              <span class="truncate">{{ option.label }}</span>
            </span>
            <Check v-if="isSelected(option)" :size="13" class="text-brand-primary stroke-[3] shrink-0" />
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>
```

### `src/components/ai-agent/AIAgent.vue`

```vue
<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick } from 'vue';
import {
  Send, Mic, Bot, User, Trash2, Smartphone, AlertCircle, Sparkle
} from 'lucide-vue-next';
import { EASEWISE_STORAGE_KEYS } from '../../constants/storage';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

interface Message {
  id: string;
  role: 'assistant' | 'user';
  content: string;
  source?: string;
  timestamp: string;
  chips?: string[];
}

const { bootstrapApp, isRegisteredUser, requestRegisteredUser } = useEaseWiseApp();
const isLoggedIn = computed(() => isRegisteredUser.value);
const input = ref('');
const messages = ref<Message[]>([]);
const chatScrollContainerRef = ref<HTMLDivElement | null>(null);

const scrollToBottom = () => {
  nextTick(() => {
    if (chatScrollContainerRef.value) {
      chatScrollContainerRef.value.scrollTo({
        top: chatScrollContainerRef.value.scrollHeight,
        behavior: 'smooth',
      });
    }
  });
};

const initDefaultMessages = () => {
  const initialText = '您好，我是您的「易如反掌」专属决策助手。今日值神为青龙守护，【丙戌年 癸巳月 己未日】，己未大溪水，宜心气沉稳行事。\n\n检测到您昨日对号码尾号 8829 的评测已经封存（综合评分: 85），目前该名格正处于“生门”繁茂兑宫位。您想深入探究下该号段的财源偏旺期、或者直接听听近期的行动指导吗？';
  const initMsg: Message = {
    id: '1',
    role: 'assistant',
    content: initialText,
    source: 'DeepSeek-R1 (大黄历规则融合版)',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    chips: ['生门在这里代表什么？', '帮我解读手机号分析结论', '今天适合求财或签合同吗？']
  };
  messages.value = [initMsg];
};

const syncChat = () => {
  if (isLoggedIn.value) {
    const stored = localStorage.getItem(EASEWISE_STORAGE_KEYS.agentConversation);
    if (stored) {
      try {
        messages.value = JSON.parse(stored);
      } catch (e) {
        initDefaultMessages();
      }
    } else {
      initDefaultMessages();
    }
  } else {
    messages.value = [];
  }
};

watch(isLoggedIn, () => {
  syncChat();
}, { immediate: true });

watch(messages, (newVal) => {
  if (isLoggedIn.value && newVal.length > 0) {
    localStorage.setItem(EASEWISE_STORAGE_KEYS.agentConversation, JSON.stringify(newVal));
  }
  scrollToBottom();
}, { deep: true });

onMounted(() => {
  void bootstrapApp();
  syncChat();
  scrollToBottom();
});

const handleSend = (textToSend?: string) => {
  const query = (textToSend || input.value).trim();
  if (!query) return;

  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const userMsg: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: query,
    timestamp
  };

  messages.value.push(userMsg);
  input.value = '';

  // Simulated responses mapping
  setTimeout(() => {
    let replyContent = '';
    let source = '易如反掌·大数理模型';

    if (query.includes('生门') || query.includes('代表什么')) {
      replyContent = '在奇门遁甲中，“生门”属艮土之格，高悬于兑金位。这预示着“号里逢土金相生，连绵不断”。对你而言，近期适宜求谋固定财产、长线投资、撰写论文或者对长者行拜问。在壬申今日，申子三合引水，利于财富的吸入与沉淀。';
      source = 'DeepSeek-R1 (奇门命盘模块)';
    } else if (query.includes('解读') || query.includes('手机号')) {
      replyContent = '正在为您抓取【尾号 8829】的命理断案... 盘面正逢“青龙得位”良局，其主求财易得、长辈青睐。但针对壬申日气运，天蓬休门有暗引，需要小心偏财过于贪恋导致的对冲损耗。';
      source = '易如反掌·大数理模型 (号段微调)';
    } else if (query.includes('求财') || query.includes('合同')) {
      replyContent = '今日己未，值神青龙逢黄道吉。因你号中巽木得气，宜进行商务报告沟通与设计规划撰写。如果是涉及大额偏财风险投资，建议推迟1-2日再做重大转账决断，保持防线坚固。';
      source = '大黄历规则兜底算引';
    } else {
      replyContent = `已收到您的咨询：“${query}”。根据奇门今日中盘局势，己未日气场厚重。建议以稳守本职，防微杜渐为主，配合此号码所藏天任文昌星进行文案与学术进修，自然能迎刃而解。`;
    }

    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: replyContent,
      source,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      chips: ['我该如何具体开运？', '尾号生门是什么位置？', '有什么彭祖百忌需要小心？']
    };

    messages.value.push(assistantMsg);
  }, 1200);
};

const handleLogin = async () => {
  await requestRegisteredUser('智能体对话');
};

const handleClearChat = () => {
  if (window.confirm('您确定要清空与智能体的所有聊天记录吗？')) {
    localStorage.removeItem(EASEWISE_STORAGE_KEYS.agentConversation);
    initDefaultMessages();
  }
};

const quickQueries = [
  '帮我解读最近一条手机号评测内容',
  '今天适合办理什么求财事务？',
  '我目前面临难关，下一步如何趋吉避凶？'
];
</script>

<template>
  <div class="flex flex-col h-[calc(100dvh-82px)] md:h-[calc(100vh-82px)] max-w-md mx-auto w-full bg-brand-paper overflow-hidden overscroll-none">
    <transition name="fade" mode="out-in">
      <!-- State 1: Login Gate UI -->
      <div
        v-if="!isLoggedIn"
        key="login-gate"
        class="flex-1 px-margin-mobile flex flex-col items-center justify-center text-center space-y-6 pb-6"
      >
        <div class="w-16 h-16 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary border border-brand-primary/20">
          <Bot :size="34" />
        </div>

        <div class="space-y-2 max-w-[90%]">
          <h2 class="font-serif text-[20px] font-bold text-brand-ink-strong leading-tight">易如反掌 · 智能体决策助手</h2>
          <p class="font-sans text-[13px] text-brand-secondary leading-relaxed">
            为提供定制的奇门排盘和黄历沟通服务，智能体需要关联您的手机测算历史与资产。未登录状态无法启用连续对话功能。
          </p>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-100 max-w-[95%] text-left space-y-2 flex items-start gap-2 font-sans text-[13px] text-brand-secondary">
          <AlertCircle :size="16" class="text-brand-primary shrink-0 mt-0.5" />
          <div>
            <span class="font-bold text-brand-ink-strong">安全声明: </span>
            <span>您的聊天内容、测算手机号完全处于安全加密沙盒中，外部小人难窥，仅用于给予高定制开运决策建议。</span>
          </div>
        </div>

        <button
          @click="handleLogin"
          class="w-full py-3.5 bg-brand-primary text-white rounded-xl font-sans text-[13px] font-bold shadow-sm hover:bg-brand-primary-strong active:scale-[0.98] transition-all cursor-pointer outline-none flex items-center justify-center gap-2"
        >
          <Smartphone :size="16" />
          <span>登录后开启智能体对话</span>
        </button>
      </div>

      <!-- State 2: Active chat view -->
      <div
        v-else
        key="chat-active"
        class="flex-grow flex flex-col min-h-0 overflow-hidden"
      >
        <!-- Top context card with copy button and clearing action -->
        <div class="px-margin-mobile pt-3 shrink-0 flex items-center justify-between gap-2">
          <div class="flex-1 bg-white p-3 rounded-xl border border-gray-100/80 flex items-start gap-2.5 shadow-sm">
            <div class="relative mt-0.5 shrink-0">
              <Sparkle :size="16" class="text-brand-gold-fixed animate-spin" style="animation-duration: 4s" fill="currentColor" />
              <span class="absolute -top-1 -right-1 block w-2 h-2 bg-green-500 border-2 border-white rounded-full"></span>
            </div>
            <p class="font-sans text-[11px] text-brand-secondary leading-relaxed font-semibold">
              智能体决策器：今日结合实时大黄历气运为您解读
            </p>
          </div>

          <button
            @click="handleClearChat"
            class="p-3 bg-white hover:bg-gray-50 text-brand-secondary hover:text-red-500 rounded-xl border border-gray-100 shadow-sm transition-all outline-none cursor-pointer"
            title="清空聊天记录"
          >
            <Trash2 :size="16" />
          </button>
        </div>

        <!-- Message logs area -->
        <div ref="chatScrollContainerRef" class="flex-1 min-h-0 overflow-y-auto overscroll-contain px-margin-mobile py-4 pb-4 flex flex-col gap-4.5 no-scrollbar">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="flex gap-2.5 max-w-[92%] items-start"
            :class="msg.role === 'assistant' ? 'self-start' : 'self-end flex-row-reverse'"
          >
            <!-- Avatar blob -->
            <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                 :class="msg.role === 'assistant' ? 'bg-white border border-gray-100 text-brand-primary shadow-sm' : 'bg-brand-primary text-white shadow-sm'">
              <Bot v-if="msg.role === 'assistant'" :size="16" />
              <User v-else :size="16" />
            </div>

            <!-- Content wrapper -->
            <div class="flex flex-col gap-1 w-full text-left">
              <!-- Message bubble -->
              <div class="px-3.5 py-2.5 rounded-2xl border font-sans text-[13px] leading-relaxed shadow-sm"
                   :class="msg.role === 'assistant' ? 'bg-white border-gray-100/60 rounded-tl-none text-brand-ink-strong' : 'bg-brand-primary text-white border-transparent rounded-tr-none'">
                <p class="whitespace-pre-wrap">{{ msg.content }}</p>
              </div>

              <!-- Source tag & timestamp for scholarly trust -->
              <div class="flex items-center gap-2 px-1 font-mono text-[10px] text-brand-secondary/60"
                   :class="msg.role === 'assistant' ? 'justify-start' : 'justify-end'">
                <span v-if="msg.role === 'assistant' && msg.source" class="font-bold text-brand-primary bg-brand-primary/5 px-1 rounded-sm scale-90 select-none">
                  {{ msg.source }}
                </span>
                <span>{{ msg.timestamp }}</span>
              </div>

              <!-- Quick click chips appended directly to AI message for layout fluency -->
              <div v-if="msg.role === 'assistant' && msg.chips" class="flex flex-wrap gap-1.5 mt-2">
                <button
                  v-for="chip in msg.chips"
                  :key="chip"
                  @click="handleSend(chip)"
                  class="bg-brand-paper hover:bg-gray-100 text-brand-primary border border-gray-200/50 px-2.5 py-1 rounded-full font-sans text-[10px] font-bold transition-all outline-none shrink-0"
                >
                  {{ chip }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom interaction space -->
        <div class="bg-brand-paper/95 backdrop-blur-sm border-t border-gray-100/80 shrink-0">
          <!-- Quick horizontal scrolling Queries -->
          <div class="px-margin-mobile py-2.5 overflow-x-auto no-scrollbar flex gap-2 w-full">
            <button
              v-for="q in quickQueries"
              :key="q"
              @click="handleSend(q)"
              class="whitespace-nowrap px-3 py-2 bg-white border border-gray-200 rounded-full font-sans text-[11px] text-brand-secondary font-bold hover:border-brand-primary transition-colors cursor-pointer outline-none shadow-sm"
            >
              {{ q }}
            </button>
          </div>

          <!-- Input Field -->
          <div class="px-4 pb-0 flex items-center gap-3">
            <div class="flex-1 bg-white p-1 rounded-2xl flex items-center gap-1.5 border border-gray-100 shadow-sm pr-3">
              <input
                class="bg-transparent border-none focus:ring-0 w-full pl-3 pr-1 py-2 font-sans text-[13px] text-brand-ink-strong outline-none placeholder-gray-400 font-medium"
                placeholder="请输入对起盘结论的追问..."
                type="text"
                v-model="input"
                @keydown.enter="handleSend()"
              />
              <Mic :size="18" class="text-brand-secondary/60 cursor-pointer hover:text-brand-primary shrink-0" />
            </div>
            <button
              @click="handleSend()"
              class="w-11 h-11 rounded-full bg-brand-primary flex items-center justify-center text-white active:scale-95 transition-transform shrink-0 outline-none shadow-md"
            >
              <Send :size="16" fill="currentColor" />
            </button>
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
</style>
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

### `src/components/auth/AuthModal.vue`

```vue
<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue';
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  Eye,
  EyeOff,
  Loader2,
  LockKeyhole,
  ShieldCheck,
  Smartphone,
  X,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const {
  state,
  cancelAuthRequest,
  checkPhoneAuthStatus,
  loginWithPhonePassword,
  customerServiceCopyForScene,
  openCustomerServiceModal,
  registerWithPhonePassword,
  humanizeError,
} = useEaseWiseApp();

type AuthMode = 'options' | 'phone' | 'login' | 'register' | 'forgot_password' | 'wechat_loading';

const mode = ref<AuthMode>('options');
const phone = ref('');
const password = ref('');
const confirmPassword = ref('');
const phoneHint = ref('');
const actionError = ref('');
const submitting = ref(false);
const passwordVisible = ref(false);
const phoneInputRef = ref<HTMLInputElement | null>(null);
const passwordInputRef = ref<HTMLInputElement | null>(null);

const visible = computed(() => state.authPromptVisible);
const promptReason = computed(() => state.authPromptReason || '继续当前操作');
const loginActionText = computed(() => {
  const reason = promptReason.value;
  if (/智能体|对话/u.test(reason)) {
    return '开启对话';
  }
  if (/个人中心|个人主页|积分记录|评测记录|修改用户名|修改密码/u.test(reason)) {
    return '开启个人中心';
  }
  if (/充值|支付|套餐/u.test(reason)) {
    return '开启充值';
  }
  return '开始评测';
});
const loginDialogTitle = computed(() => `立刻登录 · ${loginActionText.value}`);
const dialogTitle = computed(() => {
  if (mode.value === 'forgot_password') {
    return '找回密码';
  }
  if (mode.value === 'register') {
    return '开辟易理账号';
  }
  if (mode.value === 'login') {
    return loginDialogTitle.value;
  }
  if (mode.value === 'phone') {
    return loginDialogTitle.value;
  }
  if (mode.value === 'wechat_loading') {
    return '微信授权待接入';
  }
  return loginDialogTitle.value;
});
const dialogSubtitle = computed(() => {
  if (mode.value === 'forgot_password') {
    return '当前版本尚未接入短信或微信验证，先保留安全指引入口。';
  }
  if (mode.value === 'register') {
    return '建立您在 EaseWise「易如反掌」的数字命盘归位';
  }
  return '登录后方可使用评测及智能体对话功能';
});
const primaryActionLabel = computed(() => {
  if (mode.value === 'forgot_password') {
    return '返回登录';
  }
  if (mode.value === 'register') {
    return '注册';
  }
  if (mode.value === 'login') {
    return '登录';
  }
  return '下一步';
});

watch(visible, (value) => {
  if (value) {
    resetForm();
  }
});

function resetForm(): void {
  mode.value = 'options';
  phone.value = '';
  password.value = '';
  confirmPassword.value = '';
  phoneHint.value = '';
  actionError.value = '';
  submitting.value = false;
  passwordVisible.value = false;
}

function closeModal(): void {
  cancelAuthRequest();
  resetForm();
}

function validatePhoneInput(): string | null {
  const normalizedPhone = phone.value.replace(/\D/g, '');
  if (!/^1[3-9]\d{9}$/.test(normalizedPhone)) {
    actionError.value = '请输入正确的中国大陆手机号码。';
    return null;
  }
  phone.value = normalizedPhone;
  return normalizedPhone;
}

function validatePasswordStrength(value: string): boolean {
  if (value.trim() !== value) {
    return false;
  }
  if (value.length < 8 || value.length > 32) {
    return false;
  }
  if (new Set(value).size <= 1) {
    return false;
  }
  const categoryCount = [
    /\d/.test(value),
    /[a-zA-Z]/.test(value),
    /[^a-zA-Z0-9]/.test(value),
  ].filter(Boolean).length;
  return categoryCount >= 2;
}

async function handleWechatEntry(): Promise<void> {
  mode.value = 'wechat_loading';
  actionError.value = '微信一键登录入口已预留，请先使用手机号登录/注册完成测试闭环。';
}

function openForgotPasswordHelp(): void {
  mode.value = 'forgot_password';
  actionError.value = '';
  phoneHint.value = '';
}

function openForgotPasswordCustomerService(): void {
  openCustomerServiceModal('account_security');
}

async function handlePhoneNext(): Promise<void> {
  if (submitting.value) {
    return;
  }
  const normalizedPhone = validatePhoneInput();
  if (!normalizedPhone) {
    return;
  }
  submitting.value = true;
  actionError.value = '';
  phoneHint.value = '';
  try {
    const status = await checkPhoneAuthStatus(normalizedPhone);
    if (status.registered) {
      mode.value = 'login';
      phoneHint.value = '该手机号已注册，请直接输入密码登录。';
      await focusPasswordInput();
    } else {
      mode.value = 'register';
      phoneHint.value = '该手机号尚未注册，请先设置密码完成注册。';
      await focusPasswordInput();
    }
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    submitting.value = false;
  }
}

async function handleAuthSubmit(): Promise<void> {
  if (submitting.value) {
    return;
  }
  const normalizedPhone = validatePhoneInput();
  if (!normalizedPhone) {
    return;
  }
  if (mode.value === 'register') {
    if (!validatePasswordStrength(password.value)) {
      actionError.value = '密码强度不足，请使用 8-32 位且至少包含两类字符。';
      return;
    }
    if (password.value !== confirmPassword.value) {
      actionError.value = '两次输入的密码不一致。';
      return;
    }
  }
  if (mode.value === 'login' && !password.value.trim()) {
    actionError.value = '请输入密码。';
    return;
  }

  submitting.value = true;
  actionError.value = '';
  try {
    if (mode.value === 'register') {
      await registerWithPhonePassword(normalizedPhone, password.value, confirmPassword.value);
    } else {
      await loginWithPhonePassword(normalizedPhone, password.value);
    }
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    submitting.value = false;
  }
}

async function handleEnterSubmit(): Promise<void> {
  if (mode.value === 'phone') {
    await handlePhoneNext();
    return;
  }
  if (mode.value === 'login' || mode.value === 'register') {
    await handleAuthSubmit();
  }
}

function switchToPhoneFlow(): void {
  mode.value = 'phone';
  actionError.value = '';
  phoneHint.value = '';
  void focusPhoneInput();
}

function isRegisterMode(): boolean {
  return mode.value === 'register';
}

function handleBack(): void {
  if (mode.value === 'forgot_password') {
    mode.value = 'login';
    actionError.value = '';
    phoneHint.value = '';
    return;
  }
  if (mode.value === 'register' || mode.value === 'login') {
    mode.value = 'phone';
    actionError.value = '';
    phoneHint.value = '';
    return;
  }
  if (mode.value === 'phone' || mode.value === 'wechat_loading') {
    mode.value = 'options';
    actionError.value = '';
    phoneHint.value = '';
    return;
  }
  mode.value = 'options';
}

async function focusPhoneInput(): Promise<void> {
  await nextTick();
  phoneInputRef.value?.focus();
}

async function focusPasswordInput(): Promise<void> {
  await nextTick();
  passwordInputRef.value?.focus();
}
</script>

<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-[100] bg-slate-900/40 backdrop-blur-md flex items-center justify-center p-4"
      @click.self="closeModal"
    >
      <div class="w-full max-w-sm bg-white border border-brand-primary/15 rounded-3xl overflow-hidden shadow-2xl relative text-left">
        <div class="absolute -top-12 -right-12 text-brand-primary/[0.015] font-serif font-black text-[160px] pointer-events-none select-none">
          ☯
        </div>

        <button
          type="button"
          class="absolute top-4 right-4 w-7 h-7 rounded-full bg-gray-50 border border-gray-100 hover:bg-gray-100 text-gray-400 hover:text-gray-600 flex items-center justify-center hover:scale-105 active:scale-95 transition-all outline-none cursor-pointer z-10"
          @click="closeModal"
        >
          <X :size="14" />
        </button>

        <div class="px-6 pt-7 pb-4 text-center relative">
          <div class="inline-flex items-center justify-center w-11 h-11 rounded-full bg-brand-primary/10 border border-brand-primary/20 mb-3 select-none text-brand-primary text-[20px] font-serif animate-pulse">
            ☯
          </div>

          <transition name="fade" mode="out-in">
            <h2 :key="dialogTitle" class="text-base font-serif font-black text-brand-ink-strong tracking-wider uppercase mb-1">
              {{ dialogTitle }}
            </h2>
          </transition>
          <p class="text-[10px] text-brand-secondary leading-relaxed">
            {{ dialogSubtitle }}
          </p>

          <div
            v-if="promptReason && mode !== 'forgot_password'"
            class="mt-3 bg-brand-primary/5 border border-brand-primary/10 text-brand-primary-strong px-3 py-2 rounded-xl text-[10px] text-left leading-relaxed flex items-start gap-1.5"
          >
            <AlertCircle :size="12" class="shrink-0 mt-0.5 text-brand-primary" />
            <span>为了继续{{ promptReason }}，请先完成登录。</span>
          </div>
        </div>

        <div class="px-6 pb-6 space-y-4 relative">
          <transition name="shake">
            <div
              v-if="actionError"
              class="bg-rose-500/10 border border-rose-500/15 text-rose-700 rounded-xl px-3 py-2 text-[10.5px] leading-relaxed flex items-center gap-2"
            >
              <AlertCircle :size="13" class="shrink-0 text-rose-600" />
              <span>{{ actionError }}</span>
            </div>
          </transition>

          <transition name="fade">
            <div
              v-if="phoneHint"
              class="bg-emerald-500/10 border border-emerald-500/15 text-emerald-700 rounded-xl px-3 py-2 text-[10.5px] leading-relaxed flex items-center gap-2"
            >
              <CheckCircle2 :size="13" class="shrink-0 text-emerald-600" />
              <span>{{ phoneHint }}</span>
            </div>
          </transition>

          <div v-if="mode === 'options'" class="space-y-3">
            <button
              type="button"
              class="w-full py-3 bg-[#07C160] hover:bg-[#06B055] active:scale-[0.98] text-white font-semibold text-xs rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all outline-none shadow-md"
              @click="handleWechatEntry"
            >
              <span class="text-sm">💬</span>
              <span>微信一键授权安全登录</span>
            </button>

            <button
              type="button"
              class="w-full py-3 bg-brand-primary hover:bg-brand-primary-strong active:scale-[0.98] text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all outline-none border border-transparent shadow-sm"
              @click="switchToPhoneFlow"
            >
              <Smartphone :size="14" />
              <span>常用手机号安全登录 / 注册</span>
            </button>

            <div class="pt-2 text-center select-none">
              <span class="text-[9px] text-brand-secondary/40 uppercase tracking-widest font-mono">
                Secure sandboxed connection verified
              </span>
            </div>
          </div>

          <div v-else-if="mode === 'wechat_loading'" class="py-8 text-center space-y-4">
            <Loader2 class="w-10 h-10 text-[#07C160] animate-spin mx-auto" />
            <div class="space-y-1">
              <p class="text-[12.5px] font-bold text-[#07C160]">微信授权能力预留中...</p>
              <p class="text-[10px] text-brand-secondary">请先使用手机号登录/注册完成当前测试闭环</p>
            </div>
            <button
              type="button"
              class="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none"
              @click="handleBack"
            >
              <ChevronLeft :size="12" />
              <span>返回登录方式</span>
            </button>
          </div>

          <div v-else-if="mode === 'forgot_password'" class="py-5 space-y-4">
            <div class="mx-auto w-12 h-12 rounded-full bg-amber-500/10 border border-amber-200 text-amber-600 flex items-center justify-center select-none">
              <AlertCircle :size="20" />
            </div>
            <div class="space-y-2 text-center">
              <h3 class="text-[13px] font-bold text-brand-ink-strong">忘记密码暂不支持自助重置</h3>
              <p class="text-[11px] text-brand-secondary leading-relaxed px-1">
                由于短信验证和微信验证暂未接入，为保护账号资产，当前版本不开放直接重置密码。
                你可以先联系客服人工核验，或等待验证能力上线后再使用自助找回。
              </p>
              <div class="rounded-xl bg-brand-paper border border-gray-100 px-3 py-2 text-left text-[10.5px] text-brand-secondary leading-relaxed">
                <p class="font-bold text-brand-ink-strong">客服指引</p>
                <p class="mt-1">{{ customerServiceCopyForScene('account_security') }}</p>
              </div>
            </div>
            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary hover:bg-brand-primary-strong text-white active:scale-95 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none border border-transparent shadow-sm"
              @click="openForgotPasswordCustomerService"
            >
              联系客服人工核验
            </button>
            <button
              type="button"
              class="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 active:scale-95 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none border border-transparent"
              @click="handleBack"
            >
              <ChevronLeft :size="12" />
              <span>返回登录</span>
            </button>
          </div>

          <form v-else class="space-y-4" @submit.prevent="handleEnterSubmit">
            <div class="space-y-1">
              <div class="flex items-center justify-between gap-2">
                <label class="text-[9px] text-brand-secondary uppercase tracking-wider font-semibold">大陆手机号码</label>
                <button
                  v-if="mode === 'login'"
                  type="button"
                  class="text-[9.5px] text-brand-primary hover:text-brand-primary-strong outline-none cursor-pointer leading-none font-bold"
                  @click="openForgotPasswordHelp"
                >
                  忘记密码？
                </button>
              </div>
              <div class="relative flex items-center bg-brand-paper border border-gray-200 rounded-xl focus-within:border-brand-primary transition-all">
                <span class="pl-3.5 text-[11px] text-brand-primary font-bold">+86</span>
                <span class="h-4 w-px bg-gray-300 mx-2"></span>
                <input
                  ref="phoneInputRef"
                  v-model="phone"
                  type="tel"
                  inputmode="numeric"
                  autocomplete="tel"
                  maxlength="11"
                  placeholder="请输入您的11位大陆号码"
                  class="w-full bg-transparent border-none text-[12px] text-brand-ink py-2.5 pr-3.5 outline-none font-mono placeholder-gray-400"
                />
              </div>
            </div>

            <transition name="slide-down">
              <div v-if="mode !== 'phone'" class="space-y-3">
                <div class="space-y-1">
                  <div class="flex justify-between items-center">
                    <label class="text-[9px] text-brand-secondary uppercase tracking-wider font-semibold">
                      {{ isRegisterMode() ? '设置登入密码' : '账户登入密码' }}
                    </label>
                    <button
                      type="button"
                      class="text-[9.5px] text-brand-primary hover:text-brand-primary-strong outline-none cursor-pointer leading-none font-bold"
                      @click="mode = isRegisterMode() ? 'login' : 'register'; actionError = ''; phoneHint = ''"
                    >
                      {{ isRegisterMode() ? '使用已有密码登录' : '没有账号？立即注册' }}
                    </button>
                  </div>
                  <div class="relative flex items-center bg-brand-paper border border-gray-200 rounded-xl focus-within:border-brand-primary transition-all">
                    <span class="pl-3.5 text-gray-400 shrink-0"><LockKeyhole :size="12" /></span>
                    <span class="h-4 w-px bg-gray-300 mx-2"></span>
                    <input
                      ref="passwordInputRef"
                      v-model="password"
                      :type="passwordVisible ? 'text' : 'password'"
                      autocomplete="current-password"
                      placeholder="8-32位，至少包含两类字符"
                      class="w-full bg-transparent border-none text-[12px] text-brand-ink py-2.5 pr-10 outline-none placeholder-gray-400"
                    />
                    <button
                      type="button"
                      class="absolute right-3.5 text-gray-400 hover:text-gray-600 cursor-pointer select-none outline-none border-none bg-transparent"
                      @click="passwordVisible = !passwordVisible"
                    >
                      <Eye v-if="passwordVisible" :size="13" />
                      <EyeOff v-else :size="13" />
                    </button>
                  </div>
                </div>

                <transition name="slide-down">
                  <div v-if="isRegisterMode()" class="space-y-1">
                    <label class="text-[9px] text-brand-secondary uppercase tracking-wider font-semibold">确认您的登入密码</label>
                    <div class="relative flex items-center bg-brand-paper border border-gray-200 rounded-xl focus-within:border-brand-primary transition-all">
                      <span class="pl-3.5 text-gray-400 shrink-0"><LockKeyhole :size="12" /></span>
                      <span class="h-4 w-px bg-gray-300 mx-2"></span>
                      <input
                        v-model="confirmPassword"
                        type="password"
                        autocomplete="new-password"
                        placeholder="重复输入上方相同的安全密码"
                        class="w-full bg-transparent border-none text-[12px] text-brand-ink py-2.5 pr-3.5 outline-none placeholder-gray-400"
                      />
                    </div>
                  </div>
                </transition>
              </div>
            </transition>

            <div class="flex gap-2 pt-2">
              <button
                type="button"
                class="flex-1 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none"
                @click="handleBack"
              >
                <ChevronLeft :size="12" />
                <span>{{ mode === 'register' ? '上一步' : '返回' }}</span>
              </button>

              <button
                type="submit"
                class="flex-1 py-2.5 bg-brand-primary hover:bg-brand-primary-strong text-white active:scale-95 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none border border-transparent shadow-sm disabled:opacity-60"
                :disabled="submitting"
              >
                <Loader2 v-if="submitting" :size="13" class="animate-spin" />
                <ArrowRight v-else :size="13" />
                <span>{{ submitting ? '处理中' : primaryActionLabel }}</span>
              </button>
            </div>

            <div class="text-center pt-1">
              <span class="text-[9.5px] text-brand-secondary/60">
                当前阶段使用手机号 + 密码闭环，微信一键登录为后续预留。
              </span>
            </div>
          </form>

          <div
            v-if="mode === 'options' || mode === 'phone'"
            class="flex items-start gap-2 pt-2 text-[10px] text-brand-secondary leading-relaxed max-w-[95%] select-none"
          >
            <input
              type="checkbox"
              checked
              disabled
              class="accent-brand-primary rounded border-gray-300 shrink-0 mt-0.5 cursor-pointer"
            />
            <label class="cursor-default">
              <span>登录即代表同意 EaseWise 的</span>
              <span class="text-brand-primary font-bold">《用户服务协议》</span>
              <span>与</span>
              <span class="text-brand-primary font-bold">《隐私保护政策》</span>
              <span>，并允许账号安全同步积分、订单和评测记录。</span>
            </label>
          </div>

          <div class="flex items-center justify-center gap-1 text-[9px] text-brand-secondary/40 select-none bg-gray-50/50 border-t border-gray-100 pt-3">
            <ShieldCheck :size="10" />
            <span>本平台所有内容仅供娱乐，并无参考价值。</span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.shake-enter-active {
  animation: shake 0.35s ease-in-out;
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  20%,
  60% {
    transform: translateX(-4px);
  }
  40%,
  80% {
    transform: translateX(4px);
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
type LuckPollResult = 'completed' | 'processing' | 'cancelled';
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
const aspectStreamDrafts = ref<Record<string, AspectStreamDraft>>({});
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
const wheelScrollTimers = new WeakMap<HTMLElement, number>();
let waitingAnimationTimer: ReturnType<typeof setInterval> | null = null;
let waitingPoemTimer: ReturnType<typeof setInterval> | null = null;
let waitingStartedAt = 0;

const REVIEW_READY_RETRY_LIMIT = 180;
const REVIEW_READY_RETRY_DELAY_MS = 1000;
const LUCK_RENDER_RETRY_LIMIT = 90;
const LUCK_RENDER_RETRY_DELAY_MS = 2000;
const MAX_SHEN_SHA_ROWS = 3;
const LIFE_STAGE_NAMES = new Set(['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']);

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
const reviewScore = computed(() => currentReview.value?.score ?? 0);
const reviewAspects = computed<DisplayAspect[]>(() =>
  (currentReview.value?.aspects ?? []).map((aspect) => {
    const draft = aspectStreamDrafts.value[aspect.aspect_key];
    return {
      ...aspect,
      ...(draft
        ? {
            title: draft.title || aspect.title,
            content: draft.content ?? aspect.content,
            risk: draft.risk ?? aspect.risk,
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
  aspectStreamDrafts.value = {};
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
  await unlockSelectedAspect(aspect);
}

async function unlockSelectedAspect(aspect: DisplayAspect): Promise<void> {
  const review = currentReview.value;
  if (!review || aspect.is_unlocked) {
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
    clearAspectStreamDraft(aspect.aspect_key);
    if (error instanceof DOMException && error.name === 'AbortError') {
      return;
    }
    if (error instanceof ApiError && error.status === 402) {
      setError('unlock_points_insufficient');
      return;
    }
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
                  <span>{{ aspect.is_streaming ? '生成中' : (aspect.is_unlocked ? `${aspect.score ?? '--'}分` : `${aspect.unlock_points || effectiveAspectUnlockPoints}点`) }}</span>
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
                  :disabled="selectedAspectPending"
                  @click="void unlockSelectedAspect(selectedAspect)"
                >
                  <RefreshCw v-if="selectedAspectPending" :size="14" class="animate-spin" />
                  <UnlockKeyhole v-else :size="14" />
                  {{ selectedAspectPending ? '生成中' : '解锁' }}
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
  score?: number | null;
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

                    <p class="font-sans text-[10px] text-[#64748B] leading-relaxed">称骨为传统资料展示，不参与综合评分和专项判断。</p>
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

### `src/components/home/Home.vue`

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  AlertCircle,
  Calculator,
  Calendar,
  CheckCircle2,
  Coins,
  Compass,
  Fingerprint,
  Flower2,
  History,
  Sparkles,
  User,
  XCircle,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'phone-click'): void;
  (e: 'bazi-click'): void;
  (e: 'meihua-click'): void;
}>();

const { state, bootstrapApp, reviewBasePointsCost, fourPillarsBasePointsCost } = useEaseWiseApp();
const toast = ref<string | null>(null);
const yiExpanded = ref(false);
const jiExpanded = ref(false);

const points = computed(() => state.points?.balance ?? 0);
const displayDate = computed(() => {
  const rawText = state.almanac?.display_date || '';
  if (!rawText) {
    return '今日黄历加载中';
  }
  return rawText.replace(/\s*星期[一二三四五六日天]\s*$/u, '').trim();
});
const weekdayLabel = computed(() => state.almanac?.weekday_label || '--');
const almanacMetaText = computed(() => {
  if (!state.almanac) {
    return '黄历数据准备中';
  }
  return [
    weekdayLabel.value,
    state.almanac.lunar_date,
    state.almanac.ganzhi_year ? `${state.almanac.ganzhi_year}年` : '',
    state.almanac.ganzhi_month,
    state.almanac.ganzhi_day ? `${state.almanac.ganzhi_day}日` : '',
  ]
    .filter(Boolean)
    .join(' · ');
});
const yiItems = computed(() => (state.almanac?.yi.length ? state.almanac.yi : ['--']));
const jiItems = computed(() => (state.almanac?.ji.length ? state.almanac.ji : ['--']));
const yiHasMore = computed(() => (state.almanac?.yi.length || 0) > 5);
const jiHasMore = computed(() => (state.almanac?.ji.length || 0) > 5);
const visibleYiItems = computed(() => (yiExpanded.value || !yiHasMore.value ? yiItems.value : yiItems.value.slice(0, 5)));
const visibleJiItems = computed(() => (jiExpanded.value || !jiHasMore.value ? jiItems.value : jiItems.value.slice(0, 5)));
const tianShenTagText = computed(() => state.almanac?.tian_shen || '加载中');
const jiShenText = computed(() => (state.almanac?.ji_shen.length ? state.almanac.ji_shen.join(' · ') : '加载中'));
const pengzuSummary = computed(() => state.almanac?.pengzu_summary || '数据准备中');

function showToast(message: string): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, 2000);
}

function handleAlmanacClick(): void {
  if (typeof window !== 'undefined') {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }
  showToast('已为您跳转至今日黄历，可查看每日宜忌与星君值神。');
}

function handleWuxingClick(): void {
  showToast('「五行属性查询」功能正在开发中，敬请期待。');
}

onMounted(() => {
  void bootstrapApp();
});
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile relative">
    <transition name="fade-slide">
      <div
        v-if="toast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
      >
        <AlertCircle :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <section class="mb-4 mt-3">
      <div class="bg-white rounded-2xl p-4 border border-brand-paper shadow-sm relative">
        <div class="absolute -top-2.5 left-5 bg-brand-gold-fixed text-white font-sans text-[10px] font-semibold px-3 py-0.5 rounded-md tracking-widest shadow-sm flex items-center gap-1.5 z-10 select-none">
          <span class="w-1.5 h-1.5 rounded-full bg-white/80 shrink-0 animate-pulse"></span>
          <span>今日黄历 · ALMANAC</span>
        </div>

        <div class="absolute -top-2.5 right-5 bg-emerald-600 text-white font-sans text-[10px] font-semibold px-3 py-0.5 rounded-md tracking-wide shadow-sm flex items-center z-10 select-none">
          <span>值神星君 · </span>
          <span class="font-serif leading-none">{{ tianShenTagText }}</span>
        </div>

        <div class="flex justify-between items-center mb-1 text-left pt-1.5 gap-4">
          <div class="shrink-0">
            <div class="flex items-baseline gap-1.5">
              <span class="text-brand-ink-strong font-serif text-[22px] font-bold leading-none">{{ displayDate }}</span>
            </div>
          </div>
          <div class="flex-1 max-w-[50%] min-w-[130px]">
            <div class="bg-brand-primary/10 px-3 py-1.5 rounded-xl border border-brand-primary/30 flex items-center justify-between gap-1.5 shadow-sm w-full">
              <div class="flex items-center gap-1.5">
                <Sparkles :size="13" class="text-brand-gold-fixed fill-current shrink-0" />
                <span class="font-sans text-[13px] font-extrabold text-brand-secondary">余币</span>
              </div>
              <span class="font-sans text-[13px] font-extrabold text-brand-secondary whitespace-nowrap">
                <span class="text-brand-primary-strong font-serif text-[15px] font-extrabold">{{ points }}</span> 分
              </span>
            </div>
          </div>
        </div>

        <div class="mb-3.5 text-left pt-0.5 select-none animate-fadeIn">
          <p class="font-sans text-[11px] text-brand-secondary/95 font-bold tracking-wide">
            {{ almanacMetaText }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3 py-2.5 border-t border-b border-gray-100/80 mb-2 text-left">
          <div class="flex items-start gap-1.5">
            <div class="flex items-center gap-0.5 text-brand-primary font-serif text-[11px] font-bold mt-0.5 shrink-0">
              <CheckCircle2 :size="13" class="text-brand-primary" fill="currentColor" stroke="white" />
              <span>宜:</span>
            </div>
            <div class="flex flex-wrap gap-1 flex-1">
              <span v-for="v in visibleYiItems" :key="v" class="bg-brand-primary/5 text-brand-primary-strong font-serif text-[10px] px-1.5 py-0.5 rounded font-bold animate-fadeIn">{{ v }}</span>
              <button
                v-if="yiHasMore"
                class="bg-brand-primary hover:bg-brand-primary/90 text-white font-sans text-[10px] px-1.5 py-0.5 rounded font-bold cursor-pointer transition-colors border-none select-none outline-none inline-flex items-center justify-center shadow-sm shrink-0"
                @click.stop="yiExpanded = !yiExpanded"
              >
                {{ yiExpanded ? '收起' : '更多' }}
              </button>
            </div>
          </div>
          <div class="flex items-start gap-1.5 border-l border-gray-100 pl-2">
            <div class="flex items-center gap-0.5 text-brand-gold-fixed font-serif text-[11px] font-bold mt-0.5 shrink-0">
              <XCircle :size="13" class="text-brand-gold-fixed" fill="currentColor" stroke="white" />
              <span>忌:</span>
            </div>
            <div class="flex flex-wrap gap-1 flex-1">
              <span v-for="v in visibleJiItems" :key="v" class="bg-amber-50 text-brand-gold-fixed font-serif text-[10px] px-1.5 py-0.5 rounded font-bold animate-fadeIn">{{ v }}</span>
              <button
                v-if="jiHasMore"
                class="bg-brand-gold-fixed hover:bg-brand-gold-fixed/90 text-white font-sans text-[10px] px-1.5 py-0.5 rounded font-bold cursor-pointer transition-colors border-none select-none outline-none inline-flex items-center justify-center shadow-sm shrink-0"
                @click.stop="jiExpanded = !jiExpanded"
              >
                {{ jiExpanded ? '收起' : '更多' }}
              </button>
            </div>
          </div>
        </div>

        <div class="bg-brand-paper/50 rounded-xl p-2.5 font-sans text-[11px] text-brand-secondary space-y-1.5 text-left">
          <div class="flex justify-between items-baseline border-b border-gray-100 pb-1.5 gap-3">
            <span class="shrink-0">今日吉神：</span>
            <span class="text-brand-ink font-serif font-medium leading-tight text-right">{{ jiShenText }}</span>
          </div>
          <div class="flex justify-between items-baseline gap-3">
            <span class="shrink-0">彭祖百忌：</span>
            <span class="text-brand-ink font-serif font-medium leading-tight text-right">{{ pengzuSummary }}</span>
          </div>
        </div>
      </div>
    </section>

    <div class="space-y-3 mb-3.5">
      <button
        class="w-full bg-brand-primary text-white rounded-2xl p-4 shadow-sm flex items-center gap-3.5 active:scale-[0.99] hover:bg-brand-primary/95 hover:border-brand-accent/30 hover:shadow-md transition-all text-left relative overflow-hidden cursor-pointer border-none group min-h-[106px]"
        @click="emit('phone-click')"
      >
        <div class="absolute top-0 right-0 bg-brand-accent text-brand-ink-strong font-sans text-[9px] font-extrabold px-2.5 py-0.5 rounded-bl-lg uppercase tracking-wide">
          奇门遁甲 · 智能推演
        </div>
        <div class="bg-white/10 p-2.5 rounded-xl text-brand-accent shrink-0 group-hover:scale-105 transition-transform duration-200 flex items-center justify-center">
          <Calculator :size="22" class="text-brand-accent shrink-0 animate-bounce" />
        </div>
        <div class="flex-1 min-w-0 pr-12 flex flex-col gap-1 z-10">
          <span class="font-serif text-[15.5px] font-black leading-none flex items-center gap-1.5 flex-wrap text-white">
            数字奇门手机号评测
            <span class="px-1.5 py-0.5 bg-brand-accent/20 border border-brand-accent/40 rounded font-sans text-[9px] font-extrabold text-brand-accent leading-none select-none">
              消耗 {{ reviewBasePointsCost }} 积分
            </span>
          </span>
          <span class="font-sans text-[11px] text-white/80 leading-normal">
            输入你的 11 位手机号，解锁智能推演下的 13 项全面评测结果。
          </span>
        </div>
        <div class="absolute right-4 bottom-4 z-10 flex items-center gap-0.5 text-brand-accent text-[11px] font-sans font-extrabold">
          <span>立即评测</span>
          <span class="group-hover:translate-x-0.5 transition-transform duration-200">→</span>
        </div>
      </button>

      <button
        class="w-full bg-white text-brand-ink-strong rounded-2xl p-4 shadow-sm border border-brand-primary/15 flex items-center gap-3.5 active:scale-[0.99] hover:bg-slate-50/60 hover:border-brand-primary/25 hover:shadow-md transition-all text-left relative overflow-hidden cursor-pointer min-h-[106px] group"
        @click="emit('bazi-click')"
      >
        <div class="absolute top-0 right-0 bg-brand-primary/10 text-brand-primary-strong font-sans text-[9px] font-extrabold px-2.5 py-0.5 rounded-bl-lg uppercase tracking-wide">
          四柱八字 · 命盘评测
        </div>
        <div class="bg-brand-primary/10 p-2.5 rounded-xl text-brand-primary shrink-0 group-hover:scale-105 transition-transform duration-200 flex items-center justify-center">
          <Calendar :size="22" class="text-brand-primary shrink-0 bazi-float" />
        </div>
        <div class="flex-1 min-w-0 pr-12 flex flex-col gap-1 z-10">
          <span class="font-serif text-[15.5px] font-black leading-none flex items-center gap-1.5 flex-wrap text-brand-ink-strong group-hover:text-brand-primary transition-colors">
            四柱八字评测
            <span class="px-1.5 py-0.5 bg-brand-primary/10 border border-brand-primary/20 rounded font-sans text-[9px] font-extrabold text-brand-primary-strong leading-none select-none">
              消耗 {{ fourPillarsBasePointsCost }} 积分
            </span>
          </span>
          <span class="font-sans text-[11px] text-brand-secondary leading-normal">
            输入出生日期与时辰，查看命盘结构、五行比例、日主和专项趋势。
          </span>
        </div>
        <div class="absolute right-4 bottom-4 z-10 flex items-center gap-0.5 text-brand-primary-strong/80 text-[11px] font-sans font-extrabold group-hover:text-brand-primary transition-colors">
          <span>立即评测</span>
          <span class="group-hover:translate-x-0.5 transition-transform duration-200">→</span>
        </div>
      </button>

      <button
        class="w-full bg-white text-brand-ink-strong rounded-2xl p-4 shadow-sm border border-brand-primary/15 flex items-center gap-3.5 active:scale-[0.99] hover:bg-slate-50/60 hover:border-brand-primary/25 hover:shadow-md transition-all text-left relative overflow-hidden cursor-pointer min-h-[106px] group"
        @click="emit('meihua-click')"
      >
        <div class="absolute top-0 right-0 bg-brand-primary/10 text-brand-primary-strong font-sans text-[9px] font-extrabold px-2.5 py-0.5 rounded-bl-lg uppercase tracking-wide">
          梅花易数 · 起卦测算
        </div>
        <div class="bg-brand-primary/10 p-2.5 rounded-xl text-brand-primary shrink-0 group-hover:scale-105 transition-transform duration-200 flex items-center justify-center">
          <Flower2 :size="22" class="text-brand-primary shrink-0 meihua-sway" />
        </div>
        <div class="flex-1 min-w-0 pr-12 flex flex-col gap-1 z-10">
          <span class="font-serif text-[15.5px] font-black leading-none flex items-center gap-1.5 flex-wrap text-brand-ink-strong group-hover:text-brand-primary transition-colors">
            梅花易数评测
            <span class="px-1.5 py-0.5 bg-brand-primary/10 border border-brand-primary/20 rounded font-sans text-[9px] font-extrabold text-brand-primary-strong leading-none select-none">
              原型体验
            </span>
          </span>
          <span class="font-sans text-[11px] text-brand-secondary leading-normal">
            支持报数、时间、汉字起卦，初步查看体用五行生克与谋事趋势。
          </span>
        </div>
        <div class="absolute right-4 bottom-4 z-10 flex items-center gap-0.5 text-brand-primary-strong/80 text-[11px] font-sans font-extrabold group-hover:text-brand-primary transition-colors">
          <span>立即起卦</span>
          <span class="group-hover:translate-x-0.5 transition-transform duration-200">→</span>
        </div>
      </button>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-4">
      <button
        type="button"
        class="bg-white text-brand-ink-strong rounded-2xl p-3.5 shadow-sm border border-brand-primary/15 flex items-center gap-3 active:scale-[0.99] transition-all hover:bg-slate-50/60 hover:border-brand-primary/25 hover:shadow-md text-left relative overflow-hidden cursor-pointer h-[106px] group"
        @click="handleAlmanacClick"
      >
        <div class="absolute top-0 right-0 bg-brand-primary/10 text-brand-primary-strong font-sans text-[9px] font-extrabold px-2.5 py-0.5 rounded-bl-lg uppercase tracking-wide">
          常用工具
        </div>
        <div class="bg-brand-primary/10 p-2.5 rounded-xl text-brand-primary shrink-0 group-hover:scale-105 transition-transform duration-200 flex items-center justify-center">
          <History :size="22" class="shrink-0" />
        </div>
        <div class="flex-1 min-w-0 pr-10 flex flex-col gap-1 z-10">
          <span class="font-serif text-[14px] font-black leading-none text-brand-ink-strong group-hover:text-brand-primary transition-colors">黄历查询</span>
          <span class="font-sans text-[9.5px] text-brand-secondary leading-normal line-clamp-1 truncate">今日宜忌与神君值神</span>
        </div>
        <div class="absolute right-3.5 bottom-3.5 z-10 flex items-center gap-0.5 text-brand-primary-strong/80 text-[9.5px] font-sans font-extrabold group-hover:text-brand-primary transition-colors">
          <span>立即查询</span>
          <span class="group-hover:translate-x-0.5 transition-transform duration-200">→</span>
        </div>
      </button>

      <button
        type="button"
        class="bg-white text-brand-ink-strong rounded-2xl p-3.5 shadow-sm border border-brand-primary/15 flex items-center gap-3 active:scale-[0.99] transition-all hover:bg-slate-50/60 hover:border-brand-primary/25 hover:shadow-md text-left relative overflow-hidden cursor-pointer h-[106px] group"
        @click="handleWuxingClick"
      >
        <div class="absolute top-0 right-0 bg-brand-primary/10 text-brand-primary-strong font-sans text-[9px] font-extrabold px-2.5 py-0.5 rounded-bl-lg uppercase tracking-wide">
          常用工具
        </div>
        <div class="bg-brand-primary/10 p-2.5 rounded-xl text-brand-primary shrink-0 group-hover:scale-105 transition-transform duration-200 flex items-center justify-center">
          <Sparkles :size="22" class="text-brand-primary shrink-0" />
        </div>
        <div class="flex-1 min-w-0 pr-10 flex flex-col gap-1 z-10">
          <span class="font-serif text-[14px] font-black leading-none text-brand-ink-strong group-hover:text-brand-primary transition-colors">五行属性</span>
          <span class="font-sans text-[9.5px] text-brand-secondary leading-normal line-clamp-1 truncate">汉字与事理五行属性</span>
        </div>
        <div class="absolute right-3.5 bottom-3.5 z-10 flex items-center gap-0.5 text-brand-primary-strong/80 text-[9.5px] font-sans font-extrabold group-hover:text-brand-primary transition-colors">
          <span>立即查询</span>
          <span class="group-hover:translate-x-0.5 transition-transform duration-200">→</span>
        </div>
      </button>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-4">
      <button
        v-for="item in [
          { name: '微信头像', desc: '头像磁场与运势解读', icon: User },
          { name: '奇门遁甲', desc: '时家日家奇门大盘推演', icon: Compass },
          { name: '面手相学', desc: '面部五官与掌纹智能识别', icon: Fingerprint },
          { name: '六爻问事', desc: '古法铜钱起卦与周易排盘', icon: Coins },
        ]"
        :key="item.name"
        type="button"
        class="bg-white/70 text-slate-400 rounded-2xl p-3.5 border border-slate-200/60 flex items-center gap-3 text-left relative overflow-hidden h-[106px] cursor-not-allowed opacity-75"
        disabled
      >
        <div class="absolute top-0 right-0 bg-slate-100 text-slate-500 font-sans text-[8.5px] font-extrabold px-2 py-0.5 rounded-bl-lg uppercase tracking-wide">
          敬请期待
        </div>
        <div class="bg-slate-100 p-2.5 rounded-xl text-slate-400 shrink-0 flex items-center justify-center">
          <component :is="item.icon" :size="22" class="shrink-0" />
        </div>
        <div class="flex-1 min-w-0 pr-10 flex flex-col gap-1">
          <span class="font-serif text-[14px] font-black leading-none text-slate-500">{{ item.name }}</span>
          <span class="font-sans text-[9.5px] text-slate-400 leading-normal line-clamp-1 truncate">{{ item.desc }}</span>
        </div>
        <div class="absolute right-3.5 bottom-3.5 flex items-center gap-0.5 text-slate-400 text-[9.5px] font-sans font-extrabold">
          <span>暂未开放</span>
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}

.animate-fadeIn {
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(2px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
```

### `src/components/layout/BottomNav.vue`

```vue
<script setup lang="ts">
import { Home, MessageSquare, User } from 'lucide-vue-next';

defineProps<{
  activeTab: string;
}>();

const emit = defineEmits<{
  (e: 'update:activeTab', tab: string): void;
}>();

const tabs = [
  { id: 'home', label: '首页', icon: Home },
  { id: 'agent', label: '智能体', icon: MessageSquare },
  { id: 'profile', label: '我的', icon: User },
];
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 w-full z-50 flex justify-around items-center px-6 pb-6 pt-2.5 max-w-md mx-auto bg-white border-t border-gray-100 rounded-t-2xl shadow-lg backdrop-blur-md bg-white/95">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      type="button"
      @click="emit('update:activeTab', tab.id)"
      class="flex flex-col items-center justify-center transition-all duration-200 outline-none w-20 py-1 cursor-pointer font-sans"
      :class="activeTab === tab.id ? 'text-brand-primary font-semibold' : 'text-brand-secondary hover:text-brand-primary'"
      :data-icon="tab.id"
    >
      <div class="p-1 px-3.5 rounded-full transition-colors flex items-center justify-center"
           :class="activeTab === tab.id ? 'bg-brand-primary/10 text-brand-primary' : 'text-brand-secondary'">
        <component :is="tab.icon" :size="22" class="shrink-0" />
      </div>
      <span class="text-[11px] mt-1 tracking-wide">{{ tab.label }}</span>
    </button>
  </nav>
</template>
```

### `src/components/layout/Header.vue`

```vue
<script setup lang="ts">
import { Menu, Bell } from 'lucide-vue-next';

defineProps<{
  title?: string;
}>();

const emit = defineEmits<{
  (e: 'menu-click'): void;
}>();
</script>

<template>
  <header class="fixed top-0 left-0 right-0 w-full bg-brand-paper/80 backdrop-blur-md z-50 max-w-md mx-auto border-b border-gray-100">
    <div class="flex justify-between items-center px-margin-mobile h-16 w-full">
      <div class="flex items-center gap-1.5">
        <button
          @click="emit('menu-click')"
          class="p-2 hover:bg-gray-100 rounded-full transition-colors outline-none cursor-pointer"
        >
          <Menu :size="22" class="text-brand-ink-strong" data-icon="menu" />
        </button>
        <h1
          v-if="title"
          class="font-serif text-[20px] font-bold text-brand-ink-strong tracking-wide leading-tight"
        >
          {{ title ?? '易如反掌' }}
        </h1>
      </div>
      <button class="p-2 hover:bg-gray-100 rounded-full transition-colors relative outline-none cursor-pointer">
        <Bell :size="22" class="text-brand-ink-strong" data-icon="notifications" />
        <span class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-brand-paper"></span>
      </button>
    </div>
  </header>
</template>
```

### `src/components/meihua/MeihuaAnalysis.vue`

```vue
<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  AlertCircle,
  ArrowLeft,
  BookOpen,
  Check,
  Clock,
  Compass,
  Hash,
  MessageSquare,
  PenTool,
  RefreshCw,
  Sparkles,
} from 'lucide-vue-next';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string>): void;
}>();

type CastingMethod = 'number' | 'text' | 'time';
type ViewState = 'input' | 'animating' | 'result';
type LineValue = 0 | 1;

type Trigram = {
  number: number;
  name: string;
  nature: string;
  symbol: string;
  lines: [LineValue, LineValue, LineValue];
  element: string;
};

type HexagramResult = {
  upper: Trigram;
  lower: Trigram;
  lines: LineValue[];
  name: string;
};

const viewState = ref<ViewState>('input');
const castingMethod = ref<CastingMethod>('number');
const toast = ref<string | null>(null);
const inputNum1 = ref('');
const inputNum2 = ref('');
const inputText1 = ref('');
const inputText2 = ref('');
const selectHourZhi = ref('辰');
const questionAspect = ref('综合');
const animProgress = ref(0);
const animStatusText = ref('正在感应太极气场...');

const originalHexagram = ref<HexagramResult | null>(null);
const mutualHexagram = ref<HexagramResult | null>(null);
const transformedHexagram = ref<HexagramResult | null>(null);
const movingLineNum = ref(1);
const subjectTrigram = ref<Trigram | null>(null);
const objectTrigram = ref<Trigram | null>(null);
const relationshipType = ref('');
const relationshipTone = ref('');
const relationshipInterpretation = ref('');

const hourZhis = [
  { zhi: '子', time: '23:00-01:00', index: 1 },
  { zhi: '丑', time: '01:00-03:00', index: 2 },
  { zhi: '寅', time: '03:00-05:00', index: 3 },
  { zhi: '卯', time: '05:00-07:00', index: 4 },
  { zhi: '辰', time: '07:00-09:00', index: 5 },
  { zhi: '巳', time: '09:00-11:00', index: 6 },
  { zhi: '午', time: '11:00-13:00', index: 7 },
  { zhi: '未', time: '13:00-15:00', index: 8 },
  { zhi: '申', time: '15:00-17:00', index: 9 },
  { zhi: '酉', time: '17:00-19:00', index: 10 },
  { zhi: '戌', time: '19:00-21:00', index: 11 },
  { zhi: '亥', time: '21:00-23:00', index: 12 },
];

const questionAspects = ['综合', '财运', '感情', '事业', '出行', '寻物'];

const trigrams: Record<number, Trigram> = {
  1: { number: 1, name: '乾', nature: '天', symbol: '☰', lines: [1, 1, 1], element: '金' },
  2: { number: 2, name: '兑', nature: '泽', symbol: '☱', lines: [1, 1, 0], element: '金' },
  3: { number: 3, name: '离', nature: '火', symbol: '☲', lines: [1, 0, 1], element: '火' },
  4: { number: 4, name: '震', nature: '雷', symbol: '☳', lines: [1, 0, 0], element: '木' },
  5: { number: 5, name: '巽', nature: '风', symbol: '☴', lines: [0, 1, 1], element: '木' },
  6: { number: 6, name: '坎', nature: '水', symbol: '☵', lines: [0, 1, 0], element: '水' },
  7: { number: 7, name: '艮', nature: '山', symbol: '☶', lines: [0, 0, 1], element: '土' },
  8: { number: 8, name: '坤', nature: '地', symbol: '☷', lines: [0, 0, 0], element: '土' },
};

const hexagramNames: Record<string, string> = {
  '1-1': '乾为天', '1-2': '天泽履', '1-3': '天火同人', '1-4': '天雷无妄', '1-5': '天风姤', '1-6': '天水讼', '1-7': '天山遁', '1-8': '天地否',
  '2-1': '泽天夬', '2-2': '兑为泽', '2-3': '泽火革', '2-4': '泽雷随', '2-5': '泽风大过', '2-6': '泽水困', '2-7': '泽山咸', '2-8': '泽地萃',
  '3-1': '火天大有', '3-2': '火泽睽', '3-3': '离为火', '3-4': '火雷噬嗑', '3-5': '火风鼎', '3-6': '火水未济', '3-7': '火山旅', '3-8': '火地晋',
  '4-1': '雷天大壮', '4-2': '雷泽归妹', '4-3': '雷火丰', '4-4': '震为雷', '4-5': '雷风恒', '4-6': '雷水解', '4-7': '雷山小过', '4-8': '雷地豫',
  '5-1': '风天小畜', '5-2': '风泽中孚', '5-3': '风火家人', '5-4': '风雷益', '5-5': '巽为风', '5-6': '风水涣', '5-7': '风山渐', '5-8': '风地观',
  '6-1': '水天需', '6-2': '水泽节', '6-3': '水火既济', '6-4': '水雷屯', '6-5': '水风井', '6-6': '坎为水', '6-7': '水山蹇', '6-8': '水地比',
  '7-1': '山天大畜', '7-2': '山泽损', '7-3': '山火贲', '7-4': '山雷颐', '7-5': '山风蛊', '7-6': '山水蒙', '7-7': '艮为山', '7-8': '山地剥',
  '8-1': '地天泰', '8-2': '地泽临', '8-3': '地火明夷', '8-4': '地雷复', '8-5': '地风升', '8-6': '地水师', '8-7': '地山谦', '8-8': '坤为地',
};

const methodCards = [
  { key: 'number' as const, title: '报数起卦', desc: '输入两组心中吉数', icon: Hash },
  { key: 'text' as const, title: '汉字起卦', desc: '以两字笔画取象', icon: PenTool },
  { key: 'time' as const, title: '时间起卦', desc: '以当前时机成卦', icon: Clock },
];

const resultAdvice = computed(() => {
  if (!relationshipType.value) return '';
  if (relationshipType.value === '用生体' || relationshipType.value === '体用比和') {
    return '当前气机较顺，适合顺势推进。可以先做小范围验证，再逐步放大行动。';
  }
  if (relationshipType.value === '体克用') {
    return '此象重在主动掌控。事情并非无阻，但适合明确目标、拆解步骤、稳步推进。';
  }
  if (relationshipType.value === '体生用') {
    return '此象有付出之意。宜先评估成本和精力，不要因投入过多而忽略自己的节奏。';
  }
  return '外部压力较强，宜先守后动。把问题拆小，等条件更清晰时再做关键决定。';
});

function showToast(message: string): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, 2400);
}

function trigramByLines(lines: LineValue[]): Trigram {
  return Object.values(trigrams).find((item) => item.lines.every((line, index) => line === lines[index])) || trigrams[1];
}

function hexagramName(upper: Trigram, lower: Trigram): string {
  return hexagramNames[`${upper.number}-${lower.number}`] || `${upper.name}${lower.name}卦`;
}

function numberToTrigram(value: number): Trigram {
  const key = value % 8 || 8;
  return trigrams[key];
}

function safePositiveInteger(value: string): number | null {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function charScore(value: string): number {
  const char = value.trim().charAt(0);
  if (!char) return 0;
  const common: Record<string, number> = {
    梅: 11,
    花: 7,
    易: 8,
    数: 13,
    财: 10,
    情: 11,
    事: 8,
    问: 6,
    家: 10,
    人: 2,
    心: 4,
    行: 6,
    吉: 6,
    凶: 4,
    成: 6,
    败: 8,
  };
  return common[char] || (char.charCodeAt(0) % 13) + 3;
}

function currentHourBranchIndex(): number {
  const hour = new Date().getHours();
  const branch = Math.floor((hour + 1) / 2) % 12;
  return branch + 1;
}

function buildHexagram(upper: Trigram, lower: Trigram): HexagramResult {
  const lines = [...lower.lines, ...upper.lines];
  return {
    upper,
    lower,
    lines,
    name: hexagramName(upper, lower),
  };
}

function calculateMutual(lines: LineValue[]): HexagramResult {
  const lower = trigramByLines([lines[1], lines[2], lines[3]]);
  const upper = trigramByLines([lines[2], lines[3], lines[4]]);
  return buildHexagram(upper, lower);
}

function calculateTransformed(lines: LineValue[], movingLine: number): HexagramResult {
  const transformed = [...lines] as LineValue[];
  const index = movingLine - 1;
  transformed[index] = transformed[index] === 1 ? 0 : 1;
  const lower = trigramByLines([transformed[0], transformed[1], transformed[2]]);
  const upper = trigramByLines([transformed[3], transformed[4], transformed[5]]);
  return buildHexagram(upper, lower);
}

function calculateRelationship(subject: string, object: string): void {
  if (subject === object) {
    relationshipType.value = '体用比和';
    relationshipTone.value = 'text-emerald-700 bg-emerald-50 border-emerald-100';
    relationshipInterpretation.value = '体卦与用卦同气相求，内外同频，适合稳健推进。';
    return;
  }
  const generates: Record<string, string> = { 水: '木', 木: '火', 火: '土', 土: '金', 金: '水' };
  const controls: Record<string, string> = { 金: '木', 木: '土', 土: '水', 水: '火', 火: '金' };
  if (generates[object] === subject) {
    relationshipType.value = '用生体';
    relationshipTone.value = 'text-brand-primary bg-indigo-50 border-indigo-100';
    relationshipInterpretation.value = '外部条件生助自身，事情容易得到资源、时机或他人帮助。';
    return;
  }
  if (generates[subject] === object) {
    relationshipType.value = '体生用';
    relationshipTone.value = 'text-amber-700 bg-amber-50 border-amber-100';
    relationshipInterpretation.value = '自身生助事体，代表投入与消耗增加，需要守住节奏。';
    return;
  }
  if (controls[subject] === object) {
    relationshipType.value = '体克用';
    relationshipTone.value = 'text-blue-700 bg-blue-50 border-blue-100';
    relationshipInterpretation.value = '自身能制约事体，有掌控空间，但需要持续推进。';
    return;
  }
  relationshipType.value = '用克体';
  relationshipTone.value = 'text-rose-700 bg-rose-50 border-rose-100';
  relationshipInterpretation.value = '事体对自身形成压力，当前宜谨慎观察，避免急进。';
}

function resolveInputNumbers(): { first: number; second: number; hourIndex: number } | null {
  const selectedHour = hourZhis.find((item) => item.zhi === selectHourZhi.value)?.index || currentHourBranchIndex();
  if (castingMethod.value === 'number') {
    const first = safePositiveInteger(inputNum1.value);
    const second = safePositiveInteger(inputNum2.value);
    if (!first || !second) {
      showToast('请输入两组大于零的正整数。');
      return null;
    }
    return { first, second, hourIndex: selectedHour };
  }
  if (castingMethod.value === 'text') {
    const first = charScore(inputText1.value);
    const second = charScore(inputText2.value);
    if (!first || !second) {
      showToast('请输入两个用于起卦的汉字。');
      return null;
    }
    return { first, second, hourIndex: selectedHour };
  }
  const now = new Date();
  return {
    first: now.getFullYear() + now.getMonth() + 1 + now.getDate(),
    second: now.getHours() + now.getMinutes() + now.getDate(),
    hourIndex: currentHourBranchIndex(),
  };
}

function performCasting(): void {
  const input = resolveInputNumbers();
  if (!input) return;
  const upper = numberToTrigram(input.first);
  const lower = numberToTrigram(input.second);
  const movingLine = (input.first + input.second + input.hourIndex) % 6 || 6;
  const original = buildHexagram(upper, lower);
  originalHexagram.value = original;
  mutualHexagram.value = calculateMutual(original.lines);
  transformedHexagram.value = calculateTransformed(original.lines, movingLine);
  movingLineNum.value = movingLine;

  if (movingLine <= 3) {
    objectTrigram.value = lower;
    subjectTrigram.value = upper;
  } else {
    objectTrigram.value = upper;
    subjectTrigram.value = lower;
  }
  calculateRelationship(subjectTrigram.value.element, objectTrigram.value.element);
  runCastingAnimation();
}

function runCastingAnimation(): void {
  viewState.value = 'animating';
  animProgress.value = 0;
  animStatusText.value = '正在感应太极八卦气场...';
  const timer = window.setInterval(() => {
    animProgress.value = Math.min(100, animProgress.value + 12);
    if (animProgress.value > 75) {
      animStatusText.value = '爻象定局，显化体用生克...';
    } else if (animProgress.value > 45) {
      animStatusText.value = '九宫流转，推演本互变卦...';
    } else if (animProgress.value > 20) {
      animStatusText.value = '灵机初动，取数成象...';
    }
    if (animProgress.value >= 100) {
      window.clearInterval(timer);
      window.setTimeout(() => {
        viewState.value = 'result';
      }, 350);
    }
  }, 160);
}

function resetCasting(): void {
  viewState.value = 'input';
  animProgress.value = 0;
}
</script>

<template>
  <div class="min-h-screen bg-brand-paper pb-28">
    <transition name="fade-slide">
      <div
        v-if="toast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
      >
        <AlertCircle :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <header class="sticky top-0 z-20 bg-brand-paper/95 backdrop-blur border-b border-white/80">
      <div class="max-w-md mx-auto px-margin-mobile py-3 flex items-center justify-between">
        <button
          class="h-9 rounded-lg bg-white border border-gray-100 px-3 text-brand-secondary font-sans text-[12px] font-bold flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
          @click="viewState === 'result' ? resetCasting() : emit('back-to-home')"
        >
          <ArrowLeft :size="14" class="text-brand-ink-strong" />
          <span>{{ viewState === 'result' ? '重新起卦' : '返回首页' }}</span>
        </button>
        <div class="text-center">
          <h1 class="font-serif text-[17.5px] font-black text-brand-ink-strong leading-none">梅花易数精研</h1>
          <p class="font-sans text-[10.5px] text-brand-secondary mt-1">前端原型 · 后续接入正式业务</p>
        </div>
        <button
          class="w-9 h-9 rounded-lg bg-white border border-gray-100 flex items-center justify-center shadow-sm cursor-pointer"
          @click="resetCasting"
        >
          <RefreshCw :size="16" class="text-brand-secondary" />
        </button>
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
            <h2 class="font-serif text-[16px] font-black text-brand-gold-fixed leading-snug">梅花易数起卦测算</h2>
          </div>
          <p class="font-sans text-[11px] text-brand-secondary leading-relaxed mt-2">
            先吸收 AI Studio 的页面设计作为原型；正式计费、历史记录与报告生成会在后续业务开发中接入。
          </p>
        </section>

        <section class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm space-y-4">
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="method in methodCards"
              :key="method.key"
              type="button"
              class="rounded-xl border p-2.5 text-center transition-all"
              :class="castingMethod === method.key ? 'border-brand-primary bg-brand-primary/5 text-brand-primary' : 'border-gray-100 bg-brand-paper/60 text-brand-secondary'"
              @click="castingMethod = method.key"
            >
              <component :is="method.icon" :size="16" class="mx-auto mb-1" />
              <span class="block font-serif text-[12px] font-black">{{ method.title }}</span>
              <span class="block font-sans text-[9px] mt-0.5">{{ method.desc }}</span>
            </button>
          </div>

          <div v-if="castingMethod === 'number'" class="grid grid-cols-2 gap-3">
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第一组数</span>
              <input v-model="inputNum1" inputmode="numeric" placeholder="如 18" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第二组数</span>
              <input v-model="inputNum2" inputmode="numeric" placeholder="如 27" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
          </div>

          <div v-else-if="castingMethod === 'text'" class="grid grid-cols-2 gap-3">
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第一字</span>
              <input v-model="inputText1" maxlength="2" placeholder="梅" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第二字</span>
              <input v-model="inputText2" maxlength="2" placeholder="花" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
          </div>

          <div v-else class="rounded-xl bg-brand-primary/5 border border-brand-primary/15 px-3 py-3 text-left">
            <p class="font-serif text-[13px] font-black text-brand-ink-strong">以当前时间自动起卦</p>
            <p class="font-sans text-[11px] text-brand-secondary leading-relaxed mt-1">点击下方按钮后，将以当前年月日时生成本卦、互卦与变卦。</p>
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-between gap-3">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">时辰</span>
              <div class="flex-1 overflow-x-auto no-scrollbar">
                <div class="flex gap-1.5 justify-end min-w-max">
                  <button
                    v-for="hour in hourZhis"
                    :key="hour.zhi"
                    type="button"
                    class="h-8 px-2.5 rounded-lg text-[11px] font-bold border"
                    :class="selectHourZhi === hour.zhi ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
                    @click="selectHourZhi = hour.zhi"
                  >
                    {{ hour.zhi }}
                  </button>
                </div>
              </div>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">主题</span>
              <div class="flex-1 overflow-x-auto no-scrollbar">
                <div class="flex gap-1.5 justify-end min-w-max">
                  <button
                    v-for="aspect in questionAspects"
                    :key="aspect"
                    type="button"
                    class="h-8 px-2.5 rounded-lg text-[11px] font-bold border"
                    :class="questionAspect === aspect ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
                    @click="questionAspect = aspect"
                  >
                    {{ aspect }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <button
          class="w-full h-12 rounded-xl bg-brand-primary hover:bg-brand-primary-strong text-white font-sans text-[13px] font-bold shadow-md transition-all active:scale-[0.985] flex items-center justify-center gap-1.5"
          @click="performCasting"
        >
          <Sparkles :size="15" fill="currentColor" />
          <span>进入深度梅花推演</span>
        </button>
      </section>

      <section v-else-if="viewState === 'animating'" class="py-14 flex flex-col justify-center min-h-[65vh]">
        <div class="bg-white rounded-2xl p-6 border border-gray-150/75 shadow-sm space-y-6 text-center">
          <div class="relative w-28 h-28 mx-auto flex items-center justify-center select-none">
            <div class="absolute inset-0 bg-brand-primary/5 rounded-full blur-md animate-pulse"></div>
            <div class="absolute inset-3 border border-brand-primary/20 rounded-full animate-spin [animation-duration:8s]"></div>
            <Compass :size="42" class="text-brand-primary meihua-sway" />
          </div>
          <div>
            <p class="font-serif text-[17px] font-black text-brand-ink-strong">一念起卦中</p>
            <p class="font-sans text-[12px] text-brand-secondary mt-2">{{ animStatusText }}</p>
          </div>
          <div class="h-2 rounded-full bg-brand-paper overflow-hidden">
            <div class="h-full bg-brand-primary transition-all duration-200" :style="{ width: `${animProgress}%` }"></div>
          </div>
        </div>
      </section>

      <section v-else class="space-y-4">
        <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <div class="flex items-center justify-between gap-3 mb-3">
            <div>
              <p class="font-sans text-[10px] font-black tracking-wide text-brand-secondary">MEIHUA RESULT</p>
              <h2 class="font-serif text-[17px] font-black text-brand-ink-strong mt-0.5">梅花易数定盘报告</h2>
            </div>
            <div class="rounded-xl bg-brand-primary/10 text-brand-primary p-2.5">
              <BookOpen :size="20" />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <div
              v-for="item in [
                { label: '本卦', value: originalHexagram },
                { label: '互卦', value: mutualHexagram },
                { label: '变卦', value: transformedHexagram },
              ]"
              :key="item.label"
              class="rounded-xl bg-brand-paper/70 border border-gray-100 px-2 py-3 text-center"
            >
              <span class="font-sans text-[10px] font-bold text-brand-secondary">{{ item.label }}</span>
              <span class="block font-serif text-[22px] font-black text-brand-primary leading-none mt-1">{{ item.value?.upper.symbol }}{{ item.value?.lower.symbol }}</span>
              <span class="block font-serif text-[12px] font-black text-brand-ink-strong mt-1">{{ item.value?.name }}</span>
            </div>
          </div>
        </section>

        <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm space-y-3">
          <div class="flex items-center gap-2">
            <MessageSquare :size="16" class="text-brand-primary" />
            <h3 class="font-serif text-[15px] font-black text-brand-ink-strong">体用生克</h3>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="rounded-xl bg-brand-paper/70 border border-gray-100 p-3">
              <span class="font-sans text-[10px] font-bold text-brand-secondary">体卦</span>
              <p class="font-serif text-[16px] font-black text-brand-ink-strong mt-1">{{ subjectTrigram?.name }}为{{ subjectTrigram?.nature }} · {{ subjectTrigram?.element }}</p>
            </div>
            <div class="rounded-xl bg-brand-paper/70 border border-gray-100 p-3">
              <span class="font-sans text-[10px] font-bold text-brand-secondary">用卦</span>
              <p class="font-serif text-[16px] font-black text-brand-ink-strong mt-1">{{ objectTrigram?.name }}为{{ objectTrigram?.nature }} · {{ objectTrigram?.element }}</p>
            </div>
          </div>
          <div class="rounded-xl border p-3" :class="relationshipTone">
            <div class="flex items-center justify-between gap-3">
              <span class="font-serif text-[16px] font-black">{{ relationshipType }}</span>
              <span class="font-sans text-[11px] font-black">动爻 {{ movingLineNum }} 爻</span>
            </div>
            <p class="font-sans text-[12px] leading-relaxed mt-2">{{ relationshipInterpretation }}</p>
          </div>
        </section>

        <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <div class="flex items-center gap-2 mb-2">
            <Check :size="16" class="text-brand-primary" />
            <h3 class="font-serif text-[15px] font-black text-brand-ink-strong">行动锦囊</h3>
          </div>
          <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">{{ resultAdvice }}</p>
          <p class="font-sans text-[10px] text-brand-secondary/80 leading-relaxed mt-3">
            当前为前端原型结果，仅用于产品设计体验；后续会接入正式知识库、计费、记录与 AI 解读链路。
          </p>
        </section>
      </section>
    </main>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}
</style>
```

### `src/components/points-claim/PointsClaimPage.vue`

```vue
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Gift,
  Loader2,
  MessageSquare,
  RefreshCw,
  Sparkles,
  UserRound,
} from 'lucide-vue-next';
import { claimPublicPoints, getPublicPointsClaimLink } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { PointsClaimSubmitResponse, PublicPointsClaimLinkResponse } from '../../types/api';

const props = defineProps<{
  claimCode: string;
}>();

const emit = defineEmits<{
  (event: 'navigate-to-tab', tab: string): void;
}>();

type PageState =
  | 'loading'
  | 'invalid'
  | 'expired'
  | 'disabled'
  | 'not_started'
  | 'auth_required'
  | 'ready'
  | 'submitting'
  | 'granted'
  | 'already_claimed_this_week'
  | 'error';

const {
  state,
  bootstrapApp,
  requestRegisteredUser,
  refreshPoints,
  isRegisteredUser,
  displayNickname,
  humanizeError,
  openCustomerServiceModal,
} = useEaseWiseApp();

const pageState = ref<PageState>('loading');
const claimLink = ref<PublicPointsClaimLinkResponse | null>(null);
const claimResult = ref<PointsClaimSubmitResponse | null>(null);
const actionError = ref('');
const pendingClaimAfterAuth = ref(false);

const normalizedClaimCode = computed(() => props.claimCode.trim());
const currentPoints = computed(() => claimResult.value?.points?.balance ?? state.points?.balance ?? 0);
const canClaim = computed(() => pageState.value === 'ready' || pageState.value === 'auth_required');
const displayValue = computed(() => formatMoney(claimLink.value?.display_value_cents ?? 0));
const pointsAmount = computed(() => claimLink.value?.points_amount ?? 0);
const userStatusLabel = computed(() => (isRegisteredUser.value ? displayNickname.value || '已登录' : '未登录'));
const activityTitle = computed(() => claimLink.value?.title || '免费积分领用计划');
const isClaimActionState = computed(() => pageState.value === 'ready' || pageState.value === 'auth_required' || pageState.value === 'submitting');
const isProblemState = computed(() => pageState.value === 'invalid' || pageState.value === 'expired' || pageState.value === 'disabled' || pageState.value === 'not_started' || pageState.value === 'error');
const statusTitle = computed(() => {
  if (pageState.value === 'invalid') return '链接不存在';
  if (pageState.value === 'expired') return '链接已过期';
  if (pageState.value === 'disabled') return '链接已停用';
  if (pageState.value === 'not_started') return '链接尚未生效';
  if (pageState.value === 'already_claimed_this_week') return '本周已领取过免费积分';
  return '领取失败';
});
const statusDescription = computed(() => {
  if (pageState.value === 'already_claimed_this_week') return '每个账号每个自然周仅能成功领取一次，您可在下周一继续参与。';
  if (pageState.value === 'error') return actionError.value || '请稍后重试，或向客服咨询反馈。';
  return actionError.value || '请确认链接状态后再试，或向客服咨询反馈。';
});
const primaryButtonLabel = computed(() => {
  if (pageState.value === 'submitting') return '正在领取...';
  if (!isRegisteredUser.value) return '登录后领取积分';
  if (pageState.value === 'granted') return '积分已到账';
  if (pageState.value === 'already_claimed_this_week') return '本周已领取过免费积分';
  return '领取积分';
});

onMounted(async () => {
  await Promise.all([bootstrapApp(), loadClaimLink()]);
});

watch(isRegisteredUser, async (value, previousValue) => {
  if (value && !previousValue && !pendingClaimAfterAuth.value) {
    await loadClaimLink();
  }
});

watch(() => props.claimCode, async () => {
  claimResult.value = null;
  pendingClaimAfterAuth.value = false;
  await loadClaimLink();
});

async function loadClaimLink(): Promise<void> {
  if (!normalizedClaimCode.value) {
    pageState.value = 'invalid';
    return;
  }
  pageState.value = 'loading';
  actionError.value = '';
  try {
    claimLink.value = await getPublicPointsClaimLink(normalizedClaimCode.value, state.accessToken);
    applyLinkState();
  } catch (error) {
    claimLink.value = null;
    if (isNotFoundError(error)) {
      pageState.value = 'invalid';
    } else {
      actionError.value = humanizeError(error);
      pageState.value = 'error';
    }
  }
}

function applyLinkState(): void {
  const link = claimLink.value;
  if (!link) {
    pageState.value = 'invalid';
    return;
  }
  if (link.current_user_claim_status === 'already_claimed_this_week') {
    pageState.value = 'already_claimed_this_week';
    return;
  }
  if (link.effective_status === 'expired') {
    pageState.value = 'expired';
    return;
  }
  if (link.effective_status === 'disabled') {
    pageState.value = 'disabled';
    return;
  }
  if (link.effective_status === 'not_started') {
    pageState.value = 'not_started';
    return;
  }
  pageState.value = isRegisteredUser.value ? 'ready' : 'auth_required';
}

async function handlePrimaryAction(): Promise<void> {
  if (pageState.value === 'granted' || pageState.value === 'already_claimed_this_week') {
    return;
  }
  if (!canClaim.value) {
    await loadClaimLink();
    return;
  }
  if (!isRegisteredUser.value) {
    await openUnifiedAuth();
    return;
  }
  await submitClaim();
}

async function openUnifiedAuth(): Promise<void> {
  actionError.value = '';
  pendingClaimAfterAuth.value = true;
  const authenticated = await requestRegisteredUser('领取免费积分');
  if (!authenticated) {
    pendingClaimAfterAuth.value = false;
    return;
  }
  await loadClaimLink();
  if (pageState.value === 'ready') {
    await submitClaim();
    return;
  }
  pendingClaimAfterAuth.value = false;
}

async function submitClaim(): Promise<void> {
  if (!state.accessToken || pageState.value === 'submitting') {
    return;
  }
  pageState.value = 'submitting';
  actionError.value = '';
  pendingClaimAfterAuth.value = false;
  try {
    const result = await claimPublicPoints(state.accessToken, normalizedClaimCode.value);
    claimResult.value = result;
    if (result.claim_status === 'granted') {
      pageState.value = 'granted';
      await refreshPoints().catch(() => undefined);
      return;
    }
    if (result.claim_status === 'already_claimed_this_week') {
      pageState.value = 'already_claimed_this_week';
      await refreshPoints().catch(() => undefined);
      return;
    }
    pageState.value = 'error';
    actionError.value = result.message || '领取失败，请稍后重试。';
  } catch (error) {
    await loadClaimLink().catch(() => undefined);
    actionError.value = humanizeError(error);
    if (actionError.value === '本周已领取过免费积分') {
      pageState.value = 'already_claimed_this_week';
      return;
    }
    if (pageState.value === 'ready' || pageState.value === 'auth_required' || pageState.value === 'loading') {
      pageState.value = 'error';
    }
  }
}

function openCustomerService(): void {
  openCustomerServiceModal('points_insufficient', claimLink.value?.title || '免费积分领取');
}

function handleBackToHome(): void {
  emit('navigate-to-tab', 'home');
}

function isNotFoundError(error: unknown): boolean {
  return error instanceof Error && error.message === 'claim_link_not_found';
}

function formatMoney(cents: number): string {
  const amount = cents / 100;
  return Number.isInteger(amount) ? String(amount) : amount.toFixed(2);
}

function formatTime(value: string | null | undefined): string {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value.replace('T', ' ').replace('+00:00', '').replace('+08:00', '');
  }
  const pad = (part: number) => String(part).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
</script>

<template>
  <div class="min-h-screen bg-[#FBFBFA] pb-8 font-sans text-brand-ink antialiased select-none">
    <div class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-100 px-4 py-3 flex items-center justify-between">
      <button
        type="button"
        class="-ml-2 px-2 py-1.5 rounded-full text-brand-secondary hover:text-brand-ink-strong hover:bg-gray-50 active:scale-[0.98] transition-all cursor-pointer outline-none flex items-center gap-1"
        @click="handleBackToHome"
      >
        <ArrowLeft :size="17" />
        <span class="text-xs font-bold">返回首页</span>
      </button>
      <h1 class="text-sm font-bold text-brand-ink-strong">免费积分领取</h1>
      <div class="w-[68px]"></div>
    </div>

    <div class="max-w-sm mx-auto w-full px-4 py-6 space-y-5">
      <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-xs text-center animate-in">
        <div class="text-[10px] font-bold text-brand-primary/80 bg-brand-primary/10 px-2.5 py-0.5 rounded-full uppercase tracking-wider inline-flex">
          EaseWise · 福利活动
        </div>
        <h2 class="mt-2 font-serif text-lg font-black text-brand-ink-strong leading-snug truncate">
          {{ activityTitle }}
        </h2>

        <button
          type="button"
          class="mt-3 mx-auto max-w-full bg-[#F6F7F5] hover:bg-gray-50 border border-gray-100 rounded-full px-3 py-1.5 cursor-pointer transition-colors outline-none flex items-center gap-2"
          @click="!isRegisteredUser ? openUnifiedAuth() : undefined"
        >
          <span class="w-5 h-5 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center">
            <UserRound :size="11" />
          </span>
          <span class="min-w-0 text-xs font-semibold text-brand-ink truncate">
            当前身份：{{ userStatusLabel }}
          </span>
          <span v-if="!isRegisteredUser" class="pl-2 border-l border-gray-200 text-[10px] font-bold text-brand-primary">登录</span>
        </button>
      </section>

      <section v-if="pageState === 'loading'" class="bg-white rounded-[1.75rem] border border-gray-100 shadow-[0_18px_50px_rgba(15,23,42,0.08)] py-24 text-center space-y-4 animate-in">
        <div class="relative w-16 h-16 mx-auto rounded-full bg-brand-primary/5 text-brand-primary flex items-center justify-center">
          <div class="absolute inset-0 rounded-full border border-dashed border-brand-primary/25 animate-spin-slow"></div>
          <Loader2 class="w-8 h-8 animate-spin opacity-70" />
        </div>
        <div class="space-y-1">
          <p class="font-serif font-bold text-brand-ink-strong text-sm">正在读取领取链接...</p>
          <p class="text-[10px] text-brand-secondary">请稍候</p>
        </div>
      </section>

      <template v-else>
        <section class="relative bg-white rounded-[1.75rem] overflow-hidden border border-gray-100 shadow-[0_18px_50px_rgba(15,23,42,0.08)] animate-in">
          <div class="absolute top-[59%] -left-3 w-6 h-6 rounded-full bg-[#FBFBFA] border-r border-gray-100 z-10"></div>
          <div class="absolute top-[59%] -right-3 w-6 h-6 rounded-full bg-[#FBFBFA] border-l border-gray-100 z-10"></div>

          <div class="p-6 text-center flex flex-col items-center space-y-4">
            <div
              v-if="isClaimActionState"
              class="relative w-16 h-16 rounded-full bg-[#D4AF37]/10 text-[#D4AF37] flex items-center justify-center"
            >
              <div class="absolute inset-0 rounded-full border border-dashed border-[#D4AF37]/40 animate-spin-slow"></div>
              <Gift :size="28" class="animate-bounce-slow" />
            </div>
            <div
              v-else-if="pageState === 'granted'"
              class="w-16 h-16 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center"
            >
              <CheckCircle2 class="stroke-[3]" :size="30" />
            </div>
            <div
              v-else-if="pageState === 'already_claimed_this_week'"
              class="w-16 h-16 rounded-full bg-amber-50 border border-amber-100 text-amber-700 flex items-center justify-center"
            >
              <RefreshCw :size="26" />
            </div>
            <div
              v-else
              class="w-16 h-16 rounded-full bg-rose-50 border border-rose-100 text-rose-600 flex items-center justify-center"
            >
              <AlertCircle :size="28" />
            </div>

            <div v-if="claimLink && isClaimActionState" class="space-y-1">
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest">可领用积分额</p>
              <div class="flex items-baseline justify-center font-serif text-brand-ink-strong">
                <span class="text-4xl font-black text-brand-primary">{{ pointsAmount }}</span>
                <span class="ml-1 text-sm font-bold text-brand-secondary">分</span>
              </div>
            </div>

            <div v-else-if="pageState === 'granted'" class="space-y-2">
              <h2 class="font-serif font-bold text-emerald-700 text-base">积分已到账</h2>
              <p class="text-[11px] text-brand-secondary">当前可用积分余额</p>
              <div class="font-serif text-[36px] font-black text-brand-primary leading-none">{{ currentPoints }}</div>
            </div>

            <div v-else-if="pageState === 'already_claimed_this_week'" class="space-y-2">
              <h2 class="font-serif font-bold text-amber-800 text-base">本周已领取过免费积分</h2>
              <p class="text-[11px] text-brand-secondary leading-relaxed px-2">
                每个账号每个自然周仅能成功领取一次。
              </p>
            </div>

            <div v-else class="space-y-2">
              <h2 class="font-serif font-bold text-rose-700 text-base">{{ statusTitle }}</h2>
              <p class="text-[11px] text-brand-secondary leading-relaxed px-2">
                {{ statusDescription }}
              </p>
            </div>

            <div v-if="claimLink && isClaimActionState" class="grid grid-cols-2 gap-0 w-full bg-[#F7F7F4] p-3 rounded-2xl border border-gray-100">
              <div class="text-center border-r border-gray-100">
                <p class="text-[9px] font-bold text-gray-400">对应人民币价值</p>
                <p class="mt-0.5 text-sm font-serif font-black text-[#D4AF37]">￥{{ displayValue }}</p>
              </div>
              <div class="text-center">
                <p class="text-[9px] font-bold text-gray-400">当前领取状态</p>
                <p class="mt-1 inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 border border-emerald-100">可领取</p>
              </div>
            </div>
          </div>

          <div class="border-t border-dashed border-gray-100 mx-5"></div>

          <div class="p-5 bg-[#F7F7F4] rounded-b-[1.75rem]">
            <div v-if="pageState === 'auth_required' || pageState === 'ready'" class="space-y-4">
              <div class="flex items-center justify-center gap-1.5 text-[10.5px] text-brand-secondary">
                <Clock :size="12" class="text-gray-400 shrink-0" />
                <span>有效期至：{{ formatTime(claimLink?.expires_at) }}</span>
              </div>

              <button
                type="button"
                class="w-full py-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl text-xs font-bold cursor-pointer border-none shadow-md hover:shadow-lg transition-all active:scale-[0.98] outline-none flex items-center justify-center gap-1.5"
                @click="handlePrimaryAction"
              >
                <UserRound v-if="!isRegisteredUser" :size="14" />
                <Sparkles v-else :size="14" class="text-[#D4AF37] animate-pulse" />
                <span>{{ primaryButtonLabel }}</span>
              </button>

              <p class="text-[10px] text-center text-gray-400 leading-relaxed">
                登录成功后系统会自动继续发放领取。
              </p>

              <div
                v-if="actionError"
                class="bg-rose-50 border border-rose-100 rounded-xl p-3 flex items-start gap-2 text-left text-[10.5px] text-rose-800 leading-relaxed"
              >
                <AlertTriangle :size="14" class="shrink-0 mt-0.5" />
                <span>{{ actionError }}</span>
              </div>
            </div>

            <div v-else-if="pageState === 'submitting'" class="py-4 text-center flex flex-col items-center space-y-2">
              <Loader2 :size="24" class="text-brand-primary animate-spin" />
              <p class="text-xs font-bold text-brand-ink-strong">正在领取...</p>
              <p class="text-[10px] text-brand-secondary">账务安全处理中，请勿刷新页面</p>
            </div>

            <div v-else-if="pageState === 'granted'" class="py-3 text-center space-y-3">
              <p class="text-[11px] text-brand-secondary leading-relaxed">
                福利已安全记账。现在可以继续使用积分进行测算。
              </p>
              <button
                type="button"
                class="w-full py-2.5 px-4 bg-brand-primary/10 hover:bg-brand-primary/15 text-brand-primary rounded-xl text-[11px] font-bold border-none transition-colors cursor-pointer outline-none"
                @click="handleBackToHome"
              >
                立即去测算
              </button>
            </div>

            <div v-else-if="pageState === 'already_claimed_this_week'" class="py-3 text-center space-y-3">
              <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-amber-50 text-amber-600">
                <AlertCircle :size="18" />
              </div>
              <div class="space-y-1.5">
                <p class="text-xs font-bold text-amber-800">{{ statusTitle }}</p>
                <p class="text-[10px] text-brand-secondary leading-relaxed px-2">
                  {{ statusDescription }}
                </p>
              </div>
              <button
                type="button"
                class="w-full py-2.5 px-4 bg-brand-primary/10 hover:bg-brand-primary/15 text-brand-primary rounded-xl text-[11px] font-bold border-none transition-colors cursor-pointer outline-none flex items-center justify-center gap-1"
                @click="handleBackToHome"
              >
                <ArrowLeft :size="13" />
                <span>返回首页</span>
              </button>
            </div>

            <div v-else class="py-2 text-center space-y-3">
              <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-rose-50 text-rose-600">
                <AlertCircle :size="18" />
              </div>
              <div class="space-y-1.5">
                <p class="text-xs font-bold text-rose-700">{{ statusTitle }}</p>
                <p class="text-[10px] text-brand-secondary px-2 leading-relaxed">
                  {{ statusDescription }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          v-if="isProblemState"
          class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm space-y-3 text-left animate-in"
        >
          <div class="flex items-start gap-2.5">
            <div class="p-1.5 bg-brand-primary/10 rounded-lg text-brand-primary">
              <MessageSquare :size="14" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] font-bold text-brand-ink-strong">福利领取遇到问题？</p>
              <p class="text-[10px] text-brand-secondary leading-relaxed mt-0.5">
                客服可以协助核对链接状态和账号领取记录。
              </p>
            </div>
          </div>
          <button
            type="button"
            class="w-full py-2.5 bg-[#F5F3FF] hover:bg-[#EDE9FE] text-brand-primary text-[11px] font-bold rounded-xl border border-[#DDD6FE]/60 cursor-pointer select-none transition-all outline-none flex items-center justify-center gap-1.5"
            @click="openCustomerService"
          >
            联系客服
          </button>
        </section>
      </template>
    </div>

    <div class="py-5 text-center space-y-1 mt-auto bg-gray-50/50 border-t border-gray-100">
      <p class="text-[9.5px] text-gray-400 font-mono tracking-widest">EASEWISE · 易如反掌系统</p>
      <p class="text-[9px] text-gray-400">数字与传统学术指导 · 账务安全审计链</p>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation: enter 0.18s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-spin-slow {
  animation: spin-slow 20s linear infinite;
}

.animate-bounce-slow {
  animation: bounce-slow 2.4s ease-in-out infinite;
}

@keyframes enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes bounce-slow {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}
</style>
```

### `src/components/profile/AmbassadorDetail.vue`

```vue
<script setup lang="ts">
import {
  ArrowLeft,
  BadgeCheck,
  CheckCircle2,
  Coins,
  Gift,
  Share2,
  ShieldCheck,
  Sparkles,
  Users,
  WalletCards,
} from 'lucide-vue-next';

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const benefitCards = [
  {
    title: '专属推广身份',
    desc: '达成准入条件并审核通过后，可获得推广大使身份与专属推广入口。',
    icon: BadgeCheck,
  },
  {
    title: '邀请收益返佣',
    desc: '直邀用户完成符合规则的订单后，可按身份等级获得推广收益。',
    icon: Coins,
  },
  {
    title: '收益灵活处理',
    desc: '推广收益可按正式规则申请提现，并在推广资产页面查看结算状态。',
    icon: WalletCards,
  },
];

const thresholds = [
  { label: '推广大使', value: '累计充值 398 元', desc: '适合刚开始推广的用户' },
  { label: 'VIP 推广大使', value: '累计充值 3980 元', desc: '适合持续推广与深度合作用户' },
  { label: 'SVIP 推广大使', value: '以后台规则为准', desc: '适合重点合作与高价值推广用户' },
];

const rules = [
  '推广身份需要用户主动申请，并由后台审核通过后生效。',
  '推广收益只计算直邀用户，不存在团队层级收益。',
  '返佣比例、提现门槛和结算周期以后台正式配置为准。',
  '前台默认只展示服务积分，推广收益仅在推广大使相关页面展示。',
];
</script>

<template>
  <div class="min-h-dvh max-w-md mx-auto bg-brand-paper text-brand-ink-strong font-sans text-left relative overflow-x-hidden">
    <header class="fixed top-0 left-0 right-0 z-50 max-w-md mx-auto bg-brand-paper/90 backdrop-blur-md border-b border-gray-100">
      <div class="h-16 px-margin-mobile flex items-center justify-between">
        <button
          type="button"
          class="w-10 h-10 rounded-full bg-white border border-gray-100 shadow-sm flex items-center justify-center text-brand-ink-strong active:scale-95 transition-all outline-none cursor-pointer"
          aria-label="返回我的页面"
          @click="emit('back')"
        >
          <ArrowLeft :size="19" />
        </button>
        <h1 class="font-serif text-[19px] leading-none font-bold tracking-wide text-brand-ink-strong">
          推广大使
        </h1>
        <div class="w-10 h-10"></div>
      </div>
    </header>

    <main class="pt-16 pb-12">
      <section class="px-margin-mobile pt-4">
        <div class="relative overflow-hidden rounded-2xl bg-brand-ink-strong text-white p-5 shadow-md">
          <div class="absolute -right-8 -top-10 w-32 h-32 rounded-full border border-white/10"></div>
          <div class="absolute -right-3 bottom-4 text-white/5">
            <Share2 :size="108" />
          </div>

          <div class="relative z-10 space-y-4">
            <div class="inline-flex items-center gap-1.5 rounded-full bg-brand-accent/15 border border-brand-accent/30 px-3 py-1 text-brand-accent font-sans text-[11px] font-bold">
              <Sparkles :size="13" class="shrink-0" />
              <span>邀请同行 · 共修共赢</span>
            </div>

            <div class="space-y-2">
              <h2 class="font-serif text-[26px] leading-tight font-bold tracking-wide">
                成为易如反掌推广大使
              </h2>
              <p class="font-sans text-[13px] leading-relaxed text-white/75">
                邀请好友使用手机号评测、智能体与后续服务能力，符合正式规则的订单可获得推广收益。
              </p>
            </div>

            <div class="grid grid-cols-3 gap-2.5 pt-1">
              <div class="rounded-xl bg-white/8 border border-white/10 p-3 text-center">
                <p class="font-serif text-[18px] leading-none font-bold text-brand-accent">3档</p>
                <p class="mt-1 font-sans text-[10px] text-white/60">推广身份</p>
              </div>
              <div class="rounded-xl bg-white/8 border border-white/10 p-3 text-center">
                <p class="font-serif text-[18px] leading-none font-bold text-brand-accent">直邀</p>
                <p class="mt-1 font-sans text-[10px] text-white/60">收益来源</p>
              </div>
              <div class="rounded-xl bg-white/8 border border-white/10 p-3 text-center">
                <p class="font-serif text-[18px] leading-none font-bold text-brand-accent">审核</p>
                <p class="mt-1 font-sans text-[10px] text-white/60">开通方式</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center justify-between gap-3 mb-4">
            <div>
              <p class="font-serif text-[18px] leading-tight font-bold text-brand-ink-strong">推广权益</p>
              <p class="mt-1 font-sans text-[11px] text-brand-secondary">身份、收益与服务支持统一展示</p>
            </div>
            <div class="w-9 h-9 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center shrink-0">
              <Gift :size="17" />
            </div>
          </div>

          <div class="space-y-3">
            <div
              v-for="item in benefitCards"
              :key="item.title"
              class="rounded-xl bg-brand-paper/60 border border-gray-100 p-3.5 flex gap-3"
            >
              <div class="w-9 h-9 rounded-full bg-white text-brand-primary flex items-center justify-center shrink-0 shadow-sm">
                <component :is="item.icon" :size="17" />
              </div>
              <div class="min-w-0">
                <p class="font-sans text-[13px] leading-tight font-bold text-brand-ink-strong">{{ item.title }}</p>
                <p class="mt-1 font-sans text-[11px] leading-relaxed text-brand-secondary">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-9 h-9 rounded-full bg-brand-accent/40 text-brand-ink-strong flex items-center justify-center shrink-0">
              <Users :size="17" />
            </div>
            <div>
              <p class="font-serif text-[18px] leading-tight font-bold text-brand-ink-strong">准入门槛</p>
              <p class="mt-1 font-sans text-[11px] text-brand-secondary">门槛数值以后端正式规则配置为准</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="item in thresholds"
              :key="item.label"
              class="rounded-xl border border-brand-primary/10 bg-brand-primary/5 p-3"
            >
              <p class="font-sans text-[11px] font-bold text-brand-primary leading-tight">{{ item.label }}</p>
              <p class="mt-2 font-serif text-[18px] font-bold text-brand-ink-strong leading-tight">{{ item.value }}</p>
              <p class="mt-1 font-sans text-[10px] leading-relaxed text-brand-secondary">{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-9 h-9 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <ShieldCheck :size="17" />
            </div>
            <div>
              <p class="font-serif text-[18px] leading-tight font-bold text-brand-ink-strong">规则说明</p>
              <p class="mt-1 font-sans text-[11px] text-brand-secondary">推广收益与服务积分分开展示</p>
            </div>
          </div>

          <div class="space-y-3">
            <div
              v-for="rule in rules"
              :key="rule"
              class="flex items-start gap-2.5"
            >
              <CheckCircle2 :size="15" class="mt-0.5 text-brand-primary shrink-0" />
              <p class="font-sans text-[12px] leading-relaxed text-brand-ink">{{ rule }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="rounded-2xl bg-brand-primary text-white p-4 shadow-md flex items-center justify-between gap-4">
          <div>
            <p class="font-serif text-[17px] leading-tight font-bold">准备申请推广大使？</p>
            <p class="mt-1 font-sans text-[11px] leading-relaxed text-white/75">请通过客服或正式申请入口完成身份开通。</p>
          </div>
          <button
            type="button"
            class="px-4 py-2 rounded-xl bg-white text-brand-primary font-sans text-[12px] font-bold shrink-0 active:scale-95 transition-all cursor-pointer outline-none"
          >
            了解规则
          </button>
        </div>
      </section>
    </main>
  </div>
</template>
```

### `src/components/profile/Profile.vue`

```vue
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  Camera,
  ChevronRight,
  Receipt,
  History,
  MessageSquare,
  Share2,
  X,
  AlertTriangle,
  RefreshCw,
  LogOut,
  LogIn,
  PencilLine,
  KeyRound,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { resolveApiAssetUrl } from '../../lib/api';
import type { FourPillarsReviewSummary, PointsLedgerEntryResponse, ReviewSummary } from '../../types/api';
import SystemIntro from './SystemIntro.vue';

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
}>();

type CombinedReviewHistoryItem =
  | (ReviewSummary & { type: 'phone' })
  | (FourPillarsReviewSummary & { type: 'bazi' });

const {
  state,
  bootstrapApp,
  refreshPointsLedger,
  refreshReviewHistory,
  refreshFourPillarsHistory,
  refreshCurrentReview,
  refreshCurrentFourPillarsReview,
  logout,
  updateProfile,
  uploadAvatar,
  changePassword,
  displayNickname,
  displayAvatarText,
  isGuestUser,
  isRegisteredUser,
  requestRegisteredUser,
  openCustomerServiceModal,
  humanizeError,
} = useEaseWiseApp();

const activeModal = ref<string | null>(null);
const feedbackText = ref('');
const showSystemIntro = ref(false);
const openingReviewId = ref<string | null>(null);
const historyActionError = ref('');
const profileEditorVisible = ref(false);
const profileNicknameDraft = ref('');
const profileSaveError = ref('');
const profileSaving = ref(false);
const avatarInputRef = ref<HTMLInputElement | null>(null);
const avatarUploading = ref(false);
const avatarUploadError = ref('');
const avatarImageFailed = ref(false);
const passwordEditorVisible = ref(false);
const currentPasswordDraft = ref('');
const newPasswordDraft = ref('');
const confirmPasswordDraft = ref('');
const passwordSaveError = ref('');
const passwordSaveSuccess = ref('');
const passwordSaving = ref(false);
const logoutSaving = ref(false);
const logoutError = ref('');

const currentPoints = computed(() => state.points?.balance ?? 0);
const reportHistory = computed(() => state.reviewHistory);
const combinedHistory = computed<CombinedReviewHistoryItem[]>(() => {
  const phoneItems = state.reviewHistory.map((item) => ({
    ...item,
    type: 'phone' as const,
  }));
  const baziItems = state.fourPillarsHistory.map((item) => ({
    ...item,
    type: 'bazi' as const,
  }));
  return [...phoneItems, ...baziItems].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
});
const ledgerRecords = computed(() => state.pointsLedger);
const userReady = computed(() => Boolean(state.user));
const profileAvatarUrl = computed(() => resolveApiAssetUrl(state.user?.avatar_url));
const profileUserUidDisplay = computed(() => state.user?.uid || '未生成');
const primaryAccountActionLabel = computed(() => (isRegisteredUser.value ? '退出登录' : '登录 / 注册'));
const profileIdentityLabel = computed(() => {
  if (!isRegisteredUser.value) {
    return '游客';
  }
  const identityLevel = state.user?.identity_level || 'normal_user';
  const identityMap: Record<string, string> = {
    normal_user: '普通用户',
    promoter: '推广大使',
    promotion_ambassador: '推广大使',
    vip_promoter: 'VIP 推广大使',
    vip_promotion_ambassador: 'VIP 推广大使',
    senior_promoter: 'VIP 推广大使',
    senior_promotion_ambassador: 'VIP 推广大使',
    svip_promoter: 'SVIP 推广大使',
    svip_promotion_ambassador: 'SVIP 推广大使',
  };
  return identityMap[identityLevel] || '普通用户';
});
const profileIdentityClass = computed(() => {
  if (profileIdentityLabel.value.startsWith('SVIP')) {
    return 'bg-gradient-to-r from-violet-600 via-pink-600 to-amber-500 text-white font-black text-[11.5px] px-4 py-1.5 rounded-full shadow-[0_8px_24px_rgba(139,92,246,0.45)] tracking-widest border-2 border-amber-300/40 uppercase';
  }
  if (profileIdentityLabel.value.startsWith('VIP')) {
    return 'bg-gradient-to-r from-rose-500 via-orange-500 to-rose-600 text-white font-black text-[11px] px-3.5 py-1.5 rounded-full shadow-[0_6px_16px_rgba(244,63,94,0.35)] tracking-wider border border-white/20';
  }
  if (profileIdentityLabel.value === '推广大使') {
    return 'bg-gradient-to-r from-[#DFB26F] via-[#F6DFA2] to-[#B38C4F] text-[#422C0A] border border-[#F6DFA2]/40 font-black text-[10.5px] px-3.5 py-1.5 rounded-full shadow-[0_4px_12px_rgba(223,178,111,0.32)] tracking-wide';
  }
  if (profileIdentityLabel.value === '普通用户') {
    return 'bg-sky-50 text-sky-700 border border-sky-200/80 text-[10.5px] font-bold px-3 py-1 rounded-full shadow-[0_2px_6px_rgba(14,165,233,0.1)]';
  }
  return 'bg-neutral-100 text-neutral-600 border border-neutral-200/60 text-[10.5px] font-medium px-2.5 py-1 rounded-full';
});
const connectionHint = computed(() => {
  if (state.connectionError) {
    return `本地 API 暂未连通：${state.connectionError}`;
  }
  return '';
});
const profileFallbackTitle = computed(() => {
  if (state.booting) {
    return '正在同步账户状态';
  }
  if (state.connectionError) {
    return '数据连接暂时不可用';
  }
  return '游客状态无法使用评测类功能及智能体';
});
const profileFallbackActionLabel = computed(() => {
  if (state.booting) {
    return '同步中';
  }
  if (state.connectionError) {
    return '重新连接';
  }
  return '登录 / 注册';
});

onMounted(() => {
  void bootstrapApp();
});

watch(
  () => state.user?.avatar_url,
  () => {
    avatarImageFailed.value = false;
  },
);

watch(activeModal, async (value) => {
  if (value !== 'history') {
    openingReviewId.value = null;
    historyActionError.value = '';
  }
  if (value === 'ledger') {
    await refreshPointsLedger().catch(() => undefined);
  }
  if (value === 'history') {
    await Promise.allSettled([
      refreshReviewHistory(),
      refreshFourPillarsHistory(),
    ]);
  }
});

async function handleProfileFallbackAction(): Promise<void> {
  if (state.booting) {
    return;
  }
  if (state.connectionError) {
    await bootstrapApp();
    return;
  }
  await requestRegisteredUser('个人中心');
}

async function handleAccountAction(): Promise<void> {
  if (!isRegisteredUser.value) {
    await requestRegisteredUser('个人中心');
    return;
  }
  logoutError.value = '';
  activeModal.value = 'logout_confirm';
}

async function confirmLogout(): Promise<void> {
  if (logoutSaving.value) {
    return;
  }
  logoutSaving.value = true;
  logoutError.value = '';
  try {
    await logout();
    activeModal.value = null;
  } catch (error) {
    logoutError.value = humanizeError(error);
  } finally {
    logoutSaving.value = false;
  }
}

async function openAvatarUploader(): Promise<void> {
  const authenticated = await requestRegisteredUser('个人中心');
  if (!authenticated) {
    return;
  }
  avatarUploadError.value = '';
  avatarInputRef.value?.click();
}

async function handleAvatarFileChange(event: Event): Promise<void> {
  if (avatarUploading.value) {
    return;
  }
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = '';
  if (!file) {
    return;
  }
  if (!/^image\/(jpeg|png|webp)$/u.test(file.type)) {
    avatarUploadError.value = '请上传 JPG、PNG 或 WebP 格式的头像。';
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    avatarUploadError.value = '头像文件请控制在 5MB 以内。';
    return;
  }

  avatarUploading.value = true;
  avatarUploadError.value = '';
  try {
    const imageDataUrl = await buildAvatarDataUrl(file);
    await uploadAvatar(imageDataUrl);
  } catch (error) {
    avatarUploadError.value = humanizeError(error);
  } finally {
    avatarUploading.value = false;
  }
}

function handleAvatarImageError(): void {
  avatarImageFailed.value = true;
}

function buildAvatarDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('头像读取失败，请重新选择图片。'));
    reader.onload = () => {
      const image = new Image();
      image.onerror = () => reject(new Error('头像图片无法识别，请换一张图片。'));
      image.onload = () => {
        const size = 320;
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        if (!context) {
          reject(new Error('当前浏览器暂不支持头像压缩。'));
          return;
        }
        const scale = Math.max(size / image.width, size / image.height);
        const width = image.width * scale;
        const height = image.height * scale;
        context.drawImage(image, (size - width) / 2, (size - height) / 2, width, height);
        resolve(canvas.toDataURL('image/jpeg', 0.86));
      };
      image.src = String(reader.result || '');
    };
    reader.readAsDataURL(file);
  });
}

async function openProtectedModal(modal: 'ledger' | 'history'): Promise<void> {
  const authenticated = await requestRegisteredUser(modal === 'ledger' ? '积分记录' : '评测记录');
  if (authenticated) {
    activeModal.value = modal;
  }
}

async function openProfileEditor(): Promise<void> {
  const authenticated = await requestRegisteredUser('修改用户名');
  if (!authenticated) {
    return;
  }
  profileNicknameDraft.value = state.user?.nickname?.trim() || '';
  profileSaveError.value = '';
  profileEditorVisible.value = true;
}

async function submitProfileEditor(): Promise<void> {
  if (profileSaving.value) {
    return;
  }
  const nickname = profileNicknameDraft.value.trim();
  if (!nickname) {
    profileSaveError.value = '请输入用户名/昵称。';
    return;
  }
  profileSaving.value = true;
  profileSaveError.value = '';
  try {
    await updateProfile({ nickname });
    profileEditorVisible.value = false;
  } catch (error) {
    profileSaveError.value = humanizeError(error);
  } finally {
    profileSaving.value = false;
  }
}

function resetPasswordEditor(): void {
  currentPasswordDraft.value = '';
  newPasswordDraft.value = '';
  confirmPasswordDraft.value = '';
  passwordSaveError.value = '';
  passwordSaveSuccess.value = '';
  passwordSaving.value = false;
}

function closePasswordEditor(): void {
  passwordEditorVisible.value = false;
  resetPasswordEditor();
}

function validatePasswordStrength(value: string): boolean {
  if (value.trim() !== value) {
    return false;
  }
  if (value.length < 8 || value.length > 32) {
    return false;
  }
  if (new Set(value).size <= 1) {
    return false;
  }
  const categoryCount = [
    /\d/.test(value),
    /[a-zA-Z]/.test(value),
    /[^a-zA-Z0-9]/.test(value),
  ].filter(Boolean).length;
  return categoryCount >= 2;
}

async function openPasswordEditor(): Promise<void> {
  const authenticated = await requestRegisteredUser('修改密码');
  if (!authenticated) {
    return;
  }
  resetPasswordEditor();
  passwordEditorVisible.value = true;
}

async function submitPasswordEditor(): Promise<void> {
  if (passwordSaving.value) {
    return;
  }
  passwordSaveError.value = '';
  passwordSaveSuccess.value = '';

  if (!currentPasswordDraft.value.trim()) {
    passwordSaveError.value = '请输入当前密码。';
    return;
  }
  if (!validatePasswordStrength(newPasswordDraft.value)) {
    passwordSaveError.value = '新密码强度不足，请使用 8-32 位且至少包含两类字符。';
    return;
  }
  if (newPasswordDraft.value !== confirmPasswordDraft.value) {
    passwordSaveError.value = '两次输入的新密码不一致。';
    return;
  }
  if (newPasswordDraft.value === currentPasswordDraft.value) {
    passwordSaveError.value = '新密码不能与当前密码相同。';
    return;
  }

  passwordSaving.value = true;
  try {
    await changePassword(currentPasswordDraft.value, newPasswordDraft.value, confirmPasswordDraft.value);
    passwordSaveSuccess.value = '密码已更新成功，建议你立即妥善保存。';
    currentPasswordDraft.value = '';
    newPasswordDraft.value = '';
    confirmPasswordDraft.value = '';
  } catch (error) {
    passwordSaveError.value = humanizeError(error);
  } finally {
    passwordSaving.value = false;
  }
}

function handleFeedbackSubmit(): void {
  if (!feedbackText.value.trim()) {
    return;
  }
  window.alert('感谢你的反馈，我们已经记录，后续会结合产品排期继续完善。');
  feedbackText.value = '';
  activeModal.value = null;
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

const ledgerBizTypeTitleMap: Record<string, string> = {
  signup_bonus: '注册赠送积分',
  wechat_initial_grant: '注册初始积分发放',
  phone_review_base: '手机号评测扣减',
  phone_review_base_charge: '手机号评测扣减',
  phone_review_base_refund: '手机号评测失败返还',
  phone_review_aspect_unlock: '手机号评测维度解锁',
  phone_review_aspect_unlock_charge: '手机号评测维度解锁',
  recharge_order: '积分充值到账',
  manual_adjust: '后台积分调整',
};

const ledgerRemarkTitleMap: Record<string, string> = {
  'initial test points': '注册赠送积分',
  wechat_initial_grant: '注册初始积分发放',
  phone_review_base_charge: '手机号评测扣减',
  phone_review_base_refund: '手机号评测失败返还',
  phone_review_aspect_unlock_charge: '手机号评测维度解锁',
  manual_adjust: '后台积分调整',
};

function hasChineseText(value: string): boolean {
  return /[\u3400-\u9fff]/u.test(value);
}

function resolveLedgerRemarkTitle(remark: string): string | null {
  const normalizedRemark = remark.trim();
  if (!normalizedRemark) {
    return null;
  }

  const lowerCaseRemark = normalizedRemark.toLowerCase();
  if (ledgerRemarkTitleMap[lowerCaseRemark]) {
    return ledgerRemarkTitleMap[lowerCaseRemark];
  }

  if (lowerCaseRemark.startsWith('recharge_order:')) {
    return '积分充值到账';
  }

  if (lowerCaseRemark.startsWith('phone_review_aspect_unlock:')) {
    return '手机号评测维度解锁';
  }

  if (hasChineseText(normalizedRemark)) {
    return normalizedRemark;
  }

  return null;
}

function formatLedgerTitle(entry: PointsLedgerEntryResponse): string {
  if (entry.remark?.trim()) {
    const resolvedRemarkTitle = resolveLedgerRemarkTitle(entry.remark);
    if (resolvedRemarkTitle) {
      return resolvedRemarkTitle;
    }
  }

  return ledgerBizTypeTitleMap[entry.biz_type] || '积分记录更新';
}

function formatLedgerDelta(entry: PointsLedgerEntryResponse): string {
  return `${entry.delta > 0 ? '+' : ''}${entry.delta} 分`;
}

function resolveLedgerColor(entry: PointsLedgerEntryResponse): string {
  return entry.delta >= 0 ? 'text-green-500' : 'text-red-500';
}

function formatReviewStatus(review: CombinedReviewHistoryItem): string {
  if (review.status === 'completed') {
    return review.score !== null ? `评分: ${review.score} 分` : '评测已完成';
  }
  if (review.status === 'failed') {
    return '评测失败';
  }
  return review.progress_message || '评测处理中';
}

function resolveReviewActionText(review: CombinedReviewHistoryItem): string {
  if (openingReviewId.value === review.id) {
    return '打开中...';
  }
  if (review.status === 'completed') {
    return review.type === 'phone' ? '查看手机号评测详情' : '查看四柱命盘与专项分析';
  }
  if (review.status === 'failed') {
    return '查看失败原因';
  }
  return review.type === 'phone' ? '继续查看手机号评测进度' : '继续查看四柱推演进度';
}

async function handleOpenReview(review: CombinedReviewHistoryItem): Promise<void> {
  if (openingReviewId.value) {
    return;
  }

  historyActionError.value = '';
  openingReviewId.value = review.id;

  try {
    if (review.type === 'phone') {
      await refreshCurrentReview(review.id);
      activeModal.value = null;
      emit('navigate-to-tab', 'phone');
      return;
    }
    await refreshCurrentFourPillarsReview(review.id);
    activeModal.value = null;
    emit('navigate-to-tab', 'bazi');
  } catch (error) {
    historyActionError.value = humanizeError(error);
  } finally {
    openingReviewId.value = null;
  }
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile relative text-left">
    <section class="mb-5 mt-4">
      <div
        v-if="userReady"
        class="bg-white rounded-2xl p-5 border border-gray-100 flex items-center justify-between shadow-sm relative overflow-hidden"
      >
        <div class="absolute right-0 bottom-0 text-slate-100/40 font-serif text-[42px] select-none translate-y-3 translate-x-1">
          ☯
        </div>
        <div class="flex items-center gap-3.5 z-10 min-w-0 flex-1">
          <div class="relative group shrink-0">
            <div class="relative w-14 h-14 rounded-full overflow-hidden border-2 border-brand-primary/10 bg-brand-primary/5 flex items-center justify-center font-serif font-bold text-brand-primary text-[20px] shadow-inner select-none">
              <span>{{ displayAvatarText }}</span>
              <img
                v-if="profileAvatarUrl && !avatarImageFailed"
                :src="profileAvatarUrl"
                alt=""
                class="absolute inset-0 w-full h-full object-cover"
                @error="handleAvatarImageError"
              />
            </div>
            <input
              ref="avatarInputRef"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              class="hidden"
              @change="handleAvatarFileChange"
            />
            <button
              type="button"
              class="absolute -bottom-1 -right-1 bg-white border border-gray-100 hover:border-brand-primary/20 text-brand-secondary hover:text-brand-primary w-5 h-5 rounded-full flex items-center justify-center shadow-sm select-none cursor-pointer outline-none"
              title="上传头像"
              aria-label="上传头像"
              @click="openAvatarUploader"
            >
              <RefreshCw v-if="avatarUploading" :size="10" class="animate-spin" />
              <Camera v-else :size="10" />
            </button>
          </div>

          <div class="text-left min-w-0">
            <div class="flex items-center gap-1.5 flex-wrap">
              <h3 class="font-serif text-[17px] font-black text-brand-ink-strong truncate max-w-[11rem]">{{ displayNickname }}</h3>
              <button
                type="button"
                class="text-gray-400 hover:text-brand-primary cursor-pointer select-none outline-none inline-flex items-center"
                @click="openProfileEditor"
              >
                <PencilLine :size="12" />
              </button>
            </div>

            <p class="mt-1 text-[10.5px] text-brand-secondary/85 font-mono flex items-center gap-1 select-none min-w-0">
              <span class="bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded scale-90 origin-left truncate max-w-[13rem]">
                UID: {{ profileUserUidDisplay }}
              </span>
            </p>
            <p v-if="avatarUploadError" class="mt-1.5 text-[10px] text-red-500 leading-relaxed">
              {{ avatarUploadError }}
            </p>
          </div>
        </div>
        <span
          class="inline-flex items-center gap-1.5 select-none transition-all shrink-0 ml-3"
          :class="profileIdentityClass"
        >
          {{ profileIdentityLabel }}
        </span>
      </div>

      <div
        v-else
        class="bg-white rounded-2xl p-5 border border-gray-100 flex items-center justify-between shadow-sm relative overflow-hidden"
      >
        <div class="absolute right-0 bottom-0 text-slate-100/40 font-serif text-[42px] select-none translate-y-3 translate-x-1">
          ☯
        </div>
        <div class="flex items-center gap-3.5 z-10 min-w-0">
          <div class="w-14 h-14 rounded-full border border-gray-100 bg-gray-50 flex items-center justify-center text-gray-400 shrink-0 shadow-inner select-none">
            <AlertTriangle :size="20" />
          </div>
          <div class="text-left min-w-0">
            <h3 class="text-[16px] font-serif font-black text-brand-ink-strong">游客用户</h3>
            <p class="text-[10.5px] text-brand-secondary/80 mt-1 leading-relaxed">
              {{ profileFallbackTitle }}
            </p>
            <p v-if="connectionHint" class="text-[10px] text-brand-secondary/70 mt-1 leading-relaxed">
              {{ connectionHint }}
            </p>
          </div>
        </div>
        <button
          @click="handleProfileFallbackAction"
          class="z-10 inline-flex items-center gap-1 px-3.5 py-1.5 text-[10.5px] font-bold rounded-full select-none bg-neutral-100 hover:bg-neutral-200 text-neutral-600 border border-neutral-300/60 shadow-xs cursor-pointer transition-all active:scale-95"
          :disabled="state.booting"
        >
          <RefreshCw v-if="state.booting || state.connectionError" :size="13" :class="state.booting ? 'animate-spin' : ''" />
          <LogIn v-else :size="12" />
          <span>{{ profileFallbackActionLabel }}</span>
        </button>
      </div>
    </section>

    <section class="mb-5">
      <div class="bg-[#151210] border border-stone-800 text-white rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden shadow-lg">
        <div class="absolute right-[-10%] bottom-[-15%] opacity-[0.03] text-brand-accent font-serif font-black text-[120px] pointer-events-none select-none">
          ☯
        </div>

        <div class="relative z-10 flex items-center justify-between gap-5">
          <div class="min-w-0">
            <div>
              <p class="text-[10px] font-semibold text-stone-400 gap-1 uppercase tracking-widest mb-1 select-none">我的积分结存</p>
              <div class="flex items-baseline gap-1">
                <span class="font-serif text-[32px] font-black text-[#E8C895] leading-none">{{ currentPoints }}</span>
                <span class="text-[9.5px] text-stone-400 font-mono scale-90">Points</span>
              </div>
            </div>
          </div>

          <button
            @click="emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })"
            class="h-10 bg-[#DEC299] hover:bg-[#EBD3B1] text-brand-ink-strong px-5 rounded-xl text-[12px] font-black active:scale-95 transition-all shrink-0 cursor-pointer outline-none shadow-sm border border-stone-600/30 inline-flex items-center justify-center"
          >
            去充值
          </button>
        </div>
      </div>
    </section>

    <section class="mb-5">
      <div
        @click="showSystemIntro = true"
        class="bg-gradient-to-r from-brand-primary/5 to-purple-500/5 rounded-2xl p-4 border border-brand-primary/10 flex items-center justify-between cursor-pointer hover:brightness-98 transition-all"
      >
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary shrink-0">
            <Share2 :size="16" />
          </div>
          <div class="text-left">
            <p class="font-sans text-[13px] font-bold text-brand-ink-strong">升级为「易如反掌」推广大使</p>
            <p class="font-sans text-[11px] text-brand-secondary mt-0.5">邀请朋友一起体验优秀传统文化，赚取高额佣金</p>
          </div>
        </div>
        <button
          @click.stop="showSystemIntro = true"
          class="font-sans text-[11px] font-bold text-brand-primary bg-white hover:bg-brand-primary/5 px-3 py-1.5 rounded-full border border-brand-primary/20 shrink-0 cursor-pointer transition-all outline-none"
        >
          详情
        </button>
      </div>
    </section>

    <section class="mb-8">
      <div class="bg-white rounded-2xl overflow-hidden hairline-border divide-y divide-gray-100 shadow-sm">
        <div
          @click="showSystemIntro = true"
          class="flex items-center justify-between p-4 bg-brand-primary/[0.02] hover:bg-brand-primary/[0.05] transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <Share2 :size="18" class="text-brand-primary" />
            <span class="font-sans text-[14px] font-black text-brand-primary-strong">合伙与推广说明书</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-[9.5px] text-brand-primary bg-brand-primary/10 px-2 py-0.5 rounded-full font-extrabold font-sans">福利与返佣体系</span>
            <ChevronRight :size="16" class="text-brand-primary" />
          </div>
        </div>

        <div
          @click="openProtectedModal('ledger')"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <Receipt :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">积分记录</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span v-if="ledgerRecords.length > 0" class="font-sans text-[10px] text-brand-primary font-bold bg-brand-primary/10 px-1.5 py-0.5 rounded-full">
              {{ ledgerRecords.length }}
            </span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="openProtectedModal('history')"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <History :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">评测记录</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span v-if="combinedHistory.length > 0" class="font-sans text-[10px] text-brand-primary font-bold bg-brand-primary/10 px-1.5 py-0.5 rounded-full">
              {{ combinedHistory.length }}
            </span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="openPasswordEditor"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <KeyRound :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">修改密码</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="font-sans text-[9px] text-gray-400 font-bold bg-gray-100 px-1.5 py-0.5 rounded-md">密保安全</span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="activeModal = 'feedback'"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <MessageSquare :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">反馈问题</span>
          </div>
          <ChevronRight :size="16" class="text-gray-300" />
        </div>
      </div>
    </section>

    <div class="text-center px-1">
      <button
        @click="handleAccountAction"
        class="w-full py-3.5 rounded-xl bg-brand-primary text-white font-sans text-[13px] font-bold hover:bg-brand-primary-strong transition-colors active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer outline-none shadow-md"
      >
        <LogOut v-if="!isGuestUser" :size="16" />
        <LogIn v-else :size="16" />
        <span>{{ primaryAccountActionLabel }}</span>
      </button>
    </div>

    <transition name="fade">
      <div v-if="activeModal === 'logout_confirm'" class="fixed inset-0 bg-slate-900/40 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white border border-brand-primary/15 rounded-2xl p-5 w-full max-w-xs space-y-4 shadow-2xl relative text-left">
          <div class="space-y-2 text-center pb-1">
            <div class="w-11 h-11 rounded-full bg-rose-50/50 border border-rose-100 text-rose-500 flex items-center justify-center mx-auto text-center select-none scale-105">
              <AlertTriangle :size="20" />
            </div>
            <h3 class="text-sm font-serif font-black text-brand-ink-strong tracking-wide">正在登出账号</h3>
            <p class="text-[11px] text-brand-secondary leading-relaxed px-1">
              您确定要退出当前账号吗？
            </p>
            <p class="text-[11px] text-brand-secondary leading-relaxed px-1">
              评测和智能体功能必须要登录才能使用
            </p>
            <p
              v-if="logoutError"
              class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed text-left"
            >
              {{ logoutError }}
            </p>
          </div>

          <div class="flex gap-2.5 pt-1">
            <button
              type="button"
              @click="activeModal = null"
              class="flex-1 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs font-bold rounded-lg outline-none cursor-pointer"
              :disabled="logoutSaving"
            >
              取消登出
            </button>
            <button
              type="button"
              @click="confirmLogout"
              class="flex-1 py-1.5 bg-rose-500 hover:bg-rose-600 text-white hover:brightness-110 text-xs font-bold rounded-lg outline-none cursor-pointer shadow-sm border border-transparent disabled:opacity-60"
              :disabled="logoutSaving"
            >
              {{ logoutSaving ? '正在登出...' : '确认登出' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <footer class="mt-14 text-center pb-8 shrink-0">
      <p class="font-sans text-[11px] font-bold text-brand-secondary/50 tracking-widest">
        易如反掌 · 服务积分与推广规则以后端配置为准
      </p>
      <p class="font-sans text-[10px] text-gray-400 mt-2">
        易如反掌 / EaseWise
      </p>
    </footer>

    <transition name="fade">
      <div v-if="activeModal === 'ledger'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 text-left w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">积分记录</h3>
              <p class="font-sans text-[11px] text-brand-secondary">当前展示最近的积分获取与扣减记录</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer shrink-0">
              <X :size="18" />
            </button>
          </div>

          <div class="max-h-[300px] overflow-y-auto no-scrollbar space-y-3.5 pr-1 py-1">
            <div v-if="ledgerRecords.length > 0" class="space-y-3.5">
              <div v-for="entry in ledgerRecords" :key="entry.ledger_id" class="flex justify-between items-start text-xs border-b border-gray-50 pb-2.5">
                <div class="text-left">
                  <p class="font-sans text-[13px] font-bold text-brand-ink">{{ formatLedgerTitle(entry) }}</p>
                  <p class="font-sans text-[10px] text-brand-secondary mt-0.5">{{ formatDateTime(entry.created_at) }}</p>
                </div>
                <div class="text-right">
                  <span class="font-mono text-[13px] font-bold" :class="resolveLedgerColor(entry)">{{ formatLedgerDelta(entry) }}</span>
                  <p class="font-sans text-[10px] text-brand-secondary mt-0.5">余额 {{ entry.balance_after }} 分</p>
                </div>
              </div>
            </div>
            <div v-else class="py-8 text-center space-y-2">
              <p class="font-sans text-[13px] text-brand-secondary">暂无积分变动记录。</p>
              <p class="font-sans text-[10px] text-brand-secondary/60">完成手机号评测或后台发放积分后，会在这里显示。</p>
            </div>
          </div>

          <button @click="activeModal = null" class="w-full py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg shrink-0 outline-none cursor-pointer">
            确定返回
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'history'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">我的评测记录</h3>
              <p class="font-sans text-[11px] text-brand-secondary">数字奇门与四柱八字记录统一展示</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="max-h-[300px] overflow-y-auto no-scrollbar space-y-3 py-1">
            <p
              v-if="historyActionError"
              class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed"
            >
              {{ historyActionError }}
            </p>
            <div v-if="combinedHistory.length > 0" class="space-y-3">
              <button
                v-for="review in combinedHistory"
                :key="`${review.type}:${review.id}`"
                type="button"
                class="w-full bg-brand-paper/50 p-3 rounded-xl border border-gray-100 flex items-start justify-between gap-3 text-xs text-left transition-all hover:bg-white hover:border-brand-primary/20 disabled:opacity-60 disabled:cursor-not-allowed"
                :disabled="!!openingReviewId"
                @click="handleOpenReview(review)"
              >
                <div class="min-w-0 flex-1 space-y-1">
                  <div class="flex items-center gap-1.5 flex-wrap">
                    <span
                      class="font-sans text-[10px] font-black px-2 py-0.5 rounded-full border"
                      :class="review.type === 'phone'
                        ? 'bg-sky-50 text-sky-700 border-sky-100'
                        : 'bg-amber-50 text-amber-800 border-amber-100'"
                    >
                      {{ review.type === 'phone' ? '数字奇门' : '四柱八字' }}
                    </span>
                    <span class="font-sans text-[10px] text-brand-secondary">{{ formatDateTime(review.created_at) }}</span>
                  </div>
                  <p v-if="review.type === 'phone'" class="font-sans text-[13px] font-bold text-brand-ink-strong">
                    <span class="text-brand-secondary/70 text-[11px] font-medium">评测号码：</span>
                    <span class="font-black tracking-wide text-brand-primary-strong">{{ review.masked_phone || review.phone_number }}</span>
                    <span class="ml-1.5 text-[10px] font-medium text-brand-secondary bg-sky-50/70 border border-sky-100/60 px-1.5 py-0.5 rounded">
                      {{ review.gender === 'male' ? '男命' : '女命' }}
                    </span>
                  </p>
                  <div v-else class="space-y-1">
                    <p class="font-serif text-[13px] font-bold text-brand-ink-strong">
                      <span class="font-sans text-brand-secondary/70 text-[11px] font-medium">评测命造：</span>
                      <span class="text-amber-900">{{ review.name?.trim() || '生辰盘主' }}</span>
                      <span class="ml-1.5 font-sans text-[10px] font-medium text-brand-secondary bg-amber-50/70 border border-amber-100/60 px-1.5 py-0.5 rounded">
                        {{ review.gender === 'male' ? '乾造·男' : '坤造·女' }}
                      </span>
                    </p>
                    <p class="font-sans text-[10.5px] text-brand-secondary leading-snug">
                      生辰：
                      <span class="font-mono bg-zinc-50 border border-gray-150 px-1 py-0.5 rounded text-zinc-700 text-[10px]">
                        {{ review.birth_date }} {{ review.birth_time }}
                      </span>
                    </p>
                  </div>
                  <p class="font-sans text-[10px] text-brand-secondary/80 mt-1">
                    {{ resolveReviewActionText(review) }}
                  </p>
                </div>
                <div class="shrink-0 flex flex-col items-end gap-1.5">
                  <span class="font-sans text-[13px] font-bold text-brand-primary bg-brand-primary/10 px-2.5 py-1 rounded-full shrink-0">
                    {{ formatReviewStatus(review) }}
                  </span>
                  <ChevronRight :size="14" class="text-brand-secondary/60" />
                </div>
              </button>
            </div>
            <div v-else class="py-8 text-center space-y-2">
              <p class="font-sans text-[13px] text-brand-secondary">暂无评测历史记录。</p>
              <p class="font-sans text-[10px] text-brand-secondary/60">你可以先完成一次手机号评测，或到四柱八字起盘排盘。</p>
            </div>
          </div>

          <button @click="activeModal = null" class="w-full py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
            确定返回
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'feedback'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">反馈问题</h3>
              <p class="font-sans text-[11px] text-brand-secondary">提交你遇到的问题、建议或合作需求</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">反馈详情</label>
            <textarea
              v-model="feedbackText"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3.5 h-28 rounded-xl border border-gray-100 focus:border-brand-primary outline-none resize-none transition-all"
              placeholder="请输入你遇到的问题、改进建议或合作需求..."
            />
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="activeModal = null" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="handleFeedbackSubmit"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[13px] font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="!feedbackText.trim()"
            >
              提交反馈
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="profileEditorVisible" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[110] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">修改用户名</h3>
              <p class="font-sans text-[11px] text-brand-secondary">当前名称将同步到个人中心与后台可见昵称</p>
            </div>
            <button @click="profileEditorVisible = false" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">用户名 / 昵称</label>
            <input
              v-model="profileNicknameDraft"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="请输入用户名或昵称"
              maxlength="64"
            />
            <p v-if="profileSaveError" class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed">
              {{ profileSaveError }}
            </p>
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="profileEditorVisible = false" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="submitProfileEditor"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[13px] font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="profileSaving"
            >
              {{ profileSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="passwordEditorVisible" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[120] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">修改登录密码</h3>
              <p class="font-sans text-[11px] text-brand-secondary">请输入当前密码，并设置一个新的登录密码</p>
            </div>
            <button @click="closePasswordEditor" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">当前密码</label>
            <input
              v-model="currentPasswordDraft"
              type="password"
              autocomplete="current-password"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="请输入当前登录密码"
            />

            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">新密码</label>
            <input
              v-model="newPasswordDraft"
              type="password"
              autocomplete="new-password"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="8-32位，至少包含两类字符"
            />

            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">确认新密码</label>
            <input
              v-model="confirmPasswordDraft"
              type="password"
              autocomplete="new-password"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="请再次输入新密码"
            />

            <div class="rounded-xl border border-amber-100 bg-amber-50 px-3 py-2 font-sans text-[11px] text-amber-700 leading-relaxed">
              <p>如果忘记当前密码，当前版本暂未接入短信验证自助找回。请先联系客服人工核验，或等待验证能力接入后再重置。</p>
              <button
                type="button"
                class="mt-2 inline-flex items-center gap-1 rounded-lg bg-white px-2.5 py-1.5 text-[10.5px] font-bold text-amber-800 shadow-sm outline-none"
                @click="openCustomerServiceModal('account_security')"
              >
                <MessageSquare :size="11" />
                <span>联系客服</span>
              </button>
            </div>

            <p v-if="passwordSaveError" class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed">
              {{ passwordSaveError }}
            </p>
            <p v-if="passwordSaveSuccess" class="rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-2 font-sans text-[11px] text-emerald-700 leading-relaxed">
              {{ passwordSaveSuccess }}
            </p>
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="closePasswordEditor" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="submitPasswordEditor"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[13px] font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="passwordSaving"
            >
              {{ passwordSaving ? '保存中...' : '保存密码' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="slide">
      <SystemIntro v-if="showSystemIntro" @close="showSystemIntro = false" />
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

.slide-enter-active, .slide-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateY(100%);
  opacity: 0.95;
}
</style>
```

### `src/components/profile/SystemIntro.vue`

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  ArrowLeft, Coins, Award, Users, Share2, Check, Sparkles,
  TrendingUp, Users2, ShieldCheck, Landmark, CheckCircle2,
  Gift, Calculator, HelpCircle
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

// Emits to communicate with parent
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const copied = ref(false);
const showApplyPlaceholder = ref(false);
const { openCustomerServiceModal } = useEaseWiseApp();

// Interactive Calculator states
// We divide the calculator into two versions: "partner" and "ambassador"
const calcVersion = ref<'partner' | 'ambassador'>('partner');

// Sub-tier selection for the "Ambassador" version
const selectedAmbassadorTier = ref<'normal' | 'vip' | 'svip'>('normal');

// Input values for calculation (Annual estimates)
const directUsersCount = ref(50);                      // 直属推荐人脉数
const avgAnnualDirectSpend = ref(300);                  // 平均直属推荐年消费额

const normalAmbassadorPerformance = ref(30000);         // 旗下推广大使推广充值金额
const vipAmbassadorPerformance = ref(20000);            // 旗下 VIP 推广大使推广充值金额
const svipAmbassadorPerformance = ref(10000);           // 旗下 SVIP 推广大使推广充值金额

// Rates mapping for ambassador tiers
const tierRates = {
  normal: 0.10, // 普通
  vip: 0.25,    // VIP
  svip: 0.40    // SVIP
};

const asNumber = (value: number | string) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

// Computed Earnings (Annual basis: "年收益")
const directAnnualPerformance = computed(() => {
  return asNumber(directUsersCount.value) * asNumber(avgAnnualDirectSpend.value);
});

const ambassadorAnnualEarn = computed(() => {
  const rate = tierRates[selectedAmbassadorTier.value];
  return Math.round(directAnnualPerformance.value * rate);
});

const partnerDirectAnnualEarn = computed(() => {
  return Math.round(directAnnualPerformance.value * 0.15);
});

const partnerTeamManagementAnnualEarn = computed(() => {
  return Math.round(teamPerformanceTotal.value * 0.15);
});

const teamPerformanceTotal = computed(() => {
  return (
    asNumber(normalAmbassadorPerformance.value) +
    asNumber(vipAmbassadorPerformance.value) +
    asNumber(svipAmbassadorPerformance.value) +
    directAnnualPerformance.value
  );
});

const teamBonusTotal = computed(() => {
  return Math.round(
    asNumber(normalAmbassadorPerformance.value) * 0.15 +
    asNumber(vipAmbassadorPerformance.value) * 0.10 +
    asNumber(svipAmbassadorPerformance.value) * 0.05 +
    directAnnualPerformance.value * 0.05
  );
});

const partnerPersonalTeamBonus = computed(() => {
  if (!teamPerformanceTotal.value) {
    return 0;
  }

  return Math.round((directAnnualPerformance.value / teamPerformanceTotal.value) * teamBonusTotal.value);
});

const partnerTotalAnnualEarn = computed(() => {
  return partnerDirectAnnualEarn.value + partnerTeamManagementAnnualEarn.value + partnerPersonalTeamBonus.value;
});

// Format currency
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY', maximumFractionDigits: 0 }).format(val);
};

// Simple sharing summary designed to copy directly for H5 forwards
const H5SummaryLink = computed(() => {
  return `【易如反掌·起盘评测】合伙与推广说明书。推广大使直属提成10%/25%/40%，推广订单完成后7天自动结算至推广余额；创始合伙人统一招商签约，收益测算按直属15% + 团队15% + 团队奖金，合伙人推荐服务返点55%。\n官方咨询微信号: yirufanzhang888。详见个人中心推广合伙说明。`;
});

const copyManualText = () => {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(H5SummaryLink.value);
    copied.value = true;
    setTimeout(() => copied.value = false, 2000);
  } else {
    // Fallback if inside restricted webview
    const input = document.createElement('textarea');
    input.value = H5SummaryLink.value;
    document.body.appendChild(input);
    input.select();
    try {
      document.execCommand('copy');
      copied.value = true;
      setTimeout(() => copied.value = false, 2000);
    } catch (err) {
      console.error('Fallback copy failed', err);
    }
    document.body.removeChild(input);
  }
};

const handleContactSupport = () => {
  openCustomerServiceModal('promotion_consulting');
};

const handleApplyJoin = () => {
  showApplyPlaceholder.value = true;
};
</script>

<template>
  <div class="fixed inset-0 z-[120] bg-brand-paper w-full h-full flex flex-col overflow-hidden font-sans text-left">
    <!-- H5 Dynamic Header -->
    <header class="bg-white border-b border-gray-100 flex items-center justify-between px-4 py-3.5 sticky top-0 z-10 shadow-xs shrink-0">
      <button
        @click="emit('close')"
        class="flex items-center gap-1 text-brand-secondary hover:text-brand-ink-strong transition-colors cursor-pointer outline-none text-[14px]"
      >
        <ArrowLeft :size="18" />
        <span class="font-semibold">返回</span>
      </button>
      <div class="text-center absolute left-1/2 -translate-x-1/2">
        <h1 class="font-serif font-black text-[15px] text-brand-ink-strong tracking-wide">
          合伙与推广说明书
        </h1>
      </div>
      <button
        @click="copyManualText"
        class="p-2 text-brand-primary bg-indigo-50/50 hover:bg-brand-primary/5 rounded-full transition-colors cursor-pointer outline-none relative"
        title="分享大纲"
      >
        <Check v-if="copied" :size="18" class="text-green-600" />
        <Share2 v-else :size="18" />
      </button>
    </header>

    <!-- Scrollable Main Flow Page (One direct downward H5 scrollable page) -->
    <div class="flex-1 overflow-y-auto no-scrollbar pb-24 bg-gray-50/30">

      <!-- 1. H5 Master Hero Banner -->
      <section class="relative bg-brand-ink-strong text-white py-10 px-5 overflow-hidden text-center">
        <!-- Ambient grids and lights -->
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.18),transparent_70%)] pointer-events-none"></div>
        <div class="absolute inset-0 bg-[linear-gradient(to_bottom,transparent,rgba(15,17,23,0.3))] pointer-events-none"></div>
        <div class="absolute -right-12 -top-12 w-32 h-32 bg-amber-500/5 rounded-full blur-2xl pointer-events-none"></div>

        <div class="relative z-10 space-y-2.5 max-w-sm mx-auto">
          <div class="inline-flex items-center gap-1 px-3 py-0.5 bg-brand-primary/20 border border-brand-primary/45 rounded-full text-brand-accent text-[10px] font-black tracking-widest uppercase">
            👑 易如反掌 · 创富生态联盟
          </div>
          <h2 class="text-[25px] font-serif font-black tracking-wide text-amber-100">
            商业定价与合伙提成全案
          </h2>
        </div>
      </section>

      <!-- Sequential Page Container (H5 Flow) -->
      <div class="p-4 max-w-md mx-auto space-y-6">

        <!-- SECTION A: 积分核心定价(Basic Pricing) -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">一、核心计价标准</h3>
          </div>

          <!-- Base Rule intro -->
          <div class="bg-white rounded-2xl p-4 border border-gray-150/60 shadow-xs space-y-2.5">
            <p class="text-[12.5px] text-brand-secondary leading-relaxed font-sans">
              本产品的核心记号代币为<strong>平台积分</strong>。
            </p>

            <div class="grid grid-cols-2 gap-2.5 pt-1">
              <div class="bg-brand-paper p-3 rounded-xl border border-gray-100 text-left">
                <span class="text-[9px] font-bold text-brand-secondary uppercase block">常规原价</span>
                <span class="text-[13.5px] font-black text-brand-ink-strong block mt-0.5">1 元 = 50 积分</span>
                <span class="text-[8.5px] text-brand-secondary/80 block mt-0.5">普通小额充值</span>
              </div>
              <div class="bg-indigo-50/40 p-3 rounded-xl border border-brand-primary/10 text-left">
                <span class="text-[9px] font-bold text-brand-primary uppercase block">常规大额优惠</span>
                <span class="text-[13.5px] font-black text-brand-primary block mt-0.5">1 元 = 100 积分</span>
                <span class="text-[8.5px] text-brand-secondary block mt-0.5">高额大礼包回馈</span>
              </div>
            </div>

            <p class="text-[10.5px] text-slate-400 leading-tight pt-0.5">
              平均每一次功能使用成本约为 1~2 元，客户体验流畅，高性价比，极易复购。
            </p>
          </div>
        </div>

        <!-- SECTION B: 用户身份结构说明 (4 tiers simplified) -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">二、线上系统四维身份界定</h3>
          </div>

          <p class="text-[12px] text-brand-secondary leading-relaxed font-sans">
            线上各级身份对应不同分佣与结算规则，推荐客户永久锚定，无须二次引流：
          </p>

          <div class="border border-gray-150 rounded-2xl bg-white overflow-hidden shadow-xs">
            <table class="w-full table-fixed text-center border-collapse">
              <thead>
                <tr class="bg-gray-50/80 text-[9.5px] font-bold text-brand-secondary border-b border-gray-150">
                  <th class="py-2 px-1 w-1/3">身份层级</th>
                  <th class="py-2 px-1 w-1/3">销售推广分佣比例</th>
                  <th class="py-2 px-1 w-1/3">结算说明</th>
                </tr>
              </thead>
              <tbody class="text-[11px]">
                <tr class="border-b border-gray-100">
                  <td class="py-2.5 px-1 font-extrabold text-brand-ink">普通用户</td>
                  <td class="py-2.5 px-1 text-brand-secondary font-black">—</td>
                  <td class="py-2.5 px-2 text-brand-secondary font-black">—</td>
                </tr>
                <tr class="border-b border-gray-100 bg-gray-50/20">
                  <td class="py-2.5 px-1 font-bold text-amber-800">推广大使</td>
                  <td class="py-2.5 px-1 text-emerald-600 font-extrabold text-[12px]">10% 直属提成</td>
                  <td rowspan="3" class="py-2 px-2 text-left align-middle text-[10px] text-brand-secondary leading-snug border-l border-gray-100">
                    推广提成以 7 天为标准。订单完成后 7 天自动结算至推广余额，达最低提现金额后可随时提现。
                  </td>
                </tr>
                <tr class="border-b border-gray-100">
                  <td class="py-2.5 px-1 font-extrabold text-amber-600">VIP 推广大使</td>
                  <td class="py-2.5 px-1 text-emerald-600 font-black text-[12px]">25% 直属提成</td>
                </tr>
                <tr class="bg-purple-500/[0.04]">
                  <td class="py-2.5 px-1 font-black text-purple-700">SVIP 推广大使</td>
                  <td class="py-2.5 px-1 text-red-600 font-black text-[12px]">40% 直属提成</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- SECTION C: 开通机制 -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">三、开通机制</h3>
          </div>

          <div class="bg-white rounded-2xl p-4.5 border border-gray-150/60 shadow-xs space-y-3">
            <div class="flex items-center gap-1.5 text-brand-primary">
              <Award :size="16" />
              <h4 class="text-[13px] font-bold">1. 开通审核</h4>
            </div>

            <p class="text-[11.5px] text-brand-secondary leading-relaxed">
              任何注册用户仅需在个人后台点击<span class="font-bold text-brand-ink-strong">「申请成为推广大使」</span>，签署推广协议后，由客服审核开通（非自动开通）。
            </p>
            <div class="p-2.5 rounded-lg bg-slate-50 text-[11px] text-brand-ink-strong font-medium flex justify-between items-center">
              <span>开通结果：</span>
              <span class="text-emerald-600 font-extrabold text-[12.5px]">审核通过后解锁对应身份权益与结算能力</span>
            </div>
          </div>
        </div>

        <!-- SECTION D: 创始合伙人战略共建 -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">四、关于创始合伙人战略共建</h3>
          </div>

          <p class="text-[12px] text-brand-secondary leading-relaxed font-sans">
            创始合伙人由公司统一招商签约；合同年费固定为 <strong class="text-brand-ink-strong">29,800 元/年</strong>，详情请咨询客服。
          </p>

          <div class="bg-amber-500/[0.03] rounded-xl p-3 border border-amber-500/10 space-y-2 text-[11px] text-brand-secondary font-sans">
            <div class="flex justify-between font-bold text-brand-ink-strong">
              <span>🛡️ 首批抢先专享：</span>
              <span class="text-red-650 text-red-600 font-black">名额有限期权确权</span>
            </div>
            <p class="leading-relaxed mt-1 border-t border-dashed border-amber-500/15 pt-2">
              首批50名专享公司 <strong>5% 的合规期权池份额</strong>，后续均走正式的 <strong>工商变更登记确权</strong>，确保投资合伙人依法依规享有核心业务红利分润。
            </p>
          </div>

          <!-- Top 6 Privileges List -->
          <div class="bg-white rounded-2xl p-4.5 border border-gray-150/60 shadow-xs space-y-3.5">
            <h4 class="text-[13px] font-black text-brand-ink-strong font-serif mb-1">创始合伙人享有六大顶级专享权</h4>

            <div class="space-y-4">
              <!-- Item 1 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">1</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">自用账户在服务期间非商品免单</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5">合伙人自用账户在服务期间所有需要消耗积分的功能、课程均不消耗积分，积分兑换商品规则与普通用户一致。</p>
                </div>
              </div>

              <!-- Item 2 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">2</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">55% 直属充值现金直返</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    直接推荐的下属人脉在系统产生的所有消费，一律无条件给予 <strong>55% 现金返还</strong>，推广订单完成后按规则结算至推广余额。
                  </p>
                </div>
              </div>

              <!-- Item 3 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">3</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">工商确权的期权分红红利</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    作为核心业务伙伴，依法登记期权份额，并走正式的 <strong>工商变更与确权登记</strong> 流程，依照公司章程及红利规定享受持续稳定的年度持股分红派息。
                  </p>
                </div>
              </div>

              <!-- Item 4 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">4</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">15% 团队管理业绩提额</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    合伙人作为团队管理人，统一享受其名下管理的所有推广大使产生的推广充值流水总额 <strong>15% 的管理提成</strong>。
                  </p>
                </div>
              </div>

              <!-- Item 5 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">5</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">合伙人推荐服务返点 55%</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5">
                    成功推荐同行或下属开通加盟创始合伙人生态卡，立刻获取缴费费用的 <strong>55% 服务推荐返金（即单笔直返 16,390 元）</strong>，帮助合作人更快回收投入。
                  </p>
                </div>
              </div>

              <!-- Item 6: Team Performance & Bonus Mechanism -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">6</span>
                <div class="w-full">
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal flex items-center justify-between">
                    <span>团队业绩及奖金发放机制</span>
                    <span class="text-[9.5px] bg-indigo-50 border border-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-md font-bold font-sans">结算方案</span>
                  </h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    团队奖金发放基于创始合伙人所管理的推广团队旗下各类推广大使产生的业绩总和进行计算。
                  </p>

                  <div class="mt-3 text-brand-secondary rounded-xl border border-indigo-100/50 bg-indigo-50/[0.12] p-3.5 space-y-4 font-sans text-[11.5px]">
                    <div class="space-y-1.5">
                      <div class="text-[11.5px] text-indigo-950 font-extrabold flex items-center gap-1.5">
                        <span class="w-1.5 h-3 bg-indigo-600 rounded-full"></span>
                        <span>公式一：业绩总额计算</span>
                      </div>
                      <div class="bg-white px-3 py-2.5 rounded-xl border border-indigo-100/60 shadow-xs">
                        <div class="font-mono text-[10px] text-indigo-950 font-black leading-tight break-all">
                          业绩总额 = 推广大使业绩 + VIP 推广大使业绩 + SVIP 推广大使业绩 + 直属推荐人脉消费额
                        </div>
                        <div class="text-[9.5px] text-slate-500 border-t border-dashed border-indigo-50 mt-2.5 pt-2 leading-relaxed">
                          📌 <span class="font-extrabold text-amber-800">备注：</span>直属推荐人脉消费额同样计入团队业绩总额。
                        </div>
                      </div>
                    </div>

                    <div class="space-y-1.5">
                      <div class="text-[11.5px] text-indigo-950 font-extrabold flex items-center gap-1.5">
                        <span class="w-1.5 h-3 bg-indigo-600 rounded-full"></span>
                        <span>公式二：奖金总额计算</span>
                      </div>
                      <div class="bg-white px-3 py-2.5 rounded-xl border border-indigo-100/60 shadow-xs">
                        <div class="font-mono text-[10px] text-indigo-950 font-black leading-normal break-all">
                          奖金总额 = 推广大使充值 × 15% + VIP 推广大使充值 × 10% + SVIP 推广大使充值 × 5% + 直属推荐人脉消费额 × 5%
                        </div>
                      </div>
                    </div>

                    <div class="space-y-1.5">
                      <div class="text-[11.5px] text-indigo-950 font-extrabold flex items-center gap-1.5">
                        <span class="w-1.5 h-3 bg-indigo-600 rounded-full"></span>
                        <span>公式三：个人奖金分配</span>
                      </div>
                      <div class="bg-white px-3 py-2.5 rounded-xl border border-indigo-100/60 shadow-xs">
                        <div class="font-mono text-[10px] text-indigo-950 font-black leading-normal">
                          个人奖金 =（个人推广充值金额 / 业绩总额）× 奖金总额
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dynamic Sandbox calculator -->
        <div class="bg-gradient-to-br from-slate-900 to-slate-950 text-white rounded-2xl p-4.5 border border-amber-500/25 shadow-sm space-y-4">

          <!-- Header and Tab Selection -->
          <div class="flex flex-col gap-2 border-b border-white/10 pb-3">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-1.5">
                <Calculator :size="15" class="text-amber-400" />
                <span class="text-[13.5px] font-serif font-black text-amber-500">分成收益计算器</span>
              </div>
              <span class="text-[8.5px] font-mono text-slate-400">年化预估测算系统</span>
            </div>

            <!-- Tabs for Version selection -->
            <div class="grid grid-cols-2 gap-1 bg-black/40 p-1 rounded-xl border border-white/5 text-[11px] font-bold mt-1">
              <button
                @click="calcVersion = 'partner'"
                :class="calcVersion === 'partner' ? 'bg-amber-500 text-slate-950 font-black shadow-xs' : 'text-slate-300 hover:text-white'"
                class="py-1.5 rounded-lg transition-all outline-none cursor-pointer"
              >
                💼 创始合伙人版
              </button>
              <button
                @click="calcVersion = 'ambassador'"
                :class="calcVersion === 'ambassador' ? 'bg-indigo-600 text-white font-black shadow-xs' : 'text-slate-300 hover:text-white'"
                class="py-1.5 rounded-lg transition-all outline-none cursor-pointer"
              >
                📣 推广大使版
              </button>
            </div>
          </div>

          <!-- Content Panel A: Partner Version -->
          <div v-if="calcVersion === 'partner'" class="space-y-4 font-sans text-left">
            <p class="text-[11px] text-slate-300 leading-relaxed bg-white/5 p-2 rounded-lg border border-white/5">
              💡 <strong>公式</strong>：直属充值金额 × 15% + 旗下团队业绩总额 × 15% + 团队奖金。
            </p>

            <!-- Parameter 1: Direct users count -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">1. 直属推荐人脉数：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ directUsersCount }} 人</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="directUsersCount" min="2" max="500" step="1"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-10 text-center">{{ directUsersCount }}人</span>
              </div>
            </div>

            <!-- Parameter 2: Avg annual spend -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">2. 直属推荐人脉消费额：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ avgAnnualDirectSpend }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="avgAnnualDirectSpend" min="50" max="2500" step="10"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-11 text-center font-bold">{{ avgAnnualDirectSpend }}元</span>
              </div>
            </div>

            <!-- Parameter 3: Normal ambassador performance -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">3. 旗下推广大使推广充值：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ normalAmbassadorPerformance }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="normalAmbassadorPerformance" min="0" max="200000" step="1000"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-14 text-center font-bold">{{ normalAmbassadorPerformance }}元</span>
              </div>
            </div>

            <!-- Parameter 4: VIP ambassador performance -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">4. 旗下 VIP 推广大使推广充值：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ vipAmbassadorPerformance }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="vipAmbassadorPerformance" min="0" max="200000" step="1000"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-14 text-center font-bold">{{ vipAmbassadorPerformance }}元</span>
              </div>
            </div>

            <!-- Parameter 5: SVIP ambassador performance -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">5. 旗下 SVIP 推广大使推广充值：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ svipAmbassadorPerformance }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="svipAmbassadorPerformance" min="0" max="200000" step="1000"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-14 text-center font-bold">{{ svipAmbassadorPerformance }}元</span>
              </div>
              <p class="text-[9.5px] text-slate-400 leading-snug">
                合伙人的个人直推金额 {{ formatCurrency(directAnnualPerformance) }} 同步计入 SVIP 推广大使推广充值业绩。
              </p>
            </div>

            <!-- Calculations Breakdown for Partner -->
            <div class="bg-black/35 p-3.5 rounded-xl border border-white/5 grid grid-cols-2 gap-3 text-center mt-3">
              <div class="border-r border-white/10 pr-1">
                <span class="text-[8.5px] text-slate-400 block uppercase">直属充值收益 (15%)</span>
                <span class="text-[13.5px] font-extrabold text-emerald-400 block mt-1 font-mono">
                  {{ formatCurrency(partnerDirectAnnualEarn) }} <span class="text-[9px] text-slate-400">/年</span>
                </span>
              </div>
              <div class="pl-1">
                <span class="text-[8.5px] text-slate-400 block uppercase">团队管理提成 (15%)</span>
                <span class="text-[13.5px] font-extrabold text-emerald-400 block mt-1 font-mono">
                  {{ formatCurrency(partnerTeamManagementAnnualEarn) }} <span class="text-[9px] text-slate-400">/年</span>
                </span>
              </div>
              <div class="col-span-2 grid grid-cols-2 gap-2 pt-2 border-t border-white/10">
                <div>
                  <span class="text-[8.5px] text-slate-400 block uppercase">个人团队奖金分成</span>
                  <span class="text-[12px] font-extrabold text-amber-200 block mt-1 font-mono">{{ formatCurrency(partnerPersonalTeamBonus) }}</span>
                </div>
                <div>
                  <span class="text-[8.5px] text-slate-400 block uppercase">团队奖金总额</span>
                  <span class="text-[12px] font-extrabold text-amber-200 block mt-1 font-mono">{{ formatCurrency(teamBonusTotal) }}</span>
                </div>
              </div>
              <div class="col-span-2 pt-2 border-t border-white/10">
                <span class="text-[8.5px] text-slate-400 block uppercase">团队业绩总额</span>
                <span class="text-[12px] font-extrabold text-amber-200 block mt-1 font-mono">{{ formatCurrency(teamPerformanceTotal) }}</span>
              </div>
            </div>

            <!-- Cumulative Total Annual Output -->
            <div class="text-center pt-3 border-t border-white/10 mt-1">
              <p class="text-[9px] text-slate-450 uppercase tracking-widest leading-none font-bold">合伙人预计被动年化收入</p>
              <p class="text-[25px] font-black text-amber-300 tracking-tight mt-1 font-serif">
                {{ formatCurrency(partnerTotalAnnualEarn) }} <span class="text-xs font-sans font-normal text-slate-300">/ 年</span>
              </p>
              <p class="text-[8.5px] text-slate-400 mt-1 leading-normal text-center max-w-[90%] mx-auto">
                ※ 已包含直属收益、团队管理收益与个人团队奖金分成。
              </p>
            </div>
          </div>

          <!-- Content Panel B: Ambassador Version -->
          <div v-else class="space-y-4 font-sans text-left">
            <p class="text-[11px] text-indigo-200 bg-slate-850 p-2.5 rounded-lg border border-indigo-500/10 leading-relaxed bg-white/5">
              💡 <strong>公式</strong>：(直属推荐人脉数 × 平均直推年均消费额) × 大使层级提成比例。
            </p>

            <!-- Level selection small tags: 3 small tags -->
            <div class="space-y-1.5">
              <label class="text-[10.5px] text-slate-350 font-bold">已选推广大使等级比例：</label>
              <div class="grid grid-cols-3 gap-1.5 mt-1 font-sans text-[10.5px] font-extrabold">
                <button
                  @click="selectedAmbassadorTier = 'normal'"
                  :class="selectedAmbassadorTier === 'normal' ? 'bg-indigo-600 text-white border-transparent' : 'bg-slate-800 text-slate-300 border-white/5 hover:bg-slate-750'"
                  class="py-1.5 rounded-lg border text-center transition-all cursor-pointer outline-none font-sans"
                >
                  普通 (10%)
                </button>
                <button
                  @click="selectedAmbassadorTier = 'vip'"
                  :class="selectedAmbassadorTier === 'vip' ? 'bg-indigo-600 text-white border-transparent' : 'bg-slate-800 text-slate-300 border-white/5 hover:bg-slate-750'"
                  class="py-1.5 rounded-lg border text-center transition-all cursor-pointer outline-none font-sans"
                >
                  VIP (25%)
                </button>
                <button
                  @click="selectedAmbassadorTier = 'svip'"
                  :class="selectedAmbassadorTier === 'svip' ? 'bg-indigo-600 text-white border-transparent' : 'bg-slate-800 text-slate-300 border-white/5 hover:bg-slate-750'"
                  class="py-1.5 rounded-lg border text-center transition-all cursor-pointer outline-none font-sans"
                >
                  SVIP (40%)
                </button>
              </div>
            </div>

            <!-- Parameter 1: Direct users count -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-300">
                <span class="font-bold">直属推荐人脉数：</span>
                <span class="text-indigo-350 text-indigo-400 font-extrabold font-mono">{{ directUsersCount }} 人</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="directUsersCount" min="2" max="500" step="1"
                  class="flex-1 accent-indigo-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-10 text-center">{{ directUsersCount }}人</span>
              </div>
            </div>

            <!-- Parameter 2: Avg annual spend -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-300">
                <span class="font-bold">平均直推人脉年消费额：</span>
                <span class="text-indigo-350 text-indigo-400 font-extrabold font-mono">{{ avgAnnualDirectSpend }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="avgAnnualDirectSpend" min="50" max="2500" step="10"
                  class="flex-1 accent-indigo-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-11 text-center font-bold">{{ avgAnnualDirectSpend }}元</span>
              </div>
            </div>

            <!-- Cumulative Total for Ambassador -->
            <div class="text-center pt-3 border-t border-white/10 mt-3 bg-black/20 p-3 rounded-xl border border-white/5">
              <p class="text-[9px] text-slate-450 uppercase tracking-widest leading-none font-bold">大使预计被动年化收入</p>
              <p class="text-[25px] font-black text-indigo-400 tracking-tight mt-1 font-serif">
                {{ formatCurrency(ambassadorAnnualEarn) }} <span class="text-xs font-sans font-normal text-slate-300">/ 年</span>
              </p>
              <p class="text-[8.5px] text-slate-450 mt-1">
                （当前计算基于已选择提成比例：<strong class="text-indigo-300 font-bold font-mono">{{ tierRates[selectedAmbassadorTier] * 100 }}%</strong>）
              </p>
            </div>
          </div>

        </div>
      </div>

    </div>

    <transition name="slide">
      <div
        v-if="showApplyPlaceholder"
        class="absolute inset-0 z-[140] bg-brand-paper flex flex-col text-left"
      >
        <header class="bg-white border-b border-gray-100 flex items-center justify-between px-4 py-3.5 sticky top-0 z-10 shadow-xs shrink-0">
          <button
            @click="showApplyPlaceholder = false"
            class="flex items-center gap-1 text-brand-secondary hover:text-brand-ink-strong transition-colors cursor-pointer outline-none text-[14px]"
          >
            <ArrowLeft :size="18" />
            <span class="font-semibold">返回</span>
          </button>
          <h2 class="font-serif font-black text-[15px] text-brand-ink-strong tracking-wide">
            申请加入
          </h2>
          <div class="w-12"></div>
        </header>

        <main class="flex-1 flex items-center justify-center px-6 text-center">
          <div class="space-y-2">
            <p class="font-serif text-[20px] font-black text-brand-ink-strong">申请加入页面待设计</p>
            <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">
              这里先保留跳转占位，后续可替换为正式申请页面。
            </p>
          </div>
        </main>
      </div>
    </transition>

    <!-- Sticky H5 Actions Footer -->
    <div class="absolute bottom-0 inset-x-0 border-t border-gray-150/60 bg-white p-3.5 max-w-md mx-auto z-15 shadow-2xl shrink-0">
      <div class="grid grid-cols-3 gap-2 w-full">
        <button
          @click="emit('close')"
          class="px-2 py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink text-[11px] font-extrabold rounded-lg outline-none cursor-pointer border border-gray-200"
        >
          返回个人中心
        </button>
        <button
          @click="handleContactSupport"
          class="px-2 py-2.5 bg-slate-900 border border-slate-800 text-amber-300 text-[11px] font-black rounded-lg outline-none cursor-pointer hover:bg-slate-800 shadow-sm"
        >
          联系客服
        </button>
        <button
          @click="handleApplyJoin"
          class="px-2 py-2.5 bg-slate-900 border border-slate-800 text-amber-300 text-[11px] font-black rounded-lg outline-none cursor-pointer hover:bg-slate-800 shadow-sm"
        >
          申请加入
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Disable native scrollbar styles inside nested modal previews */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}

.slide-enter-from, .slide-leave-to {
  transform: translateY(100%);
  opacity: 0.95;
}
</style>
```

### `src/components/recharge/RechargePage.vue`

```vue
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  AlertTriangle,
  ArrowRight,
  Check,
  HelpCircle,
  Loader2,
  RefreshCw,
} from 'lucide-vue-next';
import {
  createRechargeOrder,
  createRechargePayment,
  getRechargePaymentStatus,
  listRechargePackages,
} from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { PaymentTransactionResponse, RechargeOrderResponse, RechargePackageResponse } from '../../types/api';

const props = defineProps<{
  routeQuery?: Record<string, string | undefined>;
}>();

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
}>();

type PageState = 'checking' | 'auth_required' | 'recharge_panel' | 'pending_payment' | 'payment_success' | 'payment_error';

const {
  state,
  bootstrapApp,
  refreshPoints,
  isRegisteredUser,
  displayNickname,
  customerServiceCopyForScene,
  requestRegisteredUser,
  openCustomerServiceModal,
  humanizeError,
} = useEaseWiseApp();

const pageState = ref<PageState>('checking');
const packages = ref<RechargePackageResponse[]>([]);
const selectedPackageKey = ref<string | null>(null);
const currentOrder = ref<RechargeOrderResponse | null>(null);
const currentPayment = ref<PaymentTransactionResponse | null>(null);
const loadingPackages = ref(false);
const creatingOrder = ref(false);
const refreshingStatus = ref(false);
const actionError = ref('');

const routeQuery = computed(() => props.routeQuery || {});
const source = computed(() => routeQuery.value.source || 'profile');
const returnTo = computed(() => routeQuery.value.return_to || 'profile');
const requiredPoints = computed(() => Number(routeQuery.value.required_points || 0));
const promoterCode = computed(() => routeQuery.value.promoter_code || '');
const campaign = computed(() => routeQuery.value.campaign || '');
const channel = computed(() => routeQuery.value.channel || 'h5');
const currentPoints = computed(() => state.points?.balance ?? 0);
const canUseBilling = computed(() => Boolean(isRegisteredUser.value && state.accessToken && state.user));
const selectedPackage = computed(() => packages.value.find((item) => item.package_key === selectedPackageKey.value) || packages.value[0] || null);
const pointsDeficiency = computed(() => Math.max(0, requiredPoints.value - currentPoints.value));
const userNickname = computed(() => displayNickname.value || '易友');
const userIdentityDisplay = computed(() => canUseBilling.value ? '已绑定正式身份' : '未登录浏览态');
const packageGridClass = computed(() => {
  const count = packages.value.length;
  if (count === 5) return 'grid grid-cols-6 gap-2 pt-1';
  if (count === 4 || count === 2) return 'grid grid-cols-2 gap-2 pt-1';
  if (count === 3 || count === 6) return 'grid grid-cols-3 gap-2 pt-1';
  return 'grid grid-cols-1 gap-2 pt-1';
});
const pageStatusMessage = computed(() => {
  if (currentPayment.value?.status === 'provider_unconfigured') {
    return '已创建订单，请联系客服完成支付；后台确认收款后，积分会自动到账。';
  }
  if (currentPayment.value?.client_message) {
    return currentPayment.value.client_message;
  }
  return '请根据支付渠道返回的状态继续处理。';
});
const paymentContactReason = computed(() => {
  const order = currentOrder.value;
  const packageTitle = order?.package_title || selectedPackage.value?.title || '充值套餐';
  const amount = order ? `￥${formatMoney(order.amount_cents)}` : '';
  const points = order?.total_points || selectedPackage.value?.total_points || 0;
  const orderText = order?.order_id ? `订单 ${order.order_id}` : '充值订单';
  return `${orderText}，${packageTitle}，${amount}，${points} 积分，用户 ${userNickname.value}`;
});
const unsuccessfulOrderState = computed(() => {
  const orderStatus = currentOrder.value?.status || '';
  const rawOrderStatus = currentOrder.value?.raw_status || '';
  if (rawOrderStatus === 'rejected' || orderStatus === 'refunded') {
    return {
      title: '订单未完成',
      message: '后台已拒绝该充值订单，积分不会到账。请重新选择套餐，或联系客服确认原因。',
    };
  }
  if (orderStatus === 'closed') {
    return {
      title: '订单已关闭',
      message: '该充值订单已关闭，无法继续支付或到账。请重新选择套餐后再次下单。',
    };
  }
  if (orderStatus === 'refund_pending') {
    return {
      title: '订单退款处理中',
      message: '该订单已进入退款处理流程，暂不能继续作为充值订单支付。',
    };
  }
  return null;
});
const paymentErrorTitle = computed(() => unsuccessfulOrderState.value?.title || '账单未能成功结付');
const paymentErrorMessage = computed(() => unsuccessfulOrderState.value?.message || '如果已经扣款或对支付结果有疑问，请联系客服协助核查。');
const paymentErrorContactContext = computed(() => unsuccessfulOrderState.value ? paymentContactReason.value : undefined);

onMounted(async () => {
  await Promise.all([bootstrapApp(), sleep(400)]);
  await syncPageFromIdentity();
});

watch(canUseBilling, async (value, previousValue) => {
  if (value && !previousValue) {
    pageState.value = 'checking';
    await syncPageFromIdentity();
  }
});

watch(routeQuery, () => {
  actionError.value = '';
});

async function syncPageFromIdentity(): Promise<void> {
  if (!canUseBilling.value) {
    pageState.value = 'auth_required';
    return;
  }
  await loadPackages();
  const restored = await restoreOrderFromUrl();
  if (!restored) {
    pageState.value = 'recharge_panel';
  }
}

async function loadPackages(): Promise<void> {
  if (!canUseBilling.value || loadingPackages.value) {
    return;
  }
  loadingPackages.value = true;
  actionError.value = '';
  try {
    packages.value = (await listRechargePackages(requireAccessToken())).items.slice(0, 6);
    recommendPackage();
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    loadingPackages.value = false;
  }
}

function recommendPackage(): void {
  if (packages.value.length === 0) {
    selectedPackageKey.value = null;
    return;
  }
  if (selectedPackageKey.value && packages.value.some((item) => item.package_key === selectedPackageKey.value)) {
    return;
  }
  const sortedPackages = [...packages.value].sort((left, right) => left.total_points - right.total_points);
  const recommended = pointsDeficiency.value > 0
    ? sortedPackages.find((item) => item.total_points >= pointsDeficiency.value)
    : sortedPackages[Math.min(1, sortedPackages.length - 1)];
  selectedPackageKey.value = (recommended || sortedPackages[sortedPackages.length - 1]).package_key;
}

async function restoreOrderFromUrl(): Promise<boolean> {
  const orderId = routeQuery.value.order_id;
  if (!orderId || !canUseBilling.value) {
    return false;
  }
  refreshingStatus.value = true;
  try {
    const response = await getRechargePaymentStatus(requireAccessToken(), orderId);
    currentOrder.value = response.order;
    currentPayment.value = response.latest_payment;
    applyPaymentState();
    return true;
  } catch (error) {
    actionError.value = humanizeError(error);
    return false;
  } finally {
    refreshingStatus.value = false;
  }
}

async function createOrder(): Promise<void> {
  if (!canUseBilling.value) {
    pageState.value = 'auth_required';
    return;
  }
  if (!selectedPackage.value || creatingOrder.value) {
    return;
  }
  creatingOrder.value = true;
  actionError.value = '';
  try {
    const order = await createRechargeOrder(requireAccessToken(), {
      package_key: selectedPackage.value.package_key,
      source: 'h5_recharge_page',
      idempotency_key: buildIdempotencyKey('order', selectedPackage.value.package_key),
      remark: JSON.stringify({
        source: source.value,
        return_to: returnTo.value,
        promoter_code: promoterCode.value || null,
        campaign: campaign.value || null,
        channel: channel.value,
      }),
    });
    currentOrder.value = order;
    updateOrderInUrl(order.order_id);
    await createPaymentForCurrentOrder();
    pageState.value = 'pending_payment';
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    creatingOrder.value = false;
  }
}

async function createPaymentForCurrentOrder(): Promise<void> {
  if (!currentOrder.value) {
    return;
  }
  currentPayment.value = await createRechargePayment(requireAccessToken(), currentOrder.value.order_id, {
    provider: 'wechat_h5',
    payment_method: 'wechat_h5',
    idempotency_key: buildIdempotencyKey('payment', currentOrder.value.order_id),
    return_url: typeof window !== 'undefined' ? window.location.href : null,
    client_context: {
      source: source.value,
      return_to: returnTo.value,
      promoter_code: promoterCode.value || null,
      campaign: campaign.value || null,
      channel: channel.value,
    },
  });
}

async function refreshPaymentStatus(): Promise<void> {
  if (!currentOrder.value || refreshingStatus.value) {
    return;
  }
  refreshingStatus.value = true;
  actionError.value = '';
  try {
    const response = await getRechargePaymentStatus(requireAccessToken(), currentOrder.value.order_id);
    currentOrder.value = response.order;
    currentPayment.value = response.latest_payment;
    applyPaymentState();
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    refreshingStatus.value = false;
  }
}

function applyPaymentState(): void {
  const orderStatus = currentOrder.value?.status;
  const rawOrderStatus = currentOrder.value?.raw_status;
  const paymentStatus = currentPayment.value?.status;
  if (orderStatus === 'paid' || orderStatus === 'completed') {
    pageState.value = 'payment_success';
    void refreshPoints().catch(() => undefined);
    return;
  }
  if (isUnsuccessfulOrderStatus(orderStatus, rawOrderStatus)) {
    pageState.value = 'payment_error';
    return;
  }
  if (paymentStatus === 'paid') {
    pageState.value = 'payment_success';
    void refreshPoints().catch(() => undefined);
    return;
  }
  if (paymentStatus === 'failed' || paymentStatus === 'cancelled') {
    pageState.value = 'payment_error';
    return;
  }
  pageState.value = 'pending_payment';
}

function isUnsuccessfulOrderStatus(orderStatus: string | undefined, rawOrderStatus: string | null | undefined): boolean {
  return rawOrderStatus === 'rejected' || orderStatus === 'refunded' || orderStatus === 'closed' || orderStatus === 'refund_pending';
}

function goToProfile(): void {
  emit('navigate-to-tab', 'profile');
}

function returnAfterPayment(): void {
  emit('navigate-to-tab', returnTo.value === 'phone' ? 'phone' : 'profile');
}

function showCurrentPayment(): void {
  if (currentPayment.value) {
    applyPaymentState();
  }
}

async function openUnifiedAuth(): Promise<void> {
  actionError.value = '';
  const authenticated = await requestRegisteredUser('充值');
  if (authenticated) {
    await syncPageFromIdentity();
  }
}

function openCustomerService(scene: string | Event = 'recharge_help', context?: string): void {
  openCustomerServiceModal(typeof scene === 'string' ? scene : 'recharge_help', context);
}

function updateOrderInUrl(orderId: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  const url = new URL(window.location.href);
  url.searchParams.set('order_id', orderId);
  window.history.replaceState(window.history.state, '', `${url.pathname}${url.search}${url.hash}`);
}

function clearOrderInUrl(): void {
  if (typeof window === 'undefined') {
    return;
  }
  const url = new URL(window.location.href);
  url.searchParams.delete('order_id');
  window.history.replaceState(window.history.state, '', `${url.pathname}${url.search}${url.hash}`);
}

function resetToRechargePanel(): void {
  currentOrder.value = null;
  currentPayment.value = null;
  actionError.value = '';
  clearOrderInUrl();
  recommendPackage();
  pageState.value = 'recharge_panel';
}

function packageSpanClass(index: number): string {
  return packages.value.length === 5 ? (index < 3 ? 'col-span-2' : 'col-span-3') : 'col-span-1';
}

function isHorizontalPackageLayout(): boolean {
  return [1, 2, 4].includes(packages.value.length);
}

function formatMoney(cents: number): string {
  const amount = cents / 100;
  return Number.isInteger(amount) ? String(amount) : amount.toFixed(2);
}

function getPaymentStatusLabel(value: string | undefined): string {
  const statusMap: Record<string, string> = {
    pending: '待支付',
    provider_unconfigured: '待联系客服支付',
    paid: '已支付',
    failed: '支付失败',
    cancelled: '已取消',
  };
  return statusMap[value || ''] || '支付交易待创建';
}

function requireAccessToken(): string {
  if (!state.accessToken) {
    throw new Error('auth_required');
  }
  return state.accessToken;
}

function buildIdempotencyKey(kind: string, seed: string): string {
  return `h5_recharge:${kind}:${seed}:${Date.now()}`;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
</script>

<template>
  <div class="min-h-screen bg-brand-paper pb-24 font-sans text-brand-ink antialiased">
    <div class="pt-4 pb-10 px-2 max-w-md mx-auto space-y-3.5">
      <div class="flex justify-start px-1">
        <button
          type="button"
          class="rounded-full bg-white/90 border border-brand-primary/8 px-3.5 py-1.5 text-[10.5px] font-bold text-brand-primary shadow-sm backdrop-blur-sm hover:bg-brand-primary/[0.04] active:scale-[0.98] transition-all cursor-pointer outline-none"
          @click="goToProfile"
        >
          返回个人中心
        </button>
      </div>

      <div class="bg-[#1C1A17] text-[#EDE7DE] rounded-2xl p-5 relative overflow-hidden shadow-xs text-left border border-[#D4C3A3]/10">
        <div class="absolute right-[-15px] bottom-[-25px] text-white/[0.02] font-serif font-black text-[120px] pointer-events-none select-none">
          ☯
        </div>

        <div class="relative z-10 flex items-center justify-between gap-4">
          <div class="space-y-0.5 min-w-0">
            <p class="text-[9.5px] font-medium text-gray-400 uppercase tracking-wider">我的积分钱包 · 结余</p>
            <div class="flex items-baseline gap-1">
              <span class="font-serif text-[32px] font-extrabold text-brand-accent leading-none">{{ currentPoints }}</span>
              <span class="text-[10px] opacity-70 font-semibold ml-0.5">分</span>
            </div>
          </div>

          <div class="shrink-0">
            <div
              v-if="canUseBilling"
              class="bg-white/[0.04] border border-white/[0.05] px-3 py-2 rounded-xl text-right max-w-[11.5rem]"
            >
              <p class="text-[11px] font-serif font-bold text-white leading-snug truncate">
                {{ userNickname }} | {{ userIdentityDisplay }}
              </p>
            </div>
            <button
              v-else
              type="button"
              class="h-9 px-4 rounded-xl bg-brand-accent hover:bg-brand-accent/90 text-brand-ink-strong text-[11.5px] font-black shadow-xs border border-[#D4C3A3]/20 active:scale-[0.98] transition-all cursor-pointer outline-none"
              @click="openUnifiedAuth"
            >
              登录
            </button>
          </div>
        </div>

        <div v-if="pointsDeficiency > 0" class="relative z-10 pt-3 border-t border-white/[0.05] flex items-center justify-between text-[10.5px] text-brand-accent mt-3">
          <span class="font-medium flex items-center gap-1">
            <span>☯ 当前功能还差 {{ pointsDeficiency }} 积分</span>
          </span>
          <span class="bg-white/10 text-gray-200 px-2 py-0.5 rounded text-[9.5px] font-bold">
            本次所需 {{ requiredPoints }} 分
          </span>
        </div>
      </div>

      <div v-if="pageState === 'checking'" class="py-24 text-center space-y-4 animate-in">
        <div class="relative w-12 h-12 mx-auto">
          <Loader2 class="w-12 h-12 text-brand-primary animate-spin opacity-50" />
          <div class="absolute inset-0 flex items-center justify-center font-serif font-black text-xs text-brand-primary">
            ☯
          </div>
        </div>
        <div class="space-y-1">
          <p class="font-serif font-bold text-brand-ink-strong text-xs">正在连接资产账户...</p>
          <p class="text-[10px] text-brand-secondary">校准当前已绑定的用户身份与积分记录</p>
        </div>
      </div>

      <div v-else-if="pageState === 'auth_required'" class="space-y-4 animate-in">
        <div class="bg-amber-500/[0.03] border border-amber-500/10 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle class="text-amber-600 shrink-0 mt-0.5" :size="16" />
          <div class="text-left space-y-1">
            <h4 class="text-xs font-bold text-amber-950 font-serif">请先验证您的常用身份</h4>
            <p class="text-[10px] text-amber-800 leading-relaxed font-sans">
              为防止更换设备或清除缓存导致资产丢失，充值前需要先完成登录，获取您的个人信息。
            </p>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 border border-brand-primary/5 shadow-xs space-y-4">
          <h3 class="text-xs font-bold text-brand-ink-strong border-b border-brand-primary/5 pb-2.5 font-serif flex items-center gap-1.5 justify-start">
            <span class="text-brand-primary">☯</span>
            <span>登录认证</span>
          </h3>

          <div class="space-y-3 text-left">
            <div class="bg-brand-primary/[0.025] border border-brand-primary/8 p-3 rounded-lg space-y-1.5 text-[10.5px] text-brand-secondary leading-relaxed font-sans">
              <p>未登录浏览态仅用于浏览页面，不能创建充值订单。</p>
              <p>登录后，积分、评测记录和支付结果会稳定绑定到您的正式账号。</p>
            </div>

            <button
              type="button"
              class="w-full py-3 bg-brand-primary hover:bg-brand-primary/95 text-white font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 cursor-pointer transition-all outline-none"
              @click="openUnifiedAuth"
            >
              <span>手机号登录/注册后继续</span>
            </button>

            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary/[0.01] border border-brand-primary/5 text-brand-secondary font-medium rounded-lg text-[10.5px] flex items-center justify-center cursor-pointer transition-colors outline-none"
              @click="openCustomerService('recharge_help')"
            >
              <span>联系客服获取协助</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="pageState === 'recharge_panel'" class="space-y-4 animate-in">
        <div v-if="campaign" class="bg-brand-primary/[0.02] border border-brand-primary/5 rounded-xl p-3 flex justify-between items-center text-left">
          <span class="text-brand-ink-strong text-xs font-semibold flex items-center gap-1.5">
            <span class="text-brand-primary">☯</span>
            <span>活动通路已关联（{{ campaign }}）</span>
          </span>
          <span class="text-[8px] bg-brand-primary text-white px-1.5 py-0.5 rounded font-bold scale-90">已关联</span>
        </div>

        <div class="space-y-3">
          <div class="flex justify-between items-center px-1">
            <h3 class="text-xs font-bold text-brand-ink-strong uppercase tracking-wider font-serif">请选择助运积分充值套餐</h3>
            <span class="text-[10px] text-brand-secondary font-mono">到账以支付状态为准</span>
          </div>

          <div v-if="loadingPackages" class="py-8 flex items-center justify-center gap-2 text-brand-secondary text-xs">
            <Loader2 :size="16" class="animate-spin" />
            <span>正在读取套餐配置...</span>
          </div>

          <div v-else-if="packages.length === 0" class="bg-amber-500/[0.03] border border-amber-500/10 rounded-xl p-4 text-[11px] text-amber-800 leading-relaxed">
            当前渠道暂无可用套餐，请联系客服确认充值入口是否开放。
          </div>

          <div v-else :class="packageGridClass">
            <button
              v-for="(item, index) in packages"
              :key="item.package_key"
              type="button"
              class="relative bg-white border rounded-xl px-2.5 py-3 flex flex-col items-center justify-center text-center cursor-pointer select-none transition-all duration-150 min-h-[76px]"
              :class="[
                packageSpanClass(index),
                selectedPackageKey === item.package_key
                  ? 'border-brand-primary bg-brand-primary/[0.03] ring-1 ring-brand-primary shadow-xs'
                  : 'border-brand-primary/10 hover:border-brand-primary/25 lg:hover:shadow-xs',
              ]"
              @click="selectedPackageKey = item.package_key"
            >
              <div
                v-if="item.title"
                class="absolute -top-2 left-1/2 transform -translate-x-1/2 text-[9px] font-black tracking-wider px-2 py-0.5 rounded-full z-10 whitespace-nowrap shadow-xs scale-90"
                :class="selectedPackageKey === item.package_key
                  ? 'bg-brand-primary text-white'
                  : 'bg-brand-primary/5 text-brand-primary border border-brand-primary/15'"
              >
                {{ item.title }}
              </div>

              <div v-if="isHorizontalPackageLayout()" class="w-full flex items-center justify-center gap-3 px-0.5">
                <div class="flex items-center justify-center shrink-0">
                  <span class="text-[10px] opacity-75 font-serif select-none mr-0.5" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-secondary/80'">☯</span>
                  <span class="font-serif text-[16px] font-black leading-none" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-ink-strong'">
                    {{ item.total_points }}
                  </span>
                  <span class="text-[8.5px] text-brand-secondary/65 font-serif scale-90 ml-0.5">分</span>
                </div>
                <div class="h-4 w-px bg-brand-primary/15 shrink-0"></div>
                <div class="flex items-center justify-center shrink-0">
                  <span class="text-[10px] text-brand-primary/70 font-sans font-bold mr-0.5 select-none">￥</span>
                  <span class="text-[16px] font-serif font-black text-brand-primary leading-none">{{ formatMoney(item.price_cents) }}</span>
                  <span class="text-[8.5px] text-transparent select-none scale-90 ml-0.5">分</span>
                </div>
              </div>

              <div v-else class="w-full flex flex-col items-center justify-center space-y-1.5">
                <div class="flex items-center justify-center leading-none">
                  <span class="text-[10px] opacity-75 font-serif shrink-0 mr-0.5" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-secondary/80'">☯</span>
                  <span class="font-serif text-[15.5px] font-black" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-ink-strong'">
                    {{ item.total_points }}
                  </span>
                  <span class="text-[8.5px] text-brand-secondary/65 font-serif scale-90 ml-0.5">分</span>
                </div>
                <div class="flex items-center justify-center leading-none">
                  <span class="text-[10px] text-brand-primary/70 font-sans font-bold mr-0.5 select-none">￥</span>
                  <span class="font-serif text-[15.5px] font-black text-brand-primary">{{ formatMoney(item.price_cents) }}</span>
                  <span class="text-[8.5px] text-transparent select-none scale-90 ml-0.5">分</span>
                </div>
              </div>
            </button>
          </div>
        </div>

        <div v-if="selectedPackage" class="bg-white border border-brand-primary/5 rounded-xl p-4.5 shadow-xs space-y-3.5 text-left">
          <div class="flex justify-between items-center text-xs">
            <div class="flex items-center gap-1">
              <span class="text-brand-secondary font-medium">已选积分：</span>
              <span class="font-serif font-black text-brand-ink-strong text-sm">{{ selectedPackage.total_points }} 积分</span>
            </div>
            <div class="font-mono flex items-center gap-1">
              <span class="text-brand-secondary font-medium">实付：</span>
              <span class="text-base font-extrabold text-brand-primary">￥{{ formatMoney(selectedPackage.price_cents) }}</span>
            </div>
          </div>

          <div v-if="promoterCode" class="text-[9.5px] bg-[#07C160]/5 text-[#07be5e] border border-[#07C160]/10 p-2.5 rounded-lg flex items-center justify-between">
            <span class="font-semibold flex items-center gap-1">
              <span>👤 推广邀请码：{{ promoterCode }}</span>
            </span>
            <span class="font-bold scale-90 origin-right">已关联归属</span>
          </div>

          <div class="space-y-2">
            <button
              type="button"
              class="w-full py-3 bg-brand-primary hover:bg-brand-primary/95 text-white font-serif font-semibold rounded-lg text-center text-xs cursor-pointer shadow-sm select-none transition-colors outline-none flex items-center justify-center gap-1.5"
              @click="currentPayment ? showCurrentPayment() : createOrder()"
            >
              <span>{{ currentPayment ? '查看当前支付状态' : '立即下单去支付' }}</span>
              <ArrowRight :size="13" />
            </button>
            <p class="text-[9px] text-center text-brand-secondary leading-relaxed">
              确认即代表您已阅读并接受充值服务规则
            </p>
          </div>
        </div>

        <div class="bg-brand-primary/[0.01] border border-brand-primary/5 rounded-xl p-4 text-left text-[10.5px] text-brand-secondary leading-relaxed">
          <p>充值订单与手机号、微信 ID 绑定，可跨平台使用</p>
        </div>
      </div>

      <div v-else-if="pageState === 'pending_payment'" class="space-y-4 animate-in">
        <div class="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4 text-left flex gap-3">
          <Loader2 class="text-indigo-600 shrink-0 mt-0.5 animate-spin" :size="16" />
          <div class="space-y-0.5 min-w-0">
            <h4 class="text-xs font-bold text-indigo-950 font-serif">充值账单已经创建，等待客服确认收款</h4>
            <p class="text-[10.5px] text-indigo-900/90 leading-relaxed font-sans font-mono break-all">
              单号：{{ currentOrder?.order_id }}
            </p>
          </div>
        </div>

        <div class="bg-white border border-brand-primary/5 rounded-xl p-5 shadow-xs text-left space-y-4">
          <div class="border-b border-brand-primary/5 pb-2.5">
            <h3 class="text-[10px] font-bold text-brand-secondary uppercase tracking-widest font-serif mb-1">支付清单明细</h3>
            <p class="text-sm font-black text-brand-ink-strong">
              助运积分充值（{{ selectedPackage?.total_points || currentOrder?.total_points }} 积分）
            </p>
          </div>

          <div class="space-y-2 text-xs font-sans text-brand-ink">
            <div class="flex justify-between items-center gap-3">
              <span class="text-brand-secondary">绑定用户账号：</span>
              <span class="font-mono font-bold text-right">{{ userNickname }}</span>
            </div>
            <div class="flex justify-between items-center gap-3">
              <span class="text-brand-secondary">获得可用积分：</span>
              <span class="font-bold text-brand-primary font-serif">{{ selectedPackage?.total_points || currentOrder?.total_points }} 积分</span>
            </div>
            <div class="flex justify-between items-center gap-3">
              <span class="text-brand-secondary">当前支付状态：</span>
              <span class="font-bold text-brand-ink-strong">{{ getPaymentStatusLabel(currentPayment?.status) }}</span>
            </div>
            <div class="flex justify-between items-center border-t border-dashed border-gray-100 mt-2.5 pt-2.5 gap-3">
              <span class="text-brand-secondary font-semibold">应付金额：</span>
              <span class="font-mono font-black text-brand-primary text-base">￥{{ formatMoney(currentOrder?.amount_cents || 0) }}</span>
            </div>
          </div>

          <div class="p-3.5 rounded-lg bg-amber-500/[0.02] border border-amber-300/30 text-[10px] leading-relaxed text-amber-900 font-sans">
            <p class="font-bold text-amber-950 pb-1 mb-1 border-b border-amber-200/40 select-none">
              当前支付说明
            </p>
            <p>{{ pageStatusMessage }}</p>
          </div>

          <div class="space-y-2 pt-1">
            <button
              type="button"
              class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-center text-xs cursor-pointer shadow-xs select-none transition-all outline-none flex items-center justify-center gap-1.5 disabled:opacity-60"
              :disabled="refreshingStatus"
              @click="refreshPaymentStatus"
            >
              <RefreshCw :size="13" :class="refreshingStatus ? 'animate-spin' : ''" />
              <span>刷新支付状态</span>
            </button>

            <button
              type="button"
              class="w-full py-2.5 bg-amber-400 hover:bg-amber-500 text-amber-950 border border-amber-300 font-bold rounded-lg text-center text-xs cursor-pointer select-none transition-all outline-none flex items-center justify-center gap-1"
              @click="openCustomerService('payment_issue', paymentContactReason)"
            >
              <span>联系客服进行支付</span>
            </button>

            <button
              type="button"
              class="w-full py-2 bg-brand-primary/[0.01] border border-brand-primary/5 hover:bg-brand-primary/[0.03] text-brand-secondary font-medium rounded-lg text-center text-[10.5px] cursor-pointer outline-none transition-all"
              @click="resetToRechargePanel"
            >
              重新挑选其他套餐
            </button>
          </div>
        </div>
      </div>

      <div v-else class="space-y-4 animate-in">
        <div v-if="pageState === 'payment_success'" class="bg-white border border-brand-primary/5 rounded-xl p-5 shadow-xs text-center space-y-5">
          <div class="w-10 h-10 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <Check class="stroke-[3]" :size="18" />
          </div>

          <div class="space-y-1">
            <h3 class="font-serif font-bold text-brand-ink-strong text-sm">积分已存入余额</h3>
            <p class="text-[11px] text-brand-secondary leading-relaxed px-4">
              本次充值积分已经进入您的钱包，可以返回继续使用相关功能。
            </p>
          </div>

          <div class="bg-brand-primary/[0.01] p-3.5 rounded-lg border border-brand-primary/5 text-left text-[11px] space-y-2 font-sans">
            <div class="flex justify-between gap-3">
              <span class="text-brand-secondary">订单单号：</span>
              <span class="font-mono text-brand-ink-strong break-all text-right">{{ currentOrder?.order_id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-brand-secondary">支付金额：</span>
              <span class="font-mono font-bold text-emerald-600">￥{{ formatMoney(currentOrder?.amount_cents || 0) }}</span>
            </div>
            <div class="flex justify-between border-t border-brand-primary/5 mt-1.5 pt-1.5">
              <span class="font-bold text-brand-ink-strong">当前可用余额：</span>
              <span class="font-mono font-bold text-brand-primary font-serif">{{ currentPoints }} 积分</span>
            </div>
          </div>

          <div class="space-y-2 pt-1">
            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-serif font-bold rounded-lg text-center text-xs cursor-pointer shadow-xs select-none transition-all outline-none"
              @click="returnAfterPayment"
            >
              确定并返回继续使用
            </button>
            <button
              type="button"
              class="w-full py-2 bg-brand-primary/[0.01] border border-brand-primary/5 hover:bg-brand-primary/[0.03] text-brand-secondary font-medium rounded-lg text-center text-[10.5px] cursor-pointer outline-none transition-colors"
              @click="resetToRechargePanel"
            >
              继续购买积分
            </button>
          </div>
        </div>

        <div v-else class="bg-white border border-brand-primary/5 rounded-xl p-5 shadow-xs text-center space-y-5">
          <div class="w-10 h-10 bg-red-50 border border-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto">
            <AlertTriangle :size="18" />
          </div>
          <div class="space-y-1">
            <h3 class="font-serif font-bold text-brand-ink-strong text-xs">{{ paymentErrorTitle }}</h3>
            <p class="text-[11px] text-brand-secondary px-4 leading-relaxed">
              {{ paymentErrorMessage }}
            </p>
          </div>
          <div class="flex flex-col gap-2 pt-1">
            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-serif font-bold rounded-lg text-center text-xs cursor-pointer select-none transition-colors outline-none flex items-center justify-center gap-1.5"
              @click="openCustomerService('payment_issue', paymentErrorContactContext)"
            >
              <span>联系客服核查</span>
            </button>
            <button
              type="button"
              class="w-full py-2 bg-brand-primary/[0.01] border border-brand-primary/5 hover:bg-brand-primary/[0.03] text-brand-secondary font-medium rounded-lg text-center text-[10.5px] cursor-pointer outline-none transition-colors"
              @click="resetToRechargePanel"
            >
              返回重新挑选套餐
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="actionError"
        class="bg-red-500/[0.02] border border-red-500/10 rounded-xl p-3 flex items-start gap-2 text-left text-[10.5px] text-red-800 leading-relaxed animate-in"
      >
        <AlertTriangle :size="14" class="shrink-0 mt-0.5" />
        <span>{{ actionError }}</span>
      </div>

      <div class="bg-white border border-brand-primary/5 rounded-xl p-4 shadow-xs text-left">
        <div class="flex items-center justify-between gap-3">
          <HelpCircle class="text-brand-primary shrink-0 mt-0.5 opacity-60" :size="16" />
          <div class="space-y-1 flex-1 min-w-0">
            <h4 class="text-xs font-bold text-brand-ink-strong font-serif">需要充值协助？</h4>
            <p class="text-[10px] text-brand-secondary leading-relaxed font-sans">
              {{ customerServiceCopyForScene('recharge_help') }}
            </p>
          </div>
          <button
            type="button"
            class="px-3.5 py-2 bg-brand-primary hover:bg-brand-primary/95 text-white text-[10.5px] font-bold rounded-lg cursor-pointer shrink-0 select-none transition-all outline-none shadow-xs"
            @click="openCustomerService"
          >
            联系客服
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation: enter 0.15s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
