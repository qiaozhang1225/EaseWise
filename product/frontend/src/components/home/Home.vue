<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import {
  Calendar, CheckCircle2, XCircle, Calculator, UserCircle, History,
  Compass, Sparkles, AlertCircle, Type,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'phone-click'): void;
}>();

const { state, bootstrapApp, reviewBasePointsCost } = useEaseWiseApp();
const toast = ref<string | null>(null);
const yiExpanded = ref(false);
const jiExpanded = ref(false);

const points = computed(() => state.points?.balance ?? state.runtimeConfig?.points.guest_initial_grant ?? 0);
const displayDate = computed(() => {
  const rawText = state.almanac?.display_date || '';
  if (!rawText) {
    return '今日黄历加载中';
  }
  return rawText.replace(/\s*星期[一二三四五六日天]\s*$/, '').trim();
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
const yiItems = computed(() => state.almanac?.yi.length ? state.almanac.yi : ['--']);
const jiItems = computed(() => state.almanac?.ji.length ? state.almanac.ji : ['--']);
const yiHasMore = computed(() => (state.almanac?.yi.length || 0) > 5);
const jiHasMore = computed(() => (state.almanac?.ji.length || 0) > 5);
const visibleYiItems = computed(() => yiExpanded.value || !yiHasMore.value ? yiItems.value : yiItems.value.slice(0, 5));
const visibleJiItems = computed(() => jiExpanded.value || !jiHasMore.value ? jiItems.value : jiItems.value.slice(0, 5));
const tianShenTagText = computed(() => state.almanac?.tian_shen || '加载中');
const jiShenText = computed(() => state.almanac?.ji_shen.length ? state.almanac.ji_shen.join(' · ') : '加载中');
const pengzuSummary = computed(() => state.almanac?.pengzu_summary || '数据准备中');

const showToast = (message: string) => {
  toast.value = message;
  setTimeout(() => {
    toast.value = null;
  }, 2000);
};

const tools = [
  { id: 'avatar', name: '头像解析', desc: '头像风格与气场参考', icon: UserCircle },
  { id: 'name', name: '姓名解析', desc: '名字结构与使用感受', icon: Type },
  { id: 'bazi', name: '八字解析', desc: '个人状态与长期趋势', icon: Calendar },
  { id: 'qimen', name: '奇门问事', desc: '问题分析与决策辅助', icon: Compass },
  { id: 'almanac', name: '黄历查询', desc: '今日宜忌与日常参考', icon: History },
  { id: 'wuxing', name: '五行属性', desc: '属性查询与基础说明', icon: Sparkles },
];

onMounted(() => {
  void bootstrapApp();
});
</script>

<template>
  <div class="pt-16 pb-32 max-w-md mx-auto px-margin-mobile relative">
    <!-- Toast Notification -->
    <transition name="fade-slide">
      <div 
        v-if="toast"
        class="fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-ui text-body shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
      >
        <AlertCircle :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <!-- Daily Almanac Card -->
    <section class="mb-4 mt-3">
      <div class="bg-white rounded-2xl p-4 border border-brand-paper shadow-sm relative">
        <div class="absolute -top-2.5 left-5 bg-brand-gold-fixed text-white font-ui text-micro font-semibold px-3 py-0.5 rounded-md tracking-widest shadow-sm flex items-center gap-1.5 z-10 select-none">
          <span class="w-1.5 h-1.5 rounded-full bg-white/80 shrink-0 animate-pulse"></span>
          <span>今日黄历 · ALMANAC</span>
        </div>

        <div class="absolute -top-2.5 right-5 bg-emerald-600 text-white font-ui text-micro font-semibold px-3 py-0.5 rounded-md tracking-wide shadow-sm flex items-center z-10 select-none">
          <span>值神星君 · </span>
          <span class="font-brand leading-none">{{ tianShenTagText }}</span>
        </div>

        <div class="flex justify-between items-center mb-1 text-left pt-1.5 gap-4">
          <div class="shrink-0">
            <div class="flex items-baseline gap-1.5">
              <span class="text-brand-ink-strong font-brand text-heading-plus font-bold leading-none">{{ displayDate }}</span>
            </div>
          </div>
          <div class="flex-1 max-w-[50%] min-w-[130px]">
            <div class="bg-brand-primary/10 px-3 py-1.5 rounded-xl border border-brand-primary/30 flex items-center justify-between gap-1.5 shadow-sm w-full">
              <div class="flex items-center gap-1.5">
                <Sparkles :size="13" class="text-brand-gold-fixed fill-current shrink-0" />
                <span class="font-ui text-body font-extrabold text-brand-secondary">余币</span>
              </div>
              <span class="font-ui text-body font-extrabold text-brand-secondary whitespace-nowrap">
                <span class="text-brand-primary-strong font-brand text-title font-extrabold">{{ points }}</span> 分
              </span>
            </div>
          </div>
        </div>

        <div class="mb-3.5 text-left pt-0.5 select-none animate-fadeIn">
          <p class="font-ui text-caption text-brand-secondary/95 font-bold tracking-wide">
            {{ almanacMetaText }}
          </p>
        </div>
        
        <!-- Custom Auspicious Grid -->
        <div class="grid grid-cols-2 gap-3 py-2.5 border-t border-b border-gray-100/80 mb-2 text-left">
          <div class="flex items-start gap-1.5">
            <div class="flex items-center gap-0.5 text-brand-primary font-brand text-caption font-bold mt-0.5 shrink-0">
              <CheckCircle2 :size="13" class="text-brand-primary" fill="currentColor" stroke="white" />
              <span>宜:</span>
            </div>
            <div class="flex flex-wrap gap-1 flex-1">
              <span v-for="v in visibleYiItems" :key="v" class="bg-brand-primary/5 text-brand-primary-strong font-brand text-micro px-1.5 py-0.5 rounded font-bold animate-fadeIn">{{ v }}</span>
              <button
                v-if="yiHasMore"
                @click.stop="yiExpanded = !yiExpanded"
                class="bg-brand-primary hover:bg-brand-primary/90 text-white font-ui text-micro px-1.5 py-0.5 rounded font-bold cursor-pointer transition-colors border-none select-none outline-none inline-flex items-center justify-center shadow-sm shrink-0"
              >
                {{ yiExpanded ? '收起' : '更多' }}
              </button>
            </div>
          </div>
          <div class="flex items-start gap-1.5 border-l border-gray-100 pl-2">
            <div class="flex items-center gap-0.5 text-brand-gold-fixed font-brand text-caption font-bold mt-0.5 shrink-0">
              <XCircle :size="13" class="text-brand-gold-fixed" fill="currentColor" stroke="white" />
              <span>忌:</span>
            </div>
            <div class="flex flex-wrap gap-1 flex-1">
              <span v-for="v in visibleJiItems" :key="v" class="bg-amber-50 text-brand-gold-fixed font-brand text-micro px-1.5 py-0.5 rounded font-bold animate-fadeIn">{{ v }}</span>
              <button
                v-if="jiHasMore"
                @click.stop="jiExpanded = !jiExpanded"
                class="bg-brand-gold-fixed hover:bg-brand-gold-fixed/90 text-white font-ui text-micro px-1.5 py-0.5 rounded font-bold cursor-pointer transition-colors border-none select-none outline-none inline-flex items-center justify-center shadow-sm shrink-0"
              >
                {{ jiExpanded ? '收起' : '更多' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Heavy metaphysical data with clean lines -->
        <div class="bg-brand-paper/50 rounded-xl p-2.5 font-ui text-caption text-brand-secondary space-y-1.5 text-left">
          <div class="flex justify-between items-baseline border-b border-gray-100 pb-1.5 gap-3">
            <span class="shrink-0">今日吉神：</span>
            <span class="text-brand-ink font-brand font-medium leading-tight text-right">{{ jiShenText }}</span>
          </div>
          <div class="flex justify-between items-baseline gap-3">
            <span class="shrink-0">彭祖百忌：</span>
            <span class="text-brand-ink font-brand font-medium leading-tight text-right">{{ pengzuSummary }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Primary CTA Card: Phone Number metaphysical calculation -->
    <section class="mb-4">
      <button 
        @click="emit('phone-click')"
        class="w-full bg-brand-primary text-white rounded-2xl p-5 shadow-md flex items-center justify-between active:scale-[0.99] transition-transform text-left relative overflow-hidden cursor-pointer"
      >
        <div class="absolute top-0 right-0 bg-brand-accent text-brand-ink-strong font-ui text-micro font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wide">
          奇门遁甲 · 智能推演
        </div>
        <div class="flex flex-col gap-1.5 z-10 max-w-[70%]">
          <span class="font-brand text-title-lg font-bold leading-tight flex items-center gap-1.5">
            数字奇门手机号评测
          </span>
          <span class="font-ui text-body text-white/80 leading-relaxed">
            输入你的 11 位手机号，解锁智能推演下的 13 项全面评测结果。
          </span>
          <div class="flex items-center gap-3 mt-1.5 flex-wrap">
            <span class="font-ui text-caption text-brand-accent font-bold">
              数字奇门手机号评测 →
            </span>
            <span class="px-2.5 py-1 bg-brand-accent/20 border border-brand-accent/40 rounded-lg font-ui text-micro font-bold text-brand-accent leading-none select-none shadow-sm">
              消耗 {{ reviewBasePointsCost }} 积分
            </span>
          </div>
        </div>
        <div class="bg-white/15 p-4 rounded-full shrink-0 z-10">
          <Calculator :size="36" class="text-brand-accent shrink-0 animate-bounce" data-icon="dialpad" />
        </div>
      </button>
    </section>

    <!-- Secondary Feature Grid (Other 5 placeholder ones) -->
    <section class="grid grid-cols-2 gap-4">
      <div 
        v-for="tool in tools"
        :key="tool.id"
        @click="showToast(`「${tool.name}」正在准备中，后续版本开放。`)"
        class="bg-white p-4.5 rounded-xl border border-gray-100 hover:border-gray-200 transition-all cursor-pointer select-none active:scale-[0.97] duration-150 flex flex-col items-center justify-center text-center relative group"
      >
        <div class="absolute top-2 right-2 bg-gray-100 font-ui text-micro px-1.5 py-0.5 rounded text-brand-secondary font-bold tracking-tight uppercase shrink-0">
          Upcoming
        </div>
        
        <div class="w-10 h-10 rounded-full bg-brand-paper flex items-center justify-center mb-3 text-brand-secondary group-hover:text-brand-primary transition-colors duration-150">
          <component :is="tool.icon" :size="22" class="shrink-0" />
        </div>
        
        <span class="font-ui text-title font-bold text-brand-ink-strong">{{ tool.name }}</span>
        <span class="font-ui text-micro text-brand-secondary mt-1">{{ tool.desc }}</span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translate(-50%, -20px);
}
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
