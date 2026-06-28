<script setup lang="ts">
import { ArrowLeft, BookOpen, Compass, ShieldCheck, Sparkles } from 'lucide-vue-next';

defineEmits<{
  (e: 'back'): void;
}>();
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left">

    <div class="flex items-center gap-2 mb-4 select-none">
      <button
        @click="$emit('back')"
        class="text-brand-ink-strong hover:text-brand-primary font-sans text-[12.5px] font-extrabold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none p-1 rounded hover:bg-zinc-100 transition-colors"
      >
        <ArrowLeft :size="16" />
        <span>返回个人中心</span>
      </button>
    </div>

    <div class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm mb-4 space-y-4">
      <div class="flex items-center gap-3">
        <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0 select-none">
          <BookOpen :size="20" />
        </div>
        <div>
          <h2 class="font-serif text-[17px] font-black text-brand-ink-strong leading-tight">系统机理与易学承袭</h2>
          <p class="font-sans text-[10.5px] text-brand-secondary mt-0.5">
            EaseWise 「易如反掌」的数理算法与流派承袭声明
          </p>
        </div>
      </div>

      <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">
        EaseWise 「易如反掌」是一款结合古法玄学数理模型与现代多模态大语言模型的决策辅助智能系统。
        我们通过数字建模还原古典玄学推演精髓，并在生成评述过程中引入专业易学语料库进行对齐微调。
      </p>
    </div>

    <!-- Metaphysical Pillars introduction -->
    <div class="space-y-3 mb-4 select-none">
      <div class="bg-white rounded-xl p-4.5 border border-brand-paper shadow-sm space-y-2">
        <div class="flex items-center gap-2 text-brand-primary-strong">
          <Compass :size="15" />
          <h3 class="font-serif text-[13.5px] font-black">1. 数字奇门卦象评测</h3>
        </div>
        <p class="font-sans text-[11px] text-brand-secondary leading-relaxed">
          源于《奇门遁甲》“时家奇门”与数理磁场理论。手机号作为日常高频使用的“磁场符咒”，其天干地支组合对持有人的五行场强具有明显的调和与偏转作用。
          我们的排盘算法结合“九星、八门、八神”落宫，深入分析其在财富、感情、事业上的吉凶暗示。
        </p>
      </div>

      <div class="bg-white rounded-xl p-4.5 border border-brand-paper shadow-sm space-y-2">
        <div class="flex items-center gap-2 text-brand-primary-strong">
          <Sparkles :size="15" />
          <h3 class="font-serif text-[13.5px] font-black">2. 四柱八字先天命盘</h3>
        </div>
        <p class="font-sans text-[11px] text-brand-secondary leading-relaxed">
          遵循宋代徐子平所著的《子平真诠》与明代万民英的《三命通会》正宗八字派系。
          结合天文算法对出生地区进行真太阳时（True Solar Time）校准，推算十天干与十二地支，精准精排藏干、地势、旬空、神煞、以及纳音。
          在此基础上，推演大运、流年，助您趋吉避凶。
        </p>
      </div>

      <div class="bg-white rounded-xl p-4.5 border border-brand-paper shadow-sm space-y-2">
        <div class="flex items-center gap-2 text-brand-primary-strong">
          <ShieldCheck :size="15" />
          <h3 class="font-serif text-[13.5px] font-black">3. 免责及理性认知声明</h3>
        </div>
        <p class="font-sans text-[11px] text-brand-secondary leading-relaxed">
          易学之理，旨在趋吉避凶、修身养性。系统所得任何测算分数及评语仅供生活、工作和谋事决策时的娱乐辅助参考，不作为绝对性、法律性或医学性的指导意见。
          命自我造，福自我求，请持客观理性之眼光探讨易学。
        </p>
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
