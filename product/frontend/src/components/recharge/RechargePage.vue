<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  AlertTriangle,
  ArrowRight,
  Check,
  HelpCircle,
  Loader2,
  RefreshCw,
} from 'lucide-vue-next';
import {
  createRechargeOrder,
  createRechargePayment,
  getRechargePaymentStatus,
  listRechargePackages,
} from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import type { PaymentTransactionResponse, RechargeOrderResponse, RechargePackageResponse } from '../../types/api';

const props = defineProps<{
  routeQuery?: Record<string, string | undefined>;
}>();

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
}>();

type PageState = 'checking' | 'auth_required' | 'recharge_panel' | 'pending_payment' | 'payment_success' | 'payment_error';

const {
  state,
  bootstrapApp,
  refreshPoints,
  isRegisteredUser,
  displayNickname,
  customerServiceCopyForScene,
  requestRegisteredUser,
  openCustomerServiceModal,
  humanizeError,
} = useEaseWiseApp();

const pageState = ref<PageState>('checking');
const packages = ref<RechargePackageResponse[]>([]);
const selectedPackageKey = ref<string | null>(null);
const currentOrder = ref<RechargeOrderResponse | null>(null);
const currentPayment = ref<PaymentTransactionResponse | null>(null);
const loadingPackages = ref(false);
const creatingOrder = ref(false);
const refreshingStatus = ref(false);
const actionError = ref('');

const routeQuery = computed(() => props.routeQuery || {});
const source = computed(() => routeQuery.value.source || 'profile');
const returnTo = computed(() => routeQuery.value.return_to || 'profile');
const requiredPoints = computed(() => Number(routeQuery.value.required_points || 0));
const promoterCode = computed(() => routeQuery.value.promoter_code || '');
const campaign = computed(() => routeQuery.value.campaign || '');
const channel = computed(() => routeQuery.value.channel || 'h5');
const currentPoints = computed(() => state.points?.balance ?? 0);
const canUseBilling = computed(() => Boolean(isRegisteredUser.value && state.accessToken && state.user));
const selectedPackage = computed(() => packages.value.find((item) => item.package_key === selectedPackageKey.value) || packages.value[0] || null);
const pointsDeficiency = computed(() => Math.max(0, requiredPoints.value - currentPoints.value));
const userNickname = computed(() => displayNickname.value || '易友');
const userIdentityDisplay = computed(() => canUseBilling.value ? '已绑定正式身份' : '未登录浏览态');
const packageGridClass = computed(() => {
  const count = packages.value.length;
  if (count === 5) return 'grid grid-cols-6 gap-2 pt-1';
  if (count === 4 || count === 2) return 'grid grid-cols-2 gap-2 pt-1';
  if (count === 3 || count === 6) return 'grid grid-cols-3 gap-2 pt-1';
  return 'grid grid-cols-1 gap-2 pt-1';
});
const pageStatusMessage = computed(() => {
  if (currentPayment.value?.status === 'provider_unconfigured') {
    return '已创建订单，请联系客服完成支付；后台确认收款后，积分会自动到账。';
  }
  if (currentPayment.value?.client_message) {
    return currentPayment.value.client_message;
  }
  return '请根据支付渠道返回的状态继续处理。';
});
const paymentContactReason = computed(() => {
  const order = currentOrder.value;
  const packageTitle = order?.package_title || selectedPackage.value?.title || '充值套餐';
  const amount = order ? `￥${formatMoney(order.amount_cents)}` : '';
  const points = order?.total_points || selectedPackage.value?.total_points || 0;
  const orderText = order?.order_id ? `订单 ${order.order_id}` : '充值订单';
  return `${orderText}，${packageTitle}，${amount}，${points} 积分，用户 ${userNickname.value}`;
});
const unsuccessfulOrderState = computed(() => {
  const orderStatus = currentOrder.value?.status || '';
  const rawOrderStatus = currentOrder.value?.raw_status || '';
  if (rawOrderStatus === 'rejected' || orderStatus === 'refunded') {
    return {
      title: '订单未完成',
      message: '后台已拒绝该充值订单，积分不会到账。请重新选择套餐，或联系客服确认原因。',
    };
  }
  if (orderStatus === 'closed') {
    return {
      title: '订单已关闭',
      message: '该充值订单已关闭，无法继续支付或到账。请重新选择套餐后再次下单。',
    };
  }
  if (orderStatus === 'refund_pending') {
    return {
      title: '订单退款处理中',
      message: '该订单已进入退款处理流程，暂不能继续作为充值订单支付。',
    };
  }
  return null;
});
const paymentErrorTitle = computed(() => unsuccessfulOrderState.value?.title || '账单未能成功结付');
const paymentErrorMessage = computed(() => unsuccessfulOrderState.value?.message || '如果已经扣款或对支付结果有疑问，请联系客服协助核查。');
const paymentErrorContactContext = computed(() => unsuccessfulOrderState.value ? paymentContactReason.value : undefined);

