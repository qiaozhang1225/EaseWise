<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  ChevronRight,
  Receipt,
  History,
  MessageSquare,
  Wallet,
  ShieldCheck,
  Share2,
  Clipboard,
  Check,
  X,
  AlertTriangle,
  RefreshCw,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { PointsLedgerEntryResponse, ReviewSummary } from '../../types/api';

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string): void;
}>();

const {
  state,
  bootstrapApp,
  refreshAppData,
  refreshPointsLedger,
  refreshReviewHistory,
  refreshCurrentReview,
  displayNickname,
  displayAvatarText,
  accountLabel,
  isGuestUser,
  customerServiceContact,
  customerServiceGuidance,
  humanizeError,
} = useEaseWiseApp();

const activeModal = ref<string | null>(null);
const copied = ref(false);
const feedbackText = ref('');
const ambassadorStatus = ref<'regular' | 'ambassador'>('regular');
const openingReviewId = ref<string | null>(null);
const historyActionError = ref('');

const currentPoints = computed(() => state.points?.balance ?? 0);
const reportHistory = computed(() => state.reviewHistory);
const ledgerRecords = computed(() => state.pointsLedger);
const userReady = computed(() => Boolean(state.user));
const statusBadgeText = computed(() => isGuestUser.value ? '游客体验' : '已登录');
const statusBadgeClass = computed(() => isGuestUser.value ? 'bg-amber-500/10 text-amber-600' : 'bg-green-500/10 text-green-600');
const connectionHint = computed(() => {
  if (state.connectionError) {
    return `本地 API 暂未连通：${state.connectionError}`;
  }
  return '本地测试已自动创建游客会话，可直接查看实时积分与评测记录。';
});

onMounted(() => {
  void bootstrapApp();
});

watch(activeModal, async (value) => {
  if (value !== 'history') {
    openingReviewId.value = null;
    historyActionError.value = '';
  }
  if (value === 'ledger') {
    await refreshPointsLedger().catch(() => undefined);
  }
  if (value === 'history') {
    await refreshReviewHistory().catch(() => undefined);
  }
});

async function handleRefreshData(): Promise<void> {
  await refreshAppData();
}

