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
import { useEaseWiseApp } from './composables/useEaseWiseApp';

type AppTab = 'home' | 'phone' | 'bazi' | 'meihua' | 'agent' | 'profile' | 'recharge' | 'points-claim';

const activeTab = ref<AppTab>('home');
const routeQuery = ref<Record<string, string>>({});
const { bootstrapApp, requestRegisteredUser } = useEaseWiseApp();
const isAdminRoute = false;

const title = computed(() => {
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
</template>