onMounted(async () => {
  await Promise.all([bootstrapApp(), sleep(400)]);
  await syncPageFromIdentity();
});

watch(canUseBilling, async (value, previousValue) => {
  if (value && !previousValue) {
    pageState.value = 'checking';
    await syncPageFromIdentity();
  }
});

watch(routeQuery, () => {
  actionError.value = '';
});

async function syncPageFromIdentity(): Promise<void> {
  if (!canUseBilling.value) {
    pageState.value = 'auth_required';
    return;
  }
  await loadPackages();
  const restored = await restoreOrderFromUrl();
  if (!restored) {
    pageState.value = 'recharge_panel';
  }
}

async function loadPackages(): Promise<void> {
  if (!canUseBilling.value || loadingPackages.value) {
    return;
  }
  loadingPackages.value = true;
  actionError.value = '';
  try {
    packages.value = (await listRechargePackages(requireAccessToken())).items.slice(0, 6);
    recommendPackage();
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    loadingPackages.value = false;
  }
}

function recommendPackage(): void {
  if (packages.value.length === 0) {
    selectedPackageKey.value = null;
    return;
  }
  if (selectedPackageKey.value && packages.value.some((item) => item.package_key === selectedPackageKey.value)) {
    return;
  }
  const sortedPackages = [...packages.value].sort((left, right) => left.total_points - right.total_points);
  const recommended = pointsDeficiency.value > 0
    ? sortedPackages.find((item) => item.total_points >= pointsDeficiency.value)
    : sortedPackages[Math.min(1, sortedPackages.length - 1)];
  selectedPackageKey.value = (recommended || sortedPackages[sortedPackages.length - 1]).package_key;
}

async function restoreOrderFromUrl(): Promise<boolean> {
  const orderId = routeQuery.value.order_id;
  if (!orderId || !canUseBilling.value) {
    return false;
  }
  refreshingStatus.value = true;
  try {
    const response = await getRechargePaymentStatus(requireAccessToken(), orderId);
    currentOrder.value = response.order;
    currentPayment.value = response.latest_payment;
    applyPaymentState();
    return true;
  } catch (error) {
    actionError.value = humanizeError(error);
    return false;
  } finally {
    refreshingStatus.value = false;
  }
}

async function createOrder(): Promise<void> {
  if (!canUseBilling.value) {
    pageState.value = 'auth_required';
    return;
  }
  if (!selectedPackage.value || creatingOrder.value) {
    return;
  }
  creatingOrder.value = true;
  actionError.value = '';
  try {
    const order = await createRechargeOrder(requireAccessToken(), {
      package_key: selectedPackage.value.package_key,
      source: 'h5_recharge_page',
      idempotency_key: buildIdempotencyKey('order', selectedPackage.value.package_key),
      remark: JSON.stringify({
        source: source.value,
        return_to: returnTo.value,
        promoter_code: promoterCode.value || null,
        campaign: campaign.value || null,
        channel: channel.value,
      }),
    });
    currentOrder.value = order;
    updateOrderInUrl(order.order_id);
    await createPaymentForCurrentOrder();
    pageState.value = 'pending_payment';
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    creatingOrder.value = false;
  }
}

