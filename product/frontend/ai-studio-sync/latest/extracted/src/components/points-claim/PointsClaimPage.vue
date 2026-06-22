<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  getPublicPointsClaimLink, claimPublicPoints
} from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import {
  Sparkles, CheckCircle, Gift, AlertCircle, RefreshCw, Milestone, Coins
} from 'lucide-vue-next';

const props = defineProps<{
  routeQuery?: Record<string, string>;
}>();

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string): void;
}>();

const { state, refreshPoints } = useEaseWiseApp();

const claimCode = ref('claim_999'); // Default mock code
const claimInfo = ref<any | null>(null);
const loading = ref(false);
const claiming = ref(false);

const errorMsg = ref<string | null>(null);
const successAmount = ref<number | null>(null);

async function loadClaimLink() {
  // Pull claim code from URL/state if present
  if (props.routeQuery?.code) {
    claimCode.value = props.routeQuery.code;
  }

  loading.value = true;
  errorMsg.value = null;
  successAmount.value = null;

  try {
    const info = await getPublicPointsClaimLink(claimCode.value, state.accessToken);
    claimInfo.value = info;
  } catch (err: any) {
    // If accessToken not loaded yet or offline, we mock the default
    claimInfo.value = {
      claim_link_id: "claim_999",
      claim_code: "claim_999",
      title: "新客专享回归礼包",
      points_amount: 100,
      enabled: true,
      claims_count: 5
    };
  } finally {
    loading.value = false;
  }
}

async function handleClaim() {
  if (claiming.value) return;

  claiming.value = true;
  errorMsg.value = null;
  successAmount.value = null;

  try {
    const res = await claimPublicPoints(state.accessToken || '', claimCode.value);
    successAmount.value = res.points_amount;
    void refreshPoints();
  } catch (err: any) {
    errorMsg.value = err.message || "每个账户限领一次，您可能已经领过或此福利码已过期。";
  } finally {
    claiming.value = false;
  }
}

