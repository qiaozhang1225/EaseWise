<script setup lang="ts">
import { ref, computed } from 'vue';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { X, Copy, CheckCircle, MessageSquare, AlertCircle, HelpCircle } from 'lucide-vue-next';

const { 
  state, customerServiceContact, customerServiceQrCodeUrl, customerServiceQrGuidanceText, 
  customerServiceCopyButtonText, customerServiceUnconfiguredText, customerServiceCopyForScene,
  customerServiceWechatId, closeCustomerServiceModal 
} = useEaseWiseApp();

const copySuccess = ref(false);
const qrCodeFailed = ref(false);

const curSupportText = computed(() => {
  return customerServiceCopyForScene(state.contactServiceScene);
});

const isConfigured = computed(() => {
  const wid = customerServiceWechatId.value;
  return Boolean(wid && wid.trim() !== '');
});

async function handleCopy() {
  if (!isConfigured.value) return;
  try {
    const textToCopy = customerServiceContact.value;
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(textToCopy);
      copySuccess.value = true;
      setTimeout(() => copySuccess.value = false, 2000);
    } else {
      const textArea = document.createElement("textarea");
      textArea.value = textToCopy;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      copySuccess.value = true;
      setTimeout(() => copySuccess.value = false, 2000);
    }
  } catch (err) {
    // Falls back silently
  }
}
</script>

<template>
  <transition name="fade">
    <div 
      v-if="state.contactServiceModalVisible" 
      class="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-3xl w-full max-w-sm p-6 border border-brand-paper shadow-2xl relative text-left">
        <!-- Close icon -->
        <button 
          @click="closeCustomerServiceModal"
          class="absolute top-4.5 right-4.5 text-brand-secondary/50 hover:text-brand-ink-strong cursor-pointer p-1.5 rounded-full hover:bg-gray-100 border-none bg-transparent outline-none transition-colors"
        >
          <X :size="16" />
        </button>

        <!-- Header info -->
        <div class="flex items-center gap-2.5 mb-4">
          <div class="p-2.5 rounded-xl bg-brand-primary/10 text-brand-primary shrink-0 select-none">
            <MessageSquare :size="18" />
          </div>
          <h2 class="font-serif text-[16px] font-bold text-brand-ink-strong leading-none">
            官方在线客服同修群
          </h2>
        </div>

        <!-- Dynamic Context description -->
        <p class="font-sans text-[11.5px] text-brand-secondary leading-relaxed bg-brand-paper/50 rounded-xl p-3.5 border border-thin border-gray-100/70 mb-4 select-text font-medium">
          {{ curSupportText }}
        </p>

        <!-- Unconfigured state fallback visual -->
        <div v-if="!isConfigured" class="py-6 px-4 bg-zinc-50 rounded-2xl border border-dashed text-center">
          <AlertCircle :size="24" class="text-zinc-400 mx-auto mb-2" />
          <p class="font-sans text-[12px] text-zinc-500 font-bold">
            {{ customerServiceUnconfiguredText || '客服专线尚未配置，请联系阁内管理员。' }}
          </p>
        </div>

        <div v-else class="space-y-4">
          <!-- QR Code section -->
          <div class="flex flex-col items-center justify-center bg-zinc-50 rounded-2xl p-4 border border-dashed border-gray-250 text-center">
            <img 
              v-if="customerServiceQrCodeUrl && !qrCodeFailed" 
              :src="customerServiceQrCodeUrl" 
              @error="qrCodeFailed = true"
              referrerpolicy="no-referrer"
              class="w-36 h-36 object-cover rounded-xl shadow-md border-2 border-white select-none pointer-events-none" 
            />
            <div v-else class="w-36 h-36 bg-gray-100 rounded-xl flex flex-col items-center justify-center border text-zinc-400 p-2">
              <HelpCircle :size="24" class="mb-1.5 text-zinc-300" />
              <span class="text-[10px] text-zinc-450 leading-relaxed">二维码加载失败或未部署</span>
            </div>
            <span class="font-sans text-[10px] text-zinc-500 mt-2.5 leading-normal max-w-[85%] block select-none">
              {{ customerServiceQrGuidanceText }}
            </span>
          </div>

          <!-- Copy entries -->
          <div class="space-y-3 text-center">
            <div class="flex items-center justify-between bg-brand-paper rounded-xl px-4 py-2.5 border border-gray-100">
              <span class="font-sans text-[11px] text-brand-secondary select-none">专属客服微信号</span>
              <span class="font-mono text-[12.5px] font-extrabold text-brand-ink-strong select-all">{{ customerServiceContact }}</span>
            </div>

            <button 
              @click="handleCopy"
              class="w-full bg-brand-primary hover:bg-brand-primary/95 text-white py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold shadow-md active:scale-95 transition-transform border-none flex items-center justify-center gap-1.5 outline-none select-none"
            >
              <CheckCircle v-if="copySuccess" :size="14" class="text-white" />
              <Copy v-else :size="14" class="text-white" />
              <span>{{ copySuccess ? '已经复制到系统剪贴板！' : customerServiceCopyButtonText }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
