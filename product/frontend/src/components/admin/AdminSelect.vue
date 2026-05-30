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