async function createPaymentForCurrentOrder(): Promise<void> {
  if (!currentOrder.value) {
    return;
  }
  currentPayment.value = await createRechargePayment(requireAccessToken(), currentOrder.value.order_id, {
    provider: 'wechat_h5',
    payment_method: 'wechat_h5',
    idempotency_key: buildIdempotencyKey('payment', currentOrder.value.order_id),
    return_url: typeof window !== 'undefined' ? window.location.href : null,
    client_context: {
      source: source.value,
      return_to: returnTo.value,
      promoter_code: promoterCode.value || null,
      campaign: campaign.value || null,
      channel: channel.value,
    },
  });
}

async function refreshPaymentStatus(): Promise<void> {
  if (!currentOrder.value || refreshingStatus.value) {
    return;
  }
  refreshingStatus.value = true;
  actionError.value = '';
  try {
    const response = await getRechargePaymentStatus(requireAccessToken(), currentOrder.value.order_id);
    currentOrder.value = response.order;
    currentPayment.value = response.latest_payment;
    applyPaymentState();
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    refreshingStatus.value = false;
  }
}

function applyPaymentState(): void {
  const orderStatus = currentOrder.value?.status;
  const rawOrderStatus = currentOrder.value?.raw_status;
  const paymentStatus = currentPayment.value?.status;
  if (orderStatus === 'paid' || orderStatus === 'completed') {
    pageState.value = 'payment_success';
    void refreshPoints().catch(() => undefined);
    return;
  }
  if (isUnsuccessfulOrderStatus(orderStatus, rawOrderStatus)) {
    pageState.value = 'payment_error';
    return;
  }
  if (paymentStatus === 'paid') {
    pageState.value = 'payment_success';
    void refreshPoints().catch(() => undefined);
    return;
  }
  if (paymentStatus === 'failed' || paymentStatus === 'cancelled') {
    pageState.value = 'payment_error';
    return;
  }
  pageState.value = 'pending_payment';
}

function isUnsuccessfulOrderStatus(orderStatus: string | undefined, rawOrderStatus: string | null | undefined): boolean {
  return rawOrderStatus === 'rejected' || orderStatus === 'refunded' || orderStatus === 'closed' || orderStatus === 'refund_pending';
}

function goToProfile(): void {
  emit('navigate-to-tab', 'profile');
}

function returnAfterPayment(): void {
  emit('navigate-to-tab', returnTo.value === 'phone' ? 'phone' : 'profile');
}

function showCurrentPayment(): void {
  if (currentPayment.value) {
    applyPaymentState();
  }
}

async function openUnifiedAuth(): Promise<void> {
  actionError.value = '';
  const authenticated = await requestRegisteredUser('充值');
  if (authenticated) {
    await syncPageFromIdentity();
  }
}

function openCustomerService(scene: string | Event = 'recharge_help', context?: string): void {
  openCustomerServiceModal(typeof scene === 'string' ? scene : 'recharge_help', context);
}

function updateOrderInUrl(orderId: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  const url = new URL(window.location.href);
  url.searchParams.set('order_id', orderId);
  window.history.replaceState(window.history.state, '', `${url.pathname}${url.search}${url.hash}`);
}

function clearOrderInUrl(): void {
  if (typeof window === 'undefined') {
    return;
  }
  const url = new URL(window.location.href);
  url.searchParams.delete('order_id');
  window.history.replaceState(window.history.state, '', `${url.pathname}${url.search}${url.hash}`);
}

function resetToRechargePanel(): void {
  currentOrder.value = null;
  currentPayment.value = null;
  actionError.value = '';
  clearOrderInUrl();
  recommendPackage();
  pageState.value = 'recharge_panel';
}

function packageSpanClass(index: number): string {
  return packages.value.length === 5 ? (index < 3 ? 'col-span-2' : 'col-span-3') : 'col-span-1';
}

function isHorizontalPackageLayout(): boolean {
  return [1, 2, 4].includes(packages.value.length);
}

function formatMoney(cents: number): string {
  const amount = cents / 100;
  return Number.isInteger(amount) ? String(amount) : amount.toFixed(2);
}

function getPaymentStatusLabel(value: string | undefined): string {
  const statusMap: Record<string, string> = {
    pending: '待支付',
    provider_unconfigured: '待联系客服支付',
    paid: '已支付',
    failed: '支付失败',
    cancelled: '已取消',
  };
  return statusMap[value || ''] || '支付交易待创建';
}

function requireAccessToken(): string {
  if (!state.accessToken) {
    throw new Error('auth_required');
  }
  return state.accessToken;
}

