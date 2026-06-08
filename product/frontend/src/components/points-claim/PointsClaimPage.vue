<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Gift,
  Loader2,
  MessageSquare,
  RefreshCw,
  Sparkles,
  UserRound,
} from 'lucide-vue-next';
import { claimPublicPoints, getPublicPointsClaimLink } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { PointsClaimSubmitResponse, PublicPointsClaimLinkResponse } from '../../types/api';

const props = defineProps<{
  claimCode: string;
}>();

const emit = defineEmits<{
  (event: 'navigate-to-tab', tab: string): void;
}>();

type PageState =
  | 'loading'
  | 'invalid'
  | 'expired'
  | 'disabled'
  | 'not_started'
  | 'auth_required'
  | 'ready'
  | 'submitting'
  | 'granted'
  | 'already_claimed_this_week'
  | 'error';

const {
  state,
  bootstrapApp,
  requestRegisteredUser,
  refreshPoints,
  isRegisteredUser,
  displayNickname,
  humanizeError,
  openCustomerServiceModal,
} = useEaseWiseApp();

const pageState = ref<PageState>('loading');
const claimLink = ref<PublicPointsClaimLinkResponse | null>(null);
const claimResult = ref<PointsClaimSubmitResponse | null>(null);
const actionError = ref('');
const pendingClaimAfterAuth = ref(false);

const normalizedClaimCode = computed(() => props.claimCode.trim());
const currentPoints = computed(() => claimResult.value?.points?.balance ?? state.points?.balance ?? 0);
const canClaim = computed(() => pageState.value === 'ready' || pageState.value === 'auth_required');
const displayValue = computed(() => formatMoney(claimLink.value?.display_value_cents ?? 0));
const pointsAmount = computed(() => claimLink.value?.points_amount ?? 0);
const userStatusLabel = computed(() => (isRegisteredUser.value ? displayNickname.value || '已登录' : '未登录'));
const activityTitle = computed(() => claimLink.value?.title || '免费积分领用计划');
const isClaimActionState = computed(() => pageState.value === 'ready' || pageState.value === 'auth_required' || pageState.value === 'submitting');
const isProblemState = computed(() => pageState.value === 'invalid' || pageState.value === 'expired' || pageState.value === 'disabled' || pageState.value === 'not_started' || pageState.value === 'error');
const statusTitle = computed(() => {
  if (pageState.value === 'invalid') return '链接不存在';
  if (pageState.value === 'expired') return '链接已过期';
  if (pageState.value === 'disabled') return '链接已停用';
  if (pageState.value === 'not_started') return '链接尚未生效';
  if (pageState.value === 'already_claimed_this_week') return '本周已领取过免费积分';
  return '领取失败';
});
const statusDescription = computed(() => {
  if (pageState.value === 'already_claimed_this_week') return '每个账号每个自然周仅能成功领取一次，您可在下周一继续参与。';
  if (pageState.value === 'error') return actionError.value || '请稍后重试，或向客服咨询反馈。';
  return actionError.value || '请确认链接状态后再试，或向客服咨询反馈。';
});
const primaryButtonLabel = computed(() => {
  if (pageState.value === 'submitting') return '正在领取...';
  if (!isRegisteredUser.value) return '登录后领取积分';
  if (pageState.value === 'granted') return '积分已到账';
  if (pageState.value === 'already_claimed_this_week') return '本周已领取过免费积分';
  return '领取积分';
});

onMounted(async () => {
  await Promise.all([bootstrapApp(), loadClaimLink()]);
});

watch(isRegisteredUser, async (value, previousValue) => {
  if (value && !previousValue && !pendingClaimAfterAuth.value) {
    await loadClaimLink();
  }
});

watch(() => props.claimCode, async () => {
  claimResult.value = null;
  pendingClaimAfterAuth.value = false;
  await loadClaimLink();
});

