<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  ArrowLeft, Calendar, Sparkles, Lock, Play, Square, Volume2,
  ChevronRight, CheckCircle2, Award, AlertTriangle, Loader2
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { useVoicePlayback } from '../../composables/useVoicePlayback';
import type { FourPillarsReviewRecord, Gender } from '../../types/api';

const emit = defineEmits<{
  (e: 'back'): void;
  (e: 'recharge-click'): void;
}>();

const {
  state, isGuestUser, fourPillarsBasePointsCost, fourPillarsAspectUnlockPointsCost,
  submitFourPillarsReview, unlockFourPillarsAspect, requestRegisteredUser, showToast, openCustomerServiceModal, humanizeError
} = useEaseWiseApp();

const toastMessage = ref<string | null>(null);

function triggerToast(msg: string) {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = null;
  }, 2200);
}

// Reuse voice playback, fetch voice configuration
const voice = useVoicePlayback({
  getAccessToken: () => state.accessToken,
  getVoiceConfig: () => (state.runtimeConfig?.modules as any)?.voice || (state.runtimeConfig?.modules as any)?.four_pillars?.voice,
  showToast: (msg) => triggerToast(msg),
});

const birthDateInput = ref('');
const birthTimeInput = ref('');
const genderInput = ref<Gender>('unknown');
const isSubmitting = ref(false);
const showHistory = ref(false);

const activeUnlockId = ref<string | null>(null);

const currentReview = computed<FourPillarsReviewRecord | null>(() => state.currentFourPillarsReview);
const historyList = computed(() => state.fourPillarsHistory || []);
const isRegistered = computed(() => !!state.accessToken);
const userPoints = computed(() => state.points?.balance ?? 0);

