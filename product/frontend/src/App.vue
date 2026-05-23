<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import Header from './components/layout/Header.vue';
import BottomNav from './components/layout/BottomNav.vue';
import Home from './components/home/Home.vue';
import Analysis from './components/analysis/Analysis.vue';
import AIAgent from './components/ai-agent/AIAgent.vue';
import Profile from './components/profile/Profile.vue';
import { useEaseWiseApp } from './composables/useEaseWiseApp';

const activeTab = ref('home');
const { bootstrapApp } = useEaseWiseApp();

const title = computed(() => {
  switch (activeTab.value) {
    case 'home': return '易如反掌';
    case 'phone': return '手机号评测';
    case 'agent': return '智能体';
    case 'profile': return '我的';
    default: return '易如反掌';
  }
});

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

onMounted(() => {
  void bootstrapApp();
});
</script>

<template>
  <div class="min-h-screen">
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
        <Profile @navigate-to-tab="navigateToTab" />
      </div>
    </main>
    
    <!-- Tab navigations -->
    <BottomNav 
      :active-tab="activeTab === 'phone' ? 'home' : activeTab" 
      @update:active-tab="navigateToTab" 
    />
  </div>
</template>
