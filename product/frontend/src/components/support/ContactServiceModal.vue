<script setup lang="ts">
import { computed, ref } from 'vue';
import { Check, Copy, QrCode, X } from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const {
  state,
  customerServiceWechatId,
  customerServiceQrCodeUrl,
  customerServiceQrGuidanceText,
  customerServiceCopyButtonText,
  customerServiceUnconfiguredText,
  customerServiceCopyForScene,
  closeCustomerServiceModal,
} = useEaseWiseApp();

const copied = ref(false);
const copyError = ref('');
const qrCodeFailed = ref(false);

const visible = computed(() => state.contactServiceModalVisible);
const scene = computed(() => state.contactServiceScene);
const description = computed(() => customerServiceCopyForScene(scene.value));
const wechatId = computed(() => customerServiceWechatId.value.trim());
const hasWechatId = computed(() => Boolean(wechatId.value));
const hasQrCode = computed(() => Boolean(customerServiceQrCodeUrl.value && !qrCodeFailed.value));
const copyButtonLabel = computed(() => customerServiceCopyButtonText.value.trim() || '复制微信');

async function copyWechatId(): Promise<void> {
  if (!hasWechatId.value) {
    return;
  }
  copyError.value = '';
  try {
    await copyTextToClipboard(wechatId.value);
    copied.value = true;
    window.setTimeout(() => {
      copied.value = false;
    }, 1800);
  } catch {
    copyError.value = '复制失败，请手动长按或选中微信号复制。';
  }
}

async function copyTextToClipboard(text: string): Promise<void> {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const input = document.createElement('textarea');
  input.value = text;
  input.setAttribute('readonly', 'true');
  input.style.position = 'fixed';
  input.style.left = '-9999px';
  input.style.top = '0';
  document.body.appendChild(input);
  input.focus();
  input.select();

  try {
    if (!document.execCommand('copy')) {
      throw new Error('copy_failed');
    }
  } finally {
    document.body.removeChild(input);
  }
}

function handleClose(): void {
  copied.value = false;
  copyError.value = '';
  closeCustomerServiceModal();
}
</script>

<template>
  <transition name="contact-fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-[220] flex items-center justify-center bg-slate-950/45 px-5 py-8 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
    >
      <div class="relative w-full max-w-[360px] overflow-hidden rounded-[28px] border border-white/70 bg-[#fffaf0] shadow-2xl shadow-slate-950/20">
        <div class="absolute -top-16 -right-16 h-36 w-36 rounded-full bg-brand-primary/10 blur-2xl"></div>
        <div class="absolute -bottom-20 -left-20 h-40 w-40 rounded-full bg-amber-300/20 blur-2xl"></div>

        <button
          type="button"
          class="absolute right-4 top-4 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-brand-secondary shadow-sm outline-none transition-colors hover:text-brand-ink-strong"
          @click="handleClose"
        >
          <X :size="15" />
        </button>

        <div class="relative space-y-5 px-5 pb-5 pt-6 text-center">
          <div class="space-y-1.5 px-7">
            <p class="font-sans text-[10px] font-black uppercase tracking-[0.22em] text-brand-primary">Customer Service</p>
            <h3 class="font-serif text-[22px] font-black leading-tight text-brand-ink-strong">联系客服</h3>
            <p class="font-sans text-[11px] leading-relaxed text-brand-secondary">
              {{ description }}
            </p>
          </div>

          <div class="rounded-[24px] border border-brand-primary/10 bg-white/85 p-4 shadow-sm">
            <div class="mx-auto flex h-48 w-48 items-center justify-center overflow-hidden rounded-[20px] border border-dashed border-brand-primary/20 bg-brand-paper/70">
              <img
                v-if="hasQrCode"
                :src="customerServiceQrCodeUrl"
                alt="客服二维码"
                class="h-full w-full object-cover"
                @error="qrCodeFailed = true"
              />
              <div v-else class="flex flex-col items-center gap-2 px-5 text-center text-brand-secondary">
                <QrCode :size="32" class="text-brand-primary/55" />
                <p class="font-sans text-[11px] leading-relaxed">客服二维码暂未配置</p>
              </div>
            </div>
            <p class="mt-3 font-sans text-[10.5px] leading-relaxed text-brand-secondary">
              {{ customerServiceQrGuidanceText }}
            </p>
          </div>

          <div class="rounded-[20px] border border-gray-100 bg-white/90 p-3 text-left">
            <p class="font-sans text-[10px] font-bold text-brand-secondary">客服微信号</p>
            <div class="mt-1.5 flex items-center justify-between gap-3">
              <span class="min-w-0 break-all font-mono text-[15px] font-black text-brand-ink-strong">
                {{ hasWechatId ? wechatId : '后台暂未配置' }}
              </span>
              <button
                type="button"
                class="shrink-0 rounded-xl px-3 py-2 font-sans text-[11px] font-black shadow-sm outline-none transition-all"
                :class="hasWechatId ? 'bg-brand-primary text-white hover:bg-brand-primary-strong' : 'cursor-not-allowed bg-gray-100 text-gray-400'"
                :disabled="!hasWechatId"
                @click="copyWechatId"
              >
                <span class="inline-flex items-center gap-1">
                  <Check v-if="copied" :size="12" />
                  <Copy v-else :size="12" />
                  <span>{{ copied ? '已复制' : copyButtonLabel }}</span>
                </span>
              </button>
            </div>
            <p v-if="!hasWechatId" class="mt-2 font-sans text-[10px] leading-relaxed text-amber-700">
              {{ customerServiceUnconfiguredText }}
            </p>
            <p v-else-if="copyError" class="mt-2 font-sans text-[10px] leading-relaxed text-red-600">
              {{ copyError }}
            </p>
          </div>

          <p class="px-2 font-sans text-[10px] leading-relaxed text-brand-secondary">
            本平台所有内容仅供娱乐，并无参考价值。
          </p>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.contact-fade-enter-active,
.contact-fade-leave-active {
  transition: opacity 0.18s ease;
}

.contact-fade-enter-from,
.contact-fade-leave-to {
  opacity: 0;
}
</style>