onMounted(() => {
  void loadClaimLink();
});
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left h-[calc(100vh-80px)] flex flex-col justify-center">
    <!-- Red envelope box container -->
    <div class="bg-gradient-to-b from-red-650 to-red-800 rounded-3xl p-6.5 text-center text-white border-4 border-amber-400/60 shadow-2xl relative overflow-hidden flex flex-col items-center">

      <!-- Metaphysics background watermarks -->
      <div class="absolute -top-12 -right-12 w-32 h-32 rounded-full border border-white/10 select-none pointer-events-none"></div>
      <div class="absolute -bottom-12 -left-12 w-36 h-36 rounded-full border border-white/5 select-none pointer-events-none"></div>

      <!-- Icon -->
      <div class="w-16 h-16 rounded-full bg-amber-400 text-red-700 flex items-center justify-center shadow-lg font-bold mb-4 shrink-0 border-2 border-amber-300">
        <Gift :size="32" class="animate-pulse" />
      </div>

      <!-- Redpacket title -->
      <h2 class="font-serif text-[24px] font-black text-amber-300 tracking-wide select-none">
        易如反掌吉祥礼
      </h2>
      <p class="font-sans text-[11px] text-red-100 select-none mix-blend-plus-lighter tracking-wider uppercase mt-1">
        METAPHYSICS POINTS RED PACKET
      </p>

      <!-- Envelope slit division line -->
      <div class="w-full my-6 border-b border-dashed border-red-500/70 relative">
        <div class="absolute left-1/2 -translate-x-1/2 -top-2.5 bg-amber-400 text-red-800 font-serif text-[10px] font-extrabold px-3.5 py-0.5 rounded-full shadow-sm">
          福运广置
        </div>
      </div>

      <!-- Active Content view -->
      <div class="w-full flex-1 flex flex-col justify-center min-h-[140px]">
        <!-- 1. LOADING -->
        <div v-if="loading" class="space-y-2 py-4 flex flex-col items-center">
          <RefreshCw class="animate-spin text-amber-400" :size="24" />
          <p class="font-serif text-[12.5px] text-red-200">正在接引喜气福礼...</p>
        </div>

        <!-- 2. SUCCESS STATE -->
        <div v-else-if="successAmount" class="space-y-4 py-3 text-center animate-fadeIn">
          <div class="inline-flex items-center justify-center p-2 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-1">
            <CheckCircle :size="20" />
          </div>
          <h3 class="font-serif text-[19px] font-bold text-amber-300">恭喜尊驾，福喜已致！</h3>

          <div class="flex items-baseline justify-center gap-1">
            <span class="font-serif text-[38px] font-black text-amber-300">{{ successAmount }}</span>
            <span class="font-serif text-[14px] text-amber-200">学分</span>
          </div>

          <p class="font-sans text-[11.5px] text-red-100 leading-relaxed px-5">
            积分已成功录入您的同修账户。您现在可以立刻消耗积分开始「手机奇门推论」或「八字运程排盘」！
          </p>

          <button
            @click="emit('navigate-to-tab', 'home')"
            class="w-full bg-amber-400 hover:bg-amber-350 text-red-900 border-none font-sans text-[13px] font-bold py-3 rounded-2xl cursor-pointer shadow-md active:scale-95 transition-transform"
          >
            回主页开始测算
          </button>
        </div>

        <!-- 3. ERROR STATE -->
        <div v-else-if="errorMsg" class="space-y-4 py-3 text-center animate-fadeIn">
          <div class="inline-flex items-center justify-center p-2 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/20 mb-1">
            <AlertCircle :size="20" />
          </div>
          <h3 class="font-serif text-[16px] font-bold text-amber-200">喜气福礼接引受阻</h3>
          <p class="font-sans text-[11.5px] text-red-100 leading-relaxed px-5">
            {{ errorMsg }}
          </p>
          <div class="flex gap-2">
            <button
              @click="loadClaimLink()"
              class="flex-1 bg-red-800/80 hover:bg-red-800 text-amber-200 border border-amber-400/25 font-sans text-[12.5px] font-bold py-2.5 rounded-xl cursor-pointer"
            >
              重试接引
            </button>
            <button
              @click="emit('navigate-to-tab', 'home')"
              class="flex-1 bg-amber-400 hover:bg-amber-350 text-red-950 border-none font-sans text-[12.5px] font-bold py-2.5 rounded-xl cursor-pointer"
            >
              回主页
            </button>
          </div>
        </div>

        <!-- 4. ACTIVE INITIAL STATE -->
        <div v-else-if="claimInfo" class="space-y-4 py-2 text-center animate-fadeIn">
          <h3 class="font-serif text-[18px] font-bold text-amber-300">
            {{ claimInfo.title }}
          </h3>

          <div class="flex items-baseline justify-center gap-1 py-1">
            <span class="font-serif text-[42px] font-black text-amber-300">{{ claimInfo.points_amount }}</span>
            <span class="font-serif text-[13.5px] text-amber-200 font-extrabold">学分</span>
          </div>

          <p class="font-sans text-[11.5px] text-red-100/90 max-w-[85%] mx-auto leading-relaxed select-none">
            易学回归特惠，添加官方微信客服，即可一键领取此项专属修行大礼，绝无门槛消耗！
          </p>

          <button
            @click="handleClaim()"
            :disabled="claiming"
            class="w-full bg-amber-400 hover:bg-amber-350 text-red-900 font-sans text-[13px] font-bold py-3 rounded-2xl cursor-pointer shadow-lg active:scale-95 transition-transform border-none select-none flex items-center justify-center gap-1.5"
          >
            <RefreshCw v-if="claiming" class="animate-spin text-red-900" :size="14" />
            <span>{{ claiming ? '正在叩问喜礼中...' : '拆开红包 · 领取积分' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.from-red-650 {
  --tw-gradient-from: #b91c1c;
  --tw-gradient-to: rgba(185, 28, 28, 0);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}
.to-red-800 {
  --tw-gradient-to: #991b1b;
}

.animate-fadeIn {
  animation: fadeIn 0.25s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97) translateY(4px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
