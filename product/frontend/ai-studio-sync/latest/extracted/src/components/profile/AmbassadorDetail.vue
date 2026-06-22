<script setup lang="ts">
import { Award, ShieldCheck, HelpCircle, ArrowRight, UserPlus, Coins, Percent } from 'lucide-vue-next';

defineProps<{
  userUid: string;
  isPromoter: boolean;
}>();

defineEmits<{
  (e: 'close'): void;
}>();
</script>

<template>
  <div class="fixed inset-0 z-50 bg-black/45 flex items-center justify-center p-4 backdrop-blur-sm">
    <div class="bg-white rounded-3xl w-full max-w-sm p-6 border border-brand-paper shadow-2xl relative max-h-[85vh] overflow-y-auto no-scrollbar flex flex-col">
      <!-- Header -->
      <div class="flex items-center gap-3 mb-5 border-b pb-3 border-gray-100 shrink-0">
        <div class="w-10 h-10 rounded-xl bg-brand-primary/10 flex items-center justify-center shrink-0">
          <Award :size="20" class="text-brand-primary" />
        </div>
        <div>
          <h3 class="font-serif text-[16px] font-bold text-brand-ink-strong">推广大使</h3>
          <p class="font-sans text-[11px] text-brand-secondary leading-none">分甘同味，结缘互励</p>
        </div>
      </div>

      <!-- Scrollable content area -->
      <div class="space-y-5 text-left font-sans text-[12px] leading-relaxed text-brand-ink flex-1">
        <!-- Benefit Section -->
        <div>
          <h4 class="font-serif text-[12.5px] font-bold text-brand-ink-strong mb-2.5 flex items-center gap-1">
            <Coins :size="13" class="text-brand-primary" />
            <span>核心权益</span>
          </h4>
          <div class="grid grid-cols-1 gap-2.5">
            <div class="p-3 bg-brand-paper/40 rounded-xl border border-gray-100 flex items-start gap-2.5">
              <div class="w-6 h-6 rounded-lg bg-orange-100 flex items-center justify-center shrink-0 text-orange-600 font-bold text-[11px]">
                1
              </div>
              <div>
                <p class="font-serif text-[12px] font-extrabold text-brand-ink-strong">专属推广身份</p>
                <p class="text-[10.5px] text-brand-secondary leading-normal mt-0.5">获得系统专属推广标识，开启合伙人分销渠道。</p>
              </div>
            </div>

            <div class="p-3 bg-brand-paper/40 rounded-xl border border-gray-100 flex items-start gap-2.5">
              <div class="w-6 h-6 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0 text-emerald-600 font-bold text-[11px]">
                2
              </div>
              <div>
                <p class="font-serif text-[12px] font-extrabold text-brand-ink-strong">邀请收益返佣</p>
                <p class="text-[10.5px] text-brand-secondary leading-normal mt-0.5">直邀新用户在平台充值时，按一定比例获取丰厚积分返佣。</p>
              </div>
            </div>

            <div class="p-3 bg-brand-paper/40 rounded-xl border border-gray-100 flex items-start gap-2.5">
              <div class="w-6 h-6 rounded-lg bg-indigo-100 flex items-center justify-center shrink-0 text-indigo-600 font-bold text-[11px]">
                3
              </div>
              <div>
                <p class="font-serif text-[12px] font-extrabold text-brand-ink-strong">收益灵活处理</p>
                <p class="text-[10.5px] text-brand-secondary leading-normal mt-0.5">可在合伙后台自助申请提现、转存积分等灵活核算形式。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tier Threshold Section -->
        <div>
          <h4 class="font-serif text-[12.5px] font-bold text-brand-ink-strong mb-2.5 flex items-center gap-1">
            <Percent :size="13" class="text-brand-primary" />
            <span>等级晋升与考核 threshold</span>
          </h4>
          <div class="grid grid-cols-2 gap-2.5">
            <div class="p-3 bg-zinc-50 border border-thin rounded-xl text-center flex flex-col justify-center">
              <span class="text-[11px] font-serif font-extrabold text-brand-ink-strong">推广大使</span>
              <span class="text-[10px] text-amber-700 font-bold mt-1">累计充值 398 元</span>
            </div>
            <div class="p-3 bg-zinc-50 border border-thin rounded-xl text-center flex flex-col justify-center">
              <span class="text-[11px] font-serif font-extrabold text-brand-ink-strong">尊享合伙人</span>
              <span class="text-[10px] text-amber-700 font-bold mt-1">累计充值 3980 元</span>
            </div>
          </div>
          <p class="text-[10.5px] text-brand-secondary text-center mt-2.5">
            * 最终门槛、特许权限均<b>以后台规则为准</b>，视阶段性调整
          </p>
        </div>

        <!-- Standard Rules Text Area -->
        <div class="p-3.5 bg-brand-paper/30 rounded-2xl border border-gray-100 space-y-2">
          <h4 class="font-serif text-[12px] font-extrabold text-brand-ink-strong mb-1 h-fit flex items-center gap-1">
            <ShieldCheck :size="13" class="text-brand-primary" />
            <span>推广规则与说明</span>
          </h4>
          <ul class="space-y-1.5 text-[11px] text-brand-secondary leading-relaxed pl-1.5 list-disc select-none">
            <li>推广身份需要用户主动申请，并由后台审核通过后生效。</li>
            <li>推广收益只计算直邀用户，不存在团队层级收益。</li>
            <li>返佣比例、提现门槛和结算周期以后台正式配置为准。</li>
            <li>前台默认只展示服务积分，推广收益仅在推广大使相关页面展示。</li>
          </ul>
        </div>
      </div>

      <!-- Footer button -->
      <button
        @click="$emit('close')"
        class="mt-6 w-full py-3 bg-brand-primary text-white text-[12.5px] font-black rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md outline-none border-none active:scale-[0.98] transition-transform"
      >
        我已晓悟退出
      </button>
    </div>
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
