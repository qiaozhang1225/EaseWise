<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { Check, Clipboard, MessageSquare, QrCode, Sparkles, X } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const { state, closeCustomerServiceModal, humanizeError } = useEaseWiseApp();

const visible = computed(() => state.customerServiceModalVisible);
const scene = computed(() => state.customerServiceScene || 'default');
const debugInfo = ref('');
const copied = ref(false);

const contactDetails = computed(() => {
  const cfg = state.runtimeConfig?.customer_service;
  return {
    wechatId: cfg?.wechat_id || 'easewise_support',
    email: cfg?.email || 'support@easewise.com',
    qrCodeUrl: cfg?.qr_code_url || '',
    note: cfg?.working_hours || '服务时间：每日 09:00 - 22:00（微信回复极速）',
  };
});

const isInsufficientPoints = computed(() => scene.value === 'points_insufficient');
const isAccountSecurity = computed(() => scene.value === 'account_security');

const displayTitle = computed(() => {
  if (isInsufficientPoints.value) return '积分额度获取';
  if (isAccountSecurity.value) return '账号密保核验';
  return '联系在线客服';
});

const displayDescription = computed(() => {
  if (isInsufficientPoints.value) {
    return '由于当前为 H5 线下结算，你可以联系客服或加入微信群，获取积分及活动额度。';
  }
  if (isAccountSecurity.value) {
    return '如需找回密码、绑定微信、或遇到账号登录受阻，可联系在线客服人工核对处理。';
  }
  return '加入官方客服微信群，不仅可获取测试积分，更能参与每日命理交流。';
});

watch(scene, (newScene) => {
  if (newScene && newScene !== 'default') {
    debugInfo.value = String(state.customerServiceMetadata || '');
  } else {
    debugInfo.value = '';
  }
});

function copyWechatId(): void {
  const value = contactDetails.value.wechatId;
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(value).then(() => {
      triggerCopiedFeedback();
    }).catch(() => {
      fallbackCopy(value);
    });
  } else {
    fallbackCopy(value);
  }
}

function fallbackCopy(text: string): void {
  try {
    const input = document.createElement('input');
    input.value = text;
    input.setAttribute('readonly', '');
    input.style.position = 'absolute';
    input.style.left = '-9999px';
    document.body.appendChild(input);
    input.select();
    const result = document.execCommand('copy');
    document.body.removeChild(input);
    if (result) {
      triggerCopiedFeedback();
    }
  } catch (err) {
    console.error('Fallback copy failed', err);
  }
}

function triggerCopiedFeedback(): void {
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 2000);
}
</script>

<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-[100] bg-slate-900/40 backdrop-blur-md flex items-center justify-center p-4"
      @click.self="closeCustomerServiceModal"
    >
      <div class="w-full max-w-sm bg-white border border-brand-primary/15 rounded-3xl overflow-hidden shadow-2xl relative text-left">
        <div class="absolute -top-12 -right-12 text-brand-primary/[0.015] font-serif font-black text-[160px] pointer-events-none select-none">
          ☯
        </div>

        <button
          type="button"
          class="absolute top-4 right-4 w-7 h-7 rounded-full bg-gray-50 border border-gray-100 hover:bg-gray-100 text-gray-400 hover:text-gray-600 flex items-center justify-center hover:scale-105 active:scale-95 transition-all outline-none cursor-pointer z-10"
          @click="closeCustomerServiceModal"
        >
          <X :size="14" />
        </button>

        <div class="p-6 text-center space-y-4">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 select-none text-brand-primary">
            <MessageSquare :size="22" />
          </div>

          <div class="space-y-1.5 px-3">
            <h3 class="font-serif text-[17px] font-black text-brand-ink-strong leading-tight">
              {{ displayTitle }}
            </h3>
            <p class="text-[11px] text-brand-secondary leading-relaxed">
              {{ displayDescription }}
            </p>
          </div>

          <div class="bg-brand-paper/50 rounded-2xl p-4.5 border border-thin text-left space-y-3.5">
            <div class="flex items-center justify-between gap-3">
              <div class="space-y-0.5">
                <span class="text-[9px] text-brand-secondary font-extrabold uppercase tracking-wider block">专属客服微信</span>
                <span class="font-mono text-[14px] font-black text-brand-ink-strong tracking-wide">{{ contactDetails.wechatId }}</span>
              </div>
              <button
                type="button"
                @click="copyWechatId"
                class="px-3.5 py-1.5 rounded-xl border font-sans text-[11px] font-black transition-all flex items-center gap-1 cursor-pointer outline-none select-none"
                :class="copied
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-600'
                  : 'bg-white border-brand-primary/20 text-brand-primary hover:bg-brand-primary/5 active:scale-95'"
              >
                <component :is="copied ? Check : Clipboard" :size="12" />
                <span>{{ copied ? '已复制' : '复制微信' }}</span>
              </button>
            </div>

            <div v-if="contactDetails.qrCodeUrl" class="border-t border-gray-100 pt-3.5 flex flex-col items-center">
              <span class="text-[9px] text-brand-secondary font-extrabold uppercase tracking-wider block mb-2">长按二维码极速扫码加入</span>
              <img :src="contactDetails.qrCodeUrl" alt="客服二维码" class="w-32 h-32 border border-gray-100 rounded-xl bg-white shadow-sm" />
            </div>
            <div v-else class="border-t border-[#EAEFF8] pt-3 flex items-start gap-2 text-[#64748B] text-[10px] leading-relaxed select-none">
              <QrCode :size="14" class="text-brand-primary shrink-0 mt-0.5" />
              <span>支持微信扫码加群，若复制微信号后无法搜到，可致信邮箱 <span class="font-mono font-bold">{{ contactDetails.email }}</span></span>
            </div>
          </div>

          <div v-if="debugInfo" class="text-left bg-zinc-50 border border-zinc-150 rounded-xl p-3 select-text max-h-[80px] overflow-y-auto no-scrollbar">
            <span class="text-[8.5px] text-zinc-400 font-black block mb-0.5">场景附言 (故障排查)</span>
            <p class="font-mono text-[10px] text-zinc-500 leading-tight break-all">{{ debugInfo }}</p>
          </div>

          <p class="text-[9.5px] text-brand-secondary/80 select-none">
            {{ contactDetails.note }}
          </p>
        </div>
      </div>
    </div>
  </transition>
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

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