async function loadClaimLink(): Promise<void> {
  if (!normalizedClaimCode.value) {
    pageState.value = 'invalid';
    return;
  }
  pageState.value = 'loading';
  actionError.value = '';
  try {
    claimLink.value = await getPublicPointsClaimLink(normalizedClaimCode.value, state.accessToken);
    applyLinkState();
  } catch (error) {
    claimLink.value = null;
    if (isNotFoundError(error)) {
      pageState.value = 'invalid';
    } else {
      actionError.value = humanizeError(error);
      pageState.value = 'error';
    }
  }
}

function applyLinkState(): void {
  const link = claimLink.value;
  if (!link) {
    pageState.value = 'invalid';
    return;
  }
  if (link.current_user_claim_status === 'already_claimed_this_week') {
    pageState.value = 'already_claimed_this_week';
    return;
  }
  if (link.effective_status === 'expired') {
    pageState.value = 'expired';
    return;
  }
  if (link.effective_status === 'disabled') {
    pageState.value = 'disabled';
    return;
  }
  if (link.effective_status === 'not_started') {
    pageState.value = 'not_started';
    return;
  }
  pageState.value = isRegisteredUser.value ? 'ready' : 'auth_required';
}

async function handlePrimaryAction(): Promise<void> {
  if (pageState.value === 'granted' || pageState.value === 'already_claimed_this_week') {
    return;
  }
  if (!canClaim.value) {
    await loadClaimLink();
    return;
  }
  if (!isRegisteredUser.value) {
    await openUnifiedAuth();
    return;
  }
  await submitClaim();
}

async function openUnifiedAuth(): Promise<void> {
  actionError.value = '';
  pendingClaimAfterAuth.value = true;
  const authenticated = await requestRegisteredUser('领取免费积分');
  if (!authenticated) {
    pendingClaimAfterAuth.value = false;
    return;
  }
  await loadClaimLink();
  if (pageState.value === 'ready') {
    await submitClaim();
    return;
  }
  pendingClaimAfterAuth.value = false;
}

async function submitClaim(): Promise<void> {
  if (!state.accessToken || pageState.value === 'submitting') {
    return;
  }
  pageState.value = 'submitting';
  actionError.value = '';
  pendingClaimAfterAuth.value = false;
  try {
    const result = await claimPublicPoints(state.accessToken, normalizedClaimCode.value);
    claimResult.value = result;
    if (result.claim_status === 'granted') {
      pageState.value = 'granted';
      await refreshPoints().catch(() => undefined);
      return;
    }
    if (result.claim_status === 'already_claimed_this_week') {
      pageState.value = 'already_claimed_this_week';
      await refreshPoints().catch(() => undefined);
      return;
    }
    pageState.value = 'error';
    actionError.value = result.message || '领取失败，请稍后重试。';
  } catch (error) {
    await loadClaimLink().catch(() => undefined);
    actionError.value = humanizeError(error);
    if (actionError.value === '本周已领取过免费积分') {
      pageState.value = 'already_claimed_this_week';
      return;
    }
    if (pageState.value === 'ready' || pageState.value === 'auth_required' || pageState.value === 'loading') {
      pageState.value = 'error';
    }
  }
}

function openCustomerService(): void {
  openCustomerServiceModal('points_insufficient', claimLink.value?.title || '免费积分领取');
}

function handleBackToHome(): void {
  emit('navigate-to-tab', 'home');
}

function isNotFoundError(error: unknown): boolean {
  return error instanceof Error && error.message === 'claim_link_not_found';
}

function formatMoney(cents: number): string {
  const amount = cents / 100;
  return Number.isInteger(amount) ? String(amount) : amount.toFixed(2);
}

function formatTime(value: string | null | undefined): string {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value.replace('T', ' ').replace('+00:00', '').replace('+08:00', '');
  }
  const pad = (part: number) => String(part).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
</script>

