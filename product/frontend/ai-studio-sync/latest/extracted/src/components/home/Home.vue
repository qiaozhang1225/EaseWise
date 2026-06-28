<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { getMockSummary } from '../../lib/api';
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
  RefreshCw,
  Sliders,
  X,
  Lock,
  Unlock,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'phone-click'): void;
  (e: 'bazi-click'): void;
  (e: 'meihua-click'): void;
}>();

const {
  state,
  bootstrapApp,
  reviewBasePointsCost,
  fourPillarsBasePointsCost,
  refreshAlmanac,
  loginWithPhonePassword,
} = useEaseWiseApp();

const toast = ref<string | null>(null);
const yiExpanded = ref(false);
const jiExpanded = ref(false);

const almanacFailed = ref(false);
const loadingAlmanac = ref(false);
const showSandbox = ref(false);
const submittingLogin = ref(false);

const demoAccounts = [
  { phone: '13800138000', label: '全量回归', tag: '20000分 / 丰满历史 / 全解', desc: '用于测试完整的报告展示、多条历史、大运及流年推演、完备的扣费账单。' },
  { phone: '13600136000', label: '低积分', tag: '120分 / 部分历史 / 触发充值', desc: '拥有120积分，刚好支持1次主评测，但余额不足以解锁单项或生成运势，可完美测试积分不足的拦截与引导官方微信客服群。' },
  { phone: '13500135000', label: '极低积分', tag: '30分 / 零历史 / 立即拦截', desc: '拥有30积分，低于任何基础评测扣减值。测试最基础的、无法开启号码/八字排盘的拦截弹窗和低额账单。' },
  { phone: '13900139000', label: '高分全新', tag: '3000分 / 零历史 / 首测', desc: '拥有3000分，历史为空。可用于测试完全空白状态下的首测、流式生成过程和空历史占位界面。' },
  { phone: '13700137000', label: '部分历史', tag: '20000分 / 混合解 / 高积分', desc: '混合历史状态，有1条手机及1条八字，部分细项已解，其他未解，可以测试部分解锁/解锁引导交互。' }
];

async function handleQuickLogin(demoPhone: string): Promise<void> {
  if (submittingLogin.value) return;
  submittingLogin.value = true;
  showToast(`正在极速登入：${demoPhone}...`);
  try {
    await loginWithPhonePassword(demoPhone, 'Easewise123!');
    showToast('登入成功！已自动加载测试账号的所有专属档案、积分与历史记录。');
    showSandbox.value = false;
  } catch (err: any) {
    if (err && (err.status === 408 || err.detail === 'request_timeout' || err.message?.includes('timeout'))) {
      showToast('Mock API 请求超时，请检查 VITE_API_BASE_URL 是否为 / 或空值');
    } else {
      showToast(`极速登入失败: ${err?.message || '网络错误'}`);
    }
  } finally {
    submittingLogin.value = false;
  }
}

const mockSummary = ref<any>(null);
const loadingMockSummary = ref(false);
const mockSummaryError = ref<string | null>(null);

const configuredApiBase = computed(() => String(import.meta.env.VITE_API_BASE_URL || '').trim());
const effectiveApiBase = computed(() => {
  const base = configuredApiBase.value.replace(/\/+$/, '');
  if (!base || base === '/api') {
    return '(空值 / 自动同源 /api/v1/... 和 /api/v1/mock/summary)';
  }
  return `${base}/v1/...`;
});

async function fetchMockSummary(): Promise<void> {
  loadingMockSummary.value = true;
  mockSummaryError.value = null;
  try {
    const summary = await getMockSummary();
    mockSummary.value = summary;
  } catch (err: any) {
    if (err && (err.status === 408 || err.detail === 'request_timeout' || err.message?.includes('timeout'))) {
      mockSummaryError.value = 'Mock API 请求超时，请检查 VITE_API_BASE_URL 是否为 / 或空值';
    } else {
      mockSummaryError.value = err?.message || '网络连接失败，请检查开发服务器';
    }
  } finally {
    loadingMockSummary.value = false;
  }
}

