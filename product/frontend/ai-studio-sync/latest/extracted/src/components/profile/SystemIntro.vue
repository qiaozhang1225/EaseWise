<script setup lang="ts">
import { ref, computed } from 'vue';
import { ArrowLeft, BookOpen, Percent, Coins, Award, HelpCircle, Sparkles, Check, ChevronRight } from 'lucide-vue-next';

defineEmits<{
  (e: 'close'): void;
}>();

// Calculator state
const targetUsers = ref(50);
const averageRecharge = ref(200);
const partnerLevel = ref<'ambassador' | 'vip' | 'svip'>('ambassador');

const partnerDetails = {
  ambassador: { label: '推广大使', ratio: 0.15 },
  vip: { label: 'VIP 推广大使', ratio: 0.20 },
  svip: { label: 'SVIP 推广大使', ratio: 0.30 }
};

const projectedEarnings = computed(() => {
  const ratio = partnerDetails[partnerLevel.value].ratio;
  return Math.round(targetUsers.value * averageRecharge.value * ratio);
});
</script>

<template>
  <div class="fixed inset-0 z-50 bg-zinc-50 overflow-y-auto no-scrollbar flex flex-col font-sans">
    <!-- Header Navigation -->
    <header class="sticky top-0 z-10 bg-white border-b border-gray-150 px-4 py-3.5 flex items-center justify-between shrink-0">
      <button
        @click="$emit('close')"
        class="flex items-center gap-1.5 text-brand-ink hover:text-brand-primary cursor-pointer border-none bg-transparent outline-none p-1 shrink-0"
      >
        <ArrowLeft :size="18" />
        <span class="text-[14px] font-bold">返回</span>
      </button>
      <h2 class="font-serif text-[15px] font-extrabold text-brand-ink-strong text-center flex-1 pr-6">
        合伙与推广说明书
      </h2>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 max-w-md mx-auto w-full px-4 pt-5 pb-16 space-y-6">

      <!-- Intro Hero Block -->
      <section class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center text-orange-600 font-serif text-[18px] font-bold shrink-0">
            案
          </div>
          <div>
            <h3 class="font-serif text-[16px] font-bold text-brand-ink-strong">商业定价与合伙提成全案</h3>
            <p class="font-sans text-[11px] text-brand-secondary leading-none mt-0.5">易如反掌 EaseWise 服务定价及分销说明</p>
          </div>
        </div>
        <p class="text-[12px] text-brand-ink leading-relaxed mt-3">
          易如反掌立足于正统周易算运及数字格局推导，通过严谨模型为广大同修提供气场指引。
          为建立健康持久的共修生态，本平台特制定本商业定价及推广佣金结算机制。
        </p>
      </section>

      <!-- Pricing Plans -->
      <section class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm text-left">
        <h3 class="font-serif text-[13.5px] font-bold text-brand-ink-strong mb-3.5 flex items-center gap-1.5 border-b border-gray-50 pb-2">
          <Coins :size="15" class="text-brand-primary" />
          <span>服务项目与商业定价</span>
        </h3>

        <div class="space-y-2 text-[12px]">
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-brand-secondary">手机号奇门格局基础评测</span>
            <span class="font-mono font-bold text-brand-ink-strong">100 积分 / 次</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-brand-secondary">生辰八字命局基础推演</span>
            <span class="font-mono font-bold text-brand-ink-strong">120 积分 / 次</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-brand-secondary">奇门/八字专属细项深批</span>
            <span class="font-mono font-bold text-brand-ink-strong">50 积分 / 项</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-brand-secondary">十年大运流变深度详解</span>
            <span class="font-mono font-bold text-brand-ink-strong">80 积分 / 周期</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-brand-secondary">具体极细流年运数精析</span>
            <span class="font-mono font-bold text-brand-ink-strong">30 积分 / 载</span>
          </div>
        </div>

        <div class="mt-4 p-3.5 bg-amber-50/50 rounded-2xl border border-amber-100/50 text-[11px] text-amber-800 leading-relaxed">
          <p class="font-bold mb-1">💡 积分兑换说明：</p>
          <span>标准兑换比例为 <b>1 元 = 10 积分</b>。购买特惠成长包或参与平台活动，享受更优积分兑换红利。</span>
        </div>
      </section>

      <!-- Identity levels -->
      <section class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm text-left">
        <h3 class="font-serif text-[13.5px] font-bold text-brand-ink-strong mb-3.5 flex items-center gap-1.5 border-b border-gray-50 pb-2">
          <Award :size="15" class="text-brand-primary" />
          <span>合伙人等级与佣金比例</span>
        </h3>

        <div class="space-y-4">
          <!-- Tier 1 -->
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center font-bold text-[11px] mt-0.5 shrink-0">
              1
            </div>
            <div>
              <p class="font-serif text-[12.5px] font-bold text-brand-ink-strong flex items-center gap-1.5">
                <span>推广大使</span>
                <span class="px-1.5 py-0.5 bg-amber-100 text-amber-800 text-[9.5px] font-black rounded">提成 15%</span>
              </p>
              <p class="text-[11px] text-brand-secondary mt-0.5 leading-normal">
                <b>核算条件：</b>新用户主动申请或个人累计充值满 <b>398 元</b>，后台审核通过。
              </p>
            </div>
          </div>

          <!-- Tier 2 -->
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center font-bold text-[11px] mt-0.5 shrink-0">
              2
            </div>
            <div>
              <p class="font-serif text-[12.5px] font-bold text-brand-ink-strong flex items-center gap-1.5">
                <span>VIP 推广大使</span>
                <span class="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 text-[9.5px] font-black rounded">提成 20%</span>
              </p>
              <p class="text-[11px] text-brand-secondary mt-0.5 leading-normal">
                <b>核算条件：</b>个人累计充值满 <b>1280 元</b>，或直邀活跃用户数达到 50 人以上。
              </p>
            </div>
          </div>

          <!-- Tier 3 -->
          <div class="flex items-start gap-3">
            <div class="w-6 h-6 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center font-bold text-[11px] mt-0.5 shrink-0">
              3
            </div>
            <div>
              <p class="font-serif text-[12.5px] font-bold text-brand-ink-strong flex items-center gap-1.5">
                <span>SVIP 推广大使</span>
                <span class="px-1.5 py-0.5 bg-purple-100 text-purple-800 text-[9.5px] font-black rounded">提成 30%</span>
              </p>
              <p class="text-[11px] text-brand-secondary mt-0.5 leading-normal">
                <b>核算条件：</b>个人累计充值满 <b>3980 元</b>，或具备强大私域流量在业内有深度共建协议。
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Interactive Calculator -->
      <section class="bg-white rounded-3xl p-5 border border-brand-paper shadow-md text-left">
        <h3 class="font-serif text-[13.5px] font-bold text-brand-ink-strong mb-1 flex items-center gap-1.5">
          <Percent :size="15" class="text-brand-primary" />
          <span>合伙收益精算器</span>
        </h3>
        <p class="text-[10.5px] text-brand-secondary mb-4 leading-none">自主精准估算每月潜在直邀收益分成</p>

        <!-- Silder 1 -->
        <div class="space-y-2 mb-4">
          <div class="flex justify-between items-center text-[12px] font-bold">
            <span class="text-brand-ink">直邀推荐注册活跃人数：</span>
            <span class="font-mono text-brand-primary-strong text-[14px]">{{ targetUsers }} 人</span>
          </div>
          <input
            v-model.number="targetUsers"
            type="range"
            min="10"
            max="500"
            step="10"
            class="w-full accent-brand-primary"
          />
          <div class="flex justify-between text-[10px] text-zinc-400">
            <span>10人</span>
            <span>250人</span>
            <span>500人</span>
          </div>
        </div>

        <!-- Slider 2 -->
        <div class="space-y-2 mb-4">
          <div class="flex justify-between items-center text-[12px] font-bold">
            <span class="text-brand-ink">平均每人累计充值金额：</span>
            <span class="font-mono text-brand-primary-strong text-[14px]">{{ averageRecharge }} 元</span>
          </div>
          <input
            v-model.number="averageRecharge"
            type="range"
            min="50"
            max="1000"
            step="50"
            class="w-full accent-brand-primary"
          />
          <div class="flex justify-between text-[10px] text-zinc-400">
            <span>50元</span>
            <span>500元</span>
            <span>1000元</span>
          </div>
        </div>

        <!-- Level Selector -->
        <div class="mb-5">
          <span class="text-[12px] font-bold text-brand-ink block mb-2">选择考核推广等级：</span>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="(lvl, key) in partnerDetails"
              :key="key"
              @click="partnerLevel = key"
              class="py-2.5 rounded-xl text-[11px] font-bold border outline-none cursor-pointer text-center"
              :class="partnerLevel === key ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper/50 border-gray-150 text-brand-secondary hover:bg-zinc-100'"
            >
              {{ lvl.label }} ({{ lvl.ratio * 100 }}%)
            </button>
          </div>
        </div>

        <!-- Output display -->
        <div class="bg-amber-50 rounded-2xl p-4 border border-amber-100 text-center">
          <p class="text-[11px] text-amber-800 font-extrabold tracking-wider leading-none">预计推广现金收益返佣价值</p>
          <p class="font-serif text-[28px] font-black text-amber-700 mt-2 leading-none">
            ¥ {{ projectedEarnings }}.00 <span class="text-[11px] font-sans font-normal text-amber-900">元</span>
          </p>
          <p class="text-[9.5px] text-amber-900/60 mt-2.5 leading-relaxed">
            * 理论估算值：测算受具体活跃度以及后台各优惠折扣、提现汇率核算最终额为准。
          </p>
        </div>
      </section>

      <!-- Application and Settlement rules -->
      <section class="bg-white rounded-3xl p-5 border border-brand-paper shadow-sm text-left">
        <h3 class="font-serif text-[13.5px] font-bold text-brand-ink-strong mb-3.5 flex items-center gap-1.5 border-b border-gray-50 pb-2">
          <BookOpen :size="15" class="text-brand-primary" />
          <span>提成考核与安全解释</span>
        </h3>

        <div class="space-y-3 font-sans text-[11.5px] leading-relaxed text-brand-secondary">
          <div class="flex gap-2 items-start">
            <Check :size="14" class="text-brand-primary mt-1 shrink-0" />
            <p><b>纯净直邀机制</b>：平台坚定遵纪守法。推广收益仅限于您<b>直接邀请的用户</b>充值额按约结算，无多级裂变、无返款团队层级关系，绿色环保，公开透明。</p>
          </div>
          <div class="flex gap-2 items-start">
            <Check :size="14" class="text-brand-primary mt-1 shrink-0" />
            <p><b>后台结算账变</b>：所有推荐同修充值交易流水由本后台安全数据库精密锁定及追踪，返佣数据与扣税门槛遵循国家财务配置实时折算。</p>
          </div>
          <div class="flex gap-2 items-start">
            <Check :size="14" class="text-brand-primary mt-1 shrink-0" />
            <p><b>安全作弊防范</b>：平台具有高精度算力检测，坚决查禁注册机、非真实用户代买及套刷行为，违规行为一经锁定将清空账户额度并终结合作。</p>
          </div>
        </div>
      </section>

      <!-- Bottom action button -->
      <div class="pt-3">
        <button
          @click="$emit('close')"
          class="w-full py-3 bg-brand-primary text-white text-[13px] font-bold rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md active:scale-95 transition-transform"
        >
          我已晓悟，返回主页
        </button>
      </div>

    </main>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
