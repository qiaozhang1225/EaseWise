<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  ArrowLeft, RefreshCw, Sparkles, ShieldAlert, Play, Square,
  Volume2, Lock, FileText, ChevronRight, CheckCircle2, Award, AlertTriangle, Loader2
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { useVoicePlayback } from '../../composables/useVoicePlayback';
import type { ReviewRecord, ReviewAspect, Gender } from '../../types/api';

const emit = defineEmits<{
  (e: 'back'): void;
  (e: 'recharge-click'): void;
}>();

const {
  state, isGuestUser, reviewBasePointsCost, aspectUnlockPointsCost,
  submitPhoneReview, unlockAspect, requestRegisteredUser, showToast, openCustomerServiceModal, humanizeError
} = useEaseWiseApp();

const toastMessage = ref<string | null>(null);

function triggerToast(msg: string) {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = null;
  }, 2200);
}

const voice = useVoicePlayback({
  getAccessToken: () => state.accessToken,
  getVoiceConfig: () => (state.runtimeConfig?.modules as any)?.voice || (state.runtimeConfig?.modules as any)?.phone_review?.voice,
  showToast: (msg) => triggerToast(msg),
});

const phoneInput = ref('');
const genderInput = ref<Gender>('unknown');
const isSubmitting = ref(false);
const showHistory = ref(false);

const activeUnlockId = ref<string | null>(null);
const activeNarratingAspect = ref<string | null>(null);

const currentReview = computed<ReviewRecord | null>(() => state.currentReview);
const historyList = computed(() => state.reviewHistory || []);
const isRegistered = computed(() => !!state.accessToken);
const userPoints = computed(() => state.points?.balance ?? 0);

onMounted(() => {
  // Try priming voice on first click inside app to satisfy browser auto play policies
  if (typeof window !== 'undefined') {
    window.addEventListener('click', () => {
      voice.primeAudioSession();
    }, { once: true });
  }
});

