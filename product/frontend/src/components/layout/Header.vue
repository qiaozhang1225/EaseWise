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
          class="font-brand text-heading-1 font-bold text-brand-ink-strong tracking-wide leading-tight"
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