async function handleStartAnalysis() {
  if (!birthDateInput.value) {
    triggerToast('请先选择公历/农历出生日期！');
    return;
  }
  if (!birthTimeInput.value) {
    triggerToast('请设定出生具体时辰！');
    return;
  }
  if (genderInput.value === 'unknown') {
    triggerToast('请先选择命盘性别极向！');
    return;
  }

  // Auth checkpoint
  const authed = await requestRegisteredUser('四柱八字排盘评测');
  if (!authed) return;

  // Points checkpoint
  if (userPoints.value < fourPillarsBasePointsCost.value) {
    openCustomerServiceModal('points_insufficient', `八字排盘扣减：余额 ${userPoints.value} 分，需要 ${fourPillarsBasePointsCost.value} 分`);
    triggerToast('积分不足，已为您调出官方客服微信群！');
    return;
  }

  isSubmitting.value = true;
  voice.stop();
  try {
    const res = await submitFourPillarsReview({
      birth_date: birthDateInput.value,
      birth_time: birthTimeInput.value,
      gender: genderInput.value,
      is_lunar: false,
      timezone: 'Asia/Shanghai',
    });
    triggerToast('八字命造卦局排盘成功！已为您扣减体验积分。');
  } catch (err: any) {
    triggerToast(humanizeError(err) || '推算排盘出现阻碍，请稍后刷新重试');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleUnlockAspect(aspect: any) {
  if (!currentReview.value) return;

  const authed = await requestRegisteredUser(`解锁“${aspect.title}”八字专项`);
  if (!authed) return;

  if (userPoints.value < fourPillarsAspectUnlockPointsCost.value) {
    openCustomerServiceModal('points_insufficient', `八字专项解锁：余额 ${userPoints.value} 分，需要 ${fourPillarsAspectUnlockPointsCost.value} 分`);
    triggerToast('积分不足，正在为您唤出微信客服专区！');
    return;
  }

  activeUnlockId.value = aspect.aspect_key;
  try {
    await unlockFourPillarsAspect(currentReview.value.id, aspect.aspect_key);
    triggerToast(`八字专项「${aspect.title}」深度剖析解锁成功！`);
  } catch (err: any) {
    triggerToast(humanizeError(err) || '解锁专项解析失败');
  } finally {
    activeUnlockId.value = null;
  }
}

function handleSelectHistoryItem(historyItem: any) {
  state.currentFourPillarsReview = null;
  voice.stop();
  state.booting = true;
  state.refreshCurrentFourPillarsReview(historyItem.id)
    .then(() => {
      showHistory.value = false;
      triggerToast('历往八字报告载入成功！');
    })
    .catch(() => {
      triggerToast('加载往期八字报告失败，请重试');
    })
    .finally(() => {
      state.booting = false;
    });
}

function handleBackToForm() {
  voice.stop();
  state.currentFourPillarsReview = null;
}

function getWuxingColorClass(wuxing: string) {
  const mapping: Record<string, string> = {
    '金': 'bg-yellow-450 text-amber-900',
    '木': 'bg-emerald-500 text-white',
    '水': 'bg-blue-600 text-white',
    '火': 'bg-red-500 text-white',
    '土': 'bg-amber-700 text-white',
  };
  return mapping[wuxing] || 'bg-zinc-500 text-white';
}

function getWuxingBgClass(wuxing: string) {
  const mapping: Record<string, string> = {
    '金': 'bg-yellow-100',
    '木': 'bg-emerald-50',
    '水': 'bg-blue-50',
    '火': 'bg-red-50',
    '土': 'bg-amber-50',
  };
  return mapping[wuxing] || 'bg-zinc-100';
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left select-text">

    <!-- Toast Message Alert -->
    <transition name="fade">
      <div
        v-if="toastMessage"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[12.5px] shadow-lg font-medium flex items-center gap-2 max-w-[85%] whitespace-nowrap"
      >
        <Sparkles :size="14" class="text-brand-accent shrink-0" />
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- BACK BUTTON OR HISTORIC TOGGLE -->
    <div class="flex justify-between items-center mb-4 select-none">
      <button
        @click="currentReview ? handleBackToForm() : emit('back')"
        class="text-brand-ink-strong hover:text-brand-primary font-sans text-[12.5px] font-extrabold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none p-1 rounded hover:bg-zinc-100 transition-colors"
      >
        <ArrowLeft :size="16" />
        <span>返回首页</span>
      </button>

      <button
        v-if="!currentReview && isRegistered && historyList.length > 0"
        @click="showHistory = !showHistory"
        class="text-brand-primary hover:underline font-sans text-[12px] font-extrabold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none"
      >
        <Calendar :size="13" />
        <span>{{ showHistory ? '发起新排盘' : '历史命造记录' }}</span>
      </button>
    </div>

    <!-- STATE 1: SEED FORM -->
    <div v-if="!currentReview && !showHistory" class="space-y-4">
      <div class="bg-white rounded-3xl p-6 border border-brand-paper shadow-sm">
        <div class="flex items-center gap-2 mb-4 select-none">
          <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0">
            <Calendar :size="18" />
          </div>
          <div>
            <h2 class="font-serif text-[17px] font-bold text-brand-ink-strong leading-tight">八字排盘算盘</h2>
            <p class="font-sans text-[10.5px] text-brand-secondary/80 mt-0.5">
              输入您的出生年月日时，推演您的天干地支命盘、喜忌五行结构。
            </p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Birth Date -->
          <div class="space-y-1.5">
            <label class="font-sans text-[11px] font-bold text-brand-secondary block">出生日期 (公历/阳历)</label>
            <input
              v-model="birthDateInput"
              type="date"
              class="w-full bg-brand-paper/30 border border-gray-150 rounded-2xl px-4 py-3 outline-none font-sans text-[12.5px] text-brand-ink-strong focus:border-brand-primary/40 focus:bg-white transition-all"
            />
          </div>

          <!-- Birth Time -->
          <div class="space-y-1.5">
            <label class="font-sans text-[11px] font-bold text-brand-secondary block">出生时辰 (具体时间)</label>
            <input
              v-model="birthTimeInput"
              type="time"
              class="w-full bg-brand-paper/30 border border-gray-150 rounded-2xl px-4 py-3 outline-none font-sans text-[12.5px] text-brand-ink-strong focus:border-brand-primary/40 focus:bg-white transition-all"
            />
          </div>

          <!-- Gender selection -->
          <div class="space-y-1.5 select-none">
            <label class="font-sans text-[11px] font-bold text-brand-secondary block">命造极向（性别）</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                @click="genderInput = 'male'"
                class="border rounded-2xl py-3 cursor-pointer text-[12.5px] font-sans font-extrabold transition-all duration-150 outline-none flex items-center justify-center gap-1.5"
                :class="genderInput === 'male'
                  ? 'bg-brand-primary border-brand-primary text-white shadow-sm'
                  : 'bg-transparent border-gray-150 text-brand-secondary hover:bg-slate-50'"
              >
                <span>乾造（男命）</span>
              </button>
              <button
                @click="genderInput = 'female'"
                class="border rounded-2xl py-3 cursor-pointer text-[12.5px] font-sans font-extrabold transition-all duration-150 outline-none flex items-center justify-center gap-1.5"
                :class="genderInput === 'female'
                  ? 'bg-brand-primary border-brand-primary text-white shadow-sm'
                  : 'bg-transparent border-gray-150 text-brand-secondary hover:bg-slate-50'"
              >
                <span>坤造（女命）</span>
              </button>
            </div>
          </div>

          <!-- Submit trigger -->
          <button
            @click="handleStartAnalysis()"
            :disabled="isSubmitting"
            class="w-full bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3.5 rounded-2xl cursor-pointer font-sans text-[13px] font-extrabold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-2 select-none"
          >
            <Loader2 v-if="isSubmitting" class="animate-spin text-white" :size="16" />
            <span>{{ isSubmitting ? '正在对照古历黄道，排定八字盘面...' : `消耗 ${fourPillarsBasePointsCost} 积分配出命盘` }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- STATE 2: HISTORIC LIST VIEW -->
    <div v-else-if="showHistory" class="space-y-3">
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <h3 class="font-serif text-[15px] font-black text-brand-ink-strong mb-3.5 select-none flex items-center gap-1.5">
          <Calendar :size="15" />
          <span>历次命盘推演记录</span>
        </h3>

        <div v-if="historyList.length === 0" class="py-12 text-center select-none text-zinc-400 font-sans text-[12px]">
          暂无任何历史命盘排盘记录
        </div>
        <div v-else class="space-y-2.5">
          <button
            v-for="item in historyList"
            :key="item.id"
            @click="handleSelectHistoryItem(item)"
            class="w-full bg-brand-paper/40 hover:bg-brand-paper/80 border border-gray-100 rounded-2xl p-3.5 text-left flex justify-between items-center transition-colors cursor-pointer outline-none select-none group"
          >
            <div class="space-y-1.5 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-serif text-[13.5px] font-bold text-brand-ink-strong tracking-wide">{{ item.birth_date }}</span>
                <span class="px-1.5 py-0.5 bg-brand-primary/10 rounded font-sans text-[9px] font-extrabold text-brand-primary-strong">
                  {{ item.gender === 'male' ? '乾造（男）' : '坤造（女）' }}
                </span>
              </div>
              <p class="font-sans text-[10.5px] text-brand-secondary/80">
                测算时间：{{ new Date(item.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) }}
              </p>
            </div>

            <div class="flex items-center gap-1.5 shrink-0 text-brand-primary font-sans text-[11px] font-extrabold">
              <span>阅命</span>
              <ChevronRight :size="14" class="group-hover:translate-x-0.5 transition-transform" />
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- STATE 3: COMPLETE REPORT -->
    <div v-else-if="currentReview" class="space-y-4 animate-fadeIn">

      <!-- Top Title Snapshot -->
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <div class="flex justify-between items-start gap-4">
          <div class="space-y-1.5">
            <div class="flex items-center gap-2">
              <h3 class="font-serif text-[16px] font-black text-brand-ink-strong">
                {{ currentReview.gender === 'male' ? '乾造命盘' : '坤造命盘' }}
              </h3>
              <span class="px-1.5 py-0.5 bg-brand-primary/10 rounded font-sans text-[9px] font-extrabold text-brand-primary-strong">
                {{ currentReview.gender === 'male' ? '男命' : '女命' }}
              </span>
            </div>
            <p class="font-sans text-[11px] text-brand-secondary leading-relaxed">
              公历诞辰：{{ currentReview.birth_date }} {{ currentReview.birth_time }}
            </p>
          </div>

          <div class="text-right select-none">
            <span class="text-[9.5px] text-brand-secondary font-extrabold block leading-none">命盘吉数</span>
            <span class="font-serif text-[32px] font-black text-brand-primary-strong leading-none mt-1.5 inline-block">{{ currentReview.score }}</span>
          </div>
        </div>
      </div>

      <!-- THE FOUR PILLARS CHINESE STEMS AND BRANCHES GRID (四柱天干地支) -->
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm select-none">
        <span class="font-serif text-[13px] font-black text-brand-secondary block mb-3.5 border-b border-gray-150 pb-1.5">
          四柱八字排盘干支（年、月、日、时）
        </span>

        <div class="grid grid-cols-4 gap-2 text-center">
          <!-- Year Pillar -->
          <div class="bg-brand-paper/50 rounded-2xl p-3 border">
            <span class="text-[10px] text-zinc-400 block mb-1">年柱</span>
            <div class="font-serif text-[18px] font-black text-brand-ink-strong space-y-1.5">
              <div class="bg-amber-100 rounded-md py-1 text-amber-900 border border-amber-200/50">{{ currentReview.ganzhi_year.slice(0, 1) }}</div>
              <div class="bg-emerald-100 rounded-md py-1 text-emerald-900 border border-emerald-200/50">{{ currentReview.ganzhi_year.slice(1, 2) }}</div>
            </div>
          </div>

          <!-- Month Pillar -->
          <div class="bg-brand-paper/50 rounded-2xl p-3 border">
            <span class="text-[10px] text-zinc-400 block mb-1">月柱</span>
            <div class="font-serif text-[18px] font-black text-brand-ink-strong space-y-1.5">
              <div class="bg-amber-100 rounded-md py-1 text-amber-900 border border-amber-200/50">{{ currentReview.ganzhi_month.slice(0, 1) }}</div>
              <div class="bg-emerald-100 rounded-md py-1 text-emerald-900 border border-emerald-200/50">{{ currentReview.ganzhi_month.slice(1, 2) }}</div>
            </div>
          </div>

          <!-- Day Pillar -->
          <div class="bg-brand-primary/5 rounded-2xl p-3 border border-brand-primary/30 relative">
            <div class="absolute -top-1.5 left-1/2 -translate-x-1/2 bg-brand-primary text-white font-sans text-[8px] font-extrabold px-1 rounded shadow-sm">
              日主
            </div>
            <span class="text-[10px] text-zinc-400 block mb-1">日柱</span>
            <div class="font-serif text-[18px] font-black text-brand-ink-strong space-y-1.5">
              <div class="bg-amber-100 rounded-md py-1 text-amber-900 border border-amber-200/50">{{ currentReview.ganzhi_day.slice(0, 1) }}</div>
              <div class="bg-emerald-100 rounded-md py-1 text-emerald-900 border border-emerald-200/50">{{ currentReview.ganzhi_day.slice(1, 2) }}</div>
            </div>
          </div>

          <!-- Hour Pillar -->
          <div class="bg-brand-paper/50 rounded-2xl p-3 border">
            <span class="text-[10px] text-zinc-400 block mb-1">时柱</span>
            <div class="font-serif text-[18px] font-black text-brand-ink-strong space-y-1.5">
              <div class="bg-amber-100 rounded-md py-1 text-amber-900 border border-amber-200/50">{{ currentReview.ganzhi_hour.slice(0, 1) }}</div>
              <div class="bg-emerald-100 rounded-md py-1 text-emerald-900 border border-emerald-200/50">{{ currentReview.ganzhi_hour.slice(1, 2) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- FIVE ELEMENTS (WOOD, FIRE, EARTH, METAL, WATER) BAR CHART GRID -->
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm select-none">
        <span class="font-serif text-[13px] font-black text-brand-secondary block mb-3 pb-1.5 border-b">
          先天五行能量比例平衡表
        </span>

        <div class="space-y-3">
          <div
            v-for="elem in currentReview.wuxing_analysis"
            :key="elem.wuxing"
            class="flex items-center gap-3"
          >
            <!-- Wuxing Symbol text -->
            <span class="font-serif text-[13px] font-black w-5 text-brand-ink-strong shrink-0 text-center">{{ elem.wuxing }}</span>

            <!-- Progress representation bar -->
            <div class="flex-1 h-5 rounded-lg overflow-hidden flex items-center relative" :class="getWuxingBgClass(elem.wuxing)">
              <div
                class="h-full rounded-r-lg transition-all duration-500 ease-out flex items-center justify-end pr-2 font-mono text-[9.5px] font-bold"
                :class="getWuxingColorClass(elem.wuxing)"
                :style="{ width: `${elem.percentage}%` }"
              >
                <!-- Percentage overlay when bar is wide enough -->
                <span v-if="elem.percentage >= 15">{{ elem.percentage }}%</span>
              </div>
              <span v-if="elem.percentage < 15" class="absolute left-2 font-mono text-[9.5px] font-bold text-zinc-500">{{ elem.percentage }}%</span>
            </div>

            <!-- Strength descriptor -->
            <span class="font-sans text-[10px] font-bold w-12 text-right text-brand-secondary shrink-0">
              {{ elem.percentage >= 30 ? '过盛' : (elem.percentage <= 10 ? '缺失' : '平衡') }}
            </span>
          </div>
        </div>
      </div>

      <!-- THE CORE DAY MASTER PERSONALITY PROFILE -->
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <span class="font-serif text-[14.5px] font-black text-brand-ink-strong block mb-2.5 pb-2 border-b">
          日主格局断语：{{ currentReview.day_master_detail?.verdict || '推演排盘完毕' }}
        </span>

        <p class="font-sans text-[12px] leading-relaxed text-brand-ink-strong font-medium whitespace-pre-wrap select-text">
          {{ currentReview.day_master_detail?.content }}
        </p>
      </div>

      <!-- PREMIUM UNLOCKABLE 4 CORE ASPECTS -->
      <div class="space-y-3">
        <h3 class="font-serif text-[15px] font-black text-brand-ink-strong mb-1 select-none flex items-center gap-1.5">
          <Award :size="15" />
          <span>八字命盘 4 项尊享高级专项解读</span>
        </h3>

        <div class="space-y-3">
          <div
            v-for="aspect in currentReview.aspects"
            :key="aspect.aspect_key"
            class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm flex flex-col transition-all duration-200"
            :class="!aspect.is_unlocked ? 'border-dashed border-gray-200 bg-gray-50/50' : 'border-gray-100 bg-white'"
          >
            <div class="flex justify-between items-start gap-4">
              <div class="space-y-1.5">
                <span class="font-serif text-[14px] font-black text-brand-ink-strong leading-none flex items-center gap-1.5">
                  {{ aspect.title }}
                  <span
                    v-if="aspect.is_unlocked"
                    class="bg-brand-primary/10 text-brand-primary-strong text-[9px] font-extrabold px-1.5 py-0.5 rounded select-none font-sans"
                  >
                    已开启
                  </span>
                </span>
                <p class="font-sans text-[11px] text-brand-secondary/80 leading-relaxed">
                  {{ aspect.description }}
                </p>
              </div>

              <!-- Unlock Status Button -->
              <div class="shrink-0 select-none">
                <button
                  v-if="!aspect.is_unlocked"
                  @click="handleUnlockAspect(aspect)"
                  :disabled="activeUnlockId !== null"
                  class="bg-brand-primary hover:bg-brand-primary/95 text-white py-2 px-3 rounded-xl font-sans text-[11px] font-bold shadow-sm active:scale-95 transition-all outline-none border-none flex items-center gap-1 cursor-pointer disabled:bg-zinc-150 disabled:text-zinc-400"
                >
                  <Loader2 v-if="activeUnlockId === aspect.aspect_key" class="animate-spin text-white" :size="11" />
                  <Lock v-else :size="11" />
                  <span>{{ activeUnlockId === aspect.aspect_key ? '正在开启...' : `${fourPillarsAspectUnlockPointsCost} 积分解锁` }}</span>
                </button>
              </div>
            </div>

            <!-- UNLOCKED CONTENT DETAIL -->
            <div
              v-if="aspect.is_unlocked"
              class="mt-4 pt-3.5 border-t border-gray-100 flex flex-col gap-3 font-sans text-[12px] leading-relaxed select-text"
            >
              <p class="text-brand-ink-strong whitespace-pre-wrap select-text font-medium bg-brand-paper/20 rounded-2xl p-4 border border-thin">
                {{ aspect.content }}
              </p>

              <div v-if="aspect.risk" class="bg-red-50/50 border border-red-100 rounded-2xl p-4 flex items-start gap-2.5">
                <AlertTriangle :size="14" class="text-red-500 shrink-0 mt-0.5 animate-pulse" />
                <div class="space-y-0.5">
                  <span class="font-bold text-red-900">格局警示：</span>
                  <p class="text-red-800 font-medium">{{ aspect.risk }}</p>
                </div>
              </div>
            </div>

            <!-- LOCKED OVERLAY -->
            <div
              v-else
              class="mt-4 py-6 border-t border-dashed border-gray-200 text-center select-none flex flex-col items-center justify-center"
            >
              <Lock :size="20" class="text-brand-secondary/40 mb-2 shrink-0" />
              <p class="font-sans text-[11px] text-brand-secondary/70">
                本项属于四柱八字深度命造天机，请使用积分进行解锁。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