async function handleCopyContact(): Promise<void> {
  try {
    await navigator.clipboard.writeText(customerServiceContact.value);
    copied.value = true;
    window.setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch {
    copied.value = false;
  }
}

function handleFeedbackSubmit(): void {
  if (!feedbackText.value.trim()) {
    return;
  }
  window.alert('感谢你的反馈，我们已经记录，后续会结合产品排期继续完善。');
  feedbackText.value = '';
  activeModal.value = null;
}

function handlePartnerInfo(): void {
  window.alert('推广大使的升级条件、返佣比例和权益展示以后端规则配置与正式规则页为准。');
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

const ledgerBizTypeTitleMap: Record<string, string> = {
  guest_bonus: '游客初始积分发放',
  guest_initial_grant: '游客初始积分发放',
  signup_bonus: '注册赠送积分',
  wechat_initial_grant: '注册初始积分发放',
  phone_review_base: '手机号评测扣减',
  phone_review_base_charge: '手机号评测扣减',
  phone_review_base_refund: '手机号评测失败返还',
  phone_review_aspect_unlock: '手机号评测维度解锁',
  phone_review_aspect_unlock_charge: '手机号评测维度解锁',
  recharge_order: '积分充值到账',
  guest_merge_transfer_out: '游客积分合并转出',
  guest_merge_transfer_in: '游客积分合并转入',
  manual_adjust: '后台积分调整',
};

const ledgerRemarkTitleMap: Record<string, string> = {
  'guest initial points': '游客初始积分发放',
  'initial test points': '注册赠送积分',
  guest_initial_grant: '游客初始积分发放',
  wechat_initial_grant: '注册初始积分发放',
  phone_review_base_charge: '手机号评测扣减',
  phone_review_base_refund: '手机号评测失败返还',
  phone_review_aspect_unlock_charge: '手机号评测维度解锁',
  guest_points_merged_out: '游客积分合并转出',
  guest_points_merged_in: '游客积分合并转入',
  manual_adjust: '后台积分调整',
};

function hasChineseText(value: string): boolean {
  return /[\u3400-\u9fff]/u.test(value);
}

function resolveLedgerRemarkTitle(remark: string): string | null {
  const normalizedRemark = remark.trim();
  if (!normalizedRemark) {
    return null;
  }

  const lowerCaseRemark = normalizedRemark.toLowerCase();
  if (ledgerRemarkTitleMap[lowerCaseRemark]) {
    return ledgerRemarkTitleMap[lowerCaseRemark];
  }

  if (lowerCaseRemark.startsWith('recharge_order:')) {
    return '积分充值到账';
  }

  if (lowerCaseRemark.startsWith('phone_review_aspect_unlock:')) {
    return '手机号评测维度解锁';
  }

  if (hasChineseText(normalizedRemark)) {
    return normalizedRemark;
  }

  return null;
}

function formatLedgerTitle(entry: PointsLedgerEntryResponse): string {
  if (entry.remark?.trim()) {
    const resolvedRemarkTitle = resolveLedgerRemarkTitle(entry.remark);
    if (resolvedRemarkTitle) {
      return resolvedRemarkTitle;
    }
  }

  return ledgerBizTypeTitleMap[entry.biz_type] || '积分记录更新';
}

function formatLedgerDelta(entry: PointsLedgerEntryResponse): string {
  return `${entry.delta > 0 ? '+' : ''}${entry.delta} 分`;
}

function resolveLedgerColor(entry: PointsLedgerEntryResponse): string {
  return entry.delta >= 0 ? 'text-green-500' : 'text-red-500';
}

function formatReviewStatus(review: ReviewSummary): string {
  if (review.status === 'completed') {
    return review.score !== null ? `评分: ${review.score} 分` : '评测已完成';
  }
  if (review.status === 'failed') {
    return '评测失败';
  }
  return review.progress_message || '评测处理中';
}

function resolveReviewActionText(review: ReviewSummary): string {
  if (openingReviewId.value === review.id) {
    return '打开中...';
  }
  if (review.status === 'completed') {
    return '查看结果';
  }
  if (review.status === 'failed') {
    return '查看失败原因';
  }
  return '继续查看';
}

async function handleOpenReview(review: ReviewSummary): Promise<void> {
  if (openingReviewId.value) {
    return;
  }

  historyActionError.value = '';
  openingReviewId.value = review.id;

  try {
    await refreshCurrentReview(review.id);
    activeModal.value = null;
    emit('navigate-to-tab', 'phone');
  } catch (error) {
    historyActionError.value = humanizeError(error);
  } finally {
    openingReviewId.value = null;
  }
}
</script>

<template>
  <div class="pt-16 pb-32 max-w-md mx-auto px-margin-mobile relative text-left">
    <section class="mb-5 mt-4">
      <div
        v-if="userReady"
        class="bg-white rounded-2xl p-5 border border-gray-100 flex items-center justify-between shadow-sm"
      >
        <div class="flex items-center gap-3.5">
          <div class="w-14 h-14 rounded-full overflow-hidden border-2 border-brand-primary/10 bg-brand-primary/5 flex items-center justify-center font-brand font-bold text-brand-primary text-heading-1 shrink-0">
            {{ displayAvatarText }}
          </div>
          <div class="text-left">
            <div class="flex items-center gap-1.5">
              <h3 class="font-ui text-heading-2 font-bold text-brand-ink-strong">{{ displayNickname }}</h3>
              <span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-micro font-bold" :class="statusBadgeClass">
                {{ statusBadgeText }}
              </span>
            </div>
            <p class="font-ui text-caption text-brand-secondary mt-1">
              {{ accountLabel }}
            </p>
          </div>
        </div>
        <span
          v-if="ambassadorStatus === 'ambassador'"
          class="inline-flex self-start mt-1 px-2.5 py-1 font-ui text-micro font-semibold bg-brand-paper rounded text-brand-secondary"
        >
          VIP推广大使
        </span>
      </div>

      <div
        v-else
        class="bg-white rounded-2xl p-5 border border-amber-200/60 bg-amber-50/20 flex flex-col items-center text-center space-y-4 shadow-sm"
      >
        <div class="w-11 h-11 rounded-full bg-amber-500/10 flex items-center justify-center text-amber-600 shrink-0">
          <AlertTriangle :size="20" />
        </div>
        <div class="space-y-1">
          <p class="font-ui text-body font-bold text-brand-ink-strong">{{ state.booting ? '正在连接本地数据' : '本地体验数据暂不可用' }}</p>
          <p class="font-ui text-caption text-brand-secondary px-4 leading-relaxed">
            {{ connectionHint }}
          </p>
        </div>
        <button
          @click="handleRefreshData"
          class="px-6 py-2 bg-brand-primary hover:bg-brand-primary-strong text-white rounded-full font-ui text-body font-bold inline-flex items-center gap-1 cursor-pointer outline-none shadow-sm transition-all"
        >
          <RefreshCw :size="13" />
          <span>重新连接本地 API</span>
        </button>
      </div>
    </section>

    <section class="mb-5">
      <div class="bg-brand-ink-strong text-white rounded-2xl p-5 relative overflow-hidden shadow-md">
        <div class="absolute top-[-10%] right-[-5%] opacity-5 text-white">
          <Wallet :size="120" />
        </div>

        <div class="relative z-10">
          <div>
            <p class="font-ui text-caption font-bold text-gray-300 tracking-widest mb-1">当前账户剩余积分</p>
            <div class="mt-3 flex items-end justify-between gap-3">
              <div class="flex items-end gap-2">
                <span class="font-brand text-display-xl leading-none font-bold text-brand-accent">{{ currentPoints }}</span>
                <span class="pb-1 font-ui text-body font-bold text-brand-accent/90">分</span>
              </div>
              <button
                @click="activeModal = 'recharge'"
                class="min-w-[104px] px-5 py-2.5 rounded-xl bg-brand-accent text-brand-ink-strong font-ui text-body font-black hover:brightness-105 active:scale-[0.98] transition-all shrink-0 cursor-pointer outline-none shadow-md"
              >
                去充值
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-5">
      <div class="bg-gradient-to-r from-brand-primary/5 to-purple-500/5 rounded-2xl p-4 border border-brand-primary/10 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary shrink-0">
            <Share2 :size="16" />
          </div>
          <div class="text-left">
            <p class="font-ui text-body font-bold text-brand-ink-strong">推广大使</p>
            <p class="font-ui text-caption text-brand-secondary mt-0.5">升级条件、返佣比例和权益展示以后端规则配置为准</p>
          </div>
        </div>
        <button
          @click="handlePartnerInfo"
          class="font-ui text-caption font-bold text-brand-primary bg-white hover:bg-brand-primary/5 px-3 py-1.5 rounded-full border border-brand-primary/20 shrink-0 cursor-pointer transition-all outline-none"
        >
          查看权益
        </button>
      </div>
    </section>

    <section class="mb-8">
      <div class="bg-white rounded-2xl overflow-hidden hairline-border divide-y divide-gray-100 shadow-sm">
        <div
          @click="activeModal = 'ledger'"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <Receipt :size="18" class="text-brand-secondary" />
            <span class="font-ui text-body font-bold text-brand-ink-strong">积分记录</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span v-if="ledgerRecords.length > 0" class="font-ui text-micro text-brand-primary font-bold bg-brand-primary/10 px-1.5 py-0.5 rounded-full">
              {{ ledgerRecords.length }}
            </span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="activeModal = 'history'"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <History :size="18" class="text-brand-secondary" />
            <span class="font-ui text-body font-bold text-brand-ink-strong">评测记录</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span v-if="reportHistory.length > 0" class="font-ui text-micro text-brand-primary font-bold bg-brand-primary/10 px-1.5 py-0.5 rounded-full">
              {{ reportHistory.length }}
            </span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="activeModal = 'feedback'"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <MessageSquare :size="18" class="text-brand-secondary" />
            <span class="font-ui text-body font-bold text-brand-ink-strong">反馈问题</span>
          </div>
          <ChevronRight :size="16" class="text-gray-300" />
        </div>
      </div>
    </section>

    <div class="text-center px-1">
      <button
        @click="handleRefreshData"
        class="w-full py-3.5 rounded-xl bg-brand-primary text-white font-ui text-body font-bold hover:bg-brand-primary-strong transition-colors active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer outline-none shadow-md"
      >
        <RefreshCw :size="16" />
        <span>{{ state.booting ? '正在刷新本地数据...' : '刷新本地数据' }}</span>
      </button>
    </div>

    <footer class="mt-14 text-center pb-8 shrink-0">
      <p class="font-ui text-caption font-bold text-brand-secondary/50 tracking-widest">
        易如反掌 · 服务积分与推广规则以后端配置为准
      </p>
      <p class="font-ui text-micro text-gray-400 mt-2">
        易如反掌 / EaseWise
      </p>
    </footer>

    <transition name="fade">
      <div v-if="activeModal === 'recharge'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-6 w-full max-w-sm space-y-6 text-center hairline-border shadow-2xl relative">
          <button @click="activeModal = null" class="absolute top-4 right-4 p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
            <X :size="18" />
          </button>

          <div class="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary mx-auto animate-bounce">
            <Wallet :size="24" />
          </div>

          <div class="space-y-2">
            <h3 class="font-brand text-heading-2 font-bold text-brand-ink-strong leading-tight">积分充值说明</h3>
            <p class="font-ui text-body text-brand-secondary leading-relaxed">
              {{ customerServiceGuidance }}
            </p>
          </div>

          <div class="bg-brand-paper p-3 rounded-xl flex items-center justify-between border border-gray-100">
            <div class="text-left font-data">
              <p class="text-micro text-brand-secondary">客服联系方式：</p>
              <p class="text-title font-bold text-brand-ink-strong">{{ customerServiceContact }}</p>
            </div>
            <button @click="handleCopyContact" class="px-3.5 py-1.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-ui text-caption font-bold rounded-lg cursor-pointer outline-none flex items-center gap-1 shrink-0 transition-all">
              <Check v-if="copied" :size="11" />
              <Clipboard v-else :size="11" />
              <span>{{ copied ? '已复制' : '复制' }}</span>
            </button>
          </div>

          <div class="font-ui text-caption text-brand-secondary/80 flex items-center gap-1.5 justify-center bg-green-50 p-2.5 rounded-lg border border-green-100">
            <ShieldCheck :size="13" class="text-green-600 shrink-0" />
            <span>充值与积分到账说明以后端规则和客服通知为准</span>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'ledger'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 text-left w-full">
            <div class="text-left">
              <h3 class="font-ui text-heading-2 font-bold text-brand-ink-strong">积分记录</h3>
              <p class="font-ui text-caption text-brand-secondary">当前展示最近的积分获取与扣减记录</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer shrink-0">
              <X :size="18" />
            </button>
          </div>

          <div class="max-h-[300px] overflow-y-auto no-scrollbar space-y-3.5 pr-1 py-1">
            <div v-if="ledgerRecords.length > 0" class="space-y-3.5">
              <div v-for="entry in ledgerRecords" :key="entry.ledger_id" class="flex justify-between items-start text-xs border-b border-gray-50 pb-2.5">
                <div class="text-left">
                  <p class="font-ui text-body font-bold text-brand-ink">{{ formatLedgerTitle(entry) }}</p>
                  <p class="font-ui text-micro text-brand-secondary mt-0.5">{{ formatDateTime(entry.created_at) }}</p>
                </div>
                <div class="text-right">
                  <span class="font-data text-body font-bold" :class="resolveLedgerColor(entry)">{{ formatLedgerDelta(entry) }}</span>
                  <p class="font-ui text-micro text-brand-secondary mt-0.5">余额 {{ entry.balance_after }} 分</p>
                </div>
              </div>
            </div>
            <div v-else class="py-8 text-center space-y-2">
              <p class="font-ui text-body text-brand-secondary">暂无积分变动记录。</p>
              <p class="font-ui text-micro text-brand-secondary/60">完成手机号评测或后台发放积分后，会在这里显示。</p>
            </div>
          </div>

          <button @click="activeModal = null" class="w-full py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink font-ui text-body font-semibold rounded-lg shrink-0 outline-none cursor-pointer">
            确定返回
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'history'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-ui text-heading-2 font-bold text-brand-ink-strong">评测记录</h3>
              <p class="font-ui text-caption text-brand-secondary">当前展示本地 API 返回的手机号评测记录</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="max-h-[300px] overflow-y-auto no-scrollbar space-y-3 py-1">
            <p
              v-if="historyActionError"
              class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-ui text-caption text-red-600 leading-relaxed"
            >
              {{ historyActionError }}
            </p>
            <div v-if="reportHistory.length > 0" class="space-y-3">
              <button
                v-for="review in reportHistory"
                :key="review.id"
                type="button"
                class="w-full bg-brand-paper/50 p-3 rounded-xl border border-gray-100 flex items-center justify-between gap-3 text-xs text-left transition-all hover:bg-white hover:border-brand-primary/20 disabled:opacity-60 disabled:cursor-not-allowed"
                :disabled="!!openingReviewId"
                @click="handleOpenReview(review)"
              >
                <div class="min-w-0">
                  <p class="font-ui text-body font-bold text-brand-ink-strong">评测号码: <span class="font-ui">{{ review.masked_phone }}</span></p>
                  <p class="font-ui text-micro text-brand-secondary mt-0.5">
                    性别: {{ review.gender === 'male' ? '男' : '女' }} · {{ formatDateTime(review.created_at) }}
                  </p>
                  <p class="font-ui text-micro text-brand-secondary/80 mt-1">
                    {{ resolveReviewActionText(review) }}
                  </p>
                </div>
                <div class="shrink-0 flex flex-col items-end gap-1.5">
                  <span class="font-ui text-body font-bold text-brand-primary bg-brand-primary/10 px-2.5 py-1 rounded-full shrink-0">
                    {{ formatReviewStatus(review) }}
                  </span>
                  <ChevronRight :size="14" class="text-brand-secondary/60" />
                </div>
              </button>
            </div>
            <div v-else class="py-8 text-center space-y-2">
              <p class="font-ui text-body text-brand-secondary">暂无手机号评测记录。</p>
              <p class="font-ui text-micro text-brand-secondary/60">你可以先完成一次手机号评测，记录会显示在这里。</p>
            </div>
          </div>

          <button @click="activeModal = null" class="w-full py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink font-ui text-body font-semibold rounded-lg outline-none cursor-pointer">
            确定返回
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'feedback'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-ui text-heading-2 font-bold text-brand-ink-strong">反馈问题</h3>
              <p class="font-ui text-caption text-brand-secondary">提交你遇到的问题、建议或合作需求</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-ui text-caption font-bold text-brand-secondary tracking-wide">反馈详情</label>
            <textarea
              v-model="feedbackText"
              class="w-full bg-brand-paper font-ui text-body text-brand-ink-strong p-3.5 h-28 rounded-xl border border-gray-100 focus:border-brand-primary outline-none resize-none transition-all"
              placeholder="请输入你遇到的问题、改进建议或合作需求..."
            />
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="activeModal = null" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-ui text-body font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="handleFeedbackSubmit"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-ui text-body font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="!feedbackText.trim()"
            >
              提交反馈
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
