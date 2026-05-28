<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import Header from './components/layout/Header.vue';
import BottomNav from './components/layout/BottomNav.vue';
import Home from './components/home/Home.vue';
import Analysis from './components/analysis/Analysis.vue';
import AIAgent from './components/ai-agent/AIAgent.vue';
import Profile from './components/profile/Profile.vue';
import AmbassadorDetail from './components/profile/AmbassadorDetail.vue';
import AdminWorkspace from './components/admin/AdminWorkspace.vue';
import { useEaseWiseApp } from './composables/useEaseWiseApp';

const activeTab = ref('home');
const showAmbassadorDetail = ref(
  typeof window !== 'undefined' && window.history.state?.view === 'ambassador-detail',
);
const { bootstrapApp } = useEaseWiseApp();
const isAdminRoute = typeof window !== 'undefined' && window.location.pathname.startsWith('/admin');

const title = computed(() => {
  if (isAdminRoute) {
    return '易如反掌后台';
  }
  switch (activeTab.value) {
    case 'home': return '易如反掌';
    case 'phone': return '手机号评测';
    case 'agent': return '智能体';
    case 'profile': return '我的';
    default: return '易如反掌';
  }
});

const pageTitle = computed(() => (showAmbassadorDetail.value ? '推广大使' : title.value));

const navigateToTab = (tab: string) => {
  const currentActiveElement = typeof document !== 'undefined' ? document.activeElement : null;
  if (currentActiveElement instanceof HTMLElement) {
    currentActiveElement.blur();
  }

  if (activeTab.value === tab) {
    return;
  }

  activeTab.value = tab;

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

const openAmbassadorDetail = () => {
  if (showAmbassadorDetail.value || typeof window === 'undefined') {
    return;
  }

  window.history.pushState({ view: 'ambassador-detail' }, '', window.location.href);
  showAmbassadorDetail.value = true;
  window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
};

const closeAmbassadorDetail = () => {
  if (typeof window === 'undefined') {
    showAmbassadorDetail.value = false;
    return;
  }

  if (window.history.state?.view === 'ambassador-detail') {
    window.history.back();
    return;
  }

  showAmbassadorDetail.value = false;
};

const handlePopState = (event: PopStateEvent) => {
  showAmbassadorDetail.value = event.state?.view === 'ambassador-detail';
};

onMounted(() => {
  void bootstrapApp();
  if (typeof window !== 'undefined') {
    window.addEventListener('popstate', handlePopState);
  }
});

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('popstate', handlePopState);
  }
});

watch(pageTitle, (value) => {
  if (typeof document !== 'undefined') {
    document.title = value;
  }
}, { immediate: true });
</script>

<template>
  <div v-if="!isAdminRoute" class="min-h-screen bg-slate-950/5 relative overflow-x-hidden" :class="showAmbassadorDetail ? 'overflow-hidden' : ''">
    <div class="min-h-screen" :class="showAmbassadorDetail ? 'invisible pointer-events-none select-none' : 'visible'">
      <!-- Top Header -->
      <Header :title="title" />

      <!-- Main viewport -->
      <main class="font-sans antialiased">
        <div v-if="activeTab === 'home'">
          <Home @phone-click="navigateToTab('phone')" />
        </div>
        <div v-else-if="activeTab === 'phone'">
          <Analysis
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
            @open-ambassador-detail="openAmbassadorDetail"
          />
        </div>
      </main>

      <!-- Tab navigations -->
      <BottomNav
        :active-tab="activeTab === 'phone' ? 'home' : activeTab"
        @update:active-tab="navigateToTab"
      />
    </div>

    <div
      v-if="showAmbassadorDetail"
      class="fixed inset-0 z-[200] bg-brand-paper overflow-y-auto no-scrollbar"
    >
      <AmbassadorDetail @back="closeAmbassadorDetail" />
    </div>
  </div>
  <AdminWorkspace v-else />
</template>