watch(
  () => state.almanac,
  (value) => {
    if (value) {
      almanacFailed.value = false;
    }
  },
  { immediate: true },
);

watch(showSandbox, (newVal) => {
  if (newVal) {
    void fetchMockSummary();
  }
});

async function handleRetryAlmanac(): Promise<void> {
  loadingAlmanac.value = true;
  almanacFailed.value = false;
  try {
    const res = await refreshAlmanac();
    if (!res) {
      almanacFailed.value = true;
      showToast('黄历加载失败：接口未返回有效数据');
    } else {
      showToast('黄历数据已成功加载与同步。');
    }
  } catch (err) {
    almanacFailed.value = true;
    showToast('黄历加载失败：请检查开发服务器连接');
  } finally {
    loadingAlmanac.value = false;
  }
}

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

onMounted(async () => {
  loadingAlmanac.value = true;
  almanacFailed.value = false;
  try {
    await bootstrapApp();
    if (!state.almanac) {
      almanacFailed.value = true;
    }
  } catch (err) {
    almanacFailed.value = true;
  } finally {
    loadingAlmanac.value = false;
  }
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

        <div v-if="almanacFailed" class="py-6 text-center space-y-3">
          <div class="mx-auto w-10 h-10 rounded-full bg-red-50 flex items-center justify-center text-red-500">
            <XCircle :size="20" />
          </div>
          <div class="space-y-1">
            <p class="text-xs font-bold text-gray-700">黄历数据加载失败</p>
            <p class="text-[10px] text-gray-400">请确保开发服务器正在运行并已连接</p>
          </div>
          <button
            type="button"
            @click="handleRetryAlmanac"
            class="px-4 py-1.5 bg-brand-primary text-white text-[11px] font-bold rounded-lg hover:bg-brand-primary-strong active:scale-95 transition-all outline-none border-none cursor-pointer"
          >
            {{ loadingAlmanac ? '正在加载...' : '重新加载' }}
          </button>
        </div>

        <div v-else-if="loadingAlmanac && !state.almanac" class="py-8 text-center space-y-3">
          <div class="mx-auto w-8 h-8 rounded-full border-2 border-brand-primary border-t-transparent animate-spin"></div>
          <p class="text-[11px] text-gray-400">正在对照古历黄道，排定吉凶宜忌...</p>
        </div>

        <div v-else>
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

    <!-- Sticky Activator Button -->
    <button
      type="button"
      @click="showSandbox = true"
      class="fixed bottom-6 right-6 z-40 bg-slate-900/95 hover:bg-slate-900 text-white font-sans text-[11px] font-bold px-4 py-2.5 rounded-full shadow-2xl flex items-center gap-2 cursor-pointer border border-white/10 active:scale-95 transition-all select-none backdrop-blur-md"
    >
      <Sliders :size="13" class="text-brand-accent animate-spin-slow" />
      <span>☯ H5测试沙盒</span>
    </button>

    <!-- Sandbox Overlay / Drawer -->
    <transition name="sandbox-fade">
      <div v-if="showSandbox" class="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-end justify-center" @click.self="showSandbox = false">
        <div class="bg-white rounded-t-[28px] shadow-2xl w-full max-w-md max-h-[85vh] flex flex-col overflow-hidden animate-slideUp">
            <!-- Header -->
            <div class="px-5 py-4 border-b border-gray-100 flex justify-between items-center bg-slate-50 shrink-0">
              <div class="flex items-center gap-2">
                <Sliders :size="15" class="text-slate-700" />
                <h3 class="font-sans text-[14px] font-black text-slate-800 leading-none">H5 Preview 测试沙盒</h3>
              </div>
              <button type="button" @click="showSandbox = false" class="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-gray-100 transition-colors border-none outline-none cursor-pointer">
                <X :size="16" />
              </button>
            </div>

            <!-- Content Area (Scrollable) -->
            <div class="p-5 overflow-y-auto space-y-5 text-left font-sans text-xs">
              <!-- Section 1: System Status & API Health -->
              <div class="space-y-2.5 bg-slate-50 p-3.5 rounded-xl border border-slate-200/60">
                <p class="font-bold text-slate-800 text-[11px] flex items-center gap-1.5 justify-between">
                  <span class="flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full" :class="mockSummary ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                    <span>系统状态与 API 健康度</span>
                  </span>
                  <span v-if="loadingMockSummary" class="text-[9px] text-gray-400 font-normal animate-pulse">正在同步...</span>
                </p>

                <!-- Config display -->
                <div class="bg-slate-100/70 p-2.5 rounded-lg text-[10px] space-y-1 font-mono text-gray-600 break-all border border-gray-200/20">
                  <div>配置值 (VITE_API_BASE_URL): <span class="font-bold text-slate-800">{{ configuredApiBase || '(未设置/空)' }}</span></div>
                  <div>有效请求前缀: <span class="font-bold text-slate-800">{{ effectiveApiBase }}</span></div>
                </div>

                <!-- Summary loading/error states -->
                <div v-if="loadingMockSummary && !mockSummary" class="bg-white p-3 rounded-lg border border-gray-100 text-center text-gray-400 py-4 flex items-center justify-center gap-1.5 text-[10px]">
                  <span class="w-3 h-3 border-2 border-brand-primary border-t-transparent rounded-full animate-spin"></span>
                  <span>正在检测 Mock API 健康摘要...</span>
                </div>

                <div v-else-if="mockSummaryError" class="bg-red-50 p-3 rounded-lg border border-red-100 text-red-600 text-[10.5px] leading-relaxed relative">
                  <div class="font-bold mb-1 flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                    <span>Mock API 连接失败</span>
                  </div>
                  <p class="font-sans font-bold whitespace-pre-line">{{ mockSummaryError }}</p>
                  <button @click="fetchMockSummary" type="button" class="mt-2 text-[10px] px-2.5 py-1 bg-red-100 text-red-800 font-bold rounded-md hover:bg-red-200 border-none outline-none cursor-pointer active:scale-95 transition-all">重新检测</button>
                </div>

                <div v-else-if="mockSummary" class="bg-emerald-50/50 p-3 rounded-lg border border-emerald-100/70 space-y-2 text-[10px]">
                  <div class="font-bold text-emerald-800 flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                    <span>Mock API 连接就绪 (Connected)</span>
                  </div>
                  <div class="grid grid-cols-2 gap-2 text-gray-600">
                    <div class="bg-white/80 p-1.5 rounded border border-gray-100 flex justify-between">
                      <span>黄历数据:</span>
                      <span class="font-bold text-emerald-600 font-sans">{{ mockSummary.almanac_available ? '可用' : '未载入' }}</span>
                    </div>
                    <div class="bg-white/80 p-1.5 rounded border border-gray-100 flex justify-between">
                      <span>系统配置:</span>
                      <span class="font-bold text-emerald-600 font-sans">{{ mockSummary.runtime_config_available ? '就绪' : '未载入' }}</span>
                    </div>
                    <div class="bg-white/80 p-1.5 rounded border border-gray-100 flex justify-between col-span-2">
                      <span>可供测试演示账号数:</span>
                      <span class="font-bold text-slate-800 font-mono">{{ mockSummary.demo_accounts?.length || 0 }} 个已预置</span>
                    </div>
                  </div>
                </div>

                <!-- Logged in state -->
                <div class="bg-white p-2.5 rounded-lg border border-gray-100 text-[10px] space-y-1">
                  <div class="flex justify-between items-center">
                    <span class="text-gray-400">当前账号 (Active Session)</span>
                    <span v-if="state.user" class="font-bold text-slate-700 font-mono">{{ state.user.phone }}</span>
                    <span class="text-gray-400" v-else>未登录 (访客模式)</span>
                  </div>
                  <div v-if="state.user" class="flex justify-between items-center border-t border-gray-50 pt-1 mt-1">
                    <span class="text-gray-400">可用积分余额</span>
                    <span class="font-bold text-brand-primary-strong font-mono">{{ points }} 分</span>
                  </div>
                </div>
              </div>

              <!-- Section 2: Demo Accounts Quick Switcher -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <p class="font-bold text-slate-800 text-[11px]">演示账号一键登录 (切换测试状态)</p>
                  <span class="text-[9px] text-gray-400">无需注册，极速同步</span>
                </div>

                <div class="space-y-2 max-h-[250px] overflow-y-auto pr-1">
                  <div
                    v-for="acc in demoAccounts"
                    :key="acc.phone"
                    class="p-3 bg-brand-paper hover:bg-brand-primary/5 rounded-xl border border-gray-100 hover:border-brand-primary/20 transition-all flex flex-col gap-1.5 relative group"
                  >
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-1.5">
                        <span class="font-mono font-bold text-slate-700 text-xs">{{ acc.phone }}</span>
                        <span class="text-[9.5px] text-brand-primary font-bold bg-brand-primary/5 px-2 py-0.5 rounded-full">{{ acc.label }}</span>
                      </div>
                      <button
                        type="button"
                        @click="handleQuickLogin(acc.phone)"
                        class="px-2.5 py-1 bg-brand-primary text-white text-[10px] font-bold rounded-lg hover:bg-brand-primary-strong cursor-pointer border-none transition-colors select-none outline-none flex items-center gap-1 shadow-sm active:scale-[0.98]"
                        :disabled="submittingLogin"
                      >
                        <Sliders :size="9" v-if="submittingLogin" class="animate-spin" />
                        <span>极速登入</span>
                      </button>
                    </div>
                    <p class="text-[10px] text-gray-400 font-mono leading-none font-bold">{{ acc.tag }}</p>
                    <p class="text-[10px] text-gray-500 leading-relaxed font-sans bg-white/60 p-2 rounded-lg border border-gray-50/50 mt-0.5">{{ acc.desc }}</p>
                  </div>
                </div>
              </div>

              <!-- Section 3: Diagnostic Hints / Testing States -->
              <div class="space-y-1.5 text-[10.5px] text-slate-600 bg-amber-50/70 p-3 rounded-xl border border-amber-200/50 leading-relaxed">
                <p class="font-bold text-slate-700 text-[11px] flex items-center gap-1">
                  <Sliders :size="12" class="text-amber-600 shrink-0" />
                  <span>测试状态诊断备忘</span>
                </p>
                <ul class="list-disc pl-4 space-y-1 font-sans">
                  <li><strong>空历史状态</strong>：登入 <code class="bg-amber-100 font-mono text-[10px] px-1 py-0.5 rounded">13900139000</code>，在号码评测/四柱记录中查看完全空白的精美引导页。</li>
                  <li><strong>低积分/充值引导</strong>：登入 <code class="bg-amber-100 font-mono text-[10px] px-1 py-0.5 rounded">13600136000</code>，点击号码/八字解锁或流派细项，观察积分不足弹框及点击进入客服微信群充值流程。</li>
                  <li><strong>未解与锁定状态</strong>：登入 <code class="bg-amber-100 font-mono text-[10px] px-1 py-0.5 rounded">13700137000</code>，打开其号码或八字解读历史，查看未解锁的项目与扣减解锁流程。</li>
                  <li><strong>全量报告展示</strong>：登入 <code class="bg-amber-100 font-mono text-[10px] px-1 py-0.5 rounded">13800138000</code>，查看完整的号码、命盘分析、大运及各细项。</li>
                </ul>
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

.sandbox-fade-enter-active,
.sandbox-fade-leave-active {
  transition: opacity 0.25s ease;
}
.sandbox-fade-enter-from,
.sandbox-fade-leave-to {
  opacity: 0;
}

.sandbox-slide-enter-active,
.sandbox-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}
.sandbox-slide-enter-from,
.sandbox-slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 8s linear infinite;
}
</style>