<template>
  <div class="min-h-screen bg-[#FBFBFA] pb-8 font-sans text-brand-ink antialiased select-none">
    <div class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-100 px-4 py-3 flex items-center justify-between">
      <button
        type="button"
        class="-ml-2 px-2 py-1.5 rounded-full text-brand-secondary hover:text-brand-ink-strong hover:bg-gray-50 active:scale-[0.98] transition-all cursor-pointer outline-none flex items-center gap-1"
        @click="handleBackToHome"
      >
        <ArrowLeft :size="17" />
        <span class="text-xs font-bold">返回首页</span>
      </button>
      <h1 class="text-sm font-bold text-brand-ink-strong">免费积分领取</h1>
      <div class="w-[68px]"></div>
    </div>

    <div class="max-w-sm mx-auto w-full px-4 py-6 space-y-5">
      <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-xs text-center animate-in">
        <div class="text-[10px] font-bold text-brand-primary/80 bg-brand-primary/10 px-2.5 py-0.5 rounded-full uppercase tracking-wider inline-flex">
          EaseWise · 福利活动
        </div>
        <h2 class="mt-2 font-serif text-lg font-black text-brand-ink-strong leading-snug truncate">
          {{ activityTitle }}
        </h2>

        <button
          type="button"
          class="mt-3 mx-auto max-w-full bg-[#F6F7F5] hover:bg-gray-50 border border-gray-100 rounded-full px-3 py-1.5 cursor-pointer transition-colors outline-none flex items-center gap-2"
          @click="!isRegisteredUser ? openUnifiedAuth() : undefined"
        >
          <span class="w-5 h-5 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center">
            <UserRound :size="11" />
          </span>
          <span class="min-w-0 text-xs font-semibold text-brand-ink truncate">
            当前身份：{{ userStatusLabel }}
          </span>
          <span v-if="!isRegisteredUser" class="pl-2 border-l border-gray-200 text-[10px] font-bold text-brand-primary">登录</span>
        </button>
      </section>

      <section v-if="pageState === 'loading'" class="bg-white rounded-[1.75rem] border border-gray-100 shadow-[0_18px_50px_rgba(15,23,42,0.08)] py-24 text-center space-y-4 animate-in">
        <div class="relative w-16 h-16 mx-auto rounded-full bg-brand-primary/5 text-brand-primary flex items-center justify-center">
          <div class="absolute inset-0 rounded-full border border-dashed border-brand-primary/25 animate-spin-slow"></div>
          <Loader2 class="w-8 h-8 animate-spin opacity-70" />
        </div>
        <div class="space-y-1">
          <p class="font-serif font-bold text-brand-ink-strong text-sm">正在读取领取链接...</p>
          <p class="text-[10px] text-brand-secondary">请稍候</p>
        </div>
      </section>

      <template v-else>
        <section class="relative bg-white rounded-[1.75rem] overflow-hidden border border-gray-100 shadow-[0_18px_50px_rgba(15,23,42,0.08)] animate-in">
          <div class="absolute top-[59%] -left-3 w-6 h-6 rounded-full bg-[#FBFBFA] border-r border-gray-100 z-10"></div>
          <div class="absolute top-[59%] -right-3 w-6 h-6 rounded-full bg-[#FBFBFA] border-l border-gray-100 z-10"></div>

          <div class="p-6 text-center flex flex-col items-center space-y-4">
            <div
              v-if="isClaimActionState"
              class="relative w-16 h-16 rounded-full bg-[#D4AF37]/10 text-[#D4AF37] flex items-center justify-center"
            >
              <div class="absolute inset-0 rounded-full border border-dashed border-[#D4AF37]/40 animate-spin-slow"></div>
              <Gift :size="28" class="animate-bounce-slow" />
            </div>
            <div
              v-else-if="pageState === 'granted'"
              class="w-16 h-16 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center"
            >
              <CheckCircle2 class="stroke-[3]" :size="30" />
            </div>
            <div
              v-else-if="pageState === 'already_claimed_this_week'"
              class="w-16 h-16 rounded-full bg-amber-50 border border-amber-100 text-amber-700 flex items-center justify-center"
            >
              <RefreshCw :size="26" />
            </div>
            <div
              v-else
              class="w-16 h-16 rounded-full bg-rose-50 border border-rose-100 text-rose-600 flex items-center justify-center"
            >
              <AlertCircle :size="28" />
            </div>

            <div v-if="claimLink && isClaimActionState" class="space-y-1">
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest">可领用积分额</p>
              <div class="flex items-baseline justify-center font-serif text-brand-ink-strong">
                <span class="text-4xl font-black text-brand-primary">{{ pointsAmount }}</span>
                <span class="ml-1 text-sm font-bold text-brand-secondary">分</span>
              </div>
            </div>

            <div v-else-if="pageState === 'granted'" class="space-y-2">
              <h2 class="font-serif font-bold text-emerald-700 text-base">积分已到账</h2>
              <p class="text-[11px] text-brand-secondary">当前可用积分余额</p>
              <div class="font-serif text-[36px] font-black text-brand-primary leading-none">{{ currentPoints }}</div>
            </div>

            <div v-else-if="pageState === 'already_claimed_this_week'" class="space-y-2">
              <h2 class="font-serif font-bold text-amber-800 text-base">本周已领取过免费积分</h2>
              <p class="text-[11px] text-brand-secondary leading-relaxed px-2">
                每个账号每个自然周仅能成功领取一次。
              </p>
            </div>

            <div v-else class="space-y-2">
              <h2 class="font-serif font-bold text-rose-700 text-base">{{ statusTitle }}</h2>
              <p class="text-[11px] text-brand-secondary leading-relaxed px-2">
                {{ statusDescription }}
              </p>
            </div>

            <div v-if="claimLink && isClaimActionState" class="grid grid-cols-2 gap-0 w-full bg-[#F7F7F4] p-3 rounded-2xl border border-gray-100">
              <div class="text-center border-r border-gray-100">
                <p class="text-[9px] font-bold text-gray-400">对应人民币价值</p>
                <p class="mt-0.5 text-sm font-serif font-black text-[#D4AF37]">￥{{ displayValue }}</p>
              </div>
              <div class="text-center">
                <p class="text-[9px] font-bold text-gray-400">当前领取状态</p>
                <p class="mt-1 inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 border border-emerald-100">可领取</p>
              </div>
            </div>
          </div>

          <div class="border-t border-dashed border-gray-100 mx-5"></div>

          <div class="p-5 bg-[#F7F7F4] rounded-b-[1.75rem]">
            <div v-if="pageState === 'auth_required' || pageState === 'ready'" class="space-y-4">
              <div class="flex items-center justify-center gap-1.5 text-[10.5px] text-brand-secondary">
                <Clock :size="12" class="text-gray-400 shrink-0" />
                <span>有效期至：{{ formatTime(claimLink?.expires_at) }}</span>
              </div>

              <button
                type="button"
                class="w-full py-3.5 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-xl text-xs font-bold cursor-pointer border-none shadow-md hover:shadow-lg transition-all active:scale-[0.98] outline-none flex items-center justify-center gap-1.5"
                @click="handlePrimaryAction"
              >
                <UserRound v-if="!isRegisteredUser" :size="14" />
                <Sparkles v-else :size="14" class="text-[#D4AF37] animate-pulse" />
                <span>{{ primaryButtonLabel }}</span>
              </button>

              <p class="text-[10px] text-center text-gray-400 leading-relaxed">
                登录成功后系统会自动继续发放领取。
              </p>

              <div
                v-if="actionError"
                class="bg-rose-50 border border-rose-100 rounded-xl p-3 flex items-start gap-2 text-left text-[10.5px] text-rose-800 leading-relaxed"
              >
                <AlertTriangle :size="14" class="shrink-0 mt-0.5" />
                <span>{{ actionError }}</span>
              </div>
            </div>

            <div v-else-if="pageState === 'submitting'" class="py-4 text-center flex flex-col items-center space-y-2">
              <Loader2 :size="24" class="text-brand-primary animate-spin" />
              <p class="text-xs font-bold text-brand-ink-strong">正在领取...</p>
              <p class="text-[10px] text-brand-secondary">账务安全处理中，请勿刷新页面</p>
            </div>

            <div v-else-if="pageState === 'granted'" class="py-3 text-center space-y-3">
              <p class="text-[11px] text-brand-secondary leading-relaxed">
                福利已安全记账。现在可以继续使用积分进行测算。
              </p>
              <button
                type="button"
                class="w-full py-2.5 px-4 bg-brand-primary/10 hover:bg-brand-primary/15 text-brand-primary rounded-xl text-[11px] font-bold border-none transition-colors cursor-pointer outline-none"
                @click="handleBackToHome"
              >
                立即去测算
              </button>
            </div>

            <div v-else-if="pageState === 'already_claimed_this_week'" class="py-3 text-center space-y-3">
              <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-amber-50 text-amber-600">
                <AlertCircle :size="18" />
              </div>
              <div class="space-y-1.5">
                <p class="text-xs font-bold text-amber-800">{{ statusTitle }}</p>
                <p class="text-[10px] text-brand-secondary leading-relaxed px-2">
                  {{ statusDescription }}
                </p>
              </div>
              <button
                type="button"
                class="w-full py-2.5 px-4 bg-brand-primary/10 hover:bg-brand-primary/15 text-brand-primary rounded-xl text-[11px] font-bold border-none transition-colors cursor-pointer outline-none flex items-center justify-center gap-1"
                @click="handleBackToHome"
              >
                <ArrowLeft :size="13" />
                <span>返回首页</span>
              </button>
            </div>

            <div v-else class="py-2 text-center space-y-3">
              <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-rose-50 text-rose-600">
                <AlertCircle :size="18" />
              </div>
              <div class="space-y-1.5">
                <p class="text-xs font-bold text-rose-700">{{ statusTitle }}</p>
                <p class="text-[10px] text-brand-secondary px-2 leading-relaxed">
                  {{ statusDescription }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          v-if="isProblemState"
          class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm space-y-3 text-left animate-in"
        >
          <div class="flex items-start gap-2.5">
            <div class="p-1.5 bg-brand-primary/10 rounded-lg text-brand-primary">
              <MessageSquare :size="14" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] font-bold text-brand-ink-strong">福利领取遇到问题？</p>
              <p class="text-[10px] text-brand-secondary leading-relaxed mt-0.5">
                客服可以协助核对链接状态和账号领取记录。
              </p>
            </div>
          </div>
          <button
            type="button"
            class="w-full py-2.5 bg-[#F5F3FF] hover:bg-[#EDE9FE] text-brand-primary text-[11px] font-bold rounded-xl border border-[#DDD6FE]/60 cursor-pointer select-none transition-all outline-none flex items-center justify-center gap-1.5"
            @click="openCustomerService"
          >
            联系客服
          </button>
        </section>
      </template>
    </div>

    <div class="py-5 text-center space-y-1 mt-auto bg-gray-50/50 border-t border-gray-100">
      <p class="text-[9.5px] text-gray-400 font-mono tracking-widest">EASEWISE · 易如反掌系统</p>
      <p class="text-[9px] text-gray-400">数字与传统学术指导 · 账务安全审计链</p>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation: enter 0.18s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-spin-slow {
  animation: spin-slow 20s linear infinite;
}

.animate-bounce-slow {
  animation: bounce-slow 2.4s ease-in-out infinite;
}

@keyframes enter {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes bounce-slow {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}
</style>