async function handleStartAnalysis() {
  const normalized = phoneInput.value.replace(/\D/g, '');
  if (!/^1[3-9]\d{9}$/.test(normalized)) {
    triggerToast('请输入 11 位正确的中国大陆手机号码！');
    return;
  }
  if (genderInput.value === 'unknown') {
    triggerToast('请先选择极向性别！');
    return;
  }

  // Pre-check registration
  const authed = await requestRegisteredUser('手机号数字奇门评测');
  if (!authed) {
    return;
  }

  // Check points balance
  if (userPoints.value < reviewBasePointsCost.value) {
    openCustomerServiceModal('points_insufficient', `用户评测扣减：余额 ${userPoints.value} 分，需要 ${reviewBasePointsCost.value} 分`);
    triggerToast('账户积分不足，正在为您唤出客服充值服务！');
    return;
  }

  isSubmitting.value = true;
  voice.stop();
  try {
    const res = await submitPhoneReview({
      phone: normalized,
      gender: genderInput.value,
      include_markdown: true,
    });
    triggerToast('恭喜！评测盘局推演成功！');
    // Start reading introduction
    setTimeout(() => {
      if (voice.autoplayEnabled.value) {
        void voice.speakPhoneSummary(res, { auto: true });
      }
    }, 1000);
  } catch (err: any) {
    triggerToast(humanizeError(err) || '推算天机有些阻碍，请稍后刷新重试');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleUnlockAspect(aspect: ReviewAspect) {
  if (!currentReview.value) return;

  const authed = await requestRegisteredUser(`解锁“${aspect.title}”专项`);
  if (!authed) return;

  if (userPoints.value < aspectUnlockPointsCost.value) {
    openCustomerServiceModal('points_insufficient', `专项解锁扣减：余额 ${userPoints.value} 分，需要 ${aspectUnlockPointsCost.value} 分`);
    triggerToast('积分不足，已为您调出官方客服微信群！');
    return;
  }

  activeUnlockId.value = aspect.aspect_key;
  try {
    const updatedReview = await unlockAspect(currentReview.value.id, aspect.aspect_key);
    triggerToast(`专项「${aspect.title}」解读成功解锁！`);

    // Auto voice output
    const refreshedAspect = updatedReview.aspects.find(a => a.aspect_key === aspect.aspect_key);
    if (refreshedAspect && voice.autoplayEnabled.value) {
      setTimeout(() => {
        void voice.speakAspect(updatedReview, refreshedAspect, { auto: true });
      }, 500);
    }
  } catch (err: any) {
    triggerToast(humanizeError(err) || '解锁专项失败');
  } finally {
    activeUnlockId.value = null;
  }
}

function handleSelectHistoryItem(historyItem: any) {
  state.currentReview = null;
  voice.stop();
  state.booting = true;
  state.refreshCurrentReview(historyItem.id)
    .then((res) => {
      showHistory.value = false;
      triggerToast('历往报告载入成功！');
      if (voice.autoplayEnabled.value) {
        void voice.speakPhoneSummary(res, { auto: true });
      }
    })
    .catch((err) => {
      triggerToast('加载往期报告失败，请重试');
    })
    .finally(() => {
      state.booting = false;
    });
}

function handleBackToForm() {
  voice.stop();
  state.currentReview = null;
}

function toggleVoiceOverall() {
  voice.setEnabled(!voice.enabled.value);
  triggerToast(voice.enabled.value ? '语音朗读服务：已开启' : '语音朗读服务：已静音关闭');
}

function toggleAutoplayOverall() {
  voice.setAutoplayEnabled(!voice.autoplayEnabled.value);
  triggerToast(voice.autoplayEnabled.value ? '解锁后自动播报：开启' : '解锁后自动播报：关闭');
}

function speakSummary() {
  if (!currentReview.value) return;
  if (voice.currentKey.value?.startsWith('phone_summary')) {
    voice.stop();
  } else {
    void voice.speakPhoneSummary(currentReview.value);
  }
}

function speakStability() {
  if (!currentReview.value) return;
  if (voice.currentKey.value?.startsWith('phone_stability')) {
    voice.stop();
  } else {
    void voice.speakStability(currentReview.value);
  }
}

function speakSingleAspect(aspect: ReviewAspect) {
  if (!currentReview.value) return;
  const currentKeyExpected = `phone_aspect:${currentReview.value.id}:${aspect.aspect_key}`;
  if (voice.currentKey.value === currentKeyExpected) {
    voice.stop();
  } else {
    void voice.speakAspect(currentReview.value, aspect);
  }
}

const formatAspectTitle = (title: string) => {
  return title.replace(/专项\s*$/u, '').trim();
};
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left select-text">

    <!-- Action Toast -->
    <transition name="fade">
      <div
        v-if="toastMessage"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[12.5px] shadow-lg font-medium flex items-center gap-2 max-w-[85%] whitespace-nowrap"
      >
        <Sparkles :size="14" class="text-brand-accent shrink-0" />
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- BACK BUTTON OR BAR -->
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
        <FileText :size="13" />
        <span>{{ showHistory ? '发起新推演' : '查看过往报告' }}</span>
      </button>
    </div>

    <!-- MAIN CARD: FORM STATE -->
    <div v-if="!currentReview && !showHistory" class="space-y-4">
      <div class="bg-white rounded-3xl p-6 border border-brand-paper shadow-sm">
        <div class="flex items-center gap-2 mb-4 select-none">
          <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0">
            <Sparkles :size="18" />
          </div>
          <div>
            <h2 class="font-serif text-[17px] font-bold text-brand-ink-strong leading-tight">数字奇门手机排盘</h2>
            <p class="font-sans text-[10.5px] text-brand-secondary/80 mt-0.5">
              输入您的 11 位手机号码与极向性别，智能推演出 13 项深层运势。
            </p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Phone Number field -->
          <div class="space-y-1.5">
            <label class="font-sans text-[11px] font-bold text-brand-secondary block">手机号（大陆 11 位）</label>
            <input
              v-model="phoneInput"
              type="tel"
              maxlength="11"
              placeholder="请输入您要评测的手机号码..."
              class="w-full bg-brand-paper/30 border border-gray-150 rounded-2xl px-4 py-3.5 outline-none font-sans text-[13px] text-brand-ink-strong focus:border-brand-primary/40 focus:bg-white transition-all"
              @keyup.enter="handleStartAnalysis()"
            />
          </div>

          <!-- Gender Choice field -->
          <div class="space-y-1.5">
            <label class="font-sans text-[11px] font-bold text-brand-secondary block select-none">极向属性（性别）</label>
            <div class="grid grid-cols-2 gap-3 select-none">
              <button
                @click="genderInput = 'male'"
                class="border rounded-2xl py-3 cursor-pointer text-[12.5px] font-sans font-extrabold transition-all duration-150 outline-none flex items-center justify-center gap-1.5"
                :class="genderInput === 'male'
                  ? 'bg-brand-primary border-brand-primary text-white shadow-sm'
                  : 'bg-transparent border-gray-150 text-brand-secondary hover:bg-slate-50'"
              >
                <span>乾造（男）</span>
              </button>
              <button
                @click="genderInput = 'female'"
                class="border rounded-2xl py-3 cursor-pointer text-[12.5px] font-sans font-extrabold transition-all duration-150 outline-none flex items-center justify-center gap-1.5"
                :class="genderInput === 'female'
                  ? 'bg-brand-primary border-brand-primary text-white shadow-sm'
                  : 'bg-transparent border-gray-150 text-brand-secondary hover:bg-slate-50'"
              >
                <span>坤造（女）</span>
              </button>
            </div>
          </div>

          <!-- Submit button -->
          <button
            @click="handleStartAnalysis()"
            :disabled="isSubmitting"
            class="w-full bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3.5 rounded-2xl cursor-pointer font-sans text-[13px] font-extrabold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-2 select-none"
          >
            <Loader2 v-if="isSubmitting" class="animate-spin text-white" :size="16" />
            <span>{{ isSubmitting ? '盘局卦理推演中，请静候...' : `扣减 ${reviewBasePointsCost} 积分并开启评测` }}</span>
          </button>
        </div>
      </div>

      <!-- Quick Warnings banner -->
      <div class="bg-amber-50 rounded-2xl p-4 border border-amber-100 font-sans text-[11px] text-zinc-600/90 leading-relaxed select-none">
        <div class="flex gap-2 items-start">
          <ShieldAlert :size="14" class="text-brand-gold-fixed shrink-0 mt-0.5" />
          <div>
            <span class="font-bold text-zinc-800">修持声明：</span>
            <span>由于奇门九星卦象和天干地支推演复杂度较高，单次报告生成时间需要 3-5 秒，请勿在提交后关闭或刷新页面。</span>
          </div>
        </div>
      </div>
    </div>

    <!-- STATE 2: HISTORIC LIST VIEW -->
    <div v-else-if="showHistory" class="space-y-3">
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <h3 class="font-serif text-[15px] font-black text-brand-ink-strong mb-3.5 select-none flex items-center gap-1.5">
          <FileText :size="15" />
          <span>往期排盘评测记录</span>
        </h3>

        <div v-if="historyList.length === 0" class="py-12 text-center select-none text-zinc-400 font-sans text-[12px]">
          暂无任何往期评测报告
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
                <span class="font-mono text-[13.5px] font-bold text-brand-ink-strong tracking-wide">{{ item.masked_phone }}</span>
                <span class="px-1.5 py-0.5 bg-brand-primary/10 rounded font-sans text-[9px] font-extrabold text-brand-primary-strong">
                  {{ item.gender === 'male' ? '乾造（男）' : '坤造（女）' }}
                </span>
              </div>
              <p class="font-sans text-[10.5px] text-brand-secondary/80">
                评测时间：{{ new Date(item.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) }}
              </p>
            </div>

            <div class="flex items-center gap-1.5 shrink-0 text-brand-primary font-sans text-[11px] font-extrabold">
              <span>阅卷</span>
              <ChevronRight :size="14" class="group-hover:translate-x-0.5 transition-transform" />
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- STATE 3: DETAILED RENDER REPORT -->
    <div v-else-if="currentReview" class="space-y-4 animate-fadeIn">

      <!-- Top Score Summary Banner -->
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <div class="flex justify-between items-start gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-mono text-[18px] font-black text-brand-ink-strong tracking-wider select-all">{{ currentReview.masked_phone }}</span>
              <span class="px-1.5 py-0.5 bg-brand-primary/10 rounded font-sans text-[9px] font-extrabold text-brand-primary-strong select-none">
                {{ currentReview.gender === 'male' ? '乾造（男）' : '坤造（女）' }}
              </span>
            </div>
            <p class="font-sans text-[10.5px] text-brand-secondary">
              测算卦历：{{ new Date(currentReview.created_at).toLocaleString() }}
            </p>
          </div>

          <!-- Metaphysical Custom Dial Score -->
          <div class="flex flex-col items-center shrink-0 select-none">
            <span class="font-sans text-[9.5px] text-brand-secondary font-extrabold">易数磁场得分</span>
            <span class="font-serif text-[32px] font-black text-brand-primary-strong leading-none mt-1">{{ currentReview.score }}</span>
          </div>
        </div>

        <!-- Global Voice Synthesis Toolbar Panel -->
        <div class="mt-4 pt-3.5 border-t border-gray-100 flex flex-wrap gap-2.5 items-center select-none justify-between">
          <div class="flex items-center gap-2">
            <button
              @click="toggleVoiceOverall"
              class="px-2.5 py-1.5 rounded-lg font-sans text-[10.5px] font-extrabold cursor-pointer border transition-colors outline-none flex items-center gap-1"
              :class="voice.enabled.value
                ? 'bg-brand-primary/10 border-brand-primary/20 text-brand-primary'
                : 'bg-zinc-50 border-gray-150 text-zinc-400 hover:bg-zinc-100'"
            >
              <Volume2 :size="12" />
              <span>{{ voice.enabled.value ? '语音朗读中' : '语音静音中' }}</span>
            </button>
            <button
              @click="toggleAutoplayOverall"
              class="px-2.5 py-1.5 rounded-lg font-sans text-[10.5px] font-extrabold cursor-pointer border transition-colors outline-none flex items-center gap-1"
              :class="voice.autoplayEnabled.value
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                : 'bg-zinc-50 border-gray-150 text-zinc-400 hover:bg-zinc-100'"
            >
              <span>解锁后自动播报: {{ voice.autoplayEnabled.value ? '开' : '关' }}</span>
            </button>
          </div>

          <!-- Overall Summary speaker button -->
          <button
            @click="speakSummary"
            class="px-3 py-1.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-sans text-[11px] font-bold rounded-lg cursor-pointer border-none shadow-sm active:scale-95 transition-all flex items-center gap-1 outline-none"
          >
            <span v-if="voice.currentKey.value?.startsWith('phone_summary')">暂停评述</span>
            <span v-else>收听评述</span>
            <Play v-if="!voice.currentKey.value?.startsWith('phone_summary')" :size="10" />
            <Square v-else :size="10" />
          </button>
        </div>
      </div>

      <!-- THE 13 SPECIFIC DETAILED ASPECTS GRID -->
      <div class="space-y-3">
        <h3 class="font-serif text-[15px] font-black text-brand-ink-strong mb-1 select-none flex items-center gap-1.5">
          <Award :size="15" />
          <span>数字奇门 13 项大盘解读</span>
        </h3>

        <div class="space-y-3">
          <div
            v-for="aspect in currentReview.aspects"
            :key="aspect.aspect_key"
            class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm flex flex-col transition-all duration-200"
            :class="!aspect.is_unlocked ? 'border-dashed border-gray-200 bg-gray-50/50' : 'border-gray-100 bg-white'"
          >
            <!-- Header aspect card -->
            <div class="flex justify-between items-start gap-4">
              <div class="space-y-1.5">
                <span class="font-serif text-[14.5px] font-black text-brand-ink-strong leading-none flex items-center gap-1.5">
                  {{ aspect.title }}
                  <span
                    v-if="aspect.is_unlocked"
                    class="bg-brand-primary/10 text-brand-primary-strong text-[9px] font-extrabold px-1.5 py-0.5 rounded select-none font-sans"
                  >
                    已解锁
                  </span>
                </span>
                <p class="font-sans text-[11px] text-brand-secondary/80 leading-relaxed">
                  {{ aspect.description }}
                </p>
              </div>

              <!-- Unlock Status Action Button -->
              <div class="shrink-0 select-none">
                <button
                  v-if="!aspect.is_unlocked"
                  @click="handleUnlockAspect(aspect)"
                  :disabled="activeUnlockId !== null"
                  class="bg-brand-primary hover:bg-brand-primary/95 text-white py-2 px-3 rounded-xl font-sans text-[11px] font-bold shadow-sm active:scale-95 transition-all outline-none border-none flex items-center gap-1 cursor-pointer disabled:bg-zinc-150 disabled:text-zinc-400"
                >
                  <Loader2 v-if="activeUnlockId === aspect.aspect_key" class="animate-spin text-white" :size="11" />
                  <Lock v-else :size="11" />
                  <span>{{ activeUnlockId === aspect.aspect_key ? '正在解锁...' : `${aspectUnlockPointsCost} 积分解锁` }}</span>
                </button>

                <!-- Voice speaker inside individual aspect card -->
                <button
                  v-else
                  @click="speakSingleAspect(aspect)"
                  class="p-2 rounded-xl border text-brand-primary transition-all duration-150 cursor-pointer flex items-center justify-center outline-none"
                  :class="voice.currentKey.value === `phone_aspect:${currentReview.id}:${aspect.aspect_key}`
                    ? 'bg-brand-primary text-white border-brand-primary'
                    : 'bg-brand-paper border-brand-primary/20 hover:bg-brand-primary/5 text-brand-primary'"
                  :title="voice.currentKey.value === `phone_aspect:${currentReview.id}:${aspect.aspect_key}` ? '暂停播放' : '播放该专项语音'"
                >
                  <Square v-if="voice.currentKey.value === `phone_aspect:${currentReview.id}:${aspect.aspect_key}`" :size="13" />
                  <Play v-else :size="13" />
                </button>
              </div>
            </div>

            <!-- UNLOCKED RICH TEXT INTERFACE -->
            <div
              v-if="aspect.is_unlocked"
              class="mt-4 pt-3.5 border-t border-gray-100 flex flex-col gap-3 font-sans text-[12px] leading-relaxed select-text"
            >
              <!-- Content Detail description -->
              <p class="text-brand-ink-strong whitespace-pre-wrap select-text font-medium bg-brand-paper/20 rounded-2xl p-4 border border-thin">
                {{ aspect.content }}
              </p>

              <!-- Optional Risk warning alert box -->
              <div v-if="aspect.risk" class="bg-red-50/50 border border-red-100 rounded-2xl p-4 flex items-start gap-2.5">
                <AlertTriangle :size="14" class="text-red-500 shrink-0 mt-0.5 animate-pulse" />
                <div class="space-y-0.5">
                  <span class="font-bold text-red-900">天星风险警示：</span>
                  <p class="text-red-800 font-medium">{{ aspect.risk }}</p>
                </div>
              </div>
            </div>

            <!-- LOCKED VISUAL COVER -->
            <div
              v-else
              class="mt-4 py-6 border-t border-dashed border-gray-200 text-center select-none flex flex-col items-center justify-center"
            >
              <Lock :size="20" class="text-brand-secondary/40 mb-2 shrink-0" />
              <p class="font-sans text-[11px] text-brand-secondary/70">
                本项属于数字奇门更深维度的天机，请使用积分进行解锁。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- CORE STABILITY & REMARK SECTION -->
      <div class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <div class="flex justify-between items-start gap-4 mb-3">
          <div class="space-y-0.5">
            <span class="font-serif text-[15px] font-black text-brand-ink-strong">长期数字磁场定论</span>
            <p class="font-sans text-[10.5px] text-brand-secondary/80">此号码是否适宜长期持有及能量修养。</p>
          </div>

          <button
            @click="speakStability"
            class="px-3 py-1.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-sans text-[10.5px] font-bold rounded-lg cursor-pointer border-none shadow-sm active:scale-95 transition-all flex items-center gap-1 outline-none select-none"
          >
            <span v-if="voice.currentKey.value?.startsWith('phone_stability')">暂停</span>
            <span v-else>播放</span>
            <Play v-if="!voice.currentKey.value?.startsWith('phone_stability')" :size="9" />
            <Square v-else :size="9" />
          </button>
        </div>

        <div class="bg-brand-paper/50 rounded-2xl p-4 border border-thin text-[12px] leading-relaxed text-brand-ink-strong">
          <div class="flex items-center gap-1.5 text-brand-primary font-bold mb-2">
            <CheckCircle2 :size="13" />
            <span>定论极向：{{ currentReview.stability_detail?.verdict || '推算完成' }}</span>
          </div>
          <p class="font-medium whitespace-pre-wrap">{{ currentReview.stability_detail?.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.animate-fadeIn {
  animation: fadeIn 0.25s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.bazi-float {
  animation: float 3s ease-in-out infinite;
}

.meihua-sway {
  animation: sway 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes sway {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(6deg); }
}
</style>
