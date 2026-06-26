<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { 
  ArrowLeft, Coins, CheckCircle2, ChevronRight, Upload, AlertCircle, ShoppingBag, 
  Loader2, BadgeHelp
} from 'lucide-vue-next';
import { 
  listRechargePackages, createRechargeOrder, createRechargePayment, 
  getRechargePaymentStatus 
} from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const props = defineProps<{
  routeQuery?: Record<string, string>;
}>();

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string): void;
}>();

const { state, refreshPoints } = useEaseWiseApp();

const packages = ref<any[]>([]);
const selectedPackageKey = ref('');
const loadingPackages = ref(false);

const paymentMethod = ref<'wechat' | 'offline'>('wechat');
const proofUrlInput = ref(''); // Mocking payment proof
const remarkInput = ref('');

const placingOrder = ref(false);
const activeOrder = ref<any | null>(null);
const orderStatusInfo = ref('');

const toastMsg = ref<string | null>(null);

function showToast(text: string) {
  toastMsg.value = text;
  setTimeout(() => toastMsg.value = null, 2500);
}

async function loadPackages() {
  loadingPackages.value = true;
  try {
    const res = await listRechargePackages(state.accessToken || '');
    packages.value = res.items;
    if (res.items.length > 0) {
      selectedPackageKey.value = res.items[0].package_key;
    }
  } catch (error) {
    // If accessToken not available yet, we fallback to pricing package
    packages.value = [
      { package_key: 'pkg_10', title: '10积分优惠包', points_amount: 10, price_cents: 600, display_price: "¥6.00" },
      { package_key: 'pkg_50', title: '50积分超值包', points_amount: 50, price_cents: 2500, display_price: "¥25.00" },
      { package_key: 'pkg_100', title: '100积分尊享包', points_amount: 100, price_cents: 4500, display_price: "¥45.00" },
      { package_key: 'pkg_500', title: '500大财运包', points_amount: 500, price_cents: 19800, display_price: "¥198.00" },
    ];
    selectedPackageKey.value = 'pkg_10';
  } finally {
    loadingPackages.value = false;
  }
}

async function handleCheckout() {
  if (!selectedPackageKey.value || placingOrder.value) return;
  
  placingOrder.value = true;
  try {
    // 1. Create Order
    const orderPayload = {
      package_key: selectedPackageKey.value,
      proof_url: paymentMethod.value === 'offline' ? (proofUrlInput.value || 'https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&w=150&q=80') : null,
      remark: remarkInput.value || 'H5 shop'
    };

    const order = await createRechargeOrder(state.accessToken || '', orderPayload);
    activeOrder.value = order;
    
    // 2. Trigger Payment execution
    const payRes = await createRechargePayment(state.accessToken || '', order.id, {
      payment_method: paymentMethod.value === 'wechat' ? 'wechat_h5' : 'offline_upload',
      proof_url: orderPayload.proof_url
    });

    if (paymentMethod.value === 'wechat') {
      showToast("微信快捷模拟支付成功，已到账！");
      void refreshPoints();
      setTimeout(() => {
        emit('navigate-to-tab', 'profile');
      }, 1500);
    } else {
      showToast("线下付款账单凭证已提交，请静候元老审核！");
      orderStatusInfo.value = 'reviewing';
    }
  } catch (error: any) {
    showToast(error.message || "订单提交失败");
  } finally {
    placingOrder.value = false;
  }
}

