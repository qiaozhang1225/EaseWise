<script setup lang="ts">
import { computed, ref } from 'vue';
import { ArrowLeft, Check, Coins, MessageSquare, Sparkles } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const { state, openCustomerServiceModal } = useEaseWiseApp();

const activePlanIndex = ref(0);

const plans = [
  { points: 100, price: 19, label: '新手起步礼包', note: '足够进行一次手机号码完整评测 + 三次单项解锁' },
  { points: 300, price: 49, label: '乾坤超值套装', note: '额外赠送 50 积分，可满足全大盘运势测算与大运综评需求', recommend: true },
  { points: 800, price: 99, label: '至尊易数全解', note: '限时加赠 200 积分，畅享四柱八字精算及大语言决策智能体无限聊天' },
];

const selectedPlan = computed(() => plans[activePlanIndex.value]);

function handleRechargeSubmit(): void {
  const plan = selectedPlan.value;
  openCustomerServiceModal('points_insufficient', `用户充值：选择方案 ${plan.label}，面额 ${plan.price} 元，对应积分 ${plan.points}`);
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
        <span>返回首页</span>
      </button>
    </div>

    <div class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm mb-4 space-y-4">
      <div class="flex items-center gap-3">
        <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0">
          <Coins :size="20" />
        </div>
        <div>
          <h2 class="font-serif text-[17px] font-black text-brand-ink-strong leading-tight">获取易理积分</h2>
          <p class="font-sans text-[10.5px] text-brand-secondary mt-0.5">
            充值额度，开启深层天机奇门排盘。
          </p>
        </div>
      </div>

      <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">
        EaseWise 采用「易理积分」机制，支持手机号码评测大盘分析、八字推盘解锁、大运流年综评、以及决策智能体深度对话。
        您可以根据需求，兑换下方的积分充值包。
      </p>
    </div>

    <!-- Recharge plans list -->
    <div class="space-y-3 mb-4">
      <button
        v-for="(plan, index) in plans"
        :key="plan.label"
        @click="activePlanIndex = index"
        class="w-full bg-white border rounded-2xl p-4 text-left transition-all relative overflow-hidden flex items-center gap-4 cursor-pointer outline-none"
        :class="activePlanIndex === index
          ? 'border-brand-primary shadow-md ring-1 ring-brand-primary/20'
          : 'border-gray-100 shadow-sm hover:border-brand-primary/20 hover:bg-slate-50/20'"
      >
        <div
          v-if="plan.recommend"
          class="absolute top-0 right-0 bg-brand-primary text-white font-sans text-[8.5px] font-extrabold px-2.5 py-0.5 rounded-bl-lg uppercase tracking-wide"
        >
          官方推荐
        </div>

        <div class="w-10 h-10 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0 flex items-center justify-center">
          <Coins :size="20" />
        </div>

        <div class="flex-1 min-w-0 pr-12">
          <span class="font-serif text-[15px] font-black text-brand-ink-strong leading-none flex items-center gap-1.5">
            {{ plan.points }} 积分
            <span class="text-[11px] text-brand-secondary">({{ plan.label }})</span>
          </span>
          <p class="font-sans text-[10px] text-brand-secondary leading-relaxed mt-1.5 pr-2">{{ plan.note }}</p>
        </div>

        <div class="shrink-0 text-right">
          <span class="font-serif text-[18px] font-black text-brand-primary-strong">￥{{ plan.price }}</span>
        </div>
      </button>
    </div>

    <button
      @click="handleRechargeSubmit"
      class="w-full bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3.5 rounded-2xl cursor-pointer font-sans text-[13px] font-extrabold shadow-md active:scale-[0.985] transition-all flex items-center justify-center gap-2 outline-none"
    >
      <MessageSquare :size="15" />
      <span>联系专属客服完成现金兑付结算</span>
    </button>
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
