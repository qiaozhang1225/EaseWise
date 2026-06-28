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
