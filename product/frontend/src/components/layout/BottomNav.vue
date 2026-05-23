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
      class="flex flex-col items-center justify-center transition-all duration-200 outline-none w-20 py-1 cursor-pointer font-ui"
      :class="activeTab === tab.id ? 'text-brand-primary font-semibold' : 'text-brand-secondary hover:text-brand-primary'"
      :data-icon="tab.id"
    >
      <div class="p-1 px-3.5 rounded-full transition-colors flex items-center justify-center"
           :class="activeTab === tab.id ? 'bg-brand-primary/10 text-brand-primary' : 'text-brand-secondary'">
        <component :is="tab.icon" :size="22" class="shrink-0" />
      </div>
      <span class="text-caption mt-1 tracking-wide">{{ tab.label }}</span>
    </button>
  </nav>
</template>
