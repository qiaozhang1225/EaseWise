<script setup lang="ts">
import { ref } from 'vue';
import { ArrowLeft, Flower2, HelpCircle, RefreshCw, Sparkles } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const { state, showToast } = useEaseWiseApp();

const method = ref<'time' | 'number' | 'character'>('time');
const number1 = ref('');
const number2 = ref('');
const charInput = ref('');
const isSubmitting = ref(false);

const generatedGua = ref<any | null>(null);

function triggerStart() {
  if (method.value === 'number') {
    if (!number1.value.trim() || !number2.value.trim()) {
      showToast('请输入完整的上下起卦数字。');
      return;
    }
  } else if (method.value === 'character') {
    if (!charInput.value.trim()) {
      showToast('请输入用于起卦的汉字组合。');
      return;
    }
  }

  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    generatedGua.value = {
      primary: { name: '雷地豫', structures: '坤上震下', element: '木' },
      mutual: { name: '水山蹇', structures: '坎上艮下', element: '水' },
      changed: { name: '震为雷', structures: '震上震下', element: '木' },
      verdict: '卦得雷地豫，初六爻动。此卦利于顺应天时，建侯行师。近期行事宜缓不宜急，借助外力合伙修持，可获丰润财气暗示。'
    };
    showToast('起卦演算成功！');
  }, 1200);
}

function handleReset() {
  generatedGua.value = null;
  number1.value = '';
  number2.value = '';
  charInput.value = '';
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left select-none">

    <div class="flex items-center gap-2 mb-4">
      <button
        @click="emit('back')"
        class="text-brand-ink-strong hover:text-brand-primary font-sans text-[12.5px] font-extrabold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none p-1 rounded hover:bg-zinc-100 transition-colors"
      >
        <ArrowLeft :size="16" />
        <span>返回首页</span>
      </button>
    </div>

    <!-- SKELETON FORM VIEW -->
    <div v-if="!generatedGua" class="space-y-4">
      <div class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm space-y-4">
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0">
            <Flower2 :size="20" />
          </div>
          <div>
            <h2 class="font-serif text-[17px] font-black text-brand-ink-strong leading-tight">梅花易数古法起卦</h2>
            <p class="font-sans text-[10.5px] text-brand-secondary mt-0.5">
              支持报数、时间、汉字起卦（原型体验）
            </p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Method choice -->
          <div class="space-y-1.5">
            <label class="text-[11px] font-bold text-brand-secondary">起卦法门</label>
            <div class="grid grid-cols-3 bg-brand-paper p-1 rounded-xl border border-gray-100">
              <button @click="method = 'time'" class="py-2 text-[11px] font-bold rounded-lg transition-all" :class="method === 'time' ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary'">时间起卦</button>
              <button @click="method = 'number'" class="py-2 text-[11px] font-bold rounded-lg transition-all" :class="method === 'number' ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary'">报数起卦</button>
              <button @click="method = 'character'" class="py-2 text-[11px] font-bold rounded-lg transition-all" :class="method === 'character' ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary'">汉字起卦</button>
            </div>
          </div>

          <!-- Fields -->
          <div v-if="method === 'time'" class="bg-brand-paper/50 rounded-xl p-3 border border-dashed border-gray-200 font-sans text-[11px] text-brand-secondary leading-relaxed">
            系统将捕获当前的北京年月日时辰，转化为干支数理，除以八所得上下卦及动爻进行排盘。
          </div>

          <div v-else-if="method === 'number'" class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-[10px] text-brand-secondary font-bold">上卦报数</label>
                <input v-model="number1" type="number" placeholder="输入任意正整数" class="w-full bg-brand-paper text-brand-ink text-[12.5px] p-2.5 rounded-xl border border-gray-100 outline-none" />
              </div>
              <div class="space-y-1">
                <label class="text-[10px] text-brand-secondary font-bold">下卦报数</label>
                <input v-model="number2" type="number" placeholder="输入任意正整数" class="w-full bg-brand-paper text-brand-ink text-[12.5px] p-2.5 rounded-xl border border-gray-100 outline-none" />
              </div>
            </div>
          </div>

          <div v-else class="space-y-1.5">
            <label class="text-[11px] font-bold text-brand-secondary">输入起卦汉字</label>
            <input v-model="charInput" placeholder="输入用于测算的汉字" class="w-full bg-brand-paper text-brand-ink text-[12.5px] p-2.5 rounded-xl border border-gray-100 outline-none" />
          </div>

          <button
            @click="triggerStart"
            :disabled="isSubmitting"
            class="w-full h-11 bg-brand-primary text-white font-sans text-xs font-bold rounded-xl shadow-md transition-all active:scale-[0.985] flex items-center justify-center gap-1 cursor-pointer"
          >
            <Sparkles :size="14" />
            <span>{{ isSubmitting ? '卦象生演中...' : '立即起卦起算' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- RESULT VIEW -->
    <div v-else class="space-y-4">
      <div class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm space-y-4">
        <div class="flex justify-between items-center border-b border-gray-100 pb-3">
          <span class="font-serif text-[15.5px] font-black text-brand-ink-strong">演化卦局结果</span>
          <button @click="handleReset" class="text-brand-primary text-xs font-bold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none">
            <RefreshCw :size="12" />
            <span>重新起卦</span>
          </button>
        </div>

        <div class="grid grid-cols-3 gap-3 text-center">
          <div class="bg-brand-paper/50 rounded-xl p-3 border border-thin">
            <span class="text-[10px] text-brand-secondary block font-bold">主卦(体用)</span>
            <span class="font-serif text-[15px] font-black text-brand-ink-strong block mt-1.5">{{ generatedGua.primary.name }}</span>
            <span class="text-[10px] text-brand-secondary block mt-0.5 font-bold">{{ generatedGua.primary.structures }}</span>
          </div>
          <div class="bg-brand-paper/50 rounded-xl p-3 border border-thin">
            <span class="text-[10px] text-brand-secondary block font-bold">互卦</span>
            <span class="font-serif text-[15px] font-black text-brand-ink-strong block mt-1.5">{{ generatedGua.mutual.name }}</span>
            <span class="text-[10px] text-brand-secondary block mt-0.5 font-bold">{{ generatedGua.mutual.structures }}</span>
          </div>
          <div class="bg-brand-paper/50 rounded-xl p-3 border border-thin">
            <span class="text-[10px] text-brand-secondary block font-bold">变卦</span>
            <span class="font-serif text-[15px] font-black text-brand-ink-strong block mt-1.5">{{ generatedGua.changed.name }}</span>
            <span class="text-[10px] text-brand-secondary block mt-0.5 font-bold">{{ generatedGua.changed.structures }}</span>
          </div>
        </div>

        <div class="bg-brand-paper/40 border border-gray-100 p-4 rounded-xl space-y-2">
          <span class="font-serif text-[13px] font-bold text-brand-primary-strong">卦义决断</span>
          <p class="font-sans text-[12.5px] leading-relaxed text-brand-secondary select-text whitespace-pre-wrap font-medium">
            {{ generatedGua.verdict }}
          </p>
        </div>
      </div>
    </div>

  </div>
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
</style>