function buildIdempotencyKey(kind: string, seed: string): string {
  return `h5_recharge:${kind}:${seed}:${Date.now()}`;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
</script>

<template>
  <div class="min-h-screen bg-brand-paper pb-24 font-sans text-brand-ink antialiased">
    <div class="pt-4 pb-10 px-2 max-w-md mx-auto space-y-3.5">
      <div class="flex justify-start px-1">
        <button
          type="button"
          class="rounded-full bg-white/90 border border-brand-primary/8 px-3.5 py-1.5 text-[10.5px] font-bold text-brand-primary shadow-sm backdrop-blur-sm hover:bg-brand-primary/[0.04] active:scale-[0.98] transition-all cursor-pointer outline-none"
          @click="goToProfile"
        >
          返回个人中心
        </button>
      </div>

      <div class="bg-[#1C1A17] text-[#EDE7DE] rounded-2xl p-5 relative overflow-hidden shadow-xs text-left border border-[#D4C3A3]/10">
        <div class="absolute right-[-15px] bottom-[-25px] text-white/[0.02] font-serif font-black text-[120px] pointer-events-none select-none">
          ☯
        </div>

        <div class="relative z-10 flex items-center justify-between gap-4">
          <div class="space-y-0.5 min-w-0">
            <p class="text-[9.5px] font-medium text-gray-400 uppercase tracking-wider">我的积分钱包 · 结余</p>
            <div class="flex items-baseline gap-1">
              <span class="font-serif text-[32px] font-extrabold text-brand-accent leading-none">{{ currentPoints }}</span>
              <span class="text-[10px] opacity-70 font-semibold ml-0.5">分</span>
            </div>
          </div>

          <div class="shrink-0">
            <div
              v-if="canUseBilling"
              class="bg-white/[0.04] border border-white/[0.05] px-3 py-2 rounded-xl text-right max-w-[11.5rem]"
            >
              <p class="text-[11px] font-serif font-bold text-white leading-snug truncate">
                {{ userNickname }} | {{ userIdentityDisplay }}
              </p>
            </div>
            <button
              v-else
              type="button"
              class="h-9 px-4 rounded-xl bg-brand-accent hover:bg-brand-accent/90 text-brand-ink-strong text-[11.5px] font-black shadow-xs border border-[#D4C3A3]/20 active:scale-[0.98] transition-all cursor-pointer outline-none"
              @click="openUnifiedAuth"
            >
              登录
            </button>
          </div>
        </div>

        <div v-if="pointsDeficiency > 0" class="relative z-10 pt-3 border-t border-white/[0.05] flex items-center justify-between text-[10.5px] text-brand-accent mt-3">
          <span class="font-medium flex items-center gap-1">
            <span>☯ 当前功能还差 {{ pointsDeficiency }} 积分</span>
          </span>
          <span class="bg-white/10 text-gray-200 px-2 py-0.5 rounded text-[9.5px] font-bold">
            本次所需 {{ requiredPoints }} 分
          </span>
        </div>
      </div>

      <div v-if="pageState === 'checking'" class="py-24 text-center space-y-4 animate-in">
        <div class="relative w-12 h-12 mx-auto">
          <Loader2 class="w-12 h-12 text-brand-primary animate-spin opacity-50" />
          <div class="absolute inset-0 flex items-center justify-center font-serif font-black text-xs text-brand-primary">
            ☯
          </div>
        </div>
        <div class="space-y-1">
          <p class="font-serif font-bold text-brand-ink-strong text-xs">正在连接资产账户...</p>
          <p class="text-[10px] text-brand-secondary">校准当前已绑定的用户身份与积分记录</p>
        </div>
      </div>

      <div v-else-if="pageState === 'auth_required'" class="space-y-4 animate-in">
        <div class="bg-amber-500/[0.03] border border-amber-500/10 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle class="text-amber-600 shrink-0 mt-0.5" :size="16" />
          <div class="text-left space-y-1">
            <h4 class="text-xs font-bold text-amber-950 font-serif">请先验证您的常用身份</h4>
            <p class="text-[10px] text-amber-800 leading-relaxed font-sans">
              为防止更换设备或清除缓存导致资产丢失，充值前需要先完成登录，获取您的个人信息。
            </p>
          </div>
        </div>

        <div class="bg-white rounded-xl p-5 border border-brand-primary/5 shadow-xs space-y-4">
          <h3 class="text-xs font-bold text-brand-ink-strong border-b border-brand-primary/5 pb-2.5 font-serif flex items-center gap-1.5 justify-start">
            <span class="text-brand-primary">☯</span>
            <span>登录认证</span>
          </h3>

          <div class="space-y-3 text-left">
            <div class="bg-brand-primary/[0.025] border border-brand-primary/8 p-3 rounded-lg space-y-1.5 text-[10.5px] text-brand-secondary leading-relaxed font-sans">
              <p>未登录浏览态仅用于浏览页面，不能创建充值订单。</p>
              <p>登录后，积分、评测记录和支付结果会稳定绑定到您的正式账号。</p>
            </div>

            <button
              type="button"
              class="w-full py-3 bg-brand-primary hover:bg-brand-primary/95 text-white font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 cursor-pointer transition-all outline-none"
              @click="openUnifiedAuth"
            >
              <span>手机号登录/注册后继续</span>
            </button>

            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary/[0.01] border border-brand-primary/5 text-brand-secondary font-medium rounded-lg text-[10.5px] flex items-center justify-center cursor-pointer transition-colors outline-none"
              @click="openCustomerService('recharge_help')"
            >
              <span>联系客服获取协助</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="pageState === 'recharge_panel'" class="space-y-4 animate-in">
        <div v-if="campaign" class="bg-brand-primary/[0.02] border border-brand-primary/5 rounded-xl p-3 flex justify-between items-center text-left">
          <span class="text-brand-ink-strong text-xs font-semibold flex items-center gap-1.5">
            <span class="text-brand-primary">☯</span>
            <span>活动通路已关联（{{ campaign }}）</span>
          </span>
          <span class="text-[8px] bg-brand-primary text-white px-1.5 py-0.5 rounded font-bold scale-90">已关联</span>
        </div>

        <div class="space-y-3">
          <div class="flex justify-between items-center px-1">
            <h3 class="text-xs font-bold text-brand-ink-strong uppercase tracking-wider font-serif">请选择助运积分充值套餐</h3>
            <span class="text-[10px] text-brand-secondary font-mono">到账以支付状态为准</span>
          </div>

          <div v-if="loadingPackages" class="py-8 flex items-center justify-center gap-2 text-brand-secondary text-xs">
            <Loader2 :size="16" class="animate-spin" />
            <span>正在读取套餐配置...</span>
          </div>

          <div v-else-if="packages.length === 0" class="bg-amber-500/[0.03] border border-amber-500/10 rounded-xl p-4 text-[11px] text-amber-800 leading-relaxed">
            当前渠道暂无可用套餐，请联系客服确认充值入口是否开放。
          </div>

          <div v-else :class="packageGridClass">
            <button
              v-for="(item, index) in packages"
              :key="item.package_key"
              type="button"
              class="relative bg-white border rounded-xl px-2.5 py-3 flex flex-col items-center justify-center text-center cursor-pointer select-none transition-all duration-150 min-h-[76px]"
              :class="[
                packageSpanClass(index),
                selectedPackageKey === item.package_key
                  ? 'border-brand-primary bg-brand-primary/[0.03] ring-1 ring-brand-primary shadow-xs'
                  : 'border-brand-primary/10 hover:border-brand-primary/25 lg:hover:shadow-xs',
              ]"
              @click="selectedPackageKey = item.package_key"
            >
              <div
                v-if="item.title"
                class="absolute -top-2 left-1/2 transform -translate-x-1/2 text-[9px] font-black tracking-wider px-2 py-0.5 rounded-full z-10 whitespace-nowrap shadow-xs scale-90"
                :class="selectedPackageKey === item.package_key
                  ? 'bg-brand-primary text-white'
                  : 'bg-brand-primary/5 text-brand-primary border border-brand-primary/15'"
              >
                {{ item.title }}
              </div>

              <div v-if="isHorizontalPackageLayout()" class="w-full flex items-center justify-center gap-3 px-0.5">
                <div class="flex items-center justify-center shrink-0">
                  <span class="text-[10px] opacity-75 font-serif select-none mr-0.5" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-secondary/80'">☯</span>
                  <span class="font-serif text-[16px] font-black leading-none" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-ink-strong'">
                    {{ item.total_points }}
                  </span>
                  <span class="text-[8.5px] text-brand-secondary/65 font-serif scale-90 ml-0.5">分</span>
                </div>
                <div class="h-4 w-px bg-brand-primary/15 shrink-0"></div>
                <div class="flex items-center justify-center shrink-0">
                  <span class="text-[10px] text-brand-primary/70 font-sans font-bold mr-0.5 select-none">￥</span>
                  <span class="text-[16px] font-serif font-black text-brand-primary leading-none">{{ formatMoney(item.price_cents) }}</span>
                  <span class="text-[8.5px] text-transparent select-none scale-90 ml-0.5">分</span>
                </div>
              </div>

              <div v-else class="w-full flex flex-col items-center justify-center space-y-1.5">
                <div class="flex items-center justify-center leading-none">
                  <span class="text-[10px] opacity-75 font-serif shrink-0 mr-0.5" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-secondary/80'">☯</span>
                  <span class="font-serif text-[15.5px] font-black" :class="selectedPackageKey === item.package_key ? 'text-brand-primary' : 'text-brand-ink-strong'">
                    {{ item.total_points }}
                  </span>
                  <span class="text-[8.5px] text-brand-secondary/65 font-serif scale-90 ml-0.5">分</span>
                </div>
                <div class="flex items-center justify-center leading-none">
                  <span class="text-[10px] text-brand-primary/70 font-sans font-bold mr-0.5 select-none">￥</span>
                  <span class="font-serif text-[15.5px] font-black text-brand-primary">{{ formatMoney(item.price_cents) }}</span>
                  <span class="text-[8.5px] text-transparent select-none scale-90 ml-0.5">分</span>
                </div>
              </div>
            </button>
          </div>
        </div>

        <div v-if="selectedPackage" class="bg-white border border-brand-primary/5 rounded-xl p-4.5 shadow-xs space-y-3.5 text-left">
          <div class="flex justify-between items-center text-xs">
            <div class="flex items-center gap-1">
              <span class="text-brand-secondary font-medium">已选积分：</span>
              <span class="font-serif font-black text-brand-ink-strong text-sm">{{ selectedPackage.total_points }} 积分</span>
            </div>
            <div class="font-mono flex items-center gap-1">
              <span class="text-brand-secondary font-medium">实付：</span>
              <span class="text-base font-extrabold text-brand-primary">￥{{ formatMoney(selectedPackage.price_cents) }}</span>
            </div>
          </div>

          <div v-if="promoterCode" class="text-[9.5px] bg-[#07C160]/5 text-[#07be5e] border border-[#07C160]/10 p-2.5 rounded-lg flex items-center justify-between">
            <span class="font-semibold flex items-center gap-1">
              <span>👤 推广邀请码：{{ promoterCode }}</span>
            </span>
            <span class="font-bold scale-90 origin-right">已关联归属</span>
          </div>

          <div class="space-y-2">
            <button
              type="button"
              class="w-full py-3 bg-brand-primary hover:bg-brand-primary/95 text-white font-serif font-semibold rounded-lg text-center text-xs cursor-pointer shadow-sm select-none transition-colors outline-none flex items-center justify-center gap-1.5"
              @click="currentPayment ? showCurrentPayment() : createOrder()"
            >
              <span>{{ currentPayment ? '查看当前支付状态' : '立即下单去支付' }}</span>
              <ArrowRight :size="13" />
            </button>
            <p class="text-[9px] text-center text-brand-secondary leading-relaxed">
              确认即代表您已阅读并接受充值服务规则
            </p>
          </div>
        </div>

        <div class="bg-brand-primary/[0.01] border border-brand-primary/5 rounded-xl p-4 text-left text-[10.5px] text-brand-secondary leading-relaxed">
          <p>充值订单与手机号、微信 ID 绑定，可跨平台使用</p>
        </div>
      </div>

      <div v-else-if="pageState === 'pending_payment'" class="space-y-4 animate-in">
        <div class="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4 text-left flex gap-3">
          <Loader2 class="text-indigo-600 shrink-0 mt-0.5 animate-spin" :size="16" />
          <div class="space-y-0.5 min-w-0">
            <h4 class="text-xs font-bold text-indigo-950 font-serif">充值账单已经创建，等待客服确认收款</h4>
            <p class="text-[10.5px] text-indigo-900/90 leading-relaxed font-sans font-mono break-all">
              单号：{{ currentOrder?.order_id }}
            </p>
          </div>
        </div>

        <div class="bg-white border border-brand-primary/5 rounded-xl p-5 shadow-xs text-left space-y-4">
          <div class="border-b border-brand-primary/5 pb-2.5">
            <h3 class="text-[10px] font-bold text-brand-secondary uppercase tracking-widest font-serif mb-1">支付清单明细</h3>
            <p class="text-sm font-black text-brand-ink-strong">
              助运积分充值（{{ selectedPackage?.total_points || currentOrder?.total_points }} 积分）
            </p>
          </div>

          <div class="space-y-2 text-xs font-sans text-brand-ink">
            <div class="flex justify-between items-center gap-3">
              <span class="text-brand-secondary">绑定用户账号：</span>
              <span class="font-mono font-bold text-right">{{ userNickname }}</span>
            </div>
            <div class="flex justify-between items-center gap-3">
              <span class="text-brand-secondary">获得可用积分：</span>
              <span class="font-bold text-brand-primary font-serif">{{ selectedPackage?.total_points || currentOrder?.total_points }} 积分</span>
            </div>
            <div class="flex justify-between items-center gap-3">
              <span class="text-brand-secondary">当前支付状态：</span>
              <span class="font-bold text-brand-ink-strong">{{ getPaymentStatusLabel(currentPayment?.status) }}</span>
            </div>
            <div class="flex justify-between items-center border-t border-dashed border-gray-100 mt-2.5 pt-2.5 gap-3">
              <span class="text-brand-secondary font-semibold">应付金额：</span>
              <span class="font-mono font-black text-brand-primary text-base">￥{{ formatMoney(currentOrder?.amount_cents || 0) }}</span>
            </div>
          </div>

          <div class="p-3.5 rounded-lg bg-amber-500/[0.02] border border-amber-300/30 text-[10px] leading-relaxed text-amber-900 font-sans">
            <p class="font-bold text-amber-950 pb-1 mb-1 border-b border-amber-200/40 select-none">
              当前支付说明
            </p>
            <p>{{ pageStatusMessage }}</p>
          </div>

          <div class="space-y-2 pt-1">
            <button
              type="button"
              class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-center text-xs cursor-pointer shadow-xs select-none transition-all outline-none flex items-center justify-center gap-1.5 disabled:opacity-60"
              :disabled="refreshingStatus"
              @click="refreshPaymentStatus"
            >
              <RefreshCw :size="13" :class="refreshingStatus ? 'animate-spin' : ''" />
              <span>刷新支付状态</span>
            </button>

            <button
              type="button"
              class="w-full py-2.5 bg-amber-400 hover:bg-amber-500 text-amber-950 border border-amber-300 font-bold rounded-lg text-center text-xs cursor-pointer select-none transition-all outline-none flex items-center justify-center gap-1"
              @click="openCustomerService('payment_issue', paymentContactReason)"
            >
              <span>联系客服进行支付</span>
            </button>

            <button
              type="button"
              class="w-full py-2 bg-brand-primary/[0.01] border border-brand-primary/5 hover:bg-brand-primary/[0.03] text-brand-secondary font-medium rounded-lg text-center text-[10.5px] cursor-pointer outline-none transition-all"
              @click="resetToRechargePanel"
            >
              重新挑选其他套餐
            </button>
          </div>
        </div>
      </div>

      <div v-else class="space-y-4 animate-in">
        <div v-if="pageState === 'payment_success'" class="bg-white border border-brand-primary/5 rounded-xl p-5 shadow-xs text-center space-y-5">
          <div class="w-10 h-10 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <Check class="stroke-[3]" :size="18" />
          </div>

          <div class="space-y-1">
            <h3 class="font-serif font-bold text-brand-ink-strong text-sm">积分已存入余额</h3>
            <p class="text-[11px] text-brand-secondary leading-relaxed px-4">
              本次充值积分已经进入您的钱包，可以返回继续使用相关功能。
            </p>
          </div>

          <div class="bg-brand-primary/[0.01] p-3.5 rounded-lg border border-brand-primary/5 text-left text-[11px] space-y-2 font-sans">
            <div class="flex justify-between gap-3">
              <span class="text-brand-secondary">订单单号：</span>
              <span class="font-mono text-brand-ink-strong break-all text-right">{{ currentOrder?.order_id }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-brand-secondary">支付金额：</span>
              <span class="font-mono font-bold text-emerald-600">￥{{ formatMoney(currentOrder?.amount_cents || 0) }}</span>
            </div>
            <div class="flex justify-between border-t border-brand-primary/5 mt-1.5 pt-1.5">
              <span class="font-bold text-brand-ink-strong">当前可用余额：</span>
              <span class="font-mono font-bold text-brand-primary font-serif">{{ currentPoints }} 积分</span>
            </div>
          </div>

          <div class="space-y-2 pt-1">
            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-serif font-bold rounded-lg text-center text-xs cursor-pointer shadow-xs select-none transition-all outline-none"
              @click="returnAfterPayment"
            >
              确定并返回继续使用
            </button>
            <button
              type="button"
              class="w-full py-2 bg-brand-primary/[0.01] border border-brand-primary/5 hover:bg-brand-primary/[0.03] text-brand-secondary font-medium rounded-lg text-center text-[10.5px] cursor-pointer outline-none transition-colors"
              @click="resetToRechargePanel"
            >
              继续购买积分
            </button>
          </div>
        </div>

        <div v-else class="bg-white border border-brand-primary/5 rounded-xl p-5 shadow-xs text-center space-y-5">
          <div class="w-10 h-10 bg-red-50 border border-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto">
            <AlertTriangle :size="18" />
          </div>
          <div class="space-y-1">
            <h3 class="font-serif font-bold text-brand-ink-strong text-xs">{{ paymentErrorTitle }}</h3>
            <p class="text-[11px] text-brand-secondary px-4 leading-relaxed">
              {{ paymentErrorMessage }}
            </p>
          </div>
          <div class="flex flex-col gap-2 pt-1">
            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-serif font-bold rounded-lg text-center text-xs cursor-pointer select-none transition-colors outline-none flex items-center justify-center gap-1.5"
              @click="openCustomerService('payment_issue', paymentErrorContactContext)"
            >
              <span>联系客服核查</span>
            </button>
            <button
              type="button"
              class="w-full py-2 bg-brand-primary/[0.01] border border-brand-primary/5 hover:bg-brand-primary/[0.03] text-brand-secondary font-medium rounded-lg text-center text-[10.5px] cursor-pointer outline-none transition-colors"
              @click="resetToRechargePanel"
            >
              返回重新挑选套餐
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="actionError"
        class="bg-red-500/[0.02] border border-red-500/10 rounded-xl p-3 flex items-start gap-2 text-left text-[10.5px] text-red-800 leading-relaxed animate-in"
      >
        <AlertTriangle :size="14" class="shrink-0 mt-0.5" />
        <span>{{ actionError }}</span>
      </div>

      <div class="bg-white border border-brand-primary/5 rounded-xl p-4 shadow-xs text-left">
        <div class="flex items-center justify-between gap-3">
          <HelpCircle class="text-brand-primary shrink-0 mt-0.5 opacity-60" :size="16" />
          <div class="space-y-1 flex-1 min-w-0">
            <h4 class="text-xs font-bold text-brand-ink-strong font-serif">需要充值协助？</h4>
            <p class="text-[10px] text-brand-secondary leading-relaxed font-sans">
              {{ customerServiceCopyForScene('recharge_help') }}
            </p>
          </div>
          <button
            type="button"
            class="px-3.5 py-2 bg-brand-primary hover:bg-brand-primary/95 text-white text-[10.5px] font-bold rounded-lg cursor-pointer shrink-0 select-none transition-all outline-none shadow-xs"
            @click="openCustomerService"
          >
            联系客服
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation: enter 0.15s cubic-bezier(0.16, 1, 0.3, 1) forwards;
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
</style>
