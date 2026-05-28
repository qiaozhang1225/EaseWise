<script setup lang="ts">
import {
  ArrowLeft,
  BadgeCheck,
  CheckCircle2,
  Coins,
  Gift,
  Share2,
  ShieldCheck,
  Sparkles,
  Users,
  WalletCards,
} from 'lucide-vue-next';

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const benefitCards = [
  {
    title: '专属推广身份',
    desc: '达成准入条件并审核通过后，可获得推广大使身份与专属推广入口。',
    icon: BadgeCheck,
  },
  {
    title: '邀请收益返佣',
    desc: '直邀用户完成符合规则的订单后，可按身份等级获得推广收益。',
    icon: Coins,
  },
  {
    title: '收益灵活处理',
    desc: '推广收益可按正式规则申请提现，或转换为服务积分继续使用。',
    icon: WalletCards,
  },
];

const thresholds = [
  { label: '普通推广大使', value: '累计充值 398 元', desc: '适合刚开始推广的用户' },
  { label: '高级推广大使', value: '累计充值 3980 元', desc: '适合持续推广与深度合作用户' },
];

const rules = [
  '推广身份需要用户主动申请，并由后台审核通过后生效。',
  '推广收益只计算直邀用户，不存在团队层级收益。',
  '返佣比例、提现门槛和结算周期以后台正式配置为准。',
  '前台默认只展示服务积分，推广收益仅在推广大使相关页面展示。',
];
</script>

