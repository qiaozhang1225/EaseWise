<script setup lang="ts">
import { computed, ref } from 'vue';
import { ArrowLeft, Check, Clipboard, Sparkles, Trophy, Users, Wallet } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'back'): void;
}>();

const { state, showToast } = useEaseWiseApp();

const copied = ref(false);

const invitationLink = computed(() => {
  if (typeof window !== 'undefined') {
    const uid = state.user?.id || 'guest';
    return `${window.location.origin}/?ref=${uid.slice(0, 8)}`;
  }
  return 'https://easewise.com/?ref=easewise';
});

function copyLink(): void {
  const value = invitationLink.value;
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(value).then(() => {
      copied.value = true;
      setTimeout(() => copied.value = false, 2000);
    }).catch(() => fallbackCopy(value));
  } else {
    fallbackCopy(value);
  }
}

function fallbackCopy(text: string): void {
  try {
    const el = document.createElement('textarea');
    el.value = text;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    copied.value = true;
    setTimeout(() => copied.value = false, 2000);
  } catch (e) {
    showToast('拷贝推广链接失败，请长按文本手动复制。');
  }
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left">

    <div class="flex items-center gap-2 mb-4 select-none">
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
        <div class="p-2.5 rounded-xl bg-emerald-50 text-emerald-600 shrink-0 select-none">
          <Trophy :size="20" />
        </div>
        <div>
          <h2 class="font-serif text-[17px] font-black text-brand-ink-strong leading-tight">推荐大使推广计划</h2>
          <p class="font-sans text-[10.5px] text-brand-secondary mt-0.5">
            独乐乐不如众乐乐，呼朋唤友共享易学天机。
          </p>
        </div>
      </div>

      <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">
        推荐大使是「易如反掌」专为易学爱好者开设的自助推广佣金奖励活动。每当有新用户通过您的链接注册并获取积分，您不仅可获得推荐点数，若用户产生现金兑付结算，您还将获得高额现金回馈提成。
      </p>
    </div>

    <!-- Stats summary card -->
    <section class="grid grid-cols-2 gap-3 mb-4 select-none">
      <div class="bg-white rounded-xl p-4 border border-brand-paper shadow-sm">
        <div class="flex items-center gap-1.5 text-brand-secondary text-[11px] font-bold mb-1">
          <Users :size="13" />
          <span>成功邀请人数</span>
        </div>
        <p class="font-serif text-[24px] font-black text-brand-ink-strong leading-none">0 <span class="text-[11px] text-brand-secondary font-bold">人</span></p>
      </div>

      <div class="bg-white rounded-xl p-4 border border-brand-paper shadow-sm">
        <div class="flex items-center gap-1.5 text-brand-secondary text-[11px] font-bold mb-1">
          <Wallet :size="13" />
          <span>累计收益现金</span>
        </div>
        <p class="font-serif text-[24px] font-black text-emerald-700 leading-none">0.00 <span class="text-[11px] text-brand-secondary font-bold">元</span></p>
      </div>
    </section>

    <!-- Reward distribution guidelines -->
    <section class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm mb-4 space-y-4">
      <h3 class="font-serif text-[14px] font-black text-brand-ink-strong border-b border-gray-100 pb-2.5 flex items-center gap-1.5 select-none">
        <Sparkles :size="14" class="text-brand-primary" />
        <span>如何获取专属佣金？</span>
      </h3>

      <div class="space-y-4 font-sans text-[12px] leading-relaxed text-brand-secondary">
        <div class="space-y-1">
          <p class="font-bold text-brand-ink-strong">第一步：拷贝专属推荐链接</p>
          <p>在下方栏位复制您的推荐连接，并发送给微信好友、朋友圈或易学交流群中。</p>
        </div>
        <div class="space-y-1">
          <p class="font-bold text-brand-ink-strong">第二步：新用户完成登入</p>
          <p>好友通过您的推广链接打开 EaseWise 并完成注册（手机号或微信登录均可）。</p>
        </div>
        <div class="space-y-1">
          <p class="font-bold text-brand-ink-strong">第三步：返现佣金自动入账</p>
          <p>系统将在后台计算关联链路。凡该好友参与线下积分获取，提成将实时到账大厅。您可以联系客服微信提现。</p>
        </div>
      </div>
    </section>

    <!-- Link copying box -->
    <section class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm mb-4 space-y-3">
      <h3 class="font-serif text-[13px] font-bold text-brand-secondary select-none">您的专属推广链接</h3>
      <div class="flex items-center gap-2 bg-brand-paper border border-gray-200 rounded-xl p-3 select-all">
        <span class="font-mono text-[11.5px] text-brand-ink-strong truncate flex-1 leading-snug">{{ invitationLink }}</span>
        <button
          type="button"
          @click="copyLink"
          class="px-3.5 py-1.5 rounded-lg border font-sans text-[11px] font-black shrink-0 transition-all cursor-pointer outline-none select-none flex items-center gap-1"
          :class="copied
            ? 'bg-emerald-50 border-emerald-200 text-emerald-600'
            : 'bg-white border-brand-primary/20 text-brand-primary hover:bg-brand-primary/5'"
        >
          <component :is="copied ? Check : Clipboard" :size="11" />
          <span>{{ copied ? '已复制' : '复制' }}</span>
        </button>
      </div>
    </section>

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