onMounted(() => {
  void loadPackages();
});
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left relative">
    <!-- Header control -->
    <div class="flex items-center gap-2 mb-4">
      <button 
        @click="emit('navigate-to-tab', 'profile')"
        class="bg-white border border-gray-150 p-2.5 rounded-xl cursor-pointer hover:bg-zinc-150 flex items-center justify-center outline-none shrink-0"
      >
        <ArrowLeft :size="15" class="text-brand-ink-strong" />
      </button>
      <h2 class="font-serif text-[17.5px] font-bold text-brand-ink-strong">充值账户积分</h2>
    </div>

    <!-- Active order processing banner -->
    <div 
      v-if="activeOrder && activeOrder.status === 'reviewing'"
      class="bg-amber-50 border border-thin border-amber-200 rounded-2xl p-4.5 mb-5 space-y-2 animate-fadeIn"
    >
      <div class="flex items-center gap-2 text-brand-gold-fixed">
        <Loader2 class="animate-spin" :size="16" />
        <span class="font-serif text-[14px] font-bold">转账审核凭证审核中...</span>
      </div>
      <p class="font-sans text-[11.5px] text-brand-secondary leading-relaxed">
        系统已锁存您的订单 <strong class="font-mono text-zinc-700">{{ activeOrder.id }}</strong>。一旦微信或银行凭条核实无误，我们将当即补入 {{ activeOrder.points_amount }} 积分！
      </p>
      <button 
        @click="activeOrder = null"
        class="text-brand-primary-strong font-bold font-sans text-[11px] underline cursor-pointer hover:text-brand-primary"
      >
        继续选购积分包
      </button>
    </div>

    <!-- Toast message popup -->
    <transition name="fade">
      <div v-if="toastMsg" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-1.5 whitespace-nowrap">
        <CheckCircle2 :size="15" />
        <span>{{ toastMsg }}</span>
      </div>
    </transition>

    <!-- Packages Selection list -->
    <section class="mb-5 bg-white rounded-2xl p-5 border border-brand-paper shadow-sm">
      <div class="flex items-center gap-2 mb-4 pb-2 border-b border-gray-50">
        <Coins :size="18" class="text-brand-primary shrink-0" />
        <h3 class="font-serif text-[15px] font-bold text-brand-ink-strong">请选择积分充值套餐</h3>
      </div>

      <div v-if="loadingPackages" class="flex items-center justify-center py-6 text-gray-400">
        <Loader2 class="animate-spin" />
        <span class="text-xs font-serif font-bold ml-1.5">加载黄历优待包中...</span>
      </div>

      <div v-else class="grid grid-cols-2 gap-3.5">
        <button
          v-for="pkg in packages"
          :key="pkg.package_key"
          @click="selectedPackageKey = pkg.package_key"
          class="bg-transparent text-left relative overflow-hidden rounded-2xl p-4 cursor-pointer border-2 transition-all flex flex-col justify-between group outline-none"
          :class="selectedPackageKey === pkg.package_key ? 'border-brand-primary bg-brand-primary/5 shadow-md' : 'border-gray-150 hover:border-gray-200 bg-white'"
        >
          <!-- Spark icon at top corner -->
          <CheckCircle2 
            v-if="selectedPackageKey === pkg.package_key" 
            :size="16" 
            class="absolute top-2.5 right-2.5 text-brand-primary" 
          />

          <span class="font-serif text-[13.5px] font-extrabold text-brand-ink-strong leading-tight select-none">
            {{ pkg.title }}
          </span>

          <div class="mt-4 flex flex-col gap-0.5">
            <span class="font-serif text-[20px] font-black text-brand-ink-strong">
              {{ pkg.display_price || `¥${(pkg.price_cents / 100).toFixed(2)}` }}
            </span>
            <span class="font-sans text-[10.5px] text-brand-secondary font-bold select-none">
              对应 +{{ pkg.points_amount }} 积分
            </span>
          </div>
        </button>
      </div>
    </section>

    <!-- Transfer Methods selection -->
    <section class="mb-5 bg-white rounded-2xl p-5 border border-brand-paper shadow-sm">
      <h3 class="font-serif text-[14.5px] font-bold text-brand-ink-strong mb-3 pb-1 border-b border-gray-50 flex items-center gap-1.5">
        <ShoppingBag :size="16" class="text-brand-primary" />
        <span>支付交易方式</span>
      </h3>

      <div class="space-y-3.5 text-left">
        <!-- WeChat native pay trigger simulation -->
        <label 
          class="flex items-center gap-3 p-3.5 bg-brand-paper/20 rounded-xl border cursor-pointer select-none"
          :class="paymentMethod === 'wechat' ? 'border-brand-primary ring-2 ring-brand-primary/5' : 'border-gray-100'"
        >
          <input 
            type="radio" 
            value="wechat" 
            v-model="paymentMethod" 
            class="accent-brand-primary" 
          />
          <div class="flex-1">
            <span class="font-sans text-[13px] font-extrabold text-brand-ink-strong block">微信闪通支付（模拟沙箱）</span>
            <span class="font-sans text-[10px] text-brand-secondary mt-0.5 block">点击支付即刻核算发币入账</span>
          </div>
        </label>

        <!-- Offline ledger check upload -->
        <label 
          class="flex items-center gap-3 p-3.5 bg-brand-paper/20 rounded-xl border cursor-pointer select-none"
          :class="paymentMethod === 'offline' ? 'border-brand-primary ring-2 ring-brand-primary/5' : 'border-gray-100'"
        >
          <input 
            type="radio" 
            value="offline" 
            v-model="paymentMethod" 
            class="accent-brand-primary" 
          />
          <div class="flex-1">
            <span class="font-sans text-[13px] font-extrabold text-brand-ink-strong block">线下付款凭证上传（转账审核）</span>
            <span class="font-sans text-[10px] text-brand-secondary mt-0.5 block">手动转账后上传截屏收据，提交元老核对</span>
          </div>
        </label>
      </div>

      <!-- Offline payment form -->
      <div 
        v-if="paymentMethod === 'offline'" 
        class="mt-4 p-4.5 bg-zinc-50 border border-gray-100 rounded-xl space-y-3 animate-fadeIn text-left"
      >
        <p class="font-sans text-[11px] text-zinc-600 leading-normal select-none">
          <span class="text-rose-500 font-bold">*</span> 
          转账账户微信：<strong class="text-zinc-800">easewise_support</strong>。转账完成后，请选择一张本设备的交易凭据账页贴入：
        </p>

        <!-- Mock file paste upload -->
        <div class="space-y-1">
          <span class="font-sans text-[11px] font-bold text-zinc-700 block">付款收条图片（URL贴图地址）</span>
          <div class="relative flex items-center">
            <input 
              v-model="proofUrlInput" 
              type="text" 
              placeholder="请粘贴本章收支证据 URL..." 
              class="w-full bg-white px-3 py-2 border rounded-lg text-[11px] font-mono outline-none pr-8 text-zinc-700" 
            />
            <Upload :size="13" class="absolute right-3.5 text-zinc-400" />
          </div>
        </div>

        <div class="space-y-1">
          <span class="font-sans text-[11px] font-bold text-zinc-700 block">附加备注说明</span>
          <input 
            v-model="remarkInput" 
            type="text" 
            placeholder="如：微信转账 微信名xxxx 充值10元..." 
            class="w-full bg-white px-3 py-2 border rounded-lg text-[11px] font-sans outline-none text-zinc-700" 
          />
        </div>
      </div>
    </section>

    <!-- Trigger Buy CTA button -->
    <div class="p-2">
      <button
        @click="handleCheckout()"
        :disabled="placingOrder || !selectedPackageKey"
        class="w-full bg-brand-primary hover:bg-brand-primary/95 text-white py-3.5 rounded-2xl cursor-pointer font-sans text-[13.5px] font-bold shadow-md active:scale-[0.98] transition-transform flex items-center justify-center gap-1.5 border-none"
      >
        <Loader2 v-if="placingOrder" class="animate-spin text-white" :size="15" />
        <span>{{ placingOrder ? '正在开启乾坤机汇...' : '立即确认支付购买' }}</span>
      </button>
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
  animation: fadeIn 0.25s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