<template>
  <div class="min-h-dvh max-w-md mx-auto bg-brand-paper text-brand-ink-strong font-sans text-left relative overflow-x-hidden">
    <header class="fixed top-0 left-0 right-0 z-50 max-w-md mx-auto bg-brand-paper/90 backdrop-blur-md border-b border-gray-100">
      <div class="h-16 px-margin-mobile flex items-center justify-between">
        <button
          type="button"
          class="w-10 h-10 rounded-full bg-white border border-gray-100 shadow-sm flex items-center justify-center text-brand-ink-strong active:scale-95 transition-all outline-none cursor-pointer"
          aria-label="返回我的页面"
          @click="emit('back')"
        >
          <ArrowLeft :size="19" />
        </button>
        <h1 class="font-serif text-[19px] leading-none font-bold tracking-wide text-brand-ink-strong">
          推广大使
        </h1>
        <div class="w-10 h-10"></div>
      </div>
    </header>

    <main class="pt-16 pb-12">
      <section class="px-margin-mobile pt-4">
        <div class="relative overflow-hidden rounded-2xl bg-brand-ink-strong text-white p-5 shadow-md">
          <div class="absolute -right-8 -top-10 w-32 h-32 rounded-full border border-white/10"></div>
          <div class="absolute -right-3 bottom-4 text-white/5">
            <Share2 :size="108" />
          </div>

          <div class="relative z-10 space-y-4">
            <div class="inline-flex items-center gap-1.5 rounded-full bg-brand-accent/15 border border-brand-accent/30 px-3 py-1 text-brand-accent font-sans text-[11px] font-bold">
              <Sparkles :size="13" class="shrink-0" />
              <span>邀请同行 · 共修共赢</span>
            </div>

            <div class="space-y-2">
              <h2 class="font-serif text-[26px] leading-tight font-bold tracking-wide">
                成为易如反掌推广大使
              </h2>
              <p class="font-sans text-[13px] leading-relaxed text-white/75">
                邀请好友使用手机号评测、智能体与后续服务能力，符合正式规则的订单可获得推广收益。
              </p>
            </div>

            <div class="grid grid-cols-3 gap-2.5 pt-1">
              <div class="rounded-xl bg-white/8 border border-white/10 p-3 text-center">
                <p class="font-serif text-[18px] leading-none font-bold text-brand-accent">2级</p>
                <p class="mt-1 font-sans text-[10px] text-white/60">身份体系</p>
              </div>
              <div class="rounded-xl bg-white/8 border border-white/10 p-3 text-center">
                <p class="font-serif text-[18px] leading-none font-bold text-brand-accent">直邀</p>
                <p class="mt-1 font-sans text-[10px] text-white/60">收益来源</p>
              </div>
              <div class="rounded-xl bg-white/8 border border-white/10 p-3 text-center">
                <p class="font-serif text-[18px] leading-none font-bold text-brand-accent">审核</p>
                <p class="mt-1 font-sans text-[10px] text-white/60">开通方式</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center justify-between gap-3 mb-4">
            <div>
              <p class="font-serif text-[18px] leading-tight font-bold text-brand-ink-strong">推广权益</p>
              <p class="mt-1 font-sans text-[11px] text-brand-secondary">身份、收益与服务支持统一展示</p>
            </div>
            <div class="w-9 h-9 rounded-full bg-brand-primary/10 text-brand-primary flex items-center justify-center shrink-0">
              <Gift :size="17" />
            </div>
          </div>

          <div class="space-y-3">
            <div
              v-for="item in benefitCards"
              :key="item.title"
              class="rounded-xl bg-brand-paper/60 border border-gray-100 p-3.5 flex gap-3"
            >
              <div class="w-9 h-9 rounded-full bg-white text-brand-primary flex items-center justify-center shrink-0 shadow-sm">
                <component :is="item.icon" :size="17" />
              </div>
              <div class="min-w-0">
                <p class="font-sans text-[13px] leading-tight font-bold text-brand-ink-strong">{{ item.title }}</p>
                <p class="mt-1 font-sans text-[11px] leading-relaxed text-brand-secondary">{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-9 h-9 rounded-full bg-brand-accent/40 text-brand-ink-strong flex items-center justify-center shrink-0">
              <Users :size="17" />
            </div>
            <div>
              <p class="font-serif text-[18px] leading-tight font-bold text-brand-ink-strong">准入门槛</p>
              <p class="mt-1 font-sans text-[11px] text-brand-secondary">门槛数值以后端正式规则配置为准</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="item in thresholds"
              :key="item.label"
              class="rounded-xl border border-brand-primary/10 bg-brand-primary/5 p-3"
            >
              <p class="font-sans text-[11px] font-bold text-brand-primary leading-tight">{{ item.label }}</p>
              <p class="mt-2 font-serif text-[18px] font-bold text-brand-ink-strong leading-tight">{{ item.value }}</p>
              <p class="mt-1 font-sans text-[10px] leading-relaxed text-brand-secondary">{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-4">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-9 h-9 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <ShieldCheck :size="17" />
            </div>
            <div>
              <p class="font-serif text-[18px] leading-tight font-bold text-brand-ink-strong">规则说明</p>
              <p class="mt-1 font-sans text-[11px] text-brand-secondary">推广收益与服务积分分开展示</p>
            </div>
          </div>

          <div class="space-y-3">
            <div
              v-for="rule in rules"
              :key="rule"
              class="flex items-start gap-2.5"
            >
              <CheckCircle2 :size="15" class="mt-0.5 text-brand-primary shrink-0" />
              <p class="font-sans text-[12px] leading-relaxed text-brand-ink">{{ rule }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="px-margin-mobile mt-5">
        <div class="rounded-2xl bg-brand-primary text-white p-4 shadow-md flex items-center justify-between gap-4">
          <div>
            <p class="font-serif text-[17px] leading-tight font-bold">准备申请推广大使？</p>
            <p class="mt-1 font-sans text-[11px] leading-relaxed text-white/75">请通过客服或正式申请入口完成身份开通。</p>
          </div>
          <button
            type="button"
            class="px-4 py-2 rounded-xl bg-white text-brand-primary font-sans text-[12px] font-bold shrink-0 active:scale-95 transition-all cursor-pointer outline-none"
          >
            了解规则
          </button>
        </div>
      </section>
    </main>
  </div>
</template>
