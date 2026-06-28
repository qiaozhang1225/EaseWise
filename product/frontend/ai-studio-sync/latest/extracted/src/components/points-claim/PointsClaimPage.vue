<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { ArrowLeft, CheckCircle2, Coins, Gift, Loader2, Sparkles } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const { state, showToast, claimDailyPoints, bootstrapApp, humanizeError } = useEaseWiseApp();

const loading = ref(false);
const claimedToday = ref(false);
const availablePoints = ref(5);

const user = computed(() => state.user);
const isRegistered = computed(() => !!state.accessToken);

onMounted(() => {
  void bootstrapApp();
  // Simply mock claimed state based on last activity or simple flag
  const lastClaim = localStorage.getItem('last_claim_date');
  const today = new Date().toDateString();
  if (lastClaim === today) {
    claimedToday.value = true;
  }
});

async function handleClaim(): Promise<void> {
  if (claimedToday.value) {
    showToast('您今日已领取过每日福利积分，请明日再来。');
    return;
  }
  loading.value = true;
  try {
    const res = await claimDailyPoints();
    claimedToday.value = true;
    localStorage.setItem('last_claim_date', new Date().toDateString());
    showToast(`恭喜领取成功！已为您注入 ${res.claimed} 分每日福利积分。`);
  } catch (err: any) {
    showToast(humanizeError(err) || '额度注入遇到一些阻碍，请稍后刷新重试');
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left select-none">

    <div class="flex items-center gap-2 mb-4">
      <button
        @click="emit('back')"
        class="text-brand-ink-strong hover:text-brand-primary font-sans text-[12.5px] font-extrabold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none p-1 rounded hover:bg-zinc-100 transition-colors"
      >
        <ArrowLeft :size="16" />
        <span>返回个人中心</span>
      </button>
    </div>

    <div class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm mb-4 space-y-4">
      <div class="flex items-center gap-3">
        <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0">
          <Gift :size="20" />
        </div>
        <div>
          <h2 class="font-serif text-[17px] font-black text-brand-ink-strong leading-tight">每日福利积分领取</h2>
          <p class="font-sans text-[10.5px] text-brand-secondary mt-0.5">
            日拱一卒，天道酬勤。每日均可免费领取体验积分。
          </p>
        </div>
      </div>

      <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">
        秉承互通共享、泽被众生之念，凡在 EaseWise「易如反掌」注册的用户，每日登录后均可在此免费申领福利积分，用以进行数字奇门推演或八字大运的辅助解锁。
      </p>
    </div>

    <!-- Claim Card -->
    <div class="bg-white rounded-2xl p-6 border border-brand-paper shadow-sm text-center space-y-4 mb-4 relative overflow-hidden">
      <div class="absolute -top-12 -right-12 text-brand-primary/[0.02] font-serif font-black text-[130px] pointer-events-none">
        福
      </div>

      <div class="inline-flex items-center justify-center w-14 h-14 rounded-full bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
        <Coins :size="26" />
      </div>

      <div class="space-y-1">
        <span class="text-[10px] text-brand-secondary font-extrabold uppercase tracking-widest block">可领福利点数</span>
        <h3 class="font-serif text-[28px] font-black text-brand-primary-strong leading-none">+{{ availablePoints }} <span class="text-[12px] text-brand-secondary">积分</span></h3>
      </div>

      <div class="pt-2">
        <button
          v-if="!claimedToday"
          @click="handleClaim"
          :disabled="loading"
          class="w-full bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3.5 rounded-2xl cursor-pointer font-sans text-[13px] font-extrabold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-2 outline-none"
        >
          <Loader2 v-if="loading" class="animate-spin text-white" :size="15" />
          <Sparkles v-else :size="15" />
          <span>{{ loading ? '额度注入中，请稍后...' : '立即申领每日功课福利' }}</span>
        </button>

        <div
          v-else
          class="w-full bg-slate-100 text-slate-500 py-3.5 rounded-2xl font-sans text-[13px] font-extrabold flex items-center justify-center gap-2"
        >
          <CheckCircle2 :size="15" />
          <span>今日功课福利已领，请明天再来</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
